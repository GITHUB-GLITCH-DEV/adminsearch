from sys import argv
import requests
import os
import threading
import time
import tldextract
import zipfile
from urllib.parse import urlparse

def print_help():
    print("""
    Welcome to AdminSearch!
    
    Usage:
    python script.py --u <URL> [options]

    Options:
    --u, --url <URL>       Specify the target URL.
    --subdom               Scan for subdomains.
    --display              Display HTTP responses for each page.
    --h                    Show this help menu.

    Example:
    python adminsearch.py --u https://example.com --subdom --display
    """)

def check_for_updates():
    repo_owner = "GITHUB-GLITCH-DEV"
    repo_name = "adminsearch"
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    response = requests.get(url)
    if response.status_code == 200:
        latest_version = response.json()["tag_name"]
        print(f"Latest version available: {latest_version}")
        update = input("Do you want to update? (y/n): ")
        if update.lower() == 'y':
            download_and_extract(repo_owner, repo_name, latest_version)

def download_and_extract(repo_owner, repo_name, version):
    url = f"https://github.com/{repo_owner}/{repo_name}/archive/{version}.zip"
    zip_file = f"{repo_name}-{version}.zip"
    os.system(f"wget {url}")
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall()
    print("Update successful.")
    os.remove(zip_file)

word_args = argv[1:]

options = []
values = {}

i = 0
while i < len(word_args):
    if word_args[i].startswith('-'):
        option = word_args[i]
        options.append(option)
        if i + 1 < len(word_args) and not word_args[i+1].startswith('-'):
            value = word_args[i+1]
            values[option] = value
            i += 1
        else:
            pass
    else:
        values[f"value_{i}"] = word_args[i]
    i += 1

if "--h" in options or "--help" in options or len(options) <= 0:
    print_help()
    exit()

check_for_updates()

url = values.get('--u') or values.get("--url")
if url is None and len(options) > 0:
    print("Please provide a valid URL. Example usage: --u https://example.com or --url https://example.com")
else:
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    hostname = parsed_url.hostname
    if scheme and hostname:
        url = f"{scheme}://{hostname}"
    else:
        print("Invalid URL provided.")
        exit(1)

    if "--subdom" in options:
        found_domains = []
        tld_info = tldextract.extract(url)
        tld = tld_info.suffix
        with open("./subdom_wordlist.txt", "r") as f:
            for line in f:
                res = requests.get(f"{scheme}://{line.strip()}.{hostname}")
                if "--display" in options:
                    print(f"[{res.status_code}] - {scheme}://{line.strip()}.{hostname}")
                
    else:
        found_pages = []
        print("Starting Admin Search...")

        def check_page(url, path):
            try:
                r = requests.get(f"{url}{path}", timeout=5)
                if "--display" in options:
                    print(f"[{r.status_code}] - {url}{path}")
                if r.status_code != 404:
                    found_pages.append(path)
            except requests.exceptions.RequestException as e:
                pass

        threads = []
        with open("./wordlist.txt", "r") as f:
            for line in f:
                t = threading.Thread(target=check_page, args=(url, line.strip()))
                threads.append(t)
                t.start()

        def interrupt_threads():
            for thread in threads:
                thread.cancel()

        timer = threading.Timer(6.0, interrupt_threads)
        timer.start()

        for t in threads:
            t.join()

        timer.cancel()

        print(f"Admin Search has finished.")
        print("Found pages:")
        for page in found_pages:
            print(page)
