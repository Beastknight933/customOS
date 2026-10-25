#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Step 06: Configure In-Session Lock Screen
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=scripts/lib/log.sh
source "$SCRIPT_DIR/lib/log.sh"
# shellcheck source=scripts/lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"
# shellcheck source=scripts/lib/backup.sh
source "$SCRIPT_DIR/lib/backup.sh"

if [[ "${INSTALL_LOCKSCREEN:-false}" != "true" && "${APPLY_LOCKSCREEN:-false}" != "true" ]]; then
    skip "Lock screen integration not selected."
    exit 0
fi

info "Configuring In-Session Plasma Lock Screen (aetherium.desktop)..."

LOCAL_PLASMA_SHELLS="$HOME/.local/share/plasma/shells/aetherium.desktop"
mkdir -p "$(dirname "$LOCAL_PLASMA_SHELLS")"

SRC_LOCKSCREEN="$BUNDLE_DIR/themes/lockscreen/aetherium.desktop"
if [[ ! -d "$SRC_LOCKSCREEN" || ! -f "$SRC_LOCKSCREEN/metadata.json" ]]; then
    err "Lock screen package source not found or missing metadata.json at $SRC_LOCKSCREEN"
    exit 1
fi

track_target "$LOCAL_PLASMA_SHELLS" "created"
rm -rf "$LOCAL_PLASMA_SHELLS"
mkdir -p "$LOCAL_PLASMA_SHELLS"
cp -r "$SRC_LOCKSCREEN/"* "$LOCAL_PLASMA_SHELLS/"

if command -v kwriteconfig6 &>/dev/null; then
    kwriteconfig6 --file plasmashellrc --group "Shell" --key "ShellPackage" "aetherium.desktop"
    kwriteconfig6 --file kscreenlockerrc --group "Greeter" --key "Theme" --delete 2>/dev/null || true
    ok "KScreenLocker configured with 'aetherium.desktop'."
else
    warn "kwriteconfig6 not found in PATH; registered package in ~/.local/share/plasma/shells/aetherium.desktop."
fi
