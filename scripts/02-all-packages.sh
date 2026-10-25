#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Step 02: Install Packages
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=scripts/lib/log.sh
source "$SCRIPT_DIR/lib/log.sh"
# shellcheck source=scripts/lib/packages.sh
source "$SCRIPT_DIR/lib/packages.sh"

export BUNDLE_DIR
export PACKAGE_GROUP="all"

if [[ "${AETHERIUM_TEST_ENV:-0}" == "1" ]]; then
    ok "Test environment detected; skipping package manager execution."
    exit 0
fi

packages_script="$BUNDLE_DIR/installer/distro/$BASE_DISTRO/packages.sh"

if [[ -f "$packages_script" ]]; then
    info "Executing package installer for $BASE_DISTRO..."
    bash "$packages_script" || warn "Package installation completed with warnings."
else
    skip "No distribution package script found for '$BASE_DISTRO'; skipping system package manager installation."
fi

ok "Package setup step completed."
