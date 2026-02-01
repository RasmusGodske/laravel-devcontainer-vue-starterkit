#!/bin/bash
# Ensures npm dependencies are installed.
#
# Usage:
#   ./npm.sh              Run setup (direct, for backwards compatibility)
#   ./npm.sh run          Run setup in tmux session (captures output)
#   ./npm.sh run --attach Run setup in tmux and attach to watch
#   ./npm.sh status       Check if dependencies are installed
#   ./npm.sh logs [N]     Show setup output from tmux session

SETUP_NAME="setup-npm"
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

cd /home/vscode/project

# The actual setup logic
do_setup() {
    if [ ! -f package-lock.json ]; then
        echo "[Error] package-lock.json not found!"
        return 1
    fi

    if [ ! -d node_modules ]; then
        echo "[Setup] Installing npm dependencies..."
        npm install
        echo "[Setup] npm dependencies installed"
    elif [ package-lock.json -nt node_modules ]; then
        echo "[Setup] package-lock.json changed, updating dependencies..."
        npm install
        echo "[Setup] npm dependencies updated"
    else
        echo "[Check] npm dependencies are up to date"
    fi
}

# Status check (quick, no setup)
do_status() {
    if [ -d node_modules ]; then
        echo "[ok] npm dependencies installed"
        return 0
    else
        echo "[missing] npm dependencies"
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
