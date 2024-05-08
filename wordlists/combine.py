#!/usr/bin/python3

import sys

# Function to read the content of a text file
def read_file(file_path):
    with open(file_path, 'r') as file:
        content = file.readlines()
    return content

# Function to combine and sort unique content from multiple files
def combine_sort_unique(file_paths, output_file):
    combined_content = []

    # Read content from each file and append it to the combined list
    for file_path in file_paths:
        content = read_file(file_path)
        combined_content.extend(content)

    # Remove duplicates and sort the combined content
    combined_content = sorted(set(combined_content))

    # Write the sorted and unique content into the output file
    with open(output_file, 'w') as file:
        file.writelines(combined_content)

if len(sys.argv) < 2 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
    print("[+] Usage : python3 combine.py <input1.txt> <input2.txt> ...")
    sys.exit(1)

# Paths to input files (excluding script name)
file_paths = sys.argv[1:]

# Path to output file
output_file_path = 'output.txt'

# Combine, sort, and get unique content from input files
combine_sort_unique(file_paths, output_file_path)

print("[+] Done! Check output.txt for the result!")
