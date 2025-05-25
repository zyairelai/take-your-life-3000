#!/bin/python3

from lunar_python import Solar
from datetime import datetime

def calc_dayun(solar, gender):
    lunar = solar.getLunar()
    eight_char = lunar.getEightChar()
    is_male = gender.lower() == 'm' or gender.lower() == '1'
    yun = eight_char.getYun(is_male)

    # Get 起运 (Qi Yun): time after birth Da Yun starts
    start_years = yun.getStartYear()
    start_months = yun.getStartMonth()
    start_days = yun.getStartDay()
    start_solar = yun.getStartSolar()
    start_solar_str = start_solar.toYmd()

    # Generate Da Yun periods
    dayun_list = yun.getDaYun()

    print("\n[十年大运]")
    for da_yun in dayun_list:
        s_year = da_yun.getStartYear()
        e_year = da_yun.getEndYear()
        gan_zhi = da_yun.getGanZhi()

        # Only show Da Yun if it overlaps 2010–2060
        if e_year >= 2015 and s_year <= 2060:
            print(f"{s_year}-{e_year} {gan_zhi}大运")

# ========== Main Script ==========

# Input section
gender = input("Gender (m/f): ").strip().lower()
birth_year = int(input("Birth Year: "))
birth_month = int(input("Birth Month: "))
birth_day = int(input("Birth Date: "))
birth_time_input = input("Birth Time (0-23, or press Enter to skip): ").strip()

if birth_time_input:
    birth_hour = int(birth_time_input)
    solar = Solar.fromYmdHms(birth_year, birth_month, birth_day, birth_hour, 0, 0)
else:
    solar = Solar.fromYmd(birth_year, birth_month, birth_day)

# Get Lunar object and GanZhi
lunar = solar.getLunar()
year_gz = lunar.getYearInGanZhi()
month_gz = lunar.getMonthInGanZhi()
day_gz = lunar.getDayInGanZhi()

if not birth_time_input:
    print("\nHour not specified. Showing 12 possible combinations:")
    for i in range(0, 24, 2):
        temp_solar = Solar.fromYmdHms(birth_year, birth_month, birth_day, i, 0, 0)
        temp_lunar = temp_solar.getLunar()
        hour_gz = temp_lunar.getTimeInGanZhi()
        time_range = f"{i:02d}:00-{i+1:02d}:59"
        # print(f"{time_range} → {birth_year}年 {year_gz}年 {month_gz}月 {day_gz}日 {hour_gz}时")
        print(f"{birth_year}年 {year_gz}年 {month_gz}月 {day_gz}日 {hour_gz}时")

print("\n四柱命盘 (BaZi):")
print(f"{birth_year}年 {year_gz}年 {month_gz}月 {day_gz}日", end="")

if birth_time_input:
    hour_gz = lunar.getTimeInGanZhi()
    print(f" {hour_gz}时")
else:
    print("")

# Calculate and print Da Yun
calc_dayun(solar, gender)
