#!/usr/bin/python3

import ccxt, pandas, requests, socket, time, os


def telegram_bot_sendtext(bot_message):
    print(bot_message)
    bot_token = os.environ.get('TELEGRAM_LIVERMORE')
    chat_id = "@swinglivermore"
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=html&text=' + bot_message
    response = requests.get(send_text)
    return response.json()


# telegram_bot_sendtext("Telegram works!")


def get_klines(pair, interval):
    tohlcv_colume = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    return pandas.DataFrame(ccxt.binance().fetch_ohlcv(pair,
                                                       interval,
                                                       limit=200),
                            columns=tohlcv_colume)


def heikin_ashi(klines):
    heikin_ashi_df = pandas.DataFrame(
        index=klines.index.values,
        columns=['ha_open', 'ha_high', 'ha_low', 'ha_close'])
    heikin_ashi_df['ha_close'] = (klines['open'] + klines['high'] +
                                  klines['low'] + klines['close']) / 4

    for i in range(len(klines)):
        if i == 0: heikin_ashi_df.iat[0, 0] = klines['open'].iloc[0]
        else:
            heikin_ashi_df.iat[i, 0] = (heikin_ashi_df.iat[i - 1, 0] +
                                        heikin_ashi_df.iat[i - 1, 3]) / 2

    heikin_ashi_df.insert(0, 'timestamp', klines['timestamp'])
    heikin_ashi_df[
        'ha_high'] = heikin_ashi_df.loc[:, ['ha_open', 'ha_close']].join(
            klines['high']).max(axis=1)
    heikin_ashi_df[
        'ha_low'] = heikin_ashi_df.loc[:, ['ha_open', 'ha_close']].join(
            klines['low']).min(axis=1)
    heikin_ashi_df['100EMA'] = klines['close'].ewm(span=100,
                                                   adjust=False).mean()

    result_cols = ['ha_high', '100EMA']
    for col in result_cols:
        heikin_ashi_df[col] = heikin_ashi_df[col].apply(no_decimal)
    return heikin_ashi_df[result_cols]


def no_decimal(val):
    if isinstance(val, float) and not pandas.isna(val): return round(val)
    return val


def cooldown_period(pair):
    cooldown = heikin_ashi(get_klines(pair, "1m"))
    if cooldown["ha_high"].iloc[-1] > cooldown["100EMA"].iloc[-1]:
        telegram_bot_sendtext("🥶 COOLDOWN RESET 🥶")
        return True
    return False


if __name__ == '__main__':
    try:
        while True:
            try:
                cooldown_period("BTCUSDC")
                time.sleep(10)
            except (ccxt.RequestTimeout, ccxt.NetworkError,
                    ConnectionResetError, socket.timeout,
                    requests.exceptions.RequestException) as e:
                print(f"Network error: {e}")
                telegram_bot_sendtext(f"Network error: {e}")
                time.sleep(60)
                continue
    except KeyboardInterrupt:
        print("\n\nAborted.\n")
