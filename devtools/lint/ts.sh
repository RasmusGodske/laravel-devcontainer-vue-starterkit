#!/bin/bash
# Run TypeScript type checking
#
# This script runs vue-tsc to check for TypeScript type errors.
# For ESLint code quality checks, use lint:js instead.
#
# Usage:
#   ./devtools/lint/ts.sh                              # Type-check all files
#   ./devtools/lint/ts.sh resources/js/Pages/Login.vue # Type-check specific file
#   ./devtools/lint/ts.sh resources/js/Pages/*.vue     # Type-check multiple files
#
# Alias: lint:ts (via symlink in /usr/local/bin)

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
            echo "Usage: lint:ts [OPTIONS] [FILES...]"
            echo ""
            echo "Run TypeScript type checking"
            echo ""
            echo "Options:"
            echo "  --help, -h     Show this help message"
            echo ""
            echo "Examples:"
            echo "  lint:ts                                # Type-check all files"
            echo "  lint:ts resources/js/Pages/Login.vue   # Type-check specific file"
            echo "  lint:ts resources/js/Pages/*.vue       # Type-check multiple files"
            echo ""
            echo "For ESLint code quality checks, use: lint:js"
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

if [ ${#FILES[@]} -eq 0 ]; then
    # No files specified - type-check everything
    echo "=== Running TypeScript type-check ==="
    run_cmd npm run type-check
else
    # Files specified - type-check only those files
    echo "=== Running TypeScript type-check on specified files ==="
    printf '  %s\n' "${FILES[@]}"
    echo ""
    run_cmd npm run type-check:files -- "${FILES[@]}"
fi

echo ""
echo "TypeScript: PASSED"
