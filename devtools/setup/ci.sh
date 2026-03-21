#!/bin/bash

# CI environment setup script
# Sets up the Laravel application for CI/GitHub Actions environments.
#
# Usage:
#   ./devtools/setup/ci.sh          # Basic setup (env, composer, app-key)
#   ./devtools/setup/ci.sh --npm    # Include npm dependencies
#   ./devtools/setup/ci.sh --build  # Include npm + build frontend assets
#
# This script:
# - Creates .env from .env.example (with testing overrides)
# - Creates SQLite database file (for package discovery)
# - Installs composer dependencies
# - Generates APP_KEY
# - Optionally installs npm and builds assets
#
# Unlike local development setup (Dev: Start), this script:
# - Does NOT start docker containers (uses SQLite, not PostgreSQL)
# - Does NOT run migrations or seeding
# - Does NOT start artisan serve or npm dev

set -e

# Resolve script location to find project root
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_DIR"

# Parse arguments
INCLUDE_NPM=false
INCLUDE_BUILD=false
for arg in "$@"; do
    case $arg in
        --npm)
            INCLUDE_NPM=true
            ;;
        --build)
            INCLUDE_NPM=true
            INCLUDE_BUILD=true
            ;;
    esac
done

echo "=== CI Environment Setup ==="

# Step 1: Create .env
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "[Setup] Creating .env from .env.example..."
        cp .env.example .env
    else
        echo "[Error] .env.example not found!"
        exit 1
    fi
else
    echo "[Check] .env exists"
fi

# Step 2: Create SQLite database file (prevents errors during package discovery)
SQLITE_DB="database/database.sqlite"
if [ ! -f "$SQLITE_DB" ]; then
    echo "[Setup] Creating SQLite database file..."
    touch "$SQLITE_DB"
else
    echo "[Check] SQLite database file exists"
fi

# Step 3: Install composer dependencies
if [ ! -f composer.lock ]; then
    echo "[Error] composer.lock not found!"
    exit 1
fi

if [ ! -d vendor ] || [ composer.lock -nt vendor/autoload.php ]; then
    echo "[Setup] Installing composer dependencies..."
    composer install --no-interaction --prefer-dist --no-progress
else
    echo "[Check] Composer dependencies are up to date"
fi

# Step 4: Generate APP_KEY if not set
if grep -q "^APP_KEY=base64:" .env 2>/dev/null; then
    echo "[Check] APP_KEY is set"
else
    echo "[Setup] Generating application key..."
    php artisan key:generate
fi

# Step 5: Optional npm dependencies
if [ "$INCLUDE_NPM" = true ]; then
    if [ ! -f package-lock.json ]; then
        echo "[Error] package-lock.json not found!"
        exit 1
    fi

    if [ ! -d node_modules ] || [ package-lock.json -nt node_modules/.package-lock.json ]; then
        echo "[Setup] Installing npm dependencies..."
        npm ci --no-progress
    else
        echo "[Check] npm dependencies are up to date"
    fi
fi

# Step 6: Optional frontend build
if [ "$INCLUDE_BUILD" = true ]; then
    if [ ! -f public/build/manifest.json ]; then
        echo "[Setup] Building frontend assets..."
        npm run build
    else
        echo "[Check] Frontend assets already built"
    fi
fi

echo "=== CI Setup Complete ==="
