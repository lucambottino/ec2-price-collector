#!/bin/bash

# Step 1: Delete the data folder
# Step 1: Check if the script has the right access to the data folder
if [ -d "./data" ]; then
  if [ -w "./data" ] && [ -x "./data" ]; then
    echo "Access check passed: Deleting the data folder..."
    rm -rf ./data
  else
    echo "Error: Insufficient permissions to delete the data folder."
    exit 1
  fi
else
  echo "Data folder does not exist. Skipping deletion."
fi

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
