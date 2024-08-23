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

# Get a list of all tables in the database
TABLES=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -t -c "SELECT tablename FROM pg_tables WHERE schemaname='public';")

# Iterate over each table and export data older than 7 days
for TABLE in $TABLES; do
    EXPORT_FILE="/tmp/${TABLE}_old_data_$(date +\%Y\%m\%d).csv"
    log_message "Exporting data older than 7 days from table $TABLE to $EXPORT_FILE."
    
    # Export data older than 7 days to a CSV file
    PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "\copy (SELECT * FROM $TABLE WHERE created_at < NOW() - INTERVAL '7 days') TO '$EXPORT_FILE' WITH CSV HEADER"

    if [ $? -eq 0 ]; then
        log_message "Data export from table $TABLE successful."
    else
        log_message "Data export from table $TABLE failed."
        continue
    fi

    # Upload the CSV file to S3
    log_message "Uploading $EXPORT_FILE to S3."
    aws s3 cp $EXPORT_FILE s3://$S3_BUCKET/ --region $REGION

    if [ $? -eq 0 ]; then
        log_message "Upload of $EXPORT_FILE successful."
    else
        log_message "Upload of $EXPORT_FILE failed."
        continue
    fi

    # Delete the CSV file after upload
    log_message "Deleting the CSV file $EXPORT_FILE."
    rm $EXPORT_FILE

    if [ $? -eq 0 ]; then
        log_message "CSV file $EXPORT_FILE deleted."
    else
        log_message "Failed to delete CSV file $EXPORT_FILE."
    fi

    # Delete old data from the table
    log_message "Deleting old data from table $TABLE."
    PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "DELETE FROM $TABLE WHERE created_at < NOW() - INTERVAL '7 days';"

    if [ $? -eq 0 ]; then
        log_message "Old data deletion from table $TABLE successful."
    else
        log_message "Old data deletion from table $TABLE failed."
    fi
done

log_message "Script completed."
