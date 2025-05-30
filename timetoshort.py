#!/usr/bin/python3

debug = True

import ccxt, pandas, requests, socket, urllib3, os

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
    heikin_ashi_df["body"]  = abs(heikin_ashi_df['ha_open'] - heikin_ashi_df['ha_close'])
    heikin_ashi_df["color"] = heikin_ashi_df.apply(color, axis=1)
    heikin_ashi_df['EMA_10'] = heikin_ashi_df['ha_close'].ewm(span=10, adjust=False).mean()
    heikin_ashi_df['EMA_20'] = heikin_ashi_df['ha_close'].ewm(span=20, adjust=False).mean()
    heikin_ashi_df['EMA_100'] = heikin_ashi_df['ha_close'].ewm(span=100, adjust=False).mean()
    heikin_ashi_df['SMA_25'] = heikin_ashi_df['ha_close'].rolling(window=25).mean()
    heikin_ashi_df['downtrend'] = heikin_ashi_df.apply(downtrend, axis=1)
    heikin_ashi_df['strike'] = heikin_ashi_df.apply(strike_through, axis=1)

    final_df = klines.merge(heikin_ashi_df, on='timestamp')
    return final_df[['ha_open', 'ha_high', 'ha_low', 'ha_close', 'color', 'EMA_10', 'EMA_20', 'EMA_100', 'SMA_25', 'downtrend', "strike"]]

def color(HA):
    if  HA['ha_open'] == HA['ha_low']: return "GREEN"
    elif HA['ha_open'] == HA['ha_high']: return "RED"
    else: return "-"

def downtrend(HA):
    if HA['EMA_20'] > HA['EMA_10'] and HA['SMA_25'] > HA["ha_close"]: return True
    else: return False

def strike_through(HA):
    if HA['ha_high'] > HA['EMA_100'] and HA['ha_low'] < HA['EMA_100']: return True
    else: return False

def time_to_short(coin):
    pair = coin + "USDT"
    direction = heikin_ashi(get_klines(pair, "1h"))
    minute_chart = heikin_ashi(get_klines(pair, "3m"))
    if debug: print(direction)

    if direction['color'].iloc[-1] == "RED" and minute_chart['strike'].iloc[-1] and minute_chart['downtrend'].iloc[-1]:
        telegram_bot_sendtext(str(coin) + " 💥 SHORT 💥")
        exit()

try:
    print("The script is running...")
    while True:
        try:
            # for coin in ["BTC", "ETH", "SOL"]: time_to_short(coin)
            for coin in ["BTC"]: time_to_short(coin)

        except (ccxt.RequestTimeout, ccxt.NetworkError, urllib3.exceptions.ProtocolError, urllib3.exceptions.ReadTimeoutError,
                requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout,
                ConnectionResetError, KeyError, OSError, socket.timeout) as e:

            error_message = str(e).lower()
            print(e)

except KeyboardInterrupt: print("\n\nAborted.\n")
