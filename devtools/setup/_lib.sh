#!/bin/bash
# Shared library for tmux-managed setup tasks
#
# Each setup script should:
#   1. Define SETUP_NAME (e.g., "setup-env")
#   2. Define do_setup() function with the actual logic
#   3. Source this file
#   4. Call run_setup_in_tmux or show_setup_logs as needed

PROJECT_ROOT="/home/vscode/project"

# Check if setup session exists
setup_session_exists() {
    tmux has-session -t "$SETUP_NAME" 2>/dev/null
}

# Show logs from the setup session
show_setup_logs() {
    local lines="${1:-50}"

    if ! setup_session_exists; then
        echo "[$SETUP_NAME] No logs available (not run yet)"
        return 1
    fi

    echo "=== $SETUP_NAME logs (last $lines lines) ==="
    tmux capture-pane -t "$SETUP_NAME" -p -S -"$lines"
}

# Run setup in tmux session
# Usage: SCRIPT_PATH=/path/to/script.sh run_setup_in_tmux [--attach]
# The calling script must set SCRIPT_PATH before calling this
run_setup_in_tmux() {
    local attach=false
    if [[ "$1" == "--attach" ]]; then
        attach=true
    fi

    # Kill previous session if exists
    if setup_session_exists; then
        tmux kill-session -t "$SETUP_NAME" 2>/dev/null || true
    fi

    # SCRIPT_PATH must be set by the calling script
    if [[ -z "$SCRIPT_PATH" ]]; then
        echo "Error: SCRIPT_PATH not set"
        return 1
    fi

    # Run the script directly (no args = backwards compatible direct run)
    # in a tmux session, capturing output
    tmux new-session -d -s "$SETUP_NAME" -c "$PROJECT_ROOT" \
        "echo '=== $SETUP_NAME ===' && echo 'Started: '\$(date) && echo '' && '$SCRIPT_PATH' && echo '' && echo '[SUCCESS] Completed at '\$(date) || echo '[FAILED] Failed at '\$(date); echo ''; echo 'Press any key to close...'; read -n 1"

    if [[ "$attach" == true ]]; then
        tmux attach-session -t "$SETUP_NAME"
    else
        # Wait for completion and show result
        echo "[$SETUP_NAME] Running..."

        local timeout=120
        local elapsed=0

        while [[ $elapsed -lt $timeout ]]; do
            sleep 1

            # Check if session output contains success/failure marker
            local output
            output=$(tmux capture-pane -t "$SETUP_NAME" -p 2>/dev/null)

            if echo "$output" | grep -q "\[SUCCESS\]"; then
                echo "[$SETUP_NAME] Completed successfully"
                return 0
            elif echo "$output" | grep -q "\[FAILED\]"; then
                echo "[$SETUP_NAME] Failed (check logs with: $0 logs)"
                return 1
            fi

            ((elapsed++)) || true
        done

        echo "[$SETUP_NAME] Timeout"
        return 1
    fi
}
