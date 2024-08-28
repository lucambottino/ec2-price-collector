import aiohttp
import asyncio
import time

class BinanceFuturesTicker:
    def __init__(self, symbols):
        self.symbols = symbols

    async def get_book_ticker_and_mark_price(self, symbol):
        async with aiohttp.ClientSession() as session:
            # Fetch book ticker data
            book_ticker_url = f"https://fapi.binance.com/fapi/v1/ticker/bookTicker?symbol={symbol}"
            async with session.get(book_ticker_url) as book_ticker_response:
                if book_ticker_response.status == 200:
                    book_ticker_data = await book_ticker_response.json()
                else:
                    print(f"Error fetching book ticker for {symbol}: {book_ticker_response.status}")
                    return None

            # Fetch mark price data
            mark_price_url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"
            async with session.get(mark_price_url) as mark_price_response:
                if mark_price_response.status == 200:
                    mark_price_data = await mark_price_response.json()
                else:
                    print(f"Error fetching mark price for {symbol}: {mark_price_response.status}")
                    return None

            # Combine book ticker and mark price data
            combined_data = {
                "symbol": symbol,
                "bidPrice": book_ticker_data.get("bidPrice", ""),
                "bidQty": book_ticker_data.get("bidQty", ""),
                "askPrice": book_ticker_data.get("askPrice", ""),
                "askQty": book_ticker_data.get("askQty", ""),
                "time": book_ticker_data.get("time", 0),
                "lastUpdateId": book_ticker_data.get("lastUpdateId", 0),
                "mark_price": mark_price_data.get("markPrice", "")
            }
            return combined_data

    async def run(self):
        while True:
            tasks = [self.get_book_ticker_and_mark_price(symbol) for symbol in self.symbols]
            results = await asyncio.gather(*tasks)
            for data in results:
                if data:
                    print(f"Data for {data['symbol']}: {data}")
            await asyncio.sleep(0.5)  # Wait for 1 second before the next request

if __name__ == "__main__":
    symbols = ['INJUSDT', 'CRVUSDT', 'ETHUSDT']  # Replace with your desired symbols
    ticker = BinanceFuturesTicker(symbols)
    asyncio.run(ticker.run())