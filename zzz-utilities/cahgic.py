#!/bin/python3
from datetime import datetime, timedelta
import os

def get_iterable_values(config_value, max_range=100):
    """
    Helper function to parse configuration strings.
    Handles 'auto', 'even', 'odd', wildcard 'x' patterns (like '1x'), or fixed numbers.
    """
    config_str = str(config_value).strip().lower()

    # --- FIX: Generate actual even numbers (00, 02, 04... 98) ---
    if config_str == "even":
        return [f"{i:02d}" for i in range(100) if i % 2 == 0]

    # --- FIX: Generate actual odd numbers (01, 03, 05... 99) ---
    if config_str == "odd":
        return [f"{i:02d}" for i in range(100) if i % 2 != 0]

    if config_str == "auto" and max_range == 16:
        return [f"{i:02d}" for i in range(1, 17)]

    if config_str == "auto":
        return [f"{i:02d}" for i in range(max_range)]

    if "x" in config_str:
        config_str = config_str.zfill(2)
        allowed_values = []
        for i in range(100):
            val_str = f"{i:02d}"
            match = True
            for char_cfg, char_val in zip(config_str, val_str):
                if char_cfg != "x" and char_cfg != char_val:
                    match = False
                    break
            if match:
                allowed_values.append(val_str)
        return allowed_values

    return [config_str.zfill(2)]


def generate_and_save_codes(config):
    # Base dates using 2024 to naturally handle leap years (Feb 29)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)

    current_date = start_date
    global_line_count = 0
    max_lines_per_file = 10000
    f = None

    year_prefix = str(config["YEAR_PREFIX"])
    is_combined = config.get("COMBINED", True)

    # Pre-resolve loops based on config
    state_codes = get_iterable_values(config["STATE_CODE"], max_range=16)
    zz_first_values = get_iterable_values(config["ZZ_FIRST_TWO"])
    zz_last_values = get_iterable_values(config["ZZ_LAST_TWO"])

    try:
        # --- COMBINED MODE INITIALIZATION ---
        # If true, open the single master file right away
        if is_combined:
            f = open("all_combined_codes.txt", "w")

        # Loop through every day of the year
        while current_date <= end_date:
            month_str = current_date.strftime("%m")
            date_str = current_date.strftime("%d")

            # 1. Filter Month
            allowed_months = get_iterable_values(config["TARGET_MONTH"])
            if config["TARGET_MONTH"] != "auto" and month_str not in allowed_months:
                current_date += timedelta(days=1)
                continue

            # 2. Filter Date
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

                        # --- CHUNKING MODE LOGIC (COMBINED = False) ---
                        if not is_combined:
                            # Create/switch files every 10,000 lines globally
                            if global_line_count % max_lines_per_file == 0:
                                if f:
                                    f.close()
                                start_range = global_line_count + 1
                                end_range = global_line_count + max_lines_per_file
                                filename = f"{start_range:05d}-{end_range:05d}.txt"
                                f = open(filename, "w")

                        f.write(code)
                        global_line_count += 1

            current_date += timedelta(days=1)

    finally:
        # Catch-all close for whatever file handler is active at the end
        if f:
            f.close()

    if global_line_count > 0:
        print(f"Success! Generated {global_line_count:,} codes overall.")
        if is_combined:
            print("Saved everything sequentially into 'all_combined_codes.txt'.")
        else:
            print(f"Saved sequentially in chunks of {max_lines_per_file:,} lines per file.")
    else:
        print("No codes generated. Please check your configurations.")


# ==========================================
# ------------ CONFIGURATION TAB -----------
# ==========================================
MY_CONFIG = {
    # 1. Base Prefixes
    "YEAR_PREFIX": "84",

    # 2. State Code Control
    # Set to "auto" to loop 01 to 16, or a specific string (e.g., "1x", "14")
    "STATE_CODE": "13",
    # 01 - Johor             02 - Kedah          03 - Kelantan
    # 04 - Melaka            05 - N. Sembilan    06 - Pahang
    # 07 - Penang            08 - Perak          09 - Perlis
    # 10 - Selangor          11 - Terengganu     12 - Sabah
    # 13 - Sarawak           14 - WP KL          15 - WP Labuan
    # 16 - WP Putrajaya

    # 3. Date Controls
    "TARGET_MONTH": "06",
    "TARGET_DATE": "11",

    # 4. Tail End Controls (Last 4 Digits)
    "ZZ_FIRST_TWO": "auto",

    # Set to "even" for actual even numbers (00, 02, ... 98)
    # Set to "odd" for actual odd numbers (01, 03, ... 99)
    "ZZ_LAST_TWO": "even",

    # 5. Output Format Option
    # True  = All outputs go into ONE single file: 'all_combined_codes.txt'
    # False = Splits outputs sequentially into '00001-10000.txt', '10001-20000.txt' blocks.
    "COMBINED": False
}

# Run the generator
generate_and_save_codes(MY_CONFIG)
# awk '{print $2}' input.txt | sort -n
