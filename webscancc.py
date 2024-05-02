import sys
import requests
from bs4 import BeautifulSoup

# Check if the correct number of command line arguments is provided
if len(sys.argv) != 2:
    print("Usage: python3 webscancc.py <ip>")
    sys.exit(1)

# Get the domain from the command line arguments
domain = sys.argv[1]

# Make a POST request to the website
url = 'https://www.webscan.cc/'
payload = {'domain': domain}
try:
    response = requests.post(url, data=payload)
    response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
except requests.exceptions.RequestException as e:
    print("Error:", e)
    sys.exit(1)

# Extract the HTML content from the response
html_content = response.text

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Find all <a> tags with class 'domain'
domain_links = soup.find_all('a', class_='domain')

# Extract the URLs (text content) from the <a> tags
urls = [link.text.strip() for link in domain_links]

# Sort the URLs
urls.sort()

# Print the sorted URLs
for url in urls:
    print(url)

# Write the sorted URLs to webscan_result.txt
with open('webscan_result.txt', 'w') as outfile:
    for url in urls:
        outfile.write(url + '\n')

print("Sorted URLs have been written to webscan_result.txt")
