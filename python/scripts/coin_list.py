import os
import requests
from threading import Timer

# API URL for fetching the coin list
API_URL = "http://nestjs:3000/coins"

# Cache the COIN_LIST
COIN_LIST = os.getenv("COIN_LIST", "").split(",")

# Update interval (e.g., update once every 24 hours)
UPDATE_INTERVAL = 24 * 60 * 60  # 24 hours


def fetch_coins():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            coins_list = [coin["coin_name"] for coin in response.json()]
            return coins_list
        else:
            print(f"Failed to fetch coins: {response.status_code}")
            return []
    except requests.RequestException as e:
        print(f"Error fetching coins: {e}")
        return []


def update_coin_list():
    global COIN_LIST
    updated_coins = fetch_coins()
    if updated_coins:
        COIN_LIST = updated_coins
        print(f"COIN_LIST updated to: {COIN_LIST}")
    else:
        print("Using previous COIN_LIST.")

    # Schedule the next update
    Timer(UPDATE_INTERVAL, update_coin_list).start()


# Start the periodic update when the module is loaded
update_coin_list()


def get_coins():
    return COIN_LIST
