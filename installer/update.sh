#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Non-Destructive Update Engine
# Refreshes desktop components, themes, and scripts while preserving user settings
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
AETHERIUM_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=installer/lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"
# shellcheck source=installer/lib/backup.sh
source "${SCRIPT_DIR}/lib/backup.sh"

echo -e "${C_BLUE}${C_BOLD}"
echo " ╭─────────────────────────────────────────────────────────╮"
echo " │                 󰓅 AETHERIUM OS UPDATER                  │"
echo " │       Non-Destructive Component & Asset Refresh         │"
echo " ╰─────────────────────────────────────────────────────────╯"
echo -e "${C_RESET}"

log_info "Initiating update process..."
init_backup

# 1. Update Core Executables
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
cp "$AETHERIUM_ROOT/core/bin/aetherium-autostart" "$BIN_DIR/aetherium-autostart"
chmod +x "$BIN_DIR/aetherium-autostart"
cp "$AETHERIUM_ROOT/core/bin/aetherium-doctor" "$BIN_DIR/aetherium-doctor"
chmod +x "$BIN_DIR/aetherium-doctor"
log_ok "Updated core binaries in $BIN_DIR"

# 2. Update Schemes Presets
CFG_TARGET="$HOME/.config/aetherium"
mkdir -p "$CFG_TARGET/schemes"
cp -r "$AETHERIUM_ROOT/desktop/schemes/"* "$CFG_TARGET/schemes/" 2>/dev/null || true
log_ok "Updated color schemes in $CFG_TARGET/schemes"

# 3. Update Plasma Lockscreen if currently installed
LOCAL_PLASMA_SHELLS="$HOME/.local/share/plasma/shells/aetherium.desktop"
if [[ -d "$LOCAL_PLASMA_SHELLS" ]]; then
    cp -r "$AETHERIUM_ROOT/themes/lockscreen/aetherium.desktop/"* "$LOCAL_PLASMA_SHELLS/"
    log_ok "Updated lockscreen shell package at $LOCAL_PLASMA_SHELLS"
fi

# 4. Update SDDM Theme if currently installed
if [[ -d "/usr/share/sddm/themes/aetherium" && $EUID -eq 0 ]]; then
    cp -r "$AETHERIUM_ROOT/themes/sddm/aetherium/"* "/usr/share/sddm/themes/aetherium/"
    log_ok "Updated SDDM theme assets in /usr/share/sddm/themes/aetherium"
fi

# 5. Validate
python3 "$AETHERIUM_ROOT/core/bin/aetherium-doctor" --validate-configs
log_ok "Update completed without altering user configuration."
