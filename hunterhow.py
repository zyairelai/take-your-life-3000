import sys
import json

# Check if the correct number of command line arguments is provided
if len(sys.argv) != 2:
    print("Usage: python3 hunterhow.py <filename>")
    sys.exit(1)

# Get the filename from the command line arguments
filename = sys.argv[1]

# Open the text file containing the JSON data
try:
    with open(filename, 'r') as file:
        # Read the content of the file
        json_data = file.read()
except FileNotFoundError:
    print("File not found.")
    sys.exit(1)

# Parse the JSON string
try:
    data = json.loads(json_data)
except json.JSONDecodeError:
    print("Invalid JSON format in the file.")
    sys.exit(1)

# Retrieve all the "web_url" values
try:
    web_urls = [item['web_url'] for item in data['data']['list']]
    for url in web_urls:
        print(url)
except (KeyError, IndexError):
    print("The JSON data does not contain the expected structure.")
