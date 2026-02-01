#!/bin/bash
# Show status of the development environment
#
# Usage:
#   ./status.sh              Show full environment status
#   ./status.sh --json       JSON output (for programmatic use)
#   ./status.sh --watch      Watch status, refresh every 2 seconds
#   ./status.sh --watch=N    Watch status, refresh every N seconds

# Resolve symlinks to get the real script directory
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
DEVTOOLS_DIR="$(dirname "$SCRIPT_DIR")"
SETUP_DIR="$DEVTOOLS_DIR/setup"
SERVICES_DIR="$DEVTOOLS_DIR/services"

# Handle --watch flag
if [[ "$1" == --watch* ]]; then
    # Extract interval (default 2 seconds)
    if [[ "$1" == --watch=* ]]; then
        INTERVAL="${1#--watch=}"
    else
        INTERVAL=2
    fi

    # Watch loop
    while true; do
        clear
        echo "Dev Environment Status (every ${INTERVAL}s, Ctrl+C to exit)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        "$SCRIPT_PATH"
        sleep "$INTERVAL"
    done
    exit 0
fi

# Helper to get status string from a command
get_status() {
    if "$@" > /dev/null 2>&1; then
        echo "ok"
    else
        echo "missing"
    fi
}

get_service_status() {
    if "$@" > /dev/null 2>&1; then
        echo "running"
    else
        echo "stopped"
    fi
}

if [[ "$1" == "--json" ]]; then
    # JSON output for programmatic use
    cat <<EOF
{
  "setup": {
    "env": "$(get_status "$SETUP_DIR/env.sh" status)",
    "app_key": "$(get_status "$SETUP_DIR/app-key.sh" status)",
    "composer": "$(get_status "$SETUP_DIR/composer.sh" status)",
    "npm": "$(get_status "$SETUP_DIR/npm.sh" status)",
    "migrated": "$(get_status "$SETUP_DIR/migrated.sh" status)"
  },
  "services": {
    "database": "$(get_service_status "$SERVICES_DIR/database.sh" status)",
    "cache": "$(get_service_status "$SERVICES_DIR/cache.sh" status)",
    "serve": "$(get_service_status "$SERVICES_DIR/serve.sh" status)",
    "vite": "$(get_service_status "$SERVICES_DIR/vite.sh" status)",
    "logs": "$(get_service_status "$SERVICES_DIR/logs.sh" status)"
  }
}
EOF
else
    # Human-readable output
    echo "=== Setup ==="
    echo ""
    "$SETUP_DIR/env.sh" status || true
    "$SETUP_DIR/app-key.sh" status || true
    "$SETUP_DIR/composer.sh" status || true
    "$SETUP_DIR/npm.sh" status || true

    # Only check migrations if database is running
    if "$SERVICES_DIR/database.sh" status > /dev/null 2>&1; then
        "$SETUP_DIR/migrated.sh" status || true
    else
        echo "[unknown] Database migrations (database not running)"
    fi

    echo ""
    echo "=== Services ==="
    echo ""
    "$SERVICES_DIR/database.sh" status || true
    "$SERVICES_DIR/cache.sh" status || true
    "$SERVICES_DIR/serve.sh" status || true
    "$SERVICES_DIR/vite.sh" status || true
    "$SERVICES_DIR/logs.sh" status || true

    echo ""
    echo "=== Tmux Sessions ==="
    tmux list-sessions 2>/dev/null || echo "No active tmux sessions"
fi
