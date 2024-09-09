COIN_LIST = ["INJUSDT", "AXSUSDT", "DYDXUSDT", "CRVUSDT", "LTCUSDT"]


def get_coins():
    coins = COIN_LIST
    return [coin["coin_name"] for coin in coins]
