import subprocess
import sys

def install_requirements():
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("All required libraries have been successfully installed. You are ready to go!")
    except subprocess.CalledProcessError:
        print("Error: Unable to install required modules.")
        sys.exit(1)

if __name__ == "__main__":
    install_requirements()