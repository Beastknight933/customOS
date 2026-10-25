#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Installer Library: Environment Detection
# ==============================================================================

set -euo pipefail

detect_distro() {
    DISTRO_ID="unknown"
    DISTRO_NAME="Linux"
    if [[ -f /etc/os-release ]]; then
        # shellcheck disable=SC1091
        source /etc/os-release
        DISTRO_ID="${ID:-unknown}"
        DISTRO_NAME="${NAME:-Linux}"
        DISTRO_LIKE="${ID_LIKE:-}"
    fi

    BASE_DISTRO="unknown"
    case "$DISTRO_ID" in
        arch|cachyos|endeavouros|manjaro|artix)
            BASE_DISTRO="arch" ;;
        fedora|rhel|centos|nobara)
            BASE_DISTRO="fedora" ;;
        debian|ubuntu|pop|linuxmint)
            BASE_DISTRO="debian" ;;
        *)
            if [[ "$DISTRO_LIKE" == *"arch"* ]]; then BASE_DISTRO="arch"
            elif [[ "$DISTRO_LIKE" == *"fedora"* ]]; then BASE_DISTRO="fedora"
            elif [[ "$DISTRO_LIKE" == *"debian"* ]]; then BASE_DISTRO="debian"
            fi
            ;;
    esac
}

detect_session() {
    SESSION_TYPE="${XDG_SESSION_TYPE:-unknown}"
    CURRENT_DESKTOP="${XDG_CURRENT_DESKTOP:-unknown}"
    IS_WAYLAND=0
    if [[ "$SESSION_TYPE" == "wayland" ]]; then
        IS_WAYLAND=1
    fi
}

detect_versions() {
    PLASMA_VER="unknown"
    if command -v plasmashell &>/dev/null; then
        PLASMA_VER="$(plasmashell --version 2>/dev/null | awk '{print $NF}' || true)"
    fi

    QT_VER="unknown"
    if command -v pkg-config &>/dev/null && pkg-config --exists Qt6Core 2>/dev/null; then
        QT_VER="$(pkg-config --modversion Qt6Core 2>/dev/null || true)"
    elif command -v qmake6 &>/dev/null; then
        QT_VER="$(qmake6 -v 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n 1 || true)"
    fi
}

check_dependencies() {
    MISSING_REQUIRED=()
    OPTIONAL_AVAILABLE=()
    OPTIONAL_MISSING=()

    local req=(bash quickshell python3)
    for bin in "${req[@]}"; do
        if ! command -v "$bin" &>/dev/null; then
            MISSING_REQUIRED+=("$bin")
        fi
    done

    local opt=(matugen cava aubio brightnessctl qalc wireplumber powerprofilesctl spectacle swappy)
    for bin in "${opt[@]}"; do
        if command -v "$bin" &>/dev/null; then
            OPTIONAL_AVAILABLE+=("$bin")
        else
            OPTIONAL_MISSING+=("$bin")
        fi
    done
}
