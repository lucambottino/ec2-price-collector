import pandas as pd
import psycopg2
from psycopg2 import sql
import os

class BinanceCoinextMerger:
    def __init__(self, binance_path, coinext_path, db_name, table_name):
        self.binance_path = binance_path
        self.coinext_path = coinext_path
        self.db_name = db_name
        self.data_binance = None
        self.data_coinext = None
        self.merged_data = None
        self.db_table_name = table_name

    def create_connection(self):
        """Create a database connection to a PostgreSQL database"""
        conn = None
        try:
            conn = psycopg2.connect(
                dbname=self.db_name,
                user="postgres",
                password="yourpassword",
                host="postgres"  # Docker service name for PostgreSQL
            )
            print(f"Successfully connected to the database {self.db_name}")
        except psycopg2.Error as e:
            print(e)
        return conn

    def load_data(self):
        """Load the data from CSV files into DataFrames."""
        self.data_binance = pd.read_csv(self.binance_path)
        self.data_coinext = pd.read_csv(self.coinext_path)

    def clean_data(self):
        """Clean and preprocess the data."""
        # Forward-fill and backward-fill missing mark_price values
        self.data_binance['mark_price'].ffill(inplace=True)
        self.data_binance['mark_price'].bfill(inplace=True)

        # Convert timestamps to datetime format
        self.data_binance['timestamp'] = pd.to_datetime(self.data_binance['timestamp'], unit='ms')
        self.data_coinext['timestamp'] = pd.to_datetime(self.data_coinext['updated_at'], unit='ms')

        self.data_binance.dropna(inplace=True)

    def sort_data(self):
        """Sort the DataFrames by timestamp."""
        self.data_binance = self.data_binance.sort_values('timestamp')
        self.data_coinext = self.data_coinext.sort_values('timestamp')

    def merge_data(self):
        """Merge the DataFrames using merge_asof."""
        self.merged_data: pd.DataFrame = pd.merge_asof(
            self.data_binance,
            self.data_coinext,
            on='timestamp',
            direction='forward'
        )
        self.merged_data.ffill(inplace=True)

    def save_to_db(self, conn):
        """Save the merged data to the PostgreSQL database incrementally."""
        try:
            with conn.cursor() as cursor:
                # Check if the table exists
                cursor.execute(sql.SQL("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    );
                """), [self.db_table_name])
                
                table_exists = cursor.fetchone()[0]

                if table_exists:
                    # Get the existing timestamps in the database
                    cursor.execute(sql.SQL(f"SELECT timestamp FROM {self.db_table_name};"))
                    existing_timestamps = set(row[0] for row in cursor.fetchall())

                    # Filter out rows that are already in the database
                    new_data = self.merged_data[~self.merged_data['timestamp'].isin(existing_timestamps)]
                else:
                    new_data = self.merged_data

                if not new_data.empty:
                    # Insert new rows into the database
                    insert_query = sql.SQL(f"""
                        INSERT INTO {self.db_table_name} (timestamp, symbol, best_bid, best_ask, best_bid_qty, best_ask_qty, mark_price, market, best_bid_price, best_bid_size, best_ask_price, best_ask_size, price, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """)
                    
                    for _, row in new_data.iterrows():
                        cursor.execute(insert_query, (
                            row['timestamp'], row['symbol'], row['best_bid'], row['best_ask'],
                            row['best_bid_qty'], row['best_ask_qty'], row['mark_price'], row['market'],
                            row['best_bid_price'], row['best_bid_size'], row['best_ask_price'], row['best_ask_size'],
                            row['price'], row['updated_at']
                        ))
                    conn.commit()
                    print(f"Saved {len(new_data)} new rows to {self.db_table_name}.")
                else:
                    print("No new data to save.")
        except psycopg2.Error as e:
            print(e)

    def process(self):
        """Perform the complete data processing and save to the database."""
        self.load_data()
        self.clean_data()
        self.sort_data()
        self.merge_data()
        
        conn = self.create_connection()
        if conn is not None:
            self.save_to_db(conn)
            conn.close()
        return self.merged_data

    def get_merged_data(self):
        """Return the merged DataFrame."""
        if self.merged_data is not None:
            return self.merged_data
        else:
            raise ValueError("Data has not been processed yet. Call the process() method first.")

# Example usage
if __name__ == "__main__":
    binance_path = '/home/tertz/tspred/ethusdt_binance.csv'
    coinext_path = '/home/tertz/tspred/data.csv'
    db_name = 'coinex_prices'
    table_name = 'ethusdt'

    processor = BinanceCoinextMerger(binance_path, coinext_path, db_name, table_name)
    merged_data = processor.process()

    print(merged_data.head())
