#!/bin/bash
# Ensures APP_KEY is set in .env by generating one if needed.
#
# Usage:
#   ./app-key.sh              Run setup (direct, for backwards compatibility)
#   ./app-key.sh run          Run setup in tmux session (captures output)
#   ./app-key.sh run --attach Run setup in tmux and attach to watch
#   ./app-key.sh status       Check if APP_KEY is set
#   ./app-key.sh logs [N]     Show setup output from tmux session

SETUP_NAME="setup-app-key"
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

cd /home/vscode/project

# The actual setup logic
do_setup() {
    if [ ! -f .env ]; then
        echo "[Error] .env file not found! Run env.sh first."
        return 1
    fi

    if grep -q "^APP_KEY=base64:" .env 2>/dev/null; then
        echo "[Check] APP_KEY is set"
    else
        echo "[Setup] Generating application key..."
        php artisan key:generate
        echo "[Setup] Application key generated"
    fi
}

# Status check (quick, no setup)
do_status() {
    if grep -q "^APP_KEY=base64:" .env 2>/dev/null; then
        echo "[ok] APP_KEY is set"
        return 0
    else
        echo "[missing] APP_KEY not set"
        return 1
    fi
}

# Source shared library for tmux functions
source "$SCRIPT_DIR/_lib.sh"

# Command dispatcher
case "${1:-}" in
    run)
        shift
        run_setup_in_tmux "$@"
        ;;
    status)
        do_status
        ;;
    logs)
        show_setup_logs "${2:-50}"
        ;;
    *)
        # Backwards compatible - run directly
        do_setup
        ;;
esac
