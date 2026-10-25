#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Distro Detection and Package Manager Interface
# ==============================================================================

if [[ -z "${AETHERIUM_PACKAGES_SOURCED:-}" ]]; then
AETHERIUM_PACKAGES_SOURCED=1

detect_base_distro() {
    local detected="unknown"
    local os_release="${AETHERIUM_OS_RELEASE:-${CAELESTIA_OS_RELEASE:-/etc/os-release}}"

    if [[ -n "${BASE_DISTRO:-}" ]]; then
        printf '%s\n' "$BASE_DISTRO"
        return 0
    fi

    if [[ -f "$os_release" ]]; then
        # shellcheck disable=SC1090
        . "$os_release"
        case "${ID:-}" in
            arch|cachyos|endeavouros|manjaro|artix)
                detected="arch"
                ;;
            fedora|nobara|bazzite|rhel|centos|almalinux|rocky)
                detected="fedora"
                ;;
            debian|ubuntu|pop|mint|kali|raspbian|elementary|zorin|deepin|devuan)
                detected="debian"
                ;;
            *)
                if echo "${ID_LIKE:-}" | grep -iq "arch"; then
                    detected="arch"
                elif echo "${ID_LIKE:-}" | grep -iq "fedora"; then
                    detected="fedora"
                elif echo "${ID_LIKE:-}" | grep -iq -E "debian|ubuntu"; then
                    detected="debian"
                fi
                ;;
        esac
    fi

    if [[ "$detected" == "unknown" ]]; then
        if command -v pacman >/dev/null 2>&1; then
            detected="arch"
        elif command -v dnf >/dev/null 2>&1; then
            detected="fedora"
        elif command -v apt-get >/dev/null 2>&1; then
            detected="debian"
        fi
    fi

    printf '%s\n' "$detected"
}

export BASE_DISTRO="$(detect_base_distro)"

package_is_installed() {
    local pkg="$1"
    case "$BASE_DISTRO" in
        arch)
            pacman -Qq "$pkg" >/dev/null 2>&1
            ;;
        fedora)
            rpm -q "$pkg" >/dev/null 2>&1
            ;;
        debian)
            dpkg-query -W -f='${Status}' "$pkg" 2>/dev/null | grep -q "install ok installed"
            ;;
        *)
            command -v "$pkg" >/dev/null 2>&1
            ;;
    esac
}

fi
