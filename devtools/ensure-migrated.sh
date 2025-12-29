#!/bin/bash

# Ensures database is migrated.
# Waits for PostgreSQL and Redis to be ready, then runs migrations if needed.
# Exit codes: 0 = success, 1 = error

set -e

cd /home/vscode/project

# Source .env to get database credentials
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

DB_USERNAME="${DB_USERNAME:-laravel}"
DB_DATABASE="${DB_DATABASE:-laravel}"

# Wait for PostgreSQL to be ready
echo "[Database] Waiting for PostgreSQL..."
MAX_ATTEMPTS=30
ATTEMPT=0
until docker compose exec -T pgsql pg_isready -U "$DB_USERNAME" -d "$DB_DATABASE" > /dev/null 2>&1; do
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
        echo "[Error] PostgreSQL did not become ready in time"
        exit 1
    fi
    sleep 1
done
echo "[Database] PostgreSQL is ready"

# Wait for Redis to be ready
echo "[Database] Waiting for Redis..."
ATTEMPT=0
until docker compose exec -T redis redis-cli ping > /dev/null 2>&1; do
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
        echo "[Error] Redis did not become ready in time"
        exit 1
    fi
    sleep 1
done
echo "[Database] Redis is ready"

echo "[Database] Checking migration status..."

# Check if we can connect and get migration status
if ! php artisan migrate:status > /dev/null 2>&1; then
    echo "[Database] Database appears empty or not initialized. Running migrate:fresh --seed..."
    php artisan migrate:fresh --seed
    echo "[Database] Migration complete"
    exit 0
fi

# Check for pending migrations
PENDING_COUNT=$(php artisan migrate:status --pending 2>/dev/null | grep -c "Pending" || echo "0")

if [ "$PENDING_COUNT" != "0" ]; then
    echo "[Database] Found $PENDING_COUNT pending migration(s). Running migrate..."
    php artisan migrate --force
    echo "[Database] Migration complete"
else
    echo "[Database] Database is up to date"
fi
