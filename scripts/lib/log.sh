#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Unified Logging Utilities
# ==============================================================================

if [[ -n "${AETHERIUM_LOG_LOADED:-}" ]]; then
    return 0
fi
AETHERIUM_LOG_LOADED=1

C_BLUE='\033[38;2;96;165;250m'
C_CYAN='\033[38;2;45;212;191m'
C_GREEN='\033[38;2;74;222;128m'
C_YELLOW='\033[38;2;251;191;36m'
C_RED='\033[38;2;248;113;113m'
C_DIM='\033[38;2;148;163;184m'
C_BOLD='\033[1m'
C_RESET='\033[0m'

info() { printf "  ${C_CYAN}[INFO]${C_RESET}  %s\n" "$*"; }
ok()   { printf "  ${C_GREEN}[OK]${C_RESET}    %s\n" "$*"; }
warn() { printf "  ${C_YELLOW}[WARN]${C_RESET}  %s\n" "$*"; }
skip() { printf "  ${C_DIM}[SKIP]${C_RESET}  %s\n" "$*"; }
err()  { printf "  ${C_RED}[ERR]${C_RESET}   %s\n" "$*" >&2; }
die()  { err "$*"; exit 1; }
