#!/usr/bin/python3

import requests, socket, os
try: import ccxt, pandas
except ImportError:
    print("library not found, run:")
    print("pip3 install ccxt pandas --break-system-packages")
    exit(1)

def telegram_bot_sendtext(bot_message):
    print(bot_message)
    bot_token = os.environ.get('TELEGRAM_LIVERMORE')
    chat_id = "@swinglivermore"
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=html&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

def get_klines(pair, interval):
    tohlcv_colume = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    return pandas.DataFrame(ccxt.binance().fetch_ohlcv(pair, interval , limit=201), columns=tohlcv_colume)

def heikin_ashi(klines):
    heikin_ashi_df = pandas.DataFrame(index=klines.index.values, columns=['ha_open', 'ha_high', 'ha_low', 'ha_close'])
    heikin_ashi_df['ha_close'] = (klines['open'] + klines['high'] + klines['low'] + klines['close']) / 4

    for i in range(len(klines)):
        if i == 0: heikin_ashi_df.iat[0, 0] = klines['open'].iloc[0]
        else: heikin_ashi_df.iat[i, 0] = (heikin_ashi_df.iat[i-1, 0] + heikin_ashi_df.iat[i-1, 3]) / 2

    heikin_ashi_df.insert(0,'timestamp', klines['timestamp'])
    heikin_ashi_df['ha_high'] = heikin_ashi_df.loc[:, ['ha_open', 'ha_close']].join(klines['high']).max(axis=1)
    heikin_ashi_df['ha_low']  = heikin_ashi_df.loc[:, ['ha_open', 'ha_close']].join(klines['low']).min(axis=1)
    heikin_ashi_df['10EMA'] = heikin_ashi_df['ha_close'].ewm(span=10, adjust=False).mean()
    heikin_ashi_df['20EMA'] = heikin_ashi_df['ha_close'].ewm(span=20, adjust=False).mean()
    heikin_ashi_df['25MA'] = heikin_ashi_df['ha_close'].rolling(window=25).mean()
    heikin_ashi_df['touch_25MA'] = five_touch_25MA(heikin_ashi_df)
    heikin_ashi_df['Open < 25MA'] = heikin_ashi_df.apply(open_below_25MA, axis=1)
    heikin_ashi_df['pattern_broken'] = heikin_ashi_df.apply(pattern_broken, axis=1)

    result_cols = ['ha_open', 'ha_high', 'ha_low', 'ha_close', '10EMA', '20EMA', '25MA', 'touch_25MA', 'Open < 25MA', 'pattern_broken']
    heikin_ashi_df["25MA"] = heikin_ashi_df["25MA"].apply(lambda x: f"{int(x)}" if pandas.notnull(x) else "")
    for col in result_cols: heikin_ashi_df[col] = heikin_ashi_df[col].apply(no_decimal)
    return heikin_ashi_df[result_cols]

def no_decimal(val):
    if isinstance(val, float) and not pandas.isna(val): return round(val)
    return val

def smart_round(val):
    if isinstance(val, float):
        str_val = f"{val:.10f}".rstrip('0')
        if '.' in str_val and len(str_val.split('.')[-1]) > 2:
            return round(val, 2)
    return val

def open_below_25MA(HA):
    if HA['25MA'] > HA['ha_open']: return True
    else: return False

def pattern_broken(HA):
    if HA['25MA'] > HA['20EMA'] and HA['25MA'] > HA['10EMA']: return True
    else: return False

def five_touch_25MA(df):
    result = [False] * len(df)
    for idx in range(4, len(df)):
        for i in range(5): # check this and previous 4 candles
            row = df.iloc[idx - i]
            if row['ha_high'] > row['25MA'] and row['ha_close'] < row['25MA']:
                result[idx] = True
                break
    return result

debug_input = input("Debug mode (y/ default n): ").strip().lower()
debug = debug_input in ('y', '1')
print("The script is running...\n")

def simple_short(coin):
    pair = coin + "USDT"
    direction = heikin_ashi(get_klines(pair, "3m"))
    if debug: print(direction)

    if direction["touch_25MA"].iloc[-1] and direction["Open < 25MA"].iloc[-1] and direction["pattern_broken"].iloc[-1]:
        telegram_bot_sendtext(str(coin) + " 💥 TIME TO SHORT 💥")
        exit()

try:
    while True:
        try: simple_short("BTC")
        except (ccxt.RequestTimeout, ccxt.NetworkError, ConnectionResetError, socket.timeout,
                requests.exceptions.RequestException) as e: print(f"Network error: {e}")
except KeyboardInterrupt: print("\n\nAborted.\n")
