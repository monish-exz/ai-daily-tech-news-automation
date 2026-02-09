import subprocess
import sys
import os

def run_command(command):
    print(f"[*] Running: {command}")
    try:
        subprocess.check_call(command, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[!] Error running command: {e}")
        return False

def main():
    print("="*50)
    print("       AI News Scraper - Project Setup")
    print("="*50)

    # 1. Install requirements
    print("\n[*] Step 1: Installing Python dependencies...")
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt"):
        print("[!] Failed to install requirements. Please check your internet connection.")
        return

    # 2. Install Playwright browsers
    print("\n[*] Step 2: Installing Playwright browsers...")
    if not run_command(f"{sys.executable} -m playwright install chromium"):
        print("[!] Failed to install Playwright browsers.")
        print("[!] Dynamic scraping (Reddit, JS-heavy sites) might not work.")
    else:
        print("[+] Playwright browsers installed successfully.")

    # 3. Create necessary directories
    print("\n[*] Step 3: Creating project directories...")
    folders = ["data/raw data", "data/cleaned", "logs"]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"[+] Created/verified: {folder}")

    print("\n" + "="*50)
    print("[+] Setup complete! You can now run the scraper using:")
    print("    python main.py")
    print("="*50)

if __name__ == "__main__":
    main()
