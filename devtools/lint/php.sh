#!/bin/bash
# Run PHPStan static analysis
#
# This script can be used both locally and in CI/CD pipelines.
# It sets up the environment and runs PHPStan.
#
# Usage:
#   ./devtools/lint/php.sh              # Run PHPStan analysis
#   ./devtools/lint/php.sh --generate-baseline  # Generate new baseline
#
# Alias: lint:php (via symlink in /usr/local/bin)

set -e

# Disable Xdebug for performance - not needed for static analysis
export XDEBUG_MODE=off

# Resolve symlinks to get actual script location
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_DIR"

ARGS=("$@")

# Helper function to run a command (kept as a thin wrapper so call sites stay
# uniform and we have a single place to add cross-cutting behavior later).
run_cmd() {
    "$@"
}

echo "=== Setting up PHPStan environment ==="

# Ensure .env exists (needed for Laravel bootstrap)
if [ ! -f .env ]; then
    echo "Creating .env from .env.testing..."
    cp .env.testing .env
fi

# Create SQLite database file if using SQLite
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

echo "=== Running PHPStan ==="

# Pass all arguments to composer phpstan
# Capture exit code to save tarnished checkpoint on success
set +e
if [ ${#ARGS[@]} -eq 0 ]; then
    run_cmd composer phpstan
else
    run_cmd ./vendor/bin/phpstan "${ARGS[@]}"
fi
exit_code=$?
set -e

# Save tarnished checkpoint on success
if [ $exit_code -eq 0 ]; then
    tarnished save lint:php 2>/dev/null || true
fi

exit $exit_code
