#!/bin/bash
# Dead code detection using Knip
#
# Usage:
#   ./devtools/lint/deadcode.sh                              # Find all unused files/exports
#   ./devtools/lint/deadcode.sh --trace-file path/to/file    # Trace what depends on a file
#   ./devtools/lint/deadcode.sh --files                      # Show unused files only
#   ./devtools/lint/deadcode.sh --exports                    # Show unused exports only
#
# Alias: lint:deadcode (via symlink in /usr/local/bin)

# Resolve symlinks to get actual script location
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_DIR"

echo "=== Dead Code Detection (Knip) ==="

# Pass all arguments through to knip
set +e
npx knip "$@"
exit_code=$?
set -e

# Save tarnished checkpoint on success (only if running full check, not --trace)
if [ $exit_code -eq 0 ] && [[ "$*" != *"--trace"* ]]; then
    tarnished save lint:deadcode 2>/dev/null || true
fi

exit $exit_code
