import sys
import time
from dotenv import load_dotenv, find_dotenv
import os
import asyncio
from concurrent.futures import ProcessPoolExecutor

sys.path.append('./coinex/')
from ws_coinex import run_coinnext_ws
from ws_binance import WSCryptoPriceTracker
from binance_coinex_merger import BinanceCoinextMerger
from create_db import create_connection, create_table, new_table_schema

def run_ws_binance_tracker(coins):
    try:
        ws_binance_tracker = WSCryptoPriceTracker()
        ws_binance_tracker.run(coins=coins)
    except Exception as e:
        print(e)

def run_coinnext_ws_process(access_id, signed_str, coins):
    try:
        run_coinnext_ws(access_id, signed_str, coins=coins)
    except Exception as e:
        print(e)

def merge_data(coins, db_name):
    # create table for each coin
    conn = create_connection(db_name)
    for coin in coins:
        try:
            create_table(conn, new_table_schema(coin.lower()))
        except Exception as e:
            print(e)

    # every 5 minutes collect the csvs and merge them
    while True:
        for coin in coins:
            binance_csv_path, coinex_csv_path,table_name = f'{coin.lower()}_binance.csv', f'{coin.lower()}_coinext.csv', f'{coin.lower()}'
            merger = BinanceCoinextMerger(binance_csv_path, coinex_csv_path, db_name, table_name)
            try:
                merger.process()
            except Exception as e:
                print(e)
            time.sleep(5)

async def main():
    dot_env_path = find_dotenv('../.env', raise_error_if_not_found=True)
    load_dotenv(dotenv_path=dot_env_path)
    access_id = os.getenv("APIKEYCOINEX")
    signed_str = os.getenv("APISECRETKEYCOINEX")
    db_name=os.getenv("DBNAME")
    coins = ["INJUSDT", "AXSUSDT", "DYDXUSDT", "SANDUSDT"]


    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as executor:
        await asyncio.gather(
            loop.run_in_executor(executor, run_coinnext_ws_process, access_id, signed_str, coins),
            loop.run_in_executor(executor, run_ws_binance_tracker, coins),
            loop.run_in_executor(executor, merge_data, coins, db_name)
        )


if __name__ == "__main__":
    asyncio.run(main())