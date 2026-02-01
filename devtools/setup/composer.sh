#!/bin/bash
# Ensures composer dependencies are installed.
#
# Usage:
#   ./composer.sh              Run setup (direct, for backwards compatibility)
#   ./composer.sh run          Run setup in tmux session (captures output)
#   ./composer.sh run --attach Run setup in tmux and attach to watch
#   ./composer.sh status       Check if dependencies are installed
#   ./composer.sh logs [N]     Show setup output from tmux session

SETUP_NAME="setup-composer"
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

cd /home/vscode/project

# The actual setup logic
do_setup() {
    if [ ! -f composer.lock ]; then
        echo "[Error] composer.lock not found!"
        return 1
    fi

    if [ ! -d vendor ]; then
        echo "[Setup] Installing composer dependencies..."
        composer install --no-interaction
        echo "[Setup] Composer dependencies installed"
    elif [ composer.lock -nt vendor ]; then
        echo "[Setup] composer.lock changed, updating dependencies..."
        composer install --no-interaction
        echo "[Setup] Composer dependencies updated"
    else
        echo "[Check] Composer dependencies are up to date"
    fi
}

# Status check (quick, no setup)
do_status() {
    if [ -d vendor ] && [ -f vendor/autoload.php ]; then
        echo "[ok] Composer dependencies installed"
        return 0
    else
        echo "[missing] Composer dependencies"
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
