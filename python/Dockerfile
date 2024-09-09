# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install PostgreSQL development libraries
RUN apt-get update && apt-get install -y gcc libpq-dev

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Ensure the initialization scripts are executable
RUN chmod +x /app/scripts/ws_coinex.py /app/scripts/ws_binance.py /app/scripts/coin_list.py

# Default command to keep the container running (e.g., start ws_coinex or ws_binance)
CMD ["bash"]
