#!/usr/bin/python3

import requests, socket, urllib3, os
try: import ccxt, pandas
except ImportError:
    print("library not found, run:")
    print("pip3 install ccxt pandas --break-system-packages")
    exit(1)

touch_input = input("Default 100 EMA, enter 25 for MA: ")
touch = 'touch_MA' if touch_input == '25' else 'touch_EMA'

debug_input = input("Debug mode (y/ default n): ").strip().lower()
debug = debug_input in ('y', '1')

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
    heikin_ashi_df['MA_25'] = heikin_ashi_df['ha_close'].rolling(window=25).mean()
    heikin_ashi_df['EMA_100'] = heikin_ashi_df['ha_close'].ewm(span=100, adjust=False).mean()
    heikin_ashi_df['touch_MA'] = heikin_ashi_df.apply(touch_MA_25, axis=1)
    heikin_ashi_df['touch_EMA'] = heikin_ashi_df.apply(touch_EMA_100, axis=1)

    result_cols = ['ha_open', 'ha_high', 'ha_low', 'ha_close', 'MA_25', 'EMA_100', 'touch_MA', 'touch_EMA']
    for col in result_cols: heikin_ashi_df[col] = heikin_ashi_df[col].apply(smart_round)
    return heikin_ashi_df[result_cols]

def smart_round(val):
    if isinstance(val, float):
        str_val = f"{val:.10f}".rstrip('0')
        if '.' in str_val and len(str_val.split('.')[-1]) > 2:
            return round(val, 2)
    return val

def touch_MA_25(HA):
    if HA['ha_high'] > HA['MA_25'] and HA['ha_low'] < HA['MA_25']: return True
    else: return False

def touch_EMA_100(HA):
    if HA['ha_high'] > HA['EMA_100'] and HA['ha_low'] < HA['EMA_100']: return True
    else: return False

def time_to_short(coin):
    pair = coin + "USDT"
    direction = heikin_ashi(get_klines(pair, "3m"))
    if debug: print(direction)

    if direction[touch].iloc[-1]:
        telegram_bot_sendtext(str(coin) + " 💥 SHORT 💥")
        exit()

try:
    print("The script is running...")
    while True:
        try:
            for coin in ["BTC"]: time_to_short(coin)

        except (ccxt.RequestTimeout, ccxt.NetworkError, urllib3.exceptions.ProtocolError, urllib3.exceptions.ReadTimeoutError,
                requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout,
                ConnectionResetError, KeyError, OSError, socket.timeout) as e:

            error_message = str(e).lower()
            print(e)

except KeyboardInterrupt: print("\n\nAborted.\n")
