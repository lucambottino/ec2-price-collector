import json
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from coin_list import COIN_LIST
from db_manager import DBManager
import threading

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()


class WSCryptoPriceTracker:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.client = UMFuturesWebsocketClient(on_message=self.on_message)
        self.db_manager = DBManager()
        self.data_batch = []  # To hold batched data
        self.batch_size = 100  # Batch size for database insertion
        self.batch_interval = 0.2  # Interval in seconds for batch insertion

        # Create and start an event loop in a new thread
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.start_loop, daemon=True).start()

    def start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def insert_batch_data_into_db(self):
        async with self.lock:
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
                    coin_id = await self.get_or_create_coin_id(new_data["symbol"])
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
                print(f"Error in batch insertion: {e}")
                await self.db_manager.conn.rollback()

    async def get_or_create_coin_id(self, symbol):
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

    async def message_handler(self, _, message):
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

            # Add to batch
            async with self.lock:
                self.data_batch.append(parsed_data)

        except Exception as e:
            logging.error(f"Error in message_handler: {e}")

    def on_message(self, _, message):
        # Schedule the coroutine in the event loop running in the thread
        self.loop.call_soon_threadsafe(
            asyncio.create_task, self.message_handler(_, message)
        )

    async def start(self, coins):
        try:
            for coin in coins:
                self.client.book_ticker(symbol=coin)
                self.client.mark_price(symbol=coin, speed=1)
            logging.info("WebSocket client started.")
        except Exception as e:
            logging.error(f"Error starting WebSocket client: {e}")
            self.client.stop()

    async def stop(self):
        try:
            self.client.stop()
            logging.info("WebSocket client stopped.")
        except Exception as e:
            logging.error(f"Error stopping WebSocket client: {e}")

    async def run(self, coins):
        coins = [coin.lower() for coin in coins]
        await self.start(coins)
        try:
            while True:
                await asyncio.sleep(self.batch_interval)
                await self.insert_batch_data_into_db()
        except KeyboardInterrupt:
            logging.info("Script interrupted by user.")
        finally:
            await self.stop()
            self.db_manager.close()


if __name__ == "__main__":
    ws_manager = WSCryptoPriceTracker()
    asyncio.run(ws_manager.run(COIN_LIST))
