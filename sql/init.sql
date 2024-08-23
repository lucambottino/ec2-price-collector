-- Create ENUM type for exchange if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'exchange_enum') THEN
        CREATE TYPE exchange_enum AS ENUM ('BINANCE', 'COINEX');
    END IF;
END $$;

-- Create coins_table if it doesn't exist
CREATE TABLE IF NOT EXISTS coins_table (
    coin_id SERIAL PRIMARY KEY,
    coin_name TEXT UNIQUE NOT NULL
);

-- Create coin_data_table if it doesn't exist
CREATE TABLE IF NOT EXISTS coin_data_table (
    data_id SERIAL PRIMARY KEY,
    coin_id INT REFERENCES coins_table(coin_id),
    timestamp TIMESTAMPTZ NOT NULL,
    best_bid REAL,
    best_ask REAL,
    best_bid_qty REAL,
    best_ask_qty REAL,
    mark_price REAL,
    last_price REAL,  
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP, 
    exchange exchange_enum NOT NULL
);
