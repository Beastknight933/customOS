#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Step 00a: System Update
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=scripts/lib/log.sh
source "$SCRIPT_DIR/lib/log.sh"
# shellcheck source=scripts/lib/privileges.sh
source "$SCRIPT_DIR/lib/privileges.sh"
# shellcheck source=scripts/lib/packages.sh
source "$SCRIPT_DIR/lib/packages.sh"

if [[ "${SKIP_SYSTEM_UPDATE:-false}" == "true" ]]; then
    skip "System update skipped by configuration."
    exit 0
fi

info "Checking for system updates on ${BASE_DISTRO}..."

case "$BASE_DISTRO" in
    arch)
        if command -v pacman >/dev/null 2>&1; then
            aetherium_sudo pacman -Syu --noconfirm || warn "System update completed with warnings."
        fi
        ;;
    fedora)
        if command -v dnf >/dev/null 2>&1; then
            aetherium_sudo dnf upgrade -y || warn "System update completed with warnings."
        fi
        ;;
    debian)
        if command -v apt-get >/dev/null 2>&1; then
            aetherium_sudo apt-get update && aetherium_sudo apt-get upgrade -y || warn "System update completed with warnings."
        fi
        ;;
    *)
        skip "Skipping system update on unmanaged distribution ($BASE_DISTRO)."
        ;;
esac

ok "System update step completed."
