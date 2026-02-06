#!/bin/bash
# ---------------------------------------------------------------------------
# Access & Port Configuration for Development Environment
# ---------------------------------------------------------------------------
#
# Problem this solves:
#   When running multiple devcontainers of the same project on one machine,
#   services conflict because they bind to the same ports (8080, 5173).
#   Additionally, Codespaces users need different URL settings depending on
#   how they access the environment (browser vs VS Code Desktop).
#
# This script handles both concerns in a single interactive menu:
#   1. Access mode (Codespaces only): browser vs localhost
#   2. Port preset: which port pair to use for Serve and Vite
#
# What it changes in .env:
#   APP_PORT               - Laravel serve port
#   VITE_PORT              - Vite dev server port
#   APP_URL                - Base URL for Laravel route generation
#   ASSET_URL              - Where Vite-built assets are served from (Codespaces)
#   VITE_DEV_SERVER_URL    - Vite dev server origin (Codespaces)
#   VITE_HMR_HOST          - WebSocket host for HMR (Codespaces)
#   VITE_HMR_PROTOCOL      - ws (local) or wss (Codespaces)
#   VITE_HMR_CLIENT_PORT   - WebSocket port the browser connects to (Codespaces)
#
# Config persistence:
#   Choices are saved to .access.json (next to this script, gitignored)
#   so subsequent runs auto-apply after 5 seconds.
#
# Usage:
#   ./configure-access.sh              Run directly
#   ./configure-access.sh status       Show current config from .env
# ---------------------------------------------------------------------------

SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

cd /home/vscode/project

# Config file (gitignored), sits next to this script
CONFIG_FILE="$SCRIPT_DIR/.access.json"

# ---------------------------------------------------------------------------
# Terminal formatting
# ---------------------------------------------------------------------------

BOLD="\033[1m"
DIM="\033[2m"
GREEN="\033[32m"
YELLOW="\033[33m"
CYAN="\033[36m"
RESET="\033[0m"

# Print a colored arrow indicator
arrow() { printf "${CYAN}>${RESET} "; }

# ---------------------------------------------------------------------------
# Port presets
# ---------------------------------------------------------------------------

PRESET_COUNT=3

preset_app_port() {
    case "$1" in
        1) echo 8080 ;; 2) echo 8081 ;; 3) echo 8082 ;; *) echo 8080 ;;
    esac
}

preset_vite_port() {
    case "$1" in
        1) echo 5173 ;; 2) echo 5174 ;; 3) echo 5175 ;; *) echo 5173 ;;
    esac
}

# Human-friendly names for presets
preset_name() {
    case "$1" in
        1) echo "Default" ;; 2) echo "Instance 2" ;; 3) echo "Instance 3" ;; *) echo "Unknown" ;;
    esac
}

# Human-friendly names for access modes
access_name() {
    case "$1" in
        codespaces-browser) echo "Codespaces (Browser)" ;;
        localhost) echo "Localhost" ;;
        *) echo "$1" ;;
    esac
}

# ---------------------------------------------------------------------------
# .env helpers
# ---------------------------------------------------------------------------

update_env() {
    local key="$1" value="$2"
    if grep -q "^${key}=" .env; then
        sed -i "s|^${key}=.*|${key}=${value}|" .env
    else
        echo "${key}=${value}" >> .env
    fi
}

remove_env() {
    local key="$1"
    sed -i "/^${key}=/d" .env
}

# ---------------------------------------------------------------------------
# Config persistence (JSON)
# ---------------------------------------------------------------------------

save_config() {
    local access="$1" preset="$2" app_port="$3" vite_port="$4"
    cat > "$CONFIG_FILE" <<ENDJSON
{
  "access": "$access",
  "preset": $preset,
  "ports": {
    "app": $app_port,
    "vite": $vite_port
  }
}
ENDJSON
}

load_config() {
    [[ -f "$CONFIG_FILE" ]] && cat "$CONFIG_FILE"
}

# Read a field from the JSON config (simple sed-based, no jq dependency)
config_value() {
    local key="$1" config result
    config=$(load_config)
    [[ -z "$config" ]] && return 1
    result=$(echo "$config" | sed -n 's/.*"'"$key"'" *: *"\([^"]*\)".*/\1/p' | head -1)
    if [[ -z "$result" ]]; then
        result=$(echo "$config" | sed -n 's/.*"'"$key"'" *: *\([0-9][0-9]*\).*/\1/p' | head -1)
    fi
    echo "$result"
}

# ---------------------------------------------------------------------------
# Configuration apply
# ---------------------------------------------------------------------------

apply_ports() {
    local app_port="$1" vite_port="$2"
    update_env "APP_PORT" "$app_port"
    update_env "VITE_PORT" "$vite_port"
}

configure_localhost() {
    local app_port="$1" vite_port="$2"
    apply_ports "$app_port" "$vite_port"
    update_env "APP_URL" "http://localhost"
    remove_env "ASSET_URL"
    remove_env "VITE_DEV_SERVER_URL"
    remove_env "VITE_HMR_HOST"
    remove_env "VITE_HMR_PROTOCOL"
    remove_env "VITE_HMR_CLIENT_PORT"
}

configure_codespaces_browser() {
    local app_port="$1" vite_port="$2"
    apply_ports "$app_port" "$vite_port"
    local codespace_url="https://${CODESPACE_NAME}-${app_port}.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    local vite_host="${CODESPACE_NAME}-${vite_port}.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    local vite_dev_server_url="https://${vite_host}"
    update_env "APP_URL" "${codespace_url}"
    update_env "ASSET_URL" "${vite_dev_server_url}"
    update_env "VITE_DEV_SERVER_URL" "${vite_dev_server_url}"
    update_env "VITE_HMR_HOST" "${vite_host}"
    update_env "VITE_HMR_PROTOCOL" "wss"
    update_env "VITE_HMR_CLIENT_PORT" "443"
}

apply_config() {
    local access_mode="$1" app_port="$2" vite_port="$3"
    if [[ "$access_mode" == "codespaces-browser" ]]; then
        configure_codespaces_browser "$app_port" "$vite_port"
    else
        configure_localhost "$app_port" "$vite_port"
    fi
}

# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

# Print the final summary after applying config
print_summary() {
    local access_mode="$1" preset="$2" app_port="$3" vite_port="$4"

    echo ""
    printf "  ${BOLD}Access${RESET}  $(access_name "$access_mode")\n"
    printf "  ${BOLD}Serve${RESET}   http://localhost:${app_port}\n"
    printf "  ${BOLD}Vite${RESET}    http://localhost:${vite_port}\n"
    echo ""
    printf "  ${GREEN}Done.${RESET} Settings written to .env\n"
}

# Print a menu option, highlighting the selected one
# Usage: print_option <number> <label> <detail> [selected]
print_option() {
    local num="$1" label="$2" detail="$3" selected="${4:-}"
    if [[ "$selected" == "selected" ]]; then
        printf "  ${GREEN}${BOLD}%s)${RESET} ${BOLD}%-14s${RESET} ${DIM}%s${RESET}\n" "$num" "$label" "$detail"
    else
        printf "  ${BOLD}%s)${RESET} %-14s ${DIM}%s${RESET}\n" "$num" "$label" "$detail"
    fi
}

# ---------------------------------------------------------------------------
# Main setup logic
# ---------------------------------------------------------------------------

do_setup() {
    echo ""
    printf "${BOLD}Configure Access & Ports${RESET}\n"

    if [[ ! -f .env ]]; then
        echo ""
        printf "  ${YELLOW}Error:${RESET} .env not found. Run devtools/setup/env.sh first.\n"
        return 1
    fi

    local is_codespaces=false
    [[ "$CODESPACES" == "true" ]] && is_codespaces=true

    # --- Check for saved config ---
    local saved_config
    saved_config=$(load_config)

    if [[ -n "$saved_config" ]]; then
        local saved_access saved_preset saved_app_port saved_vite_port
        saved_access=$(config_value "access")
        saved_preset=$(config_value "preset")
        saved_app_port=$(preset_app_port "$saved_preset")
        saved_vite_port=$(preset_vite_port "$saved_preset")

        echo ""
        printf "  ${DIM}Saved config:${RESET} $(access_name "$saved_access"), $(preset_name "$saved_preset") (ports ${saved_app_port}/${saved_vite_port})\n"
        echo ""

        # Countdown with live update
        local remaining=5
        while [[ $remaining -gt 0 ]]; do
            printf "\r  Applying in ${BOLD}%d${RESET}s... ${DIM}(press any key to change)${RESET}  " "$remaining"
            if read -t 1 -n 1 -s; then
                printf "\r%-60s\r" ""  # Clear the countdown line
                echo ""
                break
            fi
            ((remaining--))
        done

        if [[ $remaining -eq 0 ]]; then
            printf "\r%-60s\r" ""  # Clear the countdown line
            apply_config "$saved_access" "$saved_app_port" "$saved_vite_port"
            save_config "$saved_access" "$saved_preset" "$saved_app_port" "$saved_vite_port"
            print_summary "$saved_access" "$saved_preset" "$saved_app_port" "$saved_vite_port"
            return 0
        fi
    fi

    # --- First run or reconfiguring ---

    local access_mode="localhost"

    # Step 1: Access mode (Codespaces only)
    if [[ "$is_codespaces" == true ]]; then
        echo ""
        printf "  ${DIM}GitHub Codespaces detected${RESET}\n"
        echo ""
        printf "  ${BOLD}How are you accessing this Codespace?${RESET}\n"
        echo ""
        print_option "1" "Browser" "app.github.dev — URLs use forwarded domain"
        print_option "2" "VS Code Desktop" "localhost — ports are forwarded automatically"
        echo ""

        local access_choice
        printf "  Choice ${DIM}[1/2]${RESET}: "
        read -n 1 access_choice
        echo ""

        case "${access_choice:-1}" in
            1) access_mode="codespaces-browser" ;;
            2) access_mode="localhost" ;;
            *)
                printf "\n  ${YELLOW}Invalid choice.${RESET} Expected 1 or 2.\n"
                return 1
                ;;
        esac
    else
        echo ""
        printf "  ${DIM}Local devcontainer detected${RESET}\n"
    fi

    # Step 2: Port preset
    echo ""
    printf "  ${BOLD}Which instance is this?${RESET}\n"
    printf "  ${DIM}Pick different ports per devcontainer to avoid conflicts.${RESET}\n"
    echo ""

    local i
    for i in $(seq 1 $PRESET_COUNT); do
        local p_app p_vite p_name
        p_app=$(preset_app_port "$i")
        p_vite=$(preset_vite_port "$i")
        p_name=$(preset_name "$i")
        if [[ "$i" -eq 1 ]]; then
            print_option "$i" "$p_name" "ports ${p_app} / ${p_vite}" "selected"
        else
            print_option "$i" "$p_name" "ports ${p_app} / ${p_vite}"
        fi
    done
    echo ""

    local preset_choice
    printf "  Choice ${DIM}[1/2/3, default: 1]${RESET}: "
    read -n 1 preset_choice
    echo ""

    preset_choice="${preset_choice:-1}"

    case "$preset_choice" in
        1|2|3) ;;
        *)
            printf "\n  ${YELLOW}Invalid choice.${RESET} Expected 1, 2, or 3.\n"
            return 1
            ;;
    esac

    local app_port vite_port
    app_port=$(preset_app_port "$preset_choice")
    vite_port=$(preset_vite_port "$preset_choice")

    # Apply and save
    apply_config "$access_mode" "$app_port" "$vite_port"
    save_config "$access_mode" "$preset_choice" "$app_port" "$vite_port"
    print_summary "$access_mode" "$preset_choice" "$app_port" "$vite_port"
}

# ---------------------------------------------------------------------------
# Status check
# ---------------------------------------------------------------------------

do_status() {
    if [[ ! -f .env ]]; then
        echo "[missing] .env file"
        return 1
    fi

    local app_url app_port vite_port
    app_url=$(grep "^APP_URL=" .env | cut -d'=' -f2)
    app_port=$(grep "^APP_PORT=" .env | cut -d'=' -f2)
    vite_port=$(grep "^VITE_PORT=" .env | cut -d'=' -f2)

    if [[ -z "$app_url" ]]; then
        echo "[missing] APP_URL not set"
        return 1
    fi

    echo "[ok] APP_URL=$app_url  APP_PORT=${app_port:-not set}  VITE_PORT=${vite_port:-not set}"
    return 0
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
        do_setup
        ;;
esac
