# Import the get_coins function from the coin_manager module
from coin_list import get_coins
import time


def trading_logic():
    while True:
        # Access the cached coin list
        coin_list = get_coins()
        print(f"Using the following coin list: {coin_list}")

        # Your trading logic here using coin_list
        # ...

        time.sleep(0.1)  # Run every 100ms


if __name__ == "__main__":
    trading_logic()
