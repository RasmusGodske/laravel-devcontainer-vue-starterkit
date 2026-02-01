#!/bin/bash
# Run PHP tests (PHPUnit via Laravel)
#
# This script can be used both locally and in CI/CD pipelines.
# It sets up the testing environment and runs the test suite.
#
# Usage:
#   ./devtools/test/php.sh                    # Run all tests
#   ./devtools/test/php.sh --filter=TestName  # Run specific tests
#   ./devtools/test/php.sh --parallel         # Run tests in parallel
#
# Alias: test:php (via symlink in /usr/local/bin)
#
# Options:
#   --debug     Enable Xdebug (disabled by default for performance)
#   --no-lumby  Skip AI diagnosis on failure
#
# Environment variables:
#   SKIP_NPM_BUILD=1  - Skip npm install and build (faster, but view tests may fail)

set -e

# Resolve symlinks to get actual script location
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_DIR"

# Parse custom options
USE_LUMBY=true
USE_XDEBUG=false
ARGS=()
for arg in "$@"; do
    if [ "$arg" = "--no-lumby" ]; then
        USE_LUMBY=false
    elif [ "$arg" = "--debug" ]; then
        USE_XDEBUG=true
    else
        ARGS+=("$arg")
    fi
done

# Disable Xdebug by default for performance (~6x faster)
# Use --debug flag to enable Xdebug when you need to debug tests
if [ "$USE_XDEBUG" = "false" ]; then
    export XDEBUG_MODE=off
fi

# Auto-disable Lumby in CI environments when ANTHROPIC_API_KEY is not set
# When the API key is available, Lumby can authenticate Claude Code
if [ "${CI:-false}" = "true" ] && [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    USE_LUMBY=false
fi

# Helper function to run command with optional lumby
run_cmd() {
    if [ "$USE_LUMBY" = "true" ]; then
        lumby -- "$@"
    else
        "$@"
    fi
}

echo "=== Setting up testing environment ==="

# Ensure .env exists (copy from .env.testing if not)
if [ ! -f .env ]; then
    echo "Creating .env from .env.testing..."
    cp .env.testing .env
fi

# Create SQLite database file if using SQLite for testing
# This prevents errors during composer install / package discovery
SQLITE_DB="database/database.sqlite"
if [ ! -f "$SQLITE_DB" ]; then
    echo "Creating SQLite database file..."
    touch "$SQLITE_DB"
fi

# Install composer dependencies if vendor doesn't exist or composer.lock changed
if [ ! -d "vendor" ] || [ "composer.lock" -nt "vendor/autoload.php" ]; then
    echo "Installing Composer dependencies..."
    run_cmd composer install --no-interaction --prefer-dist
fi

# Generate application key if not set
if ! grep -q "^APP_KEY=base64:" .env 2>/dev/null; then
    echo "Generating application key..."
    run_cmd php artisan key:generate
fi

# Build frontend assets (needed for Inertia/view tests)
if [ "${SKIP_NPM_BUILD:-0}" != "1" ]; then
    if [ ! -d "node_modules" ] || [ "package-lock.json" -nt "node_modules/.package-lock.json" ]; then
        echo "Installing npm dependencies..."
        run_cmd npm ci
    fi

    if [ ! -f "public/build/manifest.json" ]; then
        echo "Building frontend assets..."
        run_cmd npm run build
    fi
fi

echo "=== Running tests ==="

# Pass all arguments to php artisan test
# Default to --parallel if no arguments provided
# Capture exit code to save tarnished checkpoint on success
set +e
if [ ${#ARGS[@]} -eq 0 ]; then
    run_cmd php artisan test --parallel
else
    run_cmd php artisan test "${ARGS[@]}"
fi
exit_code=$?
set -e

# Save tarnished checkpoint on success
if [ $exit_code -eq 0 ]; then
    tarnished save test:php 2>/dev/null || true
fi

exit $exit_code
