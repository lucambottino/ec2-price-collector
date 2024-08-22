import json
import time
import logging
import psycopg2
import os
from threading import Lock
from dotenv import load_dotenv
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from coin_list import COIN_LIST

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()


class WSCryptoPriceTracker:
    def __init__(self):
        self.lock = Lock()
        self.client = UMFuturesWebsocketClient(on_message=self.message_handler)
        self.conn = None
        self.cursor = None
        self.setup_db_connection()

    def setup_db_connection(self):
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host=os.getenv("POSTGRES_HOST"),
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            logging.error(f"Error connecting to DB: {e}")

    def close_db_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def insert_data_into_db(self, new_data):
        try:

            self.cursor.execute(
                "SELECT coin_id FROM coins_table WHERE coin_name = %s",
                (new_data["symbol"],),
            )
            coin_id = self.cursor.fetchone()

            if coin_id is None:
                self.cursor.execute(
                    "INSERT INTO coins_table (coin_name) VALUES (%s) RETURNING coin_id",
                    (new_data["symbol"],),
                )
                coin_id = self.cursor.fetchone()[0]
            else:
                coin_id = coin_id[0]

            insert_query = """
            INSERT INTO coin_data_table (
                coin_id, timestamp, best_bid, best_ask, best_bid_qty, best_ask_qty, mark_price, last_price, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            );
            """

            self.cursor.execute(
                insert_query,
                (
                    coin_id,
                    new_data["timestamp"],
                    new_data["best_bid"],
                    new_data["best_ask"],
                    new_data["best_bid_qty"],
                    new_data["best_ask_qty"],
                    new_data["mark_price"],
                    new_data["last_price"],
                    new_data["timestamp"],
                ),
            )

            self.conn.commit()

        except Exception as e:
            logging.error(f"Error inserting data into DB: {e}")

    def message_handler(self, _, message):
        try:
            message = json.loads(message)

            if "u" in message and "b" in message and "a" in message:
                parsed_data = {
                    "symbol": message["s"],
                    "best_bid": float(message["b"]),
                    "best_ask": float(message["a"]),
                    "best_bid_qty": float(message["B"]),
                    "best_ask_qty": float(message["A"]),
                    "mark_price": None,
                    "last_price": None,
                    "timestamp": message["E"],
                }
            elif (
                "p" in message and "r" in message and "T" in message
            ):  # markPrice messages
                parsed_data = {
                    "symbol": message["s"],
                    "best_bid": None,
                    "best_ask": None,
                    "best_bid_qty": None,
                    "best_ask_qty": None,
                    "mark_price": float(message["p"]),
                    "last_price": float(message["p"]),
                    "timestamp": message["E"],
                }

            # self.insert_data_into_db(parsed_data)
            print(parsed_data)

        except Exception as e:
            logging.error(f"Error in message_handler: {e}")

    def start(self, coins):
        try:
            for coin in coins:
                self.client.book_ticker(symbol=coin)
                self.client.mark_price(symbol=coin, speed=1)
            logging.info("WebSocket client started.")
        except Exception as e:
            logging.error(f"Error starting WebSocket client: {e}")
            self.client.stop()

    def stop(self):
        try:
            self.client.stop()
            logging.info("WebSocket client stopped.")
        except Exception as e:
            logging.error(f"Error stopping WebSocket client: {e}")

    def run(self, coins):
        coins = [coin.lower() for coin in coins]
        try:
            self.start(coins)
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Script interrupted by user.")
        finally:
            self.stop()
            self.close_db_connection()


if __name__ == "__main__":
    ws_manager = WSCryptoPriceTracker()
    ws_manager.run(COIN_LIST)
