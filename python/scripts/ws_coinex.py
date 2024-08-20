from functools import partial
import json
import time
import websocket
import os
from dotenv import load_dotenv
import gzip
import pandas as pd
import requests
import logging

def authenticate_request(access_id, signed_str, timestamp=None):
    if timestamp is None:
        timestamp = int(time.time() * 1000)

    payload = {
        "method": "server.sign",
        "params": {
            "access_id": access_id,
            "signed_str": signed_str,
            "timestamp": timestamp
        },
        "id": 1
    }

    json_payload = json.dumps(payload)
    return json_payload

def decompress_message(compressed_message):
    decompressed_bytes = gzip.decompress(compressed_message)
    decompressed_str = decompressed_bytes.decode('utf-8')
    json_message = json.loads(decompressed_str)
    return json_message

def get_binance_future_price(token):
    r = requests.get(f"https://fapi.binance.com/fapi/v2/ticker/price?symbol={token}")
    price = float(json.loads(r.content)["price"])
    return price

def create_subscription_request(market_list):
    payload = {
        "method": "bbo.subscribe",
        "params": {
            "market_list": market_list
        },
        "id": 1
    }

    json_payload = json.dumps(payload)
    return json_payload

def on_message(ws, message):
    parsed_msg = decompress_message(message)
    if 'data' in parsed_msg:
        data = parsed_msg['data']
        token = data["market"]
        data["price"] = get_binance_future_price(token)

        file_path = f"{token.lower()}_coinext.csv"

        df = pd.DataFrame([data])

        if os.path.exists(file_path):
            df.to_csv(file_path, mode='a', header=False, index=False)
        else:
            df.to_csv(file_path, mode='w', header=True, index=False)

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"WebSocket closed: {close_status_code}, {close_msg}")
    print("Reconnecting...")
    time.sleep(0.5)  # Wait for 0.5 seconds before attempting to reconnect
    run_coinnext_ws(ws.access_id, ws.signed_str, ws.coins)

def on_open(ws, access_id, signed_str, coins=["OPUSDT", "CRVUSDT", "ETHUSDT"]):
    ws.access_id = access_id
    ws.signed_str = signed_str
    ws.coins = coins

    auth_message = authenticate_request(access_id, signed_str)
    ws.send(auth_message)
    print(f"Sent authentication message: {auth_message}")

    subscription_message = create_subscription_request(coins)
    ws.send(subscription_message)
    print(f"Sent subscription message: {subscription_message}")

def run_coinnext_ws(access_id, signed_str, coins=["OPUSDT", "CRVUSDT", "SOLUSDT"]):
    websocket_url = "wss://socket.coinex.com/v2/futures"

    on_open_func = partial(on_open, access_id=access_id, signed_str=signed_str, coins=coins)
    ws = websocket.WebSocketApp(websocket_url,
                                on_open=on_open_func,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()

if __name__ == "__main__":
    load_dotenv()

    access_id = os.getenv("COINEX_ACCESS_ID")
    signed_str = os.getenv("COINEX_SIGNED_STR")

    run_coinnext_ws(access_id, signed_str)