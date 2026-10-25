#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Privilege Management & Sudo Loop
# ==============================================================================

if [[ -z "${AETHERIUM_PRIVILEGES_SOURCED:-}" ]]; then
AETHERIUM_PRIVILEGES_SOURCED=1

aetherium_sudo_bin() {
    if [[ -n "${AETHERIUM_SUDO_BIN:-}" ]]; then
        printf '%s\n' "$AETHERIUM_SUDO_BIN"
    elif [[ -x /usr/bin/sudo ]]; then
        printf '%s\n' /usr/bin/sudo
    else
        command -v sudo || echo "sudo"
    fi
}

aetherium_sudo() {
    if [[ "$EUID" -eq 0 ]]; then
        "$@"
    else
        "$(aetherium_sudo_bin)" "$@"
    fi
}

caelestia_sudo() {
    aetherium_sudo "$@"
}

AETHERIUM_SUDO_PID=""

aetherium_prime_sudo() {
    if [[ "$EUID" -eq 0 ]]; then
        return 0
    fi

    if ! "$(aetherium_sudo_bin)" -v 2>/dev/null; then
        return 1
    fi

    (
        while true; do
            "$(aetherium_sudo_bin)" -n -v 2>/dev/null || exit 0
            sleep 45
        done
    ) &
    AETHERIUM_SUDO_PID=$!
    return 0
}

aetherium_stop_sudo_keepalive() {
    if [[ -n "$AETHERIUM_SUDO_PID" ]]; then
        kill "$AETHERIUM_SUDO_PID" 2>/dev/null || true
        wait "$AETHERIUM_SUDO_PID" 2>/dev/null || true
        AETHERIUM_SUDO_PID=""
    fi
}

caelestia_stop_sudo_keepalive() {
    aetherium_stop_sudo_keepalive
}

fi
