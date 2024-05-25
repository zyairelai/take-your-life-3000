#!/usr/bin/python3

import requests
import json

def query_domains(ip):
    url = f"https://api.webscan.cc?action=query&ip={ip}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        for entry in data:
            print(entry['domain'])
    else:
        print("Failed to retrieve data. Status code:", response.status_code)

if __name__ == "__main__":
    ip = input("Enter the IP address: ")
    query_domains(ip)
