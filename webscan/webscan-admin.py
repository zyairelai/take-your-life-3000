#!/usr/bin/python3

import requests
import sys

def check_paths(domains, paths):
    valid_urls = []

    for domain in domains:
        print(f"Checking domain: {domain}")
        domain_valid_urls = []

        for path in paths:
            url = f"http://{domain}{path}"
            try:
                response = requests.get(url, allow_redirects=True)
                if response.status_code == 200:
                    domain_valid_urls.append(url)
                    print(f"                 200 - {url}")
            except requests.RequestException:
                pass  # Silently ignore any request exceptions

        valid_urls.extend(domain_valid_urls)

    return valid_urls

def main():
    if len(sys.argv) != 2:
        print("Usage: ./webscan-admin <input>.txt")
        return

    input_file = sys.argv[1]
    output_file = input_file.replace('.txt', '-admin.txt')
    paths = ["/admin", "/admin.php", "/admin.asp", "/admin.aspx"]

    try:
        with open(input_file, 'r') as file:
            domains = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    valid_urls = check_paths(domains, paths)

    if valid_urls:
        with open(output_file, 'w') as outfile:
            for url in valid_urls:
                outfile.write(url + '\n')
        print(f"\n[+] Valid URLs have been written to {output_file}")
    else:
        print("\n[+] No valid URLs found.")

if __name__ == "__main__":
    main()
