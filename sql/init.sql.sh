#!/bin/bash

# Set environment variables (replace with actual values or export from a .env file)
POSTGRES_HOST=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=coinex-prices
POSTGRES_PORT=5432
CONTAINER_NAME="ec2-price-collector-postgres-1"

# Start Docker containers
echo "Starting Docker containers..."
docker-compose up -d

# Wait for the PostgreSQL container to be healthy
echo "Waiting for PostgreSQL container to become healthy..."
until [ "$(docker inspect -f {{.State.Health.Status}} $CONTAINER_NAME)" == "healthy" ]; do
    sleep 1
done

# Run the init.sql file inside the container
SQL_FILE_PATH="/docker-entrypoint-initdb.d/init.sql"

echo "Running init.sql script inside the container..."
docker exec -it $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB -f $SQL_FILE_PATH

echo "init.sql script executed successfully."