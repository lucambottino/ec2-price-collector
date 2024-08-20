import json
import time
import os
import logging
import pandas as pd
from dotenv import load_dotenv
from threading import Lock
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

class WSCryptoPriceTracker:
    def __init__(self):
        self.lock = Lock()
        self.client = UMFuturesWebsocketClient(on_message=self.message_handler)
        self.csv_files = {}

        # Load API keys
        self.api_key = os.getenv("APIKEYBINANCE")
        self.api_secret = os.getenv("APISECRETBINANCE")
        #if not self.api_key or not self.api_secret:
        #    raise ValueError("API Key and Secret must be set in environment variables.")

    def message_handler(self, _, message):
        try:
            message = json.loads(message)

            # Check if this is a bookTicker or markPrice message
            if 'u' in message and 'b' in message and 'a' in message:  # bookTicker messages
                self._update_csv(
                    symbol=message['s'],
                    best_bid=float(message['b']),
                    best_ask=float(message['a']),
                    best_bid_qty=float(message['B']),
                    best_ask_qty=float(message['A']),
                    timestamp=message['E']
                )
            elif 'p' in message and 'r' in message and 'T' in message:  # markPrice messages
                self._update_csv(
                    symbol=message['s'],
                    mark_price=float(message['p']),
                    timestamp=message['E']
                )

        except Exception as e:
            logging.error(f"Error in message_handler: {e}")

    def _update_csv(self, symbol, best_bid=None, best_ask=None, best_bid_qty=None, best_ask_qty=None, mark_price=None, timestamp=None):
        # Prepare the new data row
        new_data = {
            'symbol': symbol,
            'best_bid': best_bid,
            'best_ask': best_ask,
            'best_bid_qty': best_bid_qty,
            'best_ask_qty': best_ask_qty,
            'mark_price': mark_price,
            'timestamp': timestamp
        }
        new_row = pd.DataFrame([new_data])

        # Create a CSV file name based on the symbol
        csv_file = f'{symbol.lower()}_binance.csv'

        with self.lock:
            # Check if file exists to determine whether to write headers
            file_exists = os.path.exists(csv_file)

            # Write the new row to the CSV file, appending if the file already exists
            new_row.to_csv(csv_file, mode='a', header=not file_exists, index=False)

    def start(self, coins=["btcusdt", "ethusdt", "solusdt"]):
        try:
            # Subscribe to bookTicker and markPrice streams for desired symbols
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

    def run(self, coins=["btcusdt", "ethusdt", "solusdt"]):
        try:
            self.start(coins)
            while True:
                time.sleep(1)  # Keep the script running
        except KeyboardInterrupt:
            logging.info("Script interrupted by user.")
        finally:
            self.stop()

if __name__ == "__main__":
    ws_manager = WSCryptoPriceTracker()
    ws_manager.run(coins=["OPUSDT".lower(), "CRVUSDT".lower(), "ETHUSDT".lower()])