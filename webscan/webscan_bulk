#!/bin/bash

# Extract the first three octets from the input IP address
ip_prefix=$(echo $1 | cut -d '.' -f 1-3)

# Iterate over the fourth octet from 1 to 255 and run the webscan command
for i in {1..255}; do
    webscan "$ip_prefix.$i"
done
