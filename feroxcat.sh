#!/bin/bash

# Usage function
usage() {
    echo "[+] Usage: feroxcat input_file.txt"
}

# Check if the input file is provided as an argument
if [ $# -ne 1 ]; then
    usage
    exit 1
fi

# Assigning the input file from the argument
input_file="$1"

# Check if the input file exists
if [ ! -f "$input_file" ]; then
    echo "Error: Input file '$input_file' not found!"
    usage
    exit 1
fi

# Use awk to extract the URL (assuming it's always the last field)
# Then sort the entries by URL uniquely
awk '{print $NF,$0}' "$input_file" | sort -u -k1,1 | cut -d' ' -f2-
