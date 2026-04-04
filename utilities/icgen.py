#!/bin/python3
import itertools

def generate_dictionary():
    prefix = "011214"
    xx_options = ["10"]
    yy_options = [f"{i:02d}" for i in range(100)]
    zz_options = ["52"]
    
    filename = "zzz-dictionary.txt"
    
    with open(filename, "w") as f:
        count = 0
        for xx, yy, zz in itertools.product(xx_options, yy_options, zz_options):
            line = f"{prefix}{xx}{yy}{zz}\n"
            f.write(line)
            count += 1
            
    print(f"Successfully generated {count} combinations in {filename}")

if __name__ == "__main__":
    generate_dictionary()

