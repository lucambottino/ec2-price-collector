#!/bin/bash

# Step 1: Delete the data folder
echo "Deleting the data folder..."
rm -rf ./data

# Step 2: Bring down Docker containers
echo "Bringing down Docker containers..."
docker-compose down

# Step 3: Rebuild Docker images
echo "Rebuilding Docker images..."
docker-compose build

# Step 4: Bring Docker containers back up
echo "Bringing Docker containers back up..."
docker-compose up

echo "Script executed successfully!"
