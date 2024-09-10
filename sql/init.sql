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
    coin_name TEXT UNIQUE NOT NULL,
    precision_binance INT,
    precision_coinex INT,
    min_amount_binance REAL,
    min_amount_coinex REAL,
    trading BOOLEAN DEFAULT FALSE,
    collecting BOOLEAN DEFAULT FALSE
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

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL,                                 -- Unique identifier for each order
    coin_id INT REFERENCES coins_table(coin_id), -- Foreign key referencing the coins_table
    symbol VARCHAR(10) NOT NULL,               -- Cryptocurrency symbol (e.g., INJUSDT, AXSUSDT)
    side VARCHAR(5) CHECK (side IN ('LONG', 'SHORT')) NOT NULL,  -- Side of the order (LONG or SHORT)
    mean_premium DECIMAL(10, 4) DEFAULT 0.0,           -- Mean price, with a default value of 0.0
    entry_premium DECIMAL(10, 4) NOT NULL,             -- Entry price for the order
    exit_premium DECIMAL(10, 4) NOT NULL,              -- Exit price for the order
    quantity DECIMAL(10, 4) NOT NULL,          -- Quantity of the asset for the order
    executed_quantity_entry DECIMAL(10, 4) DEFAULT 0.0,  -- Executed quantity at the entry point, default is 0.0
    executed_quantity_exit DECIMAL(10, 4) DEFAULT 0.0,   -- Executed quantity at the exit point, default is 0.0
    exchange exchange_enum NOT NULL,           -- Exchange column with ENUM type
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp for when the order was created
    PRIMARY KEY (coin_id, id)  -- Composite primary key
);


-- Create latest_coin_data_table to store the most recent value of the coin data
CREATE TABLE IF NOT EXISTS latest_coin_data_table (
    coin_id INT REFERENCES coins_table(coin_id),
    data_id INT REFERENCES coin_data_table(data_id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    best_bid REAL,
    best_ask REAL,
    best_bid_qty REAL,
    best_ask_qty REAL,
    mark_price REAL,
    last_price REAL,  
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP, 
    exchange exchange_enum NOT NULL,
    PRIMARY KEY (coin_id, exchange)  -- Enforce one record per coin-exchange pair
);

-- Create or replace function to update latest_coin_data_table
CREATE OR REPLACE FUNCTION update_latest_coin_data()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert or update the latest_coin_data_table with the new data
    INSERT INTO latest_coin_data_table (
        coin_id, data_id, timestamp, best_bid, best_ask, best_bid_qty, best_ask_qty, 
        mark_price, last_price, updated_at, exchange
    )
    VALUES (
        NEW.coin_id, NEW.data_id, NEW.timestamp, NEW.best_bid, NEW.best_ask, 
        NEW.best_bid_qty, NEW.best_ask_qty, NEW.mark_price, NEW.last_price, 
        NEW.updated_at, NEW.exchange
    )
    ON CONFLICT (coin_id, exchange) 
    DO UPDATE SET 
        data_id = EXCLUDED.data_id,
        timestamp = EXCLUDED.timestamp,
        best_bid = EXCLUDED.best_bid,
        best_ask = EXCLUDED.best_ask,
        best_bid_qty = EXCLUDED.best_bid_qty,
        best_ask_qty = EXCLUDED.best_ask_qty,
        mark_price = EXCLUDED.mark_price,
        last_price = EXCLUDED.last_price,
        updated_at = EXCLUDED.updated_at;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update latest_coin_data_table after insert on coin_data_table
CREATE TRIGGER update_latest_trigger
AFTER INSERT ON coin_data_table
FOR EACH ROW
EXECUTE FUNCTION update_latest_coin_data();
