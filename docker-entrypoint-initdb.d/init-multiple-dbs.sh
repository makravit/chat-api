#!/bin/bash
set -e

# Create multiple databases if POSTGRES_MULTIPLE_DATABASES is set
if [ "$POSTGRES_MULTIPLE_DATABASES" != "" ]; then
    echo "Creating multiple databases: $POSTGRES_MULTIPLE_DATABASES"
    for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
            CREATE DATABASE "$db";
EOSQL
    done
fi
