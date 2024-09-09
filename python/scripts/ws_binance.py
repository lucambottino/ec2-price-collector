import aiohttp
import asyncio
from datetime import datetime, timezone
from db_manager import DBManager
from coin_list import get_coins


class BinanceFuturesTicker:
    def __init__(self, symbols):
        self.symbols = symbols
        self.db_manager = DBManager()  # Initialize the DBManager
        self.session = None  # Initialize aiohttp session to None

    async def get_book_ticker_and_mark_price(self, symbol):
        try:
            book_ticker_url = (
                f"https://fapi.binance.com/fapi/v1/ticker/bookTicker?symbol={symbol}"
            )
            async with self.session.get(book_ticker_url) as book_ticker_response:
                if book_ticker_response.status == 200:
                    book_ticker_data = await book_ticker_response.json()
                else:
                    print(
                        f"Error fetching book ticker for {symbol}: {book_ticker_response.status}"
                    )
                    return None

            mark_price_url = (
                f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"
            )
            async with self.session.get(mark_price_url) as mark_price_response:
                if mark_price_response.status == 200:
                    mark_price_data = await mark_price_response.json()
                else:
                    print(
                        f"Error fetching mark price for {symbol}: {mark_price_response.status}"
                    )
                    return None

            combined_data = {
                "symbol": symbol,
                "bidPrice": float(book_ticker_data.get("bidPrice", 0)),
                "bidQty": float(book_ticker_data.get("bidQty", 0)),
                "askPrice": float(book_ticker_data.get("askPrice", 0)),
                "askQty": float(book_ticker_data.get("askQty", 0)),
                "time": datetime.fromtimestamp(
                    book_ticker_data.get("time", 0) / 1000, timezone.utc
                ),  # Convert to timezone-aware datetime
                "lastUpdateId": book_ticker_data.get("lastUpdateId", 0),
                "mark_price": float(mark_price_data.get("markPrice", 0)),
            }
            return combined_data

        except Exception as e:
            print(f"Exception in fetching data for {symbol}: {e}")
            return None

    def save_to_database(self, data):
        query = """
        INSERT INTO coin_data_table (coin_id, timestamp, best_bid, best_ask, best_bid_qty, best_ask_qty, mark_price, last_price, exchange)
        VALUES ((SELECT coin_id FROM coins_table WHERE coin_name = %s), %s, %s, %s, %s, %s, %s, %s, 'BINANCE')
        RETURNING data_id;
        """
        try:
            self.db_manager.execute_query(
                query,
                (
                    data["symbol"],
                    data["time"],
                    data["bidPrice"],
                    data["askPrice"],
                    data["bidQty"],
                    data["askQty"],
                    data["mark_price"],
                    data["mark_price"],
                ),
            )
            self.db_manager.commit()  # Commit the transaction
        except Exception as e:
            print(f"Error saving data to database: {e}")

    async def run(self):
        self.session = aiohttp.ClientSession()  # Initialize the session once
        try:
            while True:
                tasks = [
                    self.get_book_ticker_and_mark_price(symbol)
                    for symbol in self.symbols
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for result in results:
                    if isinstance(result, Exception):
                        print(f"Task failed with exception: {result}")
                    elif result:
                        print(f"Data for {result['symbol']}: {result}")
                        self.save_to_database(result)

                await asyncio.sleep(0.5)
        finally:
            await self.session.close()  # Ensure the session is closed
            self.db_manager.close()  # Close the database connection when done


if __name__ == "__main__":
    ticker = BinanceFuturesTicker(get_coins())
    asyncio.run(ticker.run())
