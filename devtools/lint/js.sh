#!/bin/bash
# Run ESLint for JavaScript/Vue/TypeScript code quality
#
# This script runs ESLint to check for code quality issues.
# For TypeScript type checking, use lint:ts instead.
#
# Usage:
#   ./devtools/lint/js.sh                              # Lint all frontend files
#   ./devtools/lint/js.sh resources/js/Pages/Login.vue # Lint specific file
#   ./devtools/lint/js.sh resources/js/Pages/*.vue     # Lint multiple files
#
# Alias: lint:js (via symlink in /usr/local/bin)

set -e

# Resolve symlinks to get actual script location
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_DIR"

# Parse options
FILES=()

for arg in "$@"; do
    case $arg in
        --help|-h)
            echo "Usage: lint:js [OPTIONS] [FILES...]"
            echo ""
            echo "Run ESLint for JavaScript/Vue/TypeScript code quality"
            echo ""
            echo "Options:"
            echo "  --help, -h     Show this help message"
            echo ""
            echo "Examples:"
            echo "  lint:js                                # Lint all files"
            echo "  lint:js resources/js/Pages/Login.vue   # Lint specific file"
            echo "  lint:js resources/js/Pages/*.vue       # Lint multiple files"
            echo ""
            echo "For TypeScript type checking, use: lint:ts"
            exit 0
            ;;
        *)
            FILES+=("$arg")
            ;;
    esac
done

# Helper function to run a command (kept as a thin wrapper so call sites stay
# uniform and we have a single place to add cross-cutting behavior later).
run_cmd() {
    "$@"
}

# Capture exit code to save tarnished checkpoint on success
set +e
if [ ${#FILES[@]} -eq 0 ]; then
    # No files specified - lint everything
    echo "=== Running ESLint ==="
    run_cmd npm run lint
else
    # Files specified - lint only those files
    echo "=== Running ESLint on specified files ==="
    printf '  %s\n' "${FILES[@]}"
    echo ""
    run_cmd npx eslint "${FILES[@]}"
fi
exit_code=$?
set -e

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "ESLint: PASSED"
    # Save tarnished checkpoint on success
    tarnished save lint:js 2>/dev/null || true
fi

exit $exit_code
