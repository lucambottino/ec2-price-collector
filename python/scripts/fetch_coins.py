import requests
import json

API_URL = "http://nestjs:3000/coins"


def fetch_coins():
    response = requests.get(API_URL)
    if response.status_code == 200:
        coins_list = response.json()  # Fetch the coins data
        return coins_list


def get_coins():
    coins = fetch_coins()
    return [coin["coin_name"] for coin in coins]
