#!/bin/python3
# extract_domains_html.py
import os

def extract_domains_to_html(input_file, output_file):
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"{input_file} is not exist!")
        # Create a blank file
        with open(input_file, "w", encoding="utf-8") as f:
            f.write("")
        return

    domains = []
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line or "Domain Name" in line:  # skip header or empty line
                continue
            parts = line.split("\t")  # split by tab
            if parts:
                domains.append(parts[0])  # first column is domain name

        # build HTML
        html_content = """
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Domain List</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                a { display: block; margin: 5px 0; text-decoration: none; color: blue; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h2>Extracted Domains</h2>
        """

        for domain in domains:
            html_content += f'<a href="http://{domain}" target="_blank">{domain}</a>\n'

        html_content += """
        </body>
        </html>
        """

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"[+] Extracted {len(domains)} domains -> {output_file}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    extract_domains_to_html("domains.txt", "output.html")
