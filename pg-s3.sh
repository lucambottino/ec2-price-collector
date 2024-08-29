#!/bin/bash

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Start logging
log_message "Script started."

# Initialize NO_DELETE as true by default
NO_DELETE=true

# Check for --delete option to allow deletion
if [[ "$*" == *"--delete"* ]]; then
    NO_DELETE=false
    log_message "--delete option detected. Data will be deleted after export."
else
    log_message "No --delete option detected. Data will not be deleted after export."
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
    log_message "No format argument provided. Defaulting to binary."
    FORMAT="binary"
else
    FORMAT=$2
    log_message "Exporting data in $FORMAT format."
fi

# Fixed environment variables
POSTGRES_HOST=ec2-price-collector-postgres-1  # Update this to your Docker service name
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=coinex-prices
POSTGRES_PORT=5432
S3_BUCKET=coins-prices
REGION=sa-east-1

# Log the fixed environment variables to ensure they are set correctly
log_message "POSTGRES_HOST is set to: $POSTGRES_HOST"
log_message "POSTGRES_USER is set to: $POSTGRES_USER"
log_message "POSTGRES_DB is set to: $POSTGRES_DB"
log_message "POSTGRES_PORT is set to: $POSTGRES_PORT"
log_message "S3_BUCKET is set to: $S3_BUCKET"
log_message "REGION is set to: $REGION"

# Define the tables and their respective date columns
declare -A TABLES
TABLES=( ["coins_table"]="" ["coin_data_table"]="updated_at" )

# Iterate over each table
for TABLE in "${!TABLES[@]}"; do
    DATE_COLUMN=${TABLES[$TABLE]}
    EXPORT_FILE="/tmp/${TABLE}_old_data_$(date +\%Y\%m\%d).$FORMAT"

    if [ -n "$DATE_COLUMN" ]; then
        log_message "Running query: SELECT * FROM $TABLE WHERE $DATE_COLUMN < NOW() - INTERVAL '$DAYS days';"
        if [ "$FORMAT" == "csv" ]; then
            PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "\copy (SELECT * FROM $TABLE WHERE $DATE_COLUMN < NOW() - INTERVAL '$DAYS days') TO '$EXPORT_FILE' WITH CSV HEADER"
        elif [ "$FORMAT" == "text" ]; then
            PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "\copy (SELECT * FROM $TABLE WHERE $DATE_COLUMN < NOW() - INTERVAL '$DAYS days') TO '$EXPORT_FILE' WITH DELIMITER E'\t'"
        elif [ "$FORMAT" == "binary" ]; then
            PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "\copy $TABLE TO '$EXPORT_FILE' WITH BINARY"
        fi
    else
        log_message "Skipping table $TABLE because it doesn't have a date column."
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
    
    # Delete data from the table only if --delete is specified
    if [ "$NO_DELETE" = false ]; then
        log_message "Deleting ALL data from table $TABLE."
        PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "DELETE FROM $TABLE WHERE $DATE_COLUMN < NOW() - INTERVAL '$DAYS days';"

        if [ $? -eq 0 ]; then
            log_message "All data deletion from table $TABLE successful."
        else
            log_message "All data deletion from table $TABLE failed."
        fi
    else
        log_message "No --delete option passed. Skipping data deletion for table $TABLE."
    fi
done

log_message "Script completed."
