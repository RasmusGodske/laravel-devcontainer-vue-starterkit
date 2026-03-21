#!/bin/bash
# Sync Ziggy route types for TypeScript
#
# Usage:
#   ./devtools/sync/routes.sh       # Regenerate route types
#
# Alias: sync:routes (via symlink in /usr/local/bin)

set -e

# Disable Xdebug for performance
export XDEBUG_MODE=off

# Resolve symlinks to get actual script location
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_DIR"

echo "=== Syncing Ziggy route types ==="

set +e
php artisan ziggy:generate --types-only
exit_code=$?
set -e

# Save tarnished checkpoint on success
if [ $exit_code -eq 0 ]; then
    tarnished save sync:routes 2>/dev/null || true
fi

exit $exit_code
