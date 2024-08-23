#!/bin/bash

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Start logging
log_message "Script started."

# Load environment variables from .env file
log_message "Loading environment variables."
set -a
source "$(dirname "$0")/.env"
set +a


# Export data older than 7 days to a CSV file
EXPORT_FILE="/tmp/old_data_$(date +\%Y\%m\%d).csv"
log_message "Exporting data older than 7 days to $EXPORT_FILE."
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "\copy (SELECT * FROM your_table WHERE created_at < NOW() - INTERVAL '7 days') TO '$EXPORT_FILE' WITH CSV HEADER"

if [ $? -eq 0 ]; then
    log_message "Data export successful."
else
    log_message "Data export failed."
fi

# Upload the CSV file to S3
log_message "Uploading $EXPORT_FILE to S3."
aws s3 cp $EXPORT_FILE s3://$S3_BUCKET/ --region $REGION

if [ $? -eq 0 ]; then
    log_message "Upload successful."
else
    log_message "Upload failed."
fi

# Delete the CSV file after upload
log_message "Deleting the CSV file $EXPORT_FILE."
rm $EXPORT_FILE

if [ $? -eq 0 ]; then
    log_message "CSV file deleted."
else
    log_message "Failed to delete CSV file."
fi

# Delete old data from the database
log_message "Deleting old data from the database."
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "DELETE FROM your_table WHERE created_at < NOW() - INTERVAL '7 days';"

if [ $? -eq 0 ]; then
    log_message "Old data deletion successful."
else
    log_message "Old data deletion failed."
fi

log_message "Script completed."
