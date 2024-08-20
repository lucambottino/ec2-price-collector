import os
import psycopg2
from coins.coin_list import COIN_LIST  # Import the coin list from coin_list.py

def create_connection():
    """Create a connection to the PostgreSQL database."""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DBNAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST")
        )
        print("Successfully connected to the database")
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
    return conn

def insert_coins(conn, coins):
    """Insert coins into the coins_table."""
    try:
        with conn.cursor() as cur:
            for coin in coins:
                cur.execute("INSERT INTO coins_table (coin_name) VALUES (%s) ON CONFLICT DO NOTHING;", (coin,))
            conn.commit()
            print("Coins inserted successfully")
    except psycopg2.Error as e:
        print(f"Error inserting coins: {e}")

def main():
    conn = create_connection()
    if conn:
        # Insert the coin list into the database
        insert_coins(conn, COIN_LIST)
        conn.close()
    else:
        print("Failed to connect to the database")

if __name__ == "__main__":
    main()
