def color(HA):
    if  HA['ha_close'] > HA['ha_open']: return "GREEN"
    elif HA['ha_open'] > HA['ha_close']: return "RED"
    else: return "-"

def downtrend(HA):
    return HA['25MA'] > HA['20EMA'] and HA['25MA'] > HA['10EMA'] and HA['20EMA'] > HA['10EMA']

def smooth_criminal(HA):
    return HA['25MA'] > HA['ha_open']

def downwards_movement(timeframe):
    return timeframe["20EMA"].iloc[-2] > timeframe["20EMA"].iloc[-1] and \
           timeframe["10EMA"].iloc[-3] > timeframe["10EMA"].iloc[-2] > timeframe["10EMA"].iloc[-1]


def short_despair(pair):
    minute_3m = heikin_ashi(get_klines(pair, "3m"))
    minute_1m = heikin_ashi(get_klines(pair, "1m"))

    condition_3m = downwards_movement(minute_3m) and all(minute_3m["color"].iloc[-2:].eq("RED"))
    condition_1m = downwards_movement(minute_1m) and all(minute_1m["smooth"].iloc[-2:]) and minute_1m["downtrend"].iloc[-1]

    if condition_3m and condition_1m:
        telegram_bot_sendtext("💥 TIME TO SHORT 💥")
        exit()
