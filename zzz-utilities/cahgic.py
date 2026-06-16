#!/bin/python3
from datetime import datetime, timedelta

def generate_and_save_codes(config):
    """
    Generates and saves codes based on a fully modular configuration dictionary.
    """
    # Base dates using 2024 to naturally handle leap years (Feb 29)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)

    current_date = start_date
    line_count = 0
    max_lines_per_file = 10000
    f = None

    # Format the fixed string components safely
    year_prefix = str(config["YEAR_PREFIX"])
    yy = str(config["STATE_CODE"]).zfill(2)

    try:
        # Loop through every day of the year
        while current_date <= end_date:
            month_str = current_date.strftime("%m")
            date_str = current_date.strftime("%d")

            # 1. Filter Month
            if config["TARGET_MONTH"] != "auto" and month_str != str(config["TARGET_MONTH"]).zfill(2):
                current_date += timedelta(days=1)
                continue

            # 2. Filter Date
            if config["TARGET_DATE"] != "auto" and date_str != str(config["TARGET_DATE"]).zfill(2):
                current_date += timedelta(days=1)
                continue

            # 3. Handle zz_first loop (or single fixed value)
            zz_first_range = range(100) if config["ZZ_FIRST_TWO"] == "auto" else [int(config["ZZ_FIRST_TWO"])]
            for z1 in zz_first_range:
                z1_str = str(z1).zfill(2)

                # 4. Handle zz_last loop (or single fixed value)
                zz_last_range = range(100) if config["ZZ_LAST_TWO"] == "auto" else [int(config["ZZ_LAST_TWO"])]
                for z2 in zz_last_range:
                    z2_str = str(z2).zfill(2)

                    # --- CONSTRUCT THE CODE ---
                    # Uses the exact sequence from your requirements
                    code = f"{year_prefix}{month_str}{date_str}{yy}{z1_str}{z2_str}\n"

                    # Check if we need to open a new file chunk
                    if line_count % max_lines_per_file == 0:
                        if f:
                            f.close()

                        start_range = line_count + 1
                        end_range = line_count + max_lines_per_file
                        filename = f"{start_range:05d}-{end_range:05d}.txt"
                        f = open(filename, "w")

                    f.write(code)
                    line_count += 1

            current_date += timedelta(days=1)

    finally:
        if f:
            f.close()

    if line_count > 0:
        print(f"Success! Generated {line_count:,} codes split across files.")
    else:
        print("No codes generated. Please check your configurations.")


# ==========================================
# ------------ CONFIGURATION TAB -----------
# ==========================================
MY_CONFIG = {
    # 1. Base Prefixes
    "YEAR_PREFIX": "81",      # Adjustable year prefix (e.g., "81", "82")
    "STATE_CODE": "14",       # Your 'yy' value

    # 2. Date Controls
    # Set to "auto" to iterate through them, or a specific string (e.g., "05") to lock it
    "TARGET_MONTH": "05",
    "TARGET_DATE": "auto",

    # 3. Tail End Controls (Last 4 Digits)
    # Set to "auto" to loop 00-99, or a specific string to lock it
    "ZZ_FIRST_TWO": "auto",   # First 2 digits of the tail end
    "ZZ_LAST_TWO": "05"       # Last 2 digits of the tail end
}

# Run the generator with the config panel settings
generate_and_save_codes(MY_CONFIG)
