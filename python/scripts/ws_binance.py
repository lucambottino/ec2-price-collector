import aiohttp
import asyncio
from datetime import datetime, timedelta, timezone
from db_manager import DBManager


class BinanceFuturesTicker:
    def __init__(self):
        self.symbols = []
        self.session = None
        self.next_update_time = datetime.now(timezone.utc)
        self.db_manager = DBManager()

    async def update_symbols(self):
        if datetime.now(timezone.utc) >= self.next_update_time:
            try:
                coin_url = "http://nestjs:3000/coins"
                async with self.session.get(coin_url) as response:
                    if response.status == 200:
                        coins_data = await response.json()
                        self.symbols = [coin["coin_name"] for coin in coins_data]
                        self.next_update_time += timedelta(days=1)
                        print(f"Updated symbols: {self.symbols}")
                    else:
                        print(
                            f"Failed to fetch coin list, HTTP status: {response.status}"
                        )
            except Exception as e:
                print(f"Error fetching coin list from NestJS backend: {e}")

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
                ),
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
            self.db_manager.commit()
        except Exception as e:
            print(f"Error saving data to database: {e}")

    async def run(self):
        self.session = aiohttp.ClientSession()
        try:
            while True:
                await self.update_symbols()

                if not self.symbols:
                    print("No symbols available, skipping data fetch.")
                    await asyncio.sleep(3600)  # Sleep for an hour if no symbols
                    continue

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

                await asyncio.sleep(0.5)  # Modify sleep duration as needed
        finally:
            await self.session.close()
            self.db_manager.close()


if __name__ == "__main__":
    ticker = BinanceFuturesTicker()
    asyncio.run(ticker.run())
