#!/bin/bash

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Start logging
log_message "Script started."

# Initialize no_delete flag
NO_DELETE=false

# Check for --no-delete option
if [[ "$*" == *"--no-delete"* ]]; then
    NO_DELETE=true
    log_message "--no-delete option detected. Data will not be deleted after export."
fi

# Check if an argument is provided for the number of days
if [ -z "$1" ]; then
    log_message "No argument provided for days. Defaulting to 7 days."
    DAYS=7
else
    DAYS=$1
    log_message "Running the script for data older than $DAYS days."
fi

# Check if an argument is provided for the format
if [ -z "$2" ]; then
    log_message "No format argument provided. Defaulting to CSV."
    FORMAT="binary"
else
    FORMAT=$2
    log_message "Exporting data in $FORMAT format."
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
    EXPORT_FILE="/tmp/${TABLE}_old_data_$(date +\%Y\%m\%d).$FORMAT"

    if [ -n "$DATE_COLUMN" ]; then
        if [ "$DAYS" -eq 0 ]; then
            log_message "Exporting ALL data from table $TABLE to $EXPORT_FILE."
            if [ "$FORMAT" == "csv" ]; then
                PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "\copy (SELECT * FROM $TABLE) TO '$EXPORT_FILE' WITH CSV HEADER"
            elif [ "$FORMAT" == "text" ]; then
                PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "\copy (SELECT * FROM $TABLE) TO '$EXPORT_FILE' WITH DELIMITER E'\t'"
            elif [ "$FORMAT" == "binary" ]; then
                PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "\copy $TABLE TO '$EXPORT_FILE' WITH BINARY"
            fi
        else
            log_message "Exporting data older than $DAYS days from table $TABLE using $DATE_COLUMN to $EXPORT_FILE."
            if [ "$FORMAT" == "csv" ]; then
                PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "\copy (SELECT * FROM $TABLE WHERE $DATE_COLUMN < NOW() - INTERVAL '$DAYS days') TO '$EXPORT_FILE' WITH CSV HEADER"
            elif [ "$FORMAT" == "text" ]; then
                PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "\copy (SELECT * FROM $TABLE WHERE $DATE_COLUMN < NOW() - INTERVAL '$DAYS days') TO '$EXPORT_FILE' WITH DELIMITER E'\t'"
            elif [ "$FORMAT" == "binary" ]; then
                PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "\copy $TABLE TO '$EXPORT_FILE' WITH BINARY"
            fi
        fi

        if [ $? -eq 0 ]; then
            log_message "Data export from table $TABLE successful."
        else
            log_message "Data export from table $TABLE failed."
            continue
        fi
        
        # Upload the exported file to S3
        log_message "Uploading $EXPORT_FILE to S3."
        aws s3 cp $EXPORT_FILE s3://$S3_BUCKET/ --region $REGION
        
        if [ $? -eq 0 ]; then
            log_message "Upload of $EXPORT_FILE successful."
        else
            log_message "Upload of $EXPORT_FILE failed."
            continue
        fi
        
        # Delete the exported file after upload
        log_message "Deleting the exported file $EXPORT_FILE."
        rm $EXPORT_FILE
        
        if [ $? -eq 0 ]; then
            log_message "Exported file $EXPORT_FILE deleted."
        else
            log_message "Failed to delete exported file $EXPORT_FILE."
        fi
        
        # Delete data from the table unless --no-delete is specified
        if [ "$NO_DELETE" = false ]; then
            log_message "Deleting ALL data from table $TABLE."
            PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "DELETE FROM $TABLE;"

            if [ $? -eq 0 ]; then
                log_message "All data deletion from table $TABLE successful."
            else
                log_message "All data deletion from table $TABLE failed."
            fi
        else
            log_message "--no-delete option is set. Skipping data deletion for table $TABLE."
        fi
    else
        log_message "Skipping table $TABLE because it doesn't have a date column."
    fi
done

log_message "Script completed."
