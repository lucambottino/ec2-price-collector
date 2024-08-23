import json
import time
import websocket
import gzip
import requests
from dotenv import load_dotenv
from datetime import datetime
from db_manager import DBManager
from coin_list import COIN_LIST
import os


class CoinexWebSocket:
    def __init__(self, access_id, signed_str, coins, db_manager):
        self.access_id = access_id
        self.signed_str = signed_str
        self.coins = coins
        self.db_manager = db_manager

    def authenticate_request(self, timestamp=None):
        if timestamp is None:
            timestamp = int(time.time() * 1000)

        payload = {
            "method": "server.sign",
            "params": {
                "access_id": self.access_id,
                "signed_str": self.signed_str,
                "timestamp": timestamp,
            },
            "id": 1,
        }
        return json.dumps(payload)

    @staticmethod
    def decompress_message(compressed_message):
        decompressed_bytes = gzip.decompress(compressed_message)
        decompressed_str = decompressed_bytes.decode("utf-8")
        return json.loads(decompressed_str)

    @staticmethod
    def get_binance_future_price(token):
        r = requests.get(
            f"https://fapi.binance.com/fapi/v2/ticker/price?symbol={token}"
        )
        return float(json.loads(r.content)["price"])

    def create_subscription_request(self):
        payload = {
            "method": "bbo.subscribe",
            "params": {"market_list": self.coins},
            "id": 1,
        }
        return json.dumps(payload)

    def insert_data_into_db(self, parsed_data):
        try:
            timestamp = datetime.fromtimestamp(parsed_data["timestamp"] / 1000.0)

            query = "SELECT coin_id FROM coins_table WHERE coin_name = %s"
            coin_id = self.db_manager.execute_query(query, (parsed_data["symbol"],))

            if not coin_id:
                insert_coin_query = (
                    "INSERT INTO coins_table (coin_name) VALUES (%s) RETURNING coin_id"
                )
                coin_id = self.db_manager.execute_query(
                    insert_coin_query, (parsed_data["symbol"],)
                )
                coin_id = coin_id[0][0] if coin_id else None
            else:
                coin_id = coin_id[0][0]

            if coin_id:
                insert_data_query = """
                INSERT INTO coin_data_table (
                    coin_id, timestamp, best_bid, best_ask, best_bid_qty, best_ask_qty, mark_price, last_price, updated_at, exchange
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
                """
                self.db_manager.cursor.execute(
                    insert_data_query,
                    (
                        coin_id,
                        timestamp,
                        parsed_data["best_bid"],
                        parsed_data["best_ask"],
                        parsed_data["best_bid_qty"],
                        parsed_data["best_ask_qty"],
                        parsed_data["mark_price"],
                        parsed_data["last_price"],
                        timestamp,
                        "COINEX",
                    ),
                )
                self.db_manager.commit()
            else:
                print("Error: Could not find or insert coin_id")

        except Exception as e:
            print(f"Error inserting data into DB: {e}")

    def on_message(self, ws, message):
        parsed_msg = self.decompress_message(message)

        print(f"Received message: {parsed_msg}")

        if "data" in parsed_msg:
            data = parsed_msg["data"]
            token = data["market"]
            data["price"] = self.get_binance_future_price(token)

            parsed_data = {
                "symbol": data["market"],
                "best_bid": data["best_bid_price"],
                "best_ask": data["best_ask_size"],
                "best_bid_qty": data["best_bid_size"],
                "best_ask_qty": data["best_ask_size"],
                "mark_price": data["price"],
                "last_price": data["price"],
                "timestamp": data["updated_at"],
            }

            try:
                self.insert_data_into_db(parsed_data)
                # print(f"Data inserted into DB: {parsed_data}")
            except Exception as e:
                print(f"Error inserting data into DB: {e}")

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print(f"WebSocket closed: {close_status_code}, {close_msg}")
        print("Reconnecting...")
        time.sleep(0.5)
        self.run()

    def on_open(self, ws):
        auth_message = self.authenticate_request()
        ws.send(auth_message)
        print(f"Sent authentication message: {auth_message}")

        subscription_message = self.create_subscription_request()
        ws.send(subscription_message)
        print(f"Sent subscription message: {subscription_message}")

    def run(self):
        websocket_url = "wss://socket.coinex.com/v2/futures"
        ws = websocket.WebSocketApp(
            websocket_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        ws.run_forever()


if __name__ == "__main__":
    load_dotenv()

    db_manager = DBManager()

    access_id = os.getenv("APIKEYCOINEX")
    signed_str = os.getenv("APISECRETKEYCOINEX")
    print(f"Access ID: {access_id}")
    print(f"Signed String: {signed_str}")

    coinex_ws = CoinexWebSocket(access_id, signed_str, COIN_LIST, db_manager)
    try:
        coinex_ws.run()
    finally:
        db_manager.close()
