#!/bin/bash

# Ensures database is migrated.
# Waits for PostgreSQL and Redis to be ready, then runs migrations if needed.
# Exit codes: 0 = success, 1 = error

set -e

cd /home/vscode/project

# Wait for PostgreSQL to be ready
echo "[Database] Waiting for PostgreSQL..."
MAX_ATTEMPTS=30
ATTEMPT=0
until docker compose exec -T pgsql pg_isready -U "${DB_USERNAME:-laravel}" -d "${DB_DATABASE:-laravel}" > /dev/null 2>&1; do
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
    echo "[Database] Database appears empty or not initialized. Running migrate:fresh..."
    php artisan migrate:fresh --force
    echo "[Database] Migration complete"
else
    # Check for pending migrations
    if php artisan migrate:status --pending 2>/dev/null | grep -q "Pending"; then
        echo "[Database] Found pending migrations. Running migrate..."
        php artisan migrate --force
        echo "[Database] Migration complete"
    else
        echo "[Database] Database is up to date"
    fi
fi

# Check if database needs seeding (no users exist)
echo "[Database] Checking if seeding is needed..."
USER_COUNT=$(php artisan tinker --execute="echo \App\Models\User::count();" 2>/dev/null | tail -1)

if [ "$USER_COUNT" = "0" ] || [ -z "$USER_COUNT" ]; then
    echo "[Database] No users found. Running db:seed..."
    php artisan db:seed --force
    echo "[Database] Seeding complete"
else
    echo "[Database] Database already has data ($USER_COUNT users). Skipping seed."
fi
