#!/usr/bin/python3

import requests

def query_domains(ip):
    url = f"https://api.webscan.cc?action=query&ip={ip}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
        return []

def check_admin_paths(domain):
    paths = ["/admin", "/admin.php", "/admin.asp", "/admin.aspx", "/dede"]
    results = []
    for path in paths:
        full_url = f"http://{domain}{path}"
        try:
            response = requests.get(full_url, allow_redirects=True, timeout=7)
            if response.status_code == 200:
                if "404" not in response.text:
                    results.append(f"200 - {full_url}")
            else:
                final_url = response.url
                if final_url != full_url:
                    results.append(f"{response.status_code} - {final_url}")
        except requests.Timeout:
            results.append(f"Timeout accessing {full_url}")
        except requests.RequestException as e:
            results.append(f"Error accessing {full_url}: {e}")
    return results

if __name__ == "__main__":
    ip = input("Enter the IP address: ")
    domains_data = query_domains(ip)
    for entry in domains_data:
        domain = entry['domain']
        if domain:
            print(f"Checking domain: {domain}")
            results = check_admin_paths(domain)
            for result in results:
                print("                 " + result)
