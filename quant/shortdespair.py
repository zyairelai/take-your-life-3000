#!/usr/bin/python3

import time, os
try: import ccxt, pandas, requests, socket
except ImportError:
    print("library not found, run:\npip3 install ccxt pandas requests socket --break-system-packages")
    exit(1)

def telegram_bot_sendtext(bot_message):
    print(bot_message)
    bot_token = os.environ.get('TELEGRAM_LIVERMORE')
    chat_id = "@swinglivermore"
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=html&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

# telegram_bot_sendtext("Telegram works!")
print("The DESPAIR script is running...\n")

def get_klines(pair, interval):
    tohlcv_colume = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    return pandas.DataFrame(ccxt.binance().fetch_ohlcv(pair, interval , limit=100), columns=tohlcv_colume)

def heikin_ashi(klines):
    heikin_ashi_df = pandas.DataFrame(index=klines.index.values, columns=['ha_open', 'ha_high', 'ha_low', 'ha_close'])
    heikin_ashi_df['ha_close'] = (klines['open'] + klines['high'] + klines['low'] + klines['close']) / 4

    for i in range(len(klines)):
        if i == 0: heikin_ashi_df.iat[0, 0] = klines['open'].iloc[0]
        else: heikin_ashi_df.iat[i, 0] = (heikin_ashi_df.iat[i-1, 0] + heikin_ashi_df.iat[i-1, 3]) / 2

    heikin_ashi_df.insert(0,'timestamp', klines['timestamp'])
    heikin_ashi_df['ha_high'] = heikin_ashi_df.loc[:, ['ha_open', 'ha_close']].join(klines['high']).max(axis=1)
    heikin_ashi_df['ha_low']  = heikin_ashi_df.loc[:, ['ha_open', 'ha_close']].join(klines['low']).min(axis=1)
    heikin_ashi_df["color"] = heikin_ashi_df.apply(color, axis=1)
    heikin_ashi_df['10EMA'] = klines['close'].ewm(span=10, adjust=False).mean()
    heikin_ashi_df['20EMA'] = klines['close'].ewm(span=20, adjust=False).mean()
    heikin_ashi_df['25MA'] = klines['close'].rolling(window=25).mean()
    heikin_ashi_df['mini'] = heikin_ashi_df.apply(mini_downtrend, axis=1)
    heikin_ashi_df['downtrend'] = heikin_ashi_df.apply(downtrend, axis=1)
    heikin_ashi_df['smooth'] = heikin_ashi_df.apply(smooth_criminal, axis=1)

    result_cols = ['ha_open', 'ha_high', 'ha_low', 'ha_close', 'color', '10EMA', '20EMA', '25MA', 'mini', 'downtrend', 'smooth']
    for col in result_cols: heikin_ashi_df[col] = heikin_ashi_df[col].apply(no_decimal)
    return heikin_ashi_df[result_cols]

def no_decimal(val):
    if isinstance(val, float) and not pandas.isna(val): return round(val)
    return val

def color(HA):
    if  HA['ha_close'] > HA['ha_open']: return "GREEN"
    elif HA['ha_open'] > HA['ha_close']: return "RED"
    else: return "-"

def mini_downtrend(HA):
    return HA['20EMA'] > HA['10EMA']

def downtrend(HA):
    return HA['25MA'] > HA['20EMA'] and HA['25MA'] > HA['10EMA'] and HA['20EMA'] > HA['10EMA']

def smooth_criminal(HA):
    return HA['25MA'] > HA['ha_open']

def short_despair(pair):
    minute_3m = heikin_ashi(get_klines(pair, "3m"))
    minute_1m = heikin_ashi(get_klines(pair, "1m"))

    condition_3m = minute_3m["smooth"].iloc[-1] and minute_3m["mini"].iloc[-1] and minute_3m["color"].iloc[-1] == "RED"
    condition_1m = minute_1m["20EMA"].iloc[-3] > minute_1m["20EMA"].iloc[-2] > minute_1m["20EMA"].iloc[-1] and \
                   minute_1m["10EMA"].iloc[-3] > minute_1m["10EMA"].iloc[-2] > minute_1m["10EMA"].iloc[-1] and \
                   all(minute_1m["smooth"].iloc[-3:]) and all(minute_1m["downtrend"].iloc[-2:])

    if condition_3m and condition_1m:
        telegram_bot_sendtext("💥 TIME TO SHORT 💥")
        exit()

try:
    while True:
        try:
            short_despair("BTCUSDT")
            time.sleep(10)
        except (ccxt.RequestTimeout, ccxt.NetworkError, ConnectionResetError, socket.timeout,
                requests.exceptions.RequestException) as e:
            print(f"Network error: {e}")
            telegram_bot_sendtext(f"Network error: {e}")
            time.sleep(30)
            continue
except KeyboardInterrupt: print("\n\nAborted.\n")
