#!/bin/python3
import sys
import requests

def query_domains(ip):
    url = f"https://api.webscan.cc?action=query&ip={ip}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

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
            elif response.status_code in [403, 404]:
                pass  # Skip 403 and 404 errors
            else:
                final_url = response.url
                if final_url != full_url:
                    results.append(f"{response.status_code} - {final_url}")
        except requests.Timeout:
            pass  # Skip Timeout errors
        except requests.RequestException as e:
            pass  # Skip any other RequestException errors
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else:
        ip = input("Enter the IP address: ")
    
    domains_data = query_domains(ip)
    for entry in domains_data:
        domain = entry['domain']
        if domain:
            print(f"Checking domain: {domain}")
            results = check_admin_paths(domain)
            for result in results:
                print("                 " + result)
