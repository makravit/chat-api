#!/bin/sh
# Usage: ./scripts/create_migration.sh "Migration message"

set -e

# Start the database container if not running
if ! docker ps | grep -q "_db"; then
  echo "Starting database container..."
  docker compose up -d db
  sleep 5
fi



# Always use localhost for local migrations
export DATABASE_URL="postgresql://chatbot:chatbotpass@localhost:5432/chatbotdb"

# Run Alembic migration commands
alembic revision --autogenerate -m "$1"
alembic upgrade head

echo "Migration created and applied."
