#!/bin/bash

# Extract the first and third octets from the input IP address
ip_prefix=$(echo $1 | cut -d '.' -f 1,3)

# Iterate over the second octet from 1 to 255 and run the webscan command
for i in {1..255}; do
    webscan-class-c "$ip_prefix.$i.1"
done
