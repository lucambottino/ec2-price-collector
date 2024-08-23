import os
import psycopg2


class DBManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
            )
            self.cursor = self.conn.cursor()
            print("Connected to DB")
        except Exception as e:
            print(f"Error connecting to DB: {e}")

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error executing query: {e}")
            self.conn.rollback()  # Rollback the transaction on error
            return None

    def commit(self):
        try:
            self.conn.commit()
        except Exception as e:
            print(f"Error committing transaction: {e}")
            self.conn.rollback()  # Rollback the transaction on error
