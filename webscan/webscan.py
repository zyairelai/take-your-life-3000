#!/usr/bin/python3

import requests
import json
import sys

def query_domains(ip):
    # Replace dots with hyphens for the output filename
    # formatted_ip = ip.replace('.', '-')
    # output_filename = f"{formatted_ip}.txt"
    output_filename = ip + ".txt"

    url = f"https://api.webscan.cc?action=query&ip={ip}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if not data:
            print(f"[+] No domain is associated with the given IP {ip}")
            return

        urls = [entry['domain'] for entry in data]

        # Sort and make URLs unique
        urls = sorted(set(urls))

        # Print the sorted URLs
        for url in urls:
            print(url)

        # Write the sorted URLs to the output file
        with open(output_filename, 'w') as outfile:
            for url in urls:
                outfile.write(url + '\n')

        print(f"\n[+] Sorted URLs have been written to {output_filename}")
    else:
        print("Failed to retrieve data. Status code:", response.status_code)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else:
        ip = input("Enter the IP address: ")

    query_domains(ip)

# To use a for loop to run the IP
# for i in {1..255}; do webscan 127.0.0.$i; done
