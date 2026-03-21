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
    echo "[1/9] Ensuring .env..."
    "$SETUP_DIR/env.sh"

    echo ""
    echo "[2/9] Configuring access & ports..."
    "$SETUP_DIR/configure-ports.sh"

    echo ""
    echo "[3/9] Ensuring Composer dependencies..."
    "$SETUP_DIR/composer.sh"

    echo ""
    echo "[4/9] Ensuring APP_KEY..."
    "$SETUP_DIR/app-key.sh"

    echo ""
    echo "[5/9] Ensuring npm dependencies..."
    "$SETUP_DIR/npm.sh"
fi

echo ""
echo "[6/9] Starting database..."
"$SERVICES_DIR/database.sh" start

echo ""
echo "[7/9] Starting cache..."
"$SERVICES_DIR/cache.sh" start

if [[ "$quick_mode" == false ]]; then
    echo ""
    echo "[8/9] Ensuring database migrations..."
    "$SETUP_DIR/migrated.sh"
fi

echo ""
echo "[9/9] Starting services..."
"$SERVICES_DIR/serve.sh" start
"$SERVICES_DIR/vite.sh" start
"$SERVICES_DIR/desktop.sh" start

echo ""
echo "=== Development Environment Ready ==="
"$SCRIPT_DIR/status.sh"
