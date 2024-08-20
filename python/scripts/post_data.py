import psycopg2
import os

def create_connection():
    """Create a database connection to PostgreSQL"""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DBNAME"),
            user="postgres",
            password=os.getenv("DB_PASSWORD"),
            host="postgres" 
        )
        print("Successfully connected to the database")
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
    return conn

def get_coin_id(conn, coin_name):
    """Retrieve the coin_id from coins_table based on the coin name"""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT coin_id FROM coins_table WHERE coin_name = %s", (coin_name,))
            result = cur.fetchone()
            return result[0] if result else None
    except psycopg2.Error as e:
        print(f"Error fetching coin_id for {coin_name}: {e}")
        return None

def insert_data(conn, coin_id, data):
    """Insert data into coin_data_table using the coin_id as a foreign key"""
    try:
        with conn.cursor() as cur:
            insert_query = """
                INSERT INTO coin_data_table (
                    coin_id, timestamp, best_bid, best_ask, best_bid_qty, best_ask_qty,
                    mark_price, market, best_bid_price, best_bid_size, best_ask_price, best_ask_size, price, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(insert_query, (coin_id, *data))
            conn.commit()
            print("Data inserted successfully")
    except psycopg2.Error as e:
        print(f"Error inserting data: {e}")