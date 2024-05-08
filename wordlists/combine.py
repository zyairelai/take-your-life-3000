#!/bin/python3

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

# Paths to input files
file1_path = 'httparchive_jsp_jspa_do_action_2024_04_28.txt'
file2_path = 'bb_uwu.txt'
file3_path = 'raft-large-directories-lowercase.txt'

# Path to output file
output_file_path = 'output.txt'

# List of input file paths
file_paths = [file1_path, file2_path, file3_path]

# Combine, sort, and get unique content from input files
combine_sort_unique(file_paths, output_file_path)

print("Combining, sorting, and removing duplicates from the files is done. Check 'output.txt' for the result.")
