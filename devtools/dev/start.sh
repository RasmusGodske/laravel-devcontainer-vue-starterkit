#!/bin/bash
# Start the development environment (for CI/headless use)
#
# This script runs all setup steps and starts all services sequentially.
# For interactive use, prefer the VS Code "Dev: Start" task which shows
# each step in its own terminal.
#
# Usage:
#   ./start.sh          Start everything
#   ./start.sh --quick  Skip setup, just start services

set -e

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
SETUP_DIR="$PROJECT_ROOT/devtools/setup"
SERVICES_DIR="$PROJECT_ROOT/devtools/services"

cd "$PROJECT_ROOT"

quick_mode=false
if [[ "$1" == "--quick" ]]; then
    quick_mode=true
fi

echo "=== Starting Development Environment ==="
echo ""

if [[ "$quick_mode" == false ]]; then
    echo "[1/7] Ensuring .env..."
    "$SETUP_DIR/env.sh"

    echo ""
    echo "[2/7] Ensuring Composer dependencies..."
    "$SETUP_DIR/composer.sh"

    echo ""
    echo "[3/7] Ensuring APP_KEY..."
    "$SETUP_DIR/app-key.sh"

    echo ""
    echo "[4/7] Ensuring npm dependencies..."
    "$SETUP_DIR/npm.sh"
fi

echo ""
echo "[5/8] Starting database..."
"$SERVICES_DIR/database.sh" start

echo ""
echo "[6/8] Starting cache..."
"$SERVICES_DIR/cache.sh" start

if [[ "$quick_mode" == false ]]; then
    echo ""
    echo "[7/8] Ensuring database migrations..."
    "$SETUP_DIR/migrated.sh"

    echo ""
    echo "Configuring URLs..."
    "$SETUP_DIR/urls.sh"
fi

echo ""
echo "[8/8] Starting services..."
"$SERVICES_DIR/serve.sh" start
"$SERVICES_DIR/vite.sh" start

echo ""
echo "=== Development Environment Ready ==="
"$SCRIPT_DIR/status.sh"
