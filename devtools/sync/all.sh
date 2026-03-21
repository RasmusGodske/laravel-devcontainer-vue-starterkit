#!/bin/bash
# Run all sync scripts (models, types, routes)
#
# Usage:
#   ./devtools/sync/all.sh          # Sync all generated artifacts
#
# Alias: sync:all (via symlink in /usr/local/bin)

set -e

# Resolve symlinks to get actual script location
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"

OVERALL_EXIT=0

echo "=== Running all sync scripts ==="
echo ""

# Sync models
echo "--- sync:models ---"
set +e
"$SCRIPT_DIR/models.sh"
models_exit=$?
set -e
if [ $models_exit -eq 0 ]; then
    echo "sync:models: PASSED"
else
    echo "sync:models: FAILED (exit code $models_exit)"
    OVERALL_EXIT=1
fi
echo ""

# Sync types
echo "--- sync:types ---"
set +e
"$SCRIPT_DIR/types.sh"
types_exit=$?
set -e
if [ $types_exit -eq 0 ]; then
    echo "sync:types: PASSED"
else
    echo "sync:types: FAILED (exit code $types_exit)"
    OVERALL_EXIT=1
fi
echo ""

# Sync routes
echo "--- sync:routes ---"
set +e
"$SCRIPT_DIR/routes.sh"
routes_exit=$?
set -e
if [ $routes_exit -eq 0 ]; then
    echo "sync:routes: PASSED"
else
    echo "sync:routes: FAILED (exit code $routes_exit)"
    OVERALL_EXIT=1
fi
echo ""

# Summary
echo "=== Sync complete ==="
if [ $OVERALL_EXIT -eq 0 ]; then
    echo "All sync scripts passed."
else
    echo "One or more sync scripts failed."
fi

exit $OVERALL_EXIT
