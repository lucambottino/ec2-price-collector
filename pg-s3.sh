#!/bin/bash

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Start logging
log_message "Script started."

# Check if an argument is provided for the number of days
if [ -z "$1" ]; then
    log_message "No argument provided. Defaulting to 7 days."
    DAYS=7
else
    DAYS=$1
    log_message "Running the script for data older than $DAYS days."
fi

# Load environment variables from .env file
log_message "Loading environment variables."
set -a
source "$(dirname "$0")/.env"
set +a

# Define the tables and their respective date columns
declare -A TABLES
TABLES=( ["coins_table"]="" ["coin_data_table"]="updated_at" )

# Iterate over each table
for TABLE in "${!TABLES[@]}"; do
    DATE_COLUMN=${TABLES[$TABLE]}
    
    if [ -n "$DATE_COLUMN" ]; then
        EXPORT_FILE="/tmp/${TABLE}_old_data_$(date +\%Y\%m\%d).csv"
        
        if [ "$DAYS" -eq 0 ]; then
            log_message "Exporting ALL data from table $TABLE to $EXPORT_FILE."
            PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "\copy (SELECT * FROM $TABLE) TO '$EXPORT_FILE' WITH CSV HEADER"
        else
            log_message "Exporting data older than $DAYS days from table $TABLE using $DATE_COLUMN to $EXPORT_FILE."
            PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "\copy (SELECT * FROM $TABLE WHERE $DATE_COLUMN < NOW() - INTERVAL '$DAYS days') TO '$EXPORT_FILE' WITH CSV HEADER"
        fi

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
        if [ "$DAYS" -ne 0 ]; then
            log_message "Deleting old data from table $TABLE."
            PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "DELETE FROM $TABLE WHERE $DATE_COLUMN < NOW() - INTERVAL '$DAYS days';"
            
            if [ $? -eq 0 ]; then
                log_message "Old data deletion from table $TABLE successful."
            else
                log_message "Old data deletion from table $TABLE failed."
            fi
        else
            log_message "Skipping data deletion for table $TABLE because ALL data is being exported."
        fi
    else
        log_message "Skipping table $TABLE because it doesn't have a date column."
    fi
done

log_message "Script completed."
