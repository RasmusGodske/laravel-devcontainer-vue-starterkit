#!/bin/bash
# Vite dev server service
#
# Usage:
#   ./vite.sh start      Start vite (or report if already running)
#   ./vite.sh stop       Stop vite
#   ./vite.sh restart    Restart vite
#   ./vite.sh status     Check if running
#   ./vite.sh logs [N]   Show last N lines of output
#   ./vite.sh attach     Attach to tmux session

# Service configuration
SERVICE_NAME="dev-vite"
READY_PATTERN="VITE"
SERVICE_CMD="cd /home/vscode/project && npm run dev"

# Source the shared library (resolve symlinks)
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
source "$SCRIPT_DIR/_lib.sh"

# Run the command
run_service_command "$@"
