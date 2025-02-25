import os

def install_packages():
    print("[+] Installing required packages...")
    os.system("pip install requests pyfiglet googlesearch-python beautifulsoup4 python-nmap whois dnspython")
    print("[+] Installation complete!")

if __name__ == "__main__":
    install_packages()