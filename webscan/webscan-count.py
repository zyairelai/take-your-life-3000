#!/bin/python3

import requests

def query_domain(ip):
    url = 'https://api.webscan.cc'
    data = {
        'action': 'query',
        'ip': ip.strip()
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        result = response.json()
        return len(result) if result else 0
    else:
        return 0

def count_domains_from_file(file_path):
    with open(file_path, 'r') as f:
        ip_list = f.readlines()
    counts = []
    for ip in ip_list:
        counts.append(query_domain(ip))
    return counts

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: ./run.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    domain_counts = count_domains_from_file(input_file)
    for count in domain_counts:
        print(count)
