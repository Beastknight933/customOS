#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Installer Library: Common Utilities
# ==============================================================================

set -euo pipefail

# Semantic ANSI colors
C_BLUE='\033[38;2;96;165;250m'
C_CYAN='\033[38;2;45;212;191m'
C_GREEN='\033[38;2;74;222;128m'
C_YELLOW='\033[38;2;251;191;36m'
C_RED='\033[38;2;248;113;113m'
C_DIM='\033[38;2;148;163;184m'
C_BOLD='\033[1m'
C_RESET='\033[0m'

log_info()  { echo -e "${C_BLUE}╭─ 󰋼 INFO:${C_RESET} $*"; }
log_step()  { echo -e "${C_CYAN}│  ❯${C_RESET} $*"; }
log_ok()    { echo -e "${C_GREEN}╰─ ✔ SUCCESS:${C_RESET} $*"; }
log_warn()  { echo -e "${C_YELLOW}╰─ ⚠ WARNING:${C_RESET} $*"; }
log_err()   { echo -e "${C_RED}╰─ ✘ ERROR:${C_RESET} $*" >&2; }
die()       { log_err "$*"; exit 1; }

confirm_prompt() {
    local prompt="${1:-Continue?}"
    local default="${2:-Y}"
    if [[ "${NON_INTERACTIVE:-0}" == "1" ]]; then
        return 0
    fi
    local answer
    echo -ne "${C_YELLOW}${prompt} [Y/n]: ${C_RESET}"
    read -r answer
    answer="${answer:-$default}"
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}
