#!/bin/bash
# Laravel Pail (log tailing) service
#
# Usage:
#   ./logs.sh start      Start log tailing (or report if already running)
#   ./logs.sh stop       Stop log tailing
#   ./logs.sh restart    Restart log tailing
#   ./logs.sh status     Check if running
#   ./logs.sh logs [N]   Show last N lines of output
#   ./logs.sh attach     Attach to tmux session

# Service configuration
SERVICE_NAME="dev-logs"
READY_PATTERN="INFO"
SERVICE_CMD="cd /home/vscode/project && php artisan pail --verbose"

# Source the shared library (resolve symlinks)
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
source "$SCRIPT_DIR/_lib.sh"

# Run the command
run_service_command "$@"
