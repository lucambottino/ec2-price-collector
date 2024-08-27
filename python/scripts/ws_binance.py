import json
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from coin_list import COIN_LIST
from db_manager import DBManager
from threading import Lock, Thread

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()


class WSCryptoPriceTracker:
    def __init__(self):
        self.lock = Lock()
        self.client = UMFuturesWebsocketClient(on_message=self.on_message)
        self.db_manager = DBManager()
        self.data_batch = []  # To hold batched data
        self.batch_size = 100  # Batch size for database insertion
        self.batch_interval = 0.2  # Interval in seconds for batch insertion

        # Start the batch processing in a separate thread
        Thread(target=self.run_batch_process, daemon=True).start()

    def insert_batch_data_into_db(self):
        with self.lock:
            if not self.data_batch:
                return
            try:
                insert_query = """
                INSERT INTO coin_data_table (
                    coin_id, timestamp, best_bid, best_ask, best_bid_qty, best_ask_qty, mark_price, last_price, updated_at, exchange
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
                """
                values = []
                for new_data in self.data_batch:
                    coin_id = self.get_or_create_coin_id(new_data["symbol"])
                    if coin_id:
                        values.append(
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
                            )
                        )

                if values:
                    self.db_manager.cursor.executemany(insert_query, values)
                    self.db_manager.commit()

                self.data_batch = []  # Clear the batch after insertion

            except Exception as e:
                logging.error(f"Error in batch insertion: {e}")
                self.db_manager.conn.rollback()

    def get_or_create_coin_id(self, symbol):
        coin_id = self.db_manager.execute_query(
            "SELECT coin_id FROM coins_table WHERE coin_name = %s",
            (symbol,),
        )
        if not coin_id:
            coin_id = self.db_manager.execute_query(
                "INSERT INTO coins_table (coin_name) VALUES (%s) RETURNING coin_id",
                (symbol,),
            )
            coin_id = coin_id[0][0] if coin_id else None
        else:
            coin_id = coin_id[0][0]
        return coin_id

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
            elif "p" in message and "r" in message and "T" in message:
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
            else:
                parsed_data = None

            if parsed_data:
                with self.lock:
                    self.data_batch.append(parsed_data)

        except Exception as e:
            logging.error(f"Error in message_handler: {e}")

    def on_message(self, _, message):
        self.message_handler(_, message)

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

    def run_batch_process(self):
        while True:
            time.sleep(self.batch_interval)
            self.insert_batch_data_into_db()


if __name__ == "__main__":
    ws_manager = WSCryptoPriceTracker()
    try:
        ws_manager.start(COIN_LIST)
    except KeyboardInterrupt:
        ws_manager.stop()
