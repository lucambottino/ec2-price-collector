-- Create the database if it doesn't exist
CREATE DATABASE coinex_prices
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1;

-- Connect to the new database
\connect coinex_prices;

-- Create the coins_table to store unique coin names
CREATE TABLE IF NOT EXISTS coins_table (
    coin_id SERIAL PRIMARY KEY,
    coin_name TEXT UNIQUE NOT NULL
);

-- Create the coin_data_table with a foreign key reference to coins_table
CREATE TABLE IF NOT EXISTS coin_data_table (
    data_id SERIAL PRIMARY KEY,
    coin_id INT REFERENCES coins_table(coin_id),
    timestamp TIMESTAMPTZ NOT NULL,
    best_bid REAL,
    best_ask REAL,
    best_bid_qty REAL,
    best_ask_qty REAL,
    mark_price REAL,
    market TEXT,
    best_bid_price REAL,
    best_bid_size REAL,
    best_ask_price REAL,
    best_ask_size REAL,
    price REAL,
    updated_at TIMESTAMPTZ
);
