#!/usr/bin/python3

import requests, socket, urllib3, os
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
    heikin_ashi_df['100EMA'] = heikin_ashi_df['ha_close'].ewm(span=100, adjust=False).mean()
    heikin_ashi_df['25MA'] = heikin_ashi_df['ha_close'].rolling(window=25).mean()
    heikin_ashi_df['open_below_25MA'] = heikin_ashi_df.apply(open_below_25MA, axis=1)
    heikin_ashi_df['MA_pattern_broken'] = heikin_ashi_df.apply(MA_pattern_broken, axis=1)
    heikin_ashi_df['25MA > 100EMA'] = heikin_ashi_df.apply(MA_higher_than_100EMA, axis=1)

    result_cols = ['ha_open', 'ha_high', 'ha_low', 'ha_close', '10EMA', '20EMA', '100EMA', '25MA', 'open_below_25MA', 'MA_pattern_broken', '25MA > 100EMA']

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

def MA_higher_than_100EMA(HA):
    if HA['25MA'] > HA['100EMA'] : return True
    else: return False

def open_below_25MA(HA):
    if HA['25MA'] > HA['ha_open']: return True
    else: return False

def MA_pattern_broken(HA):
    if HA['25MA'] > HA['20EMA'] or HA['25MA'] > HA['10EMA']: return True
    else: return False

debug_input = input("Debug mode (y/ default n): ").strip().lower()
debug = debug_input in ('y', '1')

def time_to_short(coin):
    pair = coin + "USDT"
    direction = heikin_ashi(get_klines(pair, "3m"))
    if debug: print(direction)

    if direction["25MA > 100EMA"].iloc[-1]:
        if direction["open_below_25MA"].iloc[-1] and direction["MA_pattern_broken"].iloc[-1]:
            telegram_bot_sendtext(str(coin) + " 💥 TIME TO SHORT 💥")
            exit()

print("The script is running...\n")
try:
    while True:
        try: time_to_short("BTC")
        except (ccxt.RequestTimeout, ccxt.NetworkError, urllib3.exceptions.ProtocolError, urllib3.exceptions.ReadTimeoutError,
                requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout,
                ConnectionResetError, KeyError, OSError, socket.timeout) as e:
            error_message = str(e).lower()
            print(e)
except KeyboardInterrupt: print("\n\nAborted.\n")
