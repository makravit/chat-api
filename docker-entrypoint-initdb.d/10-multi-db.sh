#!/bin/bash
set -e
echo "[multi-db] Entrypoint script running as: $(whoami)"
echo "[multi-db] POSTGRES_MULTIPLE_DATABASES: $POSTGRES_MULTIPLE_DATABASES"
echo "[multi-db] POSTGRES_USER: $POSTGRES_USER"
ls -l /docker-entrypoint-initdb.d || true

# Create additional databases from comma-separated list in POSTGRES_MULTIPLE_DATABASES
if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
  echo "[multi-db] Creating multiple databases: $POSTGRES_MULTIPLE_DATABASES"
  for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
    echo "[multi-db] Creating database: $db"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -d postgres <<-EOSQL
      CREATE DATABASE "$db";
EOSQL
    if [ $? -eq 0 ]; then
      echo "[multi-db] Successfully created database: $db"
    else
      echo "[multi-db] Failed to create database: $db" >&2
    fi
  done
else
  echo "[multi-db] No additional databases to create."
fi
