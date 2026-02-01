#!/bin/bash
# Ensures .env file exists by copying from .env.example if needed.
#
# Usage:
#   ./env.sh              Run setup (direct, for backwards compatibility)
#   ./env.sh run          Run setup in tmux session (captures output)
#   ./env.sh run --attach Run setup in tmux and attach to watch
#   ./env.sh status       Check if .env exists
#   ./env.sh logs [N]     Show setup output from tmux session

SETUP_NAME="setup-env"
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

cd /home/vscode/project

# The actual setup logic
do_setup() {
    if [ ! -f .env ]; then
        if [ ! -f .env.example ]; then
            echo "[Error] .env.example not found!"
            return 1
        fi
        echo "[Setup] Creating .env from .env.example..."
        cp .env.example .env
        echo "[Setup] .env created"
    else
        echo "[Check] .env exists"
    fi
}

# Status check (quick, no setup)
do_status() {
    if [ -f .env ]; then
        echo "[ok] .env exists"
        return 0
    else
        echo "[missing] .env file"
        return 1
    fi
}

# Source shared library for tmux functions
source "$SCRIPT_DIR/_lib.sh"

# Command dispatcher
case "${1:-}" in
    run)
        shift
        SETUP_CMD="do_setup"
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
