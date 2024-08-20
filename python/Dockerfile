# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Ensure the initialize_coins.py script is executable
RUN chmod +x /app/coins/initialize_coins.py

# Command to run the initialization and main application
CMD ["bash", "-c", "python /app/coins/initialize_coins.py && python main.py"]
