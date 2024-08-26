import json
import time
import logging
from threading import Lock
from datetime import datetime  # Import datetime module
from dotenv import load_dotenv
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from coin_list import COIN_LIST
from db_manager import DBManager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()


class WSCryptoPriceTracker:
    def __init__(self):
        self.lock = Lock()
        self.client = UMFuturesWebsocketClient(on_message=self.message_handler)
        self.db_manager = DBManager()  # Use DBManager for database operations

    def insert_data_into_db(self, new_data):
        try:
            # Fetch coin_id from the database
            coin_id = self.db_manager.execute_query(
                "SELECT coin_id FROM coins_table WHERE coin_name = %s",
                (new_data["symbol"],),
            )

            if not coin_id:
                # Insert the coin if it doesn't exist
                coin_id = self.db_manager.execute_query(
                    "INSERT INTO coins_table (coin_name) VALUES (%s) RETURNING coin_id",
                    (new_data["symbol"],),
                )
                coin_id = coin_id[0][0] if coin_id else None
            else:
                coin_id = coin_id[0][0]

            if coin_id:
                # Insert the new data, including the exchange name
                insert_query = """
                INSERT INTO coin_data_table (
                    coin_id, timestamp, best_bid, best_ask, best_bid_qty, best_ask_qty, mark_price, last_price, updated_at, exchange
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
                """
                self.db_manager.cursor.execute(
                    insert_query,
                    (
                        coin_id,
                        datetime.fromtimestamp(new_data["timestamp"] / 1000.0),
                        new_data["best_bid"],
                        new_data["best_ask"],
                        new_data["best_bid_qty"],
                        new_data["best_ask_qty"],
                        new_data["mark_price"],
                        new_data["last_price"],
                        datetime.fromtimestamp(new_data["timestamp"] / 1000.0),
                        "BINANCE",
                    ),
                )
                self.db_manager.commit()

        except Exception as e:
            logging.error(f"Error inserting data into DB: {e}")
            self.db_manager.conn.rollback()  # Rollback the transaction on error

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

            try:
                self.insert_data_into_db(parsed_data)
                # print(f"Data inserted: {parsed_data}")
            except Exception as e:
                print(f"Error inserting data into DB: {e, parsed_data}")

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
            self.db_manager.close()


if __name__ == "__main__":
    ws_manager = WSCryptoPriceTracker()
    ws_manager.run(COIN_LIST)
