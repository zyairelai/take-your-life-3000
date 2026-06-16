#!/bin/python3
from datetime import datetime, timedelta

def get_iterable_values(config_value, max_range=100):
    """
    Helper function to parse configuration strings.
    Handles 'auto', wildcard 'x' patterns (like '1x'), or fixed numbers.
    """
    config_str = str(config_value).strip().lower()

    # Handle 'auto' for State Code (specifically 01 to 16 as requested)
    if config_str == "auto" and max_range == 16:
        return [f"{i:02d}" for i in range(1, 17)]

    # Handle general 'auto' (00 to 99)
    if config_str == "auto":
        return [f"{i:02d}" for i in range(max_range)]

    # Handle wildcard 'x' patterns (e.g., '1x' or 'x5')
    if "x" in config_str:
        # Pad to 2 characters if it's a short string
        config_str = config_str.zfill(2)
        allowed_values = []
        for i in range(100):
            val_str = f"{i:02d}"
            # Check if the generated numbers match the pattern (e.g., '1' matches '1', 'x' matches anything)
            match = True
            for char_cfg, char_val in zip(config_str, val_str):
                if char_cfg != "x" and char_cfg != char_val:
                    match = False
                    break
            if match:
                allowed_values.append(val_str)
        return allowed_values

    # Handle a standard fixed single value
    return [config_str.zfill(2)]


def generate_and_save_codes(config):
    # Base dates using 2024 to naturally handle leap years (Feb 29)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)

    current_date = start_date
    line_count = 0
    max_lines_per_file = 10000
    f = None

    year_prefix = str(config["YEAR_PREFIX"])

    # Pre-resolve the state code, first tail, and last tail loops based on config
    state_codes = get_iterable_values(config["STATE_CODE"], max_range=16)
    zz_first_values = get_iterable_values(config["ZZ_FIRST_TWO"])
    zz_last_values = get_iterable_values(config["ZZ_LAST_TWO"])

    try:
        # Loop through every day of the year
        while current_date <= end_date:
            month_str = current_date.strftime("%m")
            date_str = current_date.strftime("%d")

            # 1. Filter Month (Supports fixed numbers or wildcards like '0x')
            allowed_months = get_iterable_values(config["TARGET_MONTH"])
            if config["TARGET_MONTH"] != "auto" and month_str not in allowed_months:
                current_date += timedelta(days=1)
                continue

            # 2. Filter Date (Supports fixed numbers or wildcards like '1x')
            allowed_dates = get_iterable_values(config["TARGET_DATE"])
            if config["TARGET_DATE"] != "auto" and date_str not in allowed_dates:
                current_date += timedelta(days=1)
                continue

            # --- NESTED GENERATION LOOPS ---
            for yy in state_codes:
                for z1_str in zz_first_values:
                    for z2_str in zz_last_values:

                        # Construct final code sequence
                        code = f"{year_prefix}{month_str}{date_str}{yy}{z1_str}{z2_str}\n"

                        # File management chunking
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
    "YEAR_PREFIX": "91",

    # 2. State Code Control
    # Set to "auto" to loop 01 to 16, or a specific string (e.g., "1x", "05")
    "STATE_CODE": "02",
    # 01 - Johor
    # 02 - Kedah
    # 03 - Kelantan
    # 04 - Melaka
    # 05 - Negeri Sembilan
    # 06 - Pahang
    # 07 - Penang
    # 08 - Perak
    # 09 - Perlis
    # 10 - Selangor
    # 11 - Terengganu
    # 12 - Sabah
    # 13 - Sarawak
    # 14 - Federal Territory of Kuala Lumpur
    # 15 - Federal Territory of Labuan
    # 16 - Federal Territory of Putrajaya

    # 3. Date Controls
    # Set to "auto" to iterate completely, a fixed day like "15", or a wildcard pattern like "1x"
    "TARGET_MONTH": "12",
    "TARGET_DATE": "auto",      # Will loop through days 10, 11, 12, 13, 14, 15, 16, 17, 18, 19

    # 4. Tail End Controls (Last 4 Digits)
    # Set to "auto" to loop 00-99, a fixed string, or a wildcard pattern like "x5"
    "ZZ_FIRST_TWO": "auto",
    "ZZ_LAST_TWO": "18"
}

# Run the generator
generate_and_save_codes(MY_CONFIG)
# awk '{print $2}' input.txt | sort -n
