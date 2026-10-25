#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Step 01: Ensure Prerequisites
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=scripts/lib/log.sh
source "$SCRIPT_DIR/lib/log.sh"
# shellcheck source=scripts/lib/privileges.sh
source "$SCRIPT_DIR/lib/privileges.sh"
# shellcheck source=scripts/lib/packages.sh
source "$SCRIPT_DIR/lib/packages.sh"

if [[ "${AETHERIUM_TEST_ENV:-0}" == "1" ]]; then
    ok "Test environment detected; skipping package manager prerequisite installation."
    exit 0
fi

info "Verifying host prerequisites for ${BASE_DISTRO}..."

case "$BASE_DISTRO" in
    arch)
        if ! command -v git >/dev/null 2>&1 || ! command -v cmake >/dev/null 2>&1; then
            info "Installing base build tools (base-devel, git, cmake)..."
            aetherium_sudo pacman -S --needed --noconfirm base-devel git cmake || true
        fi
        if ! command -v yay >/dev/null 2>&1; then
            info "AUR helper 'yay' not detected. Checking pacman..."
            if command -v pacman >/dev/null 2>&1; then
                tmpdir="$(mktemp -d)"
                git clone --depth 1 https://aur.archlinux.org/yay-bin.git "$tmpdir" 2>/dev/null || true
                if [[ -f "$tmpdir/PKGBUILD" ]]; then
                    ( cd "$tmpdir" && makepkg -si --noconfirm ) || warn "Could not auto-install yay; packages may need manual installation."
                fi
                rm -rf "$tmpdir"
            fi
        fi
        ;;
    fedora)
        MISSING=()
        for cmd in gcc g++ cmake make git jq; do
            command -v "$cmd" >/dev/null 2>&1 || MISSING+=("$cmd")
        done
        if [[ ${#MISSING[@]} -gt 0 ]]; then
            info "Installing missing Fedora build tools (${MISSING[*]})..."
            aetherium_sudo dnf install -y gcc gcc-c++ cmake make git jq || warn "Could not install all build packages."
        fi
        ;;
    debian)
        MISSING=()
        for cmd in g++ cmake make git curl jq; do
            command -v "$cmd" >/dev/null 2>&1 || MISSING+=("$cmd")
        done
        if [[ ${#MISSING[@]} -gt 0 ]]; then
            info "Installing missing Debian/Ubuntu build tools (${MISSING[*]})..."
            aetherium_sudo apt-get update && aetherium_sudo apt-get install -y build-essential cmake make git curl jq || warn "Could not install all build packages."
        fi
        ;;
    *)
        info "Running on unmanaged or mock distribution; checking basic tools..."
        ;;
esac

ok "Prerequisites verified."
