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
#   NOVNC_PORT             - noVNC port for headed browser
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
#   ./configure-ports.sh              Run directly
#   ./configure-ports.sh run          Run in tmux session
#   ./configure-ports.sh run --attach Run in tmux and attach to see output
#   ./configure-ports.sh status       Show current config from .env

SETUP_NAME="setup-access"
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

cd /home/vscode/project

# Config file (gitignored), sits next to this script
CONFIG_FILE="$SCRIPT_DIR/.access.json"

# Terminal formatting
BOLD="\033[1m"
DIM="\033[2m"
GREEN="\033[32m"
YELLOW="\033[33m"
CYAN="\033[36m"
RESET="\033[0m"

arrow() { printf "${CYAN}>${RESET} "; }

# Port presets
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

preset_novnc_port() {
    case "$1" in
        1) echo 6080 ;; 2) echo 6081 ;; 3) echo 6082 ;; *) echo 6080 ;;
    esac
}

preset_name() {
    case "$1" in
        1) echo "Default" ;; 2) echo "Preset 2" ;; 3) echo "Preset 3" ;; *) echo "Unknown" ;;
    esac
}

access_name() {
    case "$1" in
        codespaces-browser) echo "Codespaces (Browser)" ;;
        localhost) echo "Localhost" ;;
        *) echo "$1" ;;
    esac
}

# .env helpers
update_env() {
    local key="$1" value="$2"
    if grep -q "^${key}=" .env; then
        sed -i "s|^${key}=.*|${key}=${value}|" .env
    else
        [[ -n "$(tail -c1 .env)" ]] && echo "" >> .env
        echo "${key}=${value}" >> .env
    fi
}

remove_env() {
    local key="$1"
    sed -i "/^${key}=/d" .env
}

# Config persistence
save_config() {
    local access="$1" preset="$2" app_port="$3" vite_port="$4" novnc_port="$5"
    cat > "$CONFIG_FILE" <<ENDJSON
{
  "access": "$access",
  "preset": $preset,
  "ports": {
    "app": $app_port,
    "vite": $vite_port,
    "novnc": $novnc_port
  }
}
ENDJSON
}

load_config() {
    [[ -f "$CONFIG_FILE" ]] && cat "$CONFIG_FILE"
}

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

# Configuration apply
apply_ports() {
    local app_port="$1" vite_port="$2" novnc_port="$3"
    update_env "APP_PORT" "$app_port"
    update_env "VITE_PORT" "$vite_port"
    update_env "NOVNC_PORT" "$novnc_port"
}

configure_localhost() {
    local app_port="$1" vite_port="$2" novnc_port="$3"
    apply_ports "$app_port" "$vite_port" "$novnc_port"
    update_env "APP_URL" "http://localhost"
    remove_env "ASSET_URL"
    remove_env "VITE_DEV_SERVER_URL"
    remove_env "VITE_HMR_HOST"
    remove_env "VITE_HMR_PROTOCOL"
    remove_env "VITE_HMR_CLIENT_PORT"
}

configure_codespaces_browser() {
    local app_port="$1" vite_port="$2" novnc_port="$3"
    apply_ports "$app_port" "$vite_port" "$novnc_port"
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
    local access_mode="$1" app_port="$2" vite_port="$3" novnc_port="$4"
    if [[ "$access_mode" == "codespaces-browser" ]]; then
        configure_codespaces_browser "$app_port" "$vite_port" "$novnc_port"
    else
        configure_localhost "$app_port" "$vite_port" "$novnc_port"
    fi
}

print_summary() {
    local access_mode="$1" preset="$2" app_port="$3" vite_port="$4" novnc_port="$5"
    echo ""
    printf "  ${BOLD}Access${RESET}  $(access_name "$access_mode")\n"
    printf "  ${BOLD}Serve${RESET}   http://localhost:${app_port}\n"
    printf "  ${BOLD}Vite${RESET}    http://localhost:${vite_port}\n"
    printf "  ${BOLD}noVNC${RESET}   http://localhost:${novnc_port}\n"
    echo ""
    printf "  ${GREEN}Done.${RESET} Settings written to .env\n"
}

print_option() {
    local num="$1" label="$2" detail="$3" selected="${4:-}"
    if [[ "$selected" == "selected" ]]; then
        printf "  ${GREEN}${BOLD}%s)${RESET} ${BOLD}%-14s${RESET} ${DIM}%s${RESET}\n" "$num" "$label" "$detail"
    else
        printf "  ${BOLD}%s)${RESET} %-14s ${DIM}%s${RESET}\n" "$num" "$label" "$detail"
    fi
}

print_preset_table() {
    local selected="${1:-1}" show_label="${2:-false}"
    printf "  ${DIM}%-5s%-14s%-12s%-10s%-6s${RESET}\n" "" "Preset" "Laravel" "Vite" "noVNC"
    printf "  ${DIM}%s${RESET}\n" "─────────────────────────────────────────"
    local i
    for i in $(seq 1 $PRESET_COUNT); do
        local p_app p_vite p_novnc p_name
        p_app=$(preset_app_port "$i")
        p_vite=$(preset_vite_port "$i")
        p_novnc=$(preset_novnc_port "$i")
        p_name=$(preset_name "$i")
        if [[ "$i" -eq "$selected" ]]; then
            local label=""
            [[ "$show_label" == "true" ]] && label=" ${GREEN}${BOLD}(selected)${RESET}"
            printf "  ${GREEN}${BOLD}%s)${RESET} ${BOLD}%-14s${RESET}${DIM}%-12s%-10s%-6s${RESET}%b\n" "$i" "$p_name" "$p_app" "$p_vite" "$p_novnc" "$label"
        else
            printf "  ${BOLD}%s)${RESET} %-14s${DIM}%-12s%-10s%-6s${RESET}\n" "$i" "$p_name" "$p_app" "$p_vite" "$p_novnc"
        fi
    done
}

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

    local saved_config
    saved_config=$(load_config)

    if [[ -n "$saved_config" ]]; then
        local saved_access saved_preset saved_app_port saved_vite_port saved_novnc_port
        saved_access=$(config_value "access")
        saved_preset=$(config_value "preset")
        saved_app_port=$(preset_app_port "$saved_preset")
        saved_vite_port=$(preset_vite_port "$saved_preset")
        saved_novnc_port=$(preset_novnc_port "$saved_preset")

        echo ""
        print_preset_table "$saved_preset" "true"
        echo ""

        local remaining=5 key_pressed=""
        while [[ $remaining -gt 0 ]]; do
            printf "\r  Applying in ${BOLD}%d${RESET}s... ${DIM}(press enter to confirm, number to change)${RESET}  " "$remaining"
            if read -t 1 -n 1 -s key_pressed; then
                printf "\r%-60s\r" ""
                break
            fi
            ((remaining--))
        done

        if [[ $remaining -eq 0 ]] || [[ -z "$key_pressed" || "$key_pressed" == $'\n' || "$key_pressed" == $'\r' ]]; then
            printf "\r%-60s\r" ""
            apply_config "$saved_access" "$saved_app_port" "$saved_vite_port" "$saved_novnc_port"
            save_config "$saved_access" "$saved_preset" "$saved_app_port" "$saved_vite_port" "$saved_novnc_port"
            print_summary "$saved_access" "$saved_preset" "$saved_app_port" "$saved_vite_port" "$saved_novnc_port"
            return 0
        elif [[ "$key_pressed" =~ ^[1-3]$ ]]; then
            local new_app_port new_vite_port new_novnc_port
            new_app_port=$(preset_app_port "$key_pressed")
            new_vite_port=$(preset_vite_port "$key_pressed")
            new_novnc_port=$(preset_novnc_port "$key_pressed")
            apply_config "$saved_access" "$new_app_port" "$new_vite_port" "$new_novnc_port"
            save_config "$saved_access" "$key_pressed" "$new_app_port" "$new_vite_port" "$new_novnc_port"
            print_summary "$saved_access" "$key_pressed" "$new_app_port" "$new_vite_port" "$new_novnc_port"
            return 0
        fi
        echo ""
    fi

    local access_mode="localhost"

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

    echo ""
    printf "  ${BOLD}Which port preset?${RESET}\n"
    printf "  ${DIM}Pick different ports per devcontainer to avoid conflicts.${RESET}\n"
    echo ""
    print_preset_table 1
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

    local app_port vite_port novnc_port
    app_port=$(preset_app_port "$preset_choice")
    vite_port=$(preset_vite_port "$preset_choice")
    novnc_port=$(preset_novnc_port "$preset_choice")

    apply_config "$access_mode" "$app_port" "$vite_port" "$novnc_port"
    save_config "$access_mode" "$preset_choice" "$app_port" "$vite_port" "$novnc_port"
    print_summary "$access_mode" "$preset_choice" "$app_port" "$vite_port" "$novnc_port"
}

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
        do_setup
        ;;
esac
