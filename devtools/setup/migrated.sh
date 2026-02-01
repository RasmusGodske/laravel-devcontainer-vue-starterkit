#!/bin/bash
# Ensures database is migrated.
#
# Usage:
#   ./migrated.sh              Run setup (direct, for backwards compatibility)
#   ./migrated.sh run          Run setup in tmux session (captures output)
#   ./migrated.sh run --attach Run setup in tmux and attach to watch
#   ./migrated.sh status       Check if database is migrated
#   ./migrated.sh logs [N]     Show setup output from tmux session

SETUP_NAME="setup-migrated"
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

cd /home/vscode/project

# The actual setup logic
do_setup() {
    # Wait for PostgreSQL to be ready
    echo "[Database] Waiting for PostgreSQL..."
    MAX_ATTEMPTS=30
    ATTEMPT=0
    until docker compose exec -T pgsql pg_isready -U "${DB_USERNAME:-laravel}" -d "${DB_DATABASE:-laravel}" > /dev/null 2>&1; do
        ATTEMPT=$((ATTEMPT + 1))
        if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
            echo "[Error] PostgreSQL did not become ready in time"
            return 1
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
            return 1
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

    # Set up testing database for parallel tests
    echo "[Database] Setting up testing database..."
    TESTING_DB="testing"

    # Check if testing database exists
    if docker compose exec -T pgsql psql -U "${DB_USERNAME:-laravel}" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$TESTING_DB'" 2>/dev/null | grep -q 1; then
        echo "[Database] Testing database already exists"
    else
        echo "[Database] Creating testing database..."
        docker compose exec -T pgsql psql -U "${DB_USERNAME:-laravel}" -d postgres -c "CREATE DATABASE $TESTING_DB OWNER ${DB_USERNAME:-laravel};"
        echo "[Database] Testing database created"
    fi

    # Run migrations on testing database
    echo "[Database] Migrating testing database..."
    DB_DATABASE=$TESTING_DB php artisan migrate --force
    echo "[Database] Testing database ready"
}

# Status check (quick, no setup)
do_status() {
    if php artisan migrate:status 2>/dev/null | grep -q "Ran"; then
        if php artisan migrate:status --pending 2>/dev/null | grep -q "Pending"; then
            echo "[pending] Database has pending migrations"
            return 1
        else
            echo "[ok] Database is migrated"
            return 0
        fi
    else
        echo "[missing] Database not migrated"
        return 1
    fi
}

# Source shared library for tmux functions
source "$SCRIPT_DIR/_lib.sh"

# Command dispatcher
case "${1:-}" in
    run)
        shift
        run_setup_in_tmux "$@"
        ;;
    status)
        do_status
        ;;
    logs)
        show_setup_logs "${2:-50}"
        ;;
    *)
        # Backwards compatible - run directly
        do_setup
        ;;
esac
