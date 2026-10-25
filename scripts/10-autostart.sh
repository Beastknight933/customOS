#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Step 10: Create Autostart Entries & User Services
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

info "Installing Aetherium autostart entries, daemons, and CLI tools..."

BIN_DIR="$HOME/.local/bin"
AUTOSTART_DIR="$HOME/.config/autostart"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
mkdir -p "$BIN_DIR" "$AUTOSTART_DIR" "$SYSTEMD_USER_DIR"

if [[ -f "$BUNDLE_DIR/core/bin/aetherium-autostart" ]]; then
    track_target "$BIN_DIR/aetherium-autostart" "created"
    cp "$BUNDLE_DIR/core/bin/aetherium-autostart" "$BIN_DIR/aetherium-autostart"
    chmod +x "$BIN_DIR/aetherium-autostart"
fi

if [[ -f "$BUNDLE_DIR/core/bin/aetherium-doctor" ]]; then
    track_target "$BIN_DIR/aetherium-doctor" "created"
    cp "$BUNDLE_DIR/core/bin/aetherium-doctor" "$BIN_DIR/aetherium-doctor"
    chmod +x "$BIN_DIR/aetherium-doctor"
fi

if [[ -f "$BUNDLE_DIR/packaging/aetherium-autostart.desktop" ]]; then
    track_target "$AUTOSTART_DIR/aetherium-autostart.desktop" "created"
    cp "$BUNDLE_DIR/packaging/aetherium-autostart.desktop" "$AUTOSTART_DIR/aetherium-autostart.desktop"
fi

if [[ -f "$BUNDLE_DIR/packaging/aetherium-shell.service" ]]; then
    track_target "$SYSTEMD_USER_DIR/aetherium-shell.service" "created"
    cp "$BUNDLE_DIR/packaging/aetherium-shell.service" "$SYSTEMD_USER_DIR/aetherium-shell.service"
fi

ok "Autostart entries and command-line utilities installed."
