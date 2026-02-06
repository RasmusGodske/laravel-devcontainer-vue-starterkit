#!/bin/bash
# Vite dev server service
#
# Watches VITE_PORT and HMR-related keys in .env and auto-restarts when they change.
#
# Usage:
#   ./vite.sh start      Start vite (or report if already running)
#   ./vite.sh stop       Stop vite
#   ./vite.sh restart    Restart vite
#   ./vite.sh status     Check if running
#   ./vite.sh logs [N]   Show last N lines of output
#   ./vite.sh attach     Attach to tmux session

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

# ---------------------------------------------------------------------------
# Watched runner mode (runs INSIDE the tmux session)
# ---------------------------------------------------------------------------
if [[ "${1:-}" == "--run-watched" ]]; then
    source "$SCRIPT_DIR/_env-watch.sh"

    build_vite_cmd() {
        CMD_TO_RUN="npm run dev"
    }

    WATCH_KEYS="VITE_PORT,VITE_DEV_SERVER_URL,VITE_HMR_HOST,VITE_HMR_PROTOCOL,VITE_HMR_CLIENT_PORT,APP_PORT"
    run_with_env_watch 3 "$WATCH_KEYS" build_vite_cmd
    exit $?
fi

# ---------------------------------------------------------------------------
# Normal service management mode
# ---------------------------------------------------------------------------

SERVICE_NAME="dev-vite"
READY_PATTERN="VITE"
SERVICE_CMD="cd /home/vscode/project && $SCRIPT_DIR/vite.sh --run-watched"

# Source the shared library (resolve symlinks)
source "$SCRIPT_DIR/_lib.sh"

# Run the command
run_service_command "$@"
