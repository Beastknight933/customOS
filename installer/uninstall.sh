#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Safe Uninstaller & Restoration Engine
# Reverts system configurations, restores previous themes, and cleans up assets
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
AETHERIUM_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load common utilities
# shellcheck source=installer/lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"
# shellcheck source=installer/lib/rollback.sh
source "${SCRIPT_DIR}/lib/rollback.sh"

echo -e "${C_RED}${C_BOLD}"
echo " ╭─────────────────────────────────────────────────────────╮"
echo " │                󰓅 AETHERIUM OS UNINSTALLER               │"
echo " │      Safe Reversion of Desktop, Lock Screen, and SDDM   │"
echo " ╰─────────────────────────────────────────────────────────╯"
echo -e "${C_RESET}"

confirm_prompt "Are you sure you want to uninstall Aetherium OS and restore prior settings?" "N" || {
    log_info "Uninstallation aborted."
    exit 0
}

# 1. Rollback SDDM Theme if installed
if [[ -f "/etc/sddm.conf.d/zz-aetherium.conf" || -d "/usr/share/sddm/themes/aetherium" ]]; then
    log_info "Reverting SDDM display manager theme..."
    if [[ -x "$AETHERIUM_ROOT/core/sddm-adapter/aetherium-sddm-adapter.sh" ]]; then
        bash "$AETHERIUM_ROOT/core/sddm-adapter/aetherium-sddm-adapter.sh" --uninstall || true
    fi
fi

# 2. Rollback via Manifest
log_info "Reverting installed desktop files & lock screen..."
rollback_installation

# 3. Clean autostart and local binaries
rm -f "$HOME/.config/autostart/aetherium-autostart.desktop" 2>/dev/null || true
rm -f "$HOME/.local/bin/aetherium-autostart" 2>/dev/null || true
rm -f "$HOME/.local/bin/aetherium-doctor" 2>/dev/null || true

# 4. Optional removal of user configs
if confirm_prompt "Remove user configuration directory (~/.config/aetherium)?" "N"; then
    rm -rf "$HOME/.config/aetherium"
    log_step "Removed ~/.config/aetherium"
else
    log_step "Preserved ~/.config/aetherium"
fi

# 5. Final Report
echo
log_ok "Aetherium OS uninstallation is complete."
log_info "Your previous KDE Plasma shell and display manager settings have been restored."
echo
