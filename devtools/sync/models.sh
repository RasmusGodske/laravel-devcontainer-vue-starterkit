#!/bin/bash
# Sync model @property annotations using ide-helper
#
# Usage:
#   ./devtools/sync/models.sh       # Regenerate model annotations
#
# Alias: sync:models (via symlink in /usr/local/bin)

set -e

# Disable Xdebug for performance
export XDEBUG_MODE=off

# Resolve symlinks to get actual script location
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_DIR"

# Ensure .env exists (needed for Laravel bootstrap)
if [ ! -f .env ]; then
    echo "Creating .env from .env.testing..."
    cp .env.testing .env
fi

# Create SQLite database file if using SQLite (needed for ide-helper schema introspection)
SQLITE_DB="database/database.sqlite"
if [ ! -f "$SQLITE_DB" ]; then
    echo "Creating SQLite database file..."
    touch "$SQLITE_DB"
fi

# Install composer dependencies if vendor doesn't exist or composer.lock changed
if [ ! -d "vendor" ] || [ "composer.lock" -nt "vendor/autoload.php" ]; then
    echo "Installing Composer dependencies..."
    composer install --no-interaction --prefer-dist
fi

# Generate application key if not set
if ! grep -q "^APP_KEY=base64:" .env 2>/dev/null; then
    echo "Generating application key..."
    php artisan key:generate
fi

echo "=== Syncing model annotations ==="

set +e
php artisan ide-helper:models -W
exit_code=$?
set -e

# Save tarnished checkpoint on success
if [ $exit_code -eq 0 ]; then
    tarnished save sync:models 2>/dev/null || true
fi

exit $exit_code
