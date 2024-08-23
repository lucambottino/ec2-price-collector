#!/bin/bash

# Load environment variables from .env file
set -a
source "$(dirname "$0")/.env"
set +a

# Export data older than 7 days to a CSV file
EXPORT_FILE="/tmp/old_data_$(date +\%Y\%m\%d).csv"
psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "\copy (SELECT * FROM your_table WHERE created_at < NOW() - INTERVAL '7 days') TO '$EXPORT_FILE' WITH CSV HEADER"

# Upload the CSV file to S3
aws s3 cp $EXPORT_FILE s3://$S3_BUCKET/ --region $REGION

# Delete the CSV file after upload
rm $EXPORT_FILE

# Delete old data from the database
psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "DELETE FROM your_table WHERE created_at < NOW() - INTERVAL '7 days';"
