#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Primary Uninstallation & System Restoration Engine
# Safely restores prior system state, KDE configurations, and display manager
# ==============================================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_DIR="$SCRIPT_DIR"

# shellcheck source=scripts/lib/log.sh
source "$BUNDLE_DIR/scripts/lib/log.sh" 2>/dev/null || source "$BUNDLE_DIR/installer/lib/common.sh"
# shellcheck source=scripts/lib/privileges.sh
source "$BUNDLE_DIR/scripts/lib/privileges.sh" 2>/dev/null || true
# shellcheck source=scripts/lib/rollback.sh
source "$BUNDLE_DIR/scripts/lib/rollback.sh" 2>/dev/null || source "$BUNDLE_DIR/installer/lib/rollback.sh"

cat << 'EOF'
    ___         __   __               _                 ____   _____ 
   /   |  ___  / /__/ /_  ___   _____(_)__  ______ ___  / __ \ / ___/ 
  / /| | / _ \/ __/ __ \ / _ \ / ___/ / / / / __  __ \/ / / / \__ \  
 / ___ |/  __/ /_/ / / //  __// /  / / /_/ / / / / / / /_/ / ___/ /  
/_/  |_|\___/\__/_/ /_/ \___//_/  /_/\__,_/_/ /_/ /_/\____(_)____/   
+------------------------------------------------------------------+
|                   AETHERIUM OS UNINSTALLER                       |
+------------------------------------------------------------------+
EOF
echo
echo " This will remove Aetherium shell files, services, and configurations."
echo " Prior KDE Plasma and SDDM configurations will be restored."
echo

read -r -p "Are you sure you want to uninstall Aetherium OS? [y/N]: " _confirm
[[ "${_confirm,,}" == "y" || "${_confirm,,}" == "yes" ]] || {
    echo "Uninstallation cancelled."
    exit 0
}

# Check for available backups
STATE_ROOT="${XDG_STATE_HOME:-$HOME/.local/state}/aetherium"
BACKUPS_DIR="$STATE_ROOT/backups"
SELECTED_BACKUP=""

if [[ -d "$BACKUPS_DIR" ]]; then
    mapfile -t backups < <(find "$BACKUPS_DIR" -mindepth 1 -maxdepth 1 -type d -name 'backup-*' | sort -r 2>/dev/null || true)
    if [[ ${#backups[@]} -gt 0 ]]; then
        echo
        info "Available snapshots to restore from:"
        for i in "${!backups[@]}"; do
            bdir="${backups[$i]}"
            bname="$(basename "$bdir" | sed 's/backup-//')"
            echo "  $((i+1))) Snapshot: $bname"
        done
        echo "  0) Standard Cleanup (revert to default KDE settings)"
        echo
        read -r -p "Select a backup to restore [1]: " _bsel
        _bsel="${_bsel:-1}"
        if [[ "$_bsel" =~ ^[0-9]+$ ]] && [[ "$_bsel" -gt 0 ]] && [[ "$_bsel" -le ${#backups[@]} ]]; then
            SELECTED_BACKUP="${backups[$((_bsel-1))]}"
            info "Selected snapshot: $SELECTED_BACKUP"
        fi
    fi
fi

echo
info "Step 1/5: Reverting SDDM Display Manager Theme..."
if [[ -f "/etc/sddm.conf.d/zz-aetherium.conf" || -d "$STATE_ROOT/sddm" ]]; then
    ADAPTER="$BUNDLE_DIR/core/sddm-adapter/aetherium-sddm-adapter.sh"
    if [[ -x "$ADAPTER" || -f "$ADAPTER" ]]; then
        bash "$ADAPTER" --rollback || warn "SDDM rollback reported warnings."
    else
        aetherium_sudo rm -f "/etc/sddm.conf.d/zz-aetherium.conf" 2>/dev/null || true
    fi
    ok "SDDM theme restored."
else
    skip "No Aetherium SDDM drop-in detected."
fi

info "Step 2/5: Reverting KDE Plasma Lock Screen Configuration..."
if [[ -n "$SELECTED_BACKUP" && -f "$SELECTED_BACKUP/plasma_state.txt" ]]; then
    # Exact restoration from snapshot
    while IFS='=' read -r key val; do
        case "$key" in
            SHELL_PACKAGE)
                if [[ "$val" == "__UNSET__" ]]; then
                    kwriteconfig6 --file plasmashellrc --group "Shell" --key "ShellPackage" --delete 2>/dev/null || true
                elif [[ -n "$val" ]]; then
                    kwriteconfig6 --file plasmashellrc --group "Shell" --key "ShellPackage" "$val" 2>/dev/null || true
                fi
                ;;
            GREETER_THEME)
                if [[ "$val" == "__UNSET__" ]]; then
                    kwriteconfig6 --file kscreenlockerrc --group "Greeter" --key "Theme" --delete 2>/dev/null || true
                elif [[ -n "$val" ]]; then
                    kwriteconfig6 --file kscreenlockerrc --group "Greeter" --key "Theme" "$val" 2>/dev/null || true
                fi
                ;;
        esac
    done < "$SELECTED_BACKUP/plasma_state.txt"
    ok "Lock screen configuration restored from snapshot."
else
    if command -v kwriteconfig6 >/dev/null 2>&1; then
        kwriteconfig6 --file plasmashellrc --group "Shell" --key "ShellPackage" --delete 2>/dev/null || true
        kwriteconfig6 --file kscreenlockerrc --group "Greeter" --key "Theme" --delete 2>/dev/null || true
        ok "Lock screen configuration reset to KDE Plasma default."
    fi
fi

info "Step 3/5: Removing Aetherium User Services & Autostart Entries..."
pkill -f "quickshell.*aetherium" 2>/dev/null || true
pkill -f "aetherium-autostart" 2>/dev/null || true

rm -f "$HOME/.config/autostart/aetherium-autostart.desktop"
rm -f "$HOME/.config/systemd/user/aetherium-shell.service"
rm -f "$HOME/.local/bin/aetherium-autostart"
rm -f "$HOME/.local/bin/aetherium-doctor"
ok "Autostart entries and background processes removed."

info "Step 4/5: Removing Session Environment Drop-ins..."
rm -f "$HOME/.config/environment.d/aetherium.conf"
rm -f "$HOME/.config/plasma-workspace/env/aetherium.sh"
ok "Session environment drop-ins removed."

info "Step 5/5: Removing Aetherium Shell & Theme Packages..."
rm -rf "$HOME/.local/share/plasma/shells/aetherium.desktop"
rm -rf "$HOME/.config/quickshell/aetherium"

read -r -p "Remove user configuration directory (~/.config/aetherium)? [y/N]: " _rm_cfg
if [[ "${_rm_cfg,,}" == "y" || "${_rm_cfg,,}" == "yes" ]]; then
    rm -rf "$HOME/.config/aetherium"
    ok "User configuration directory removed."
else
    info "Preserved ~/.config/aetherium."
fi

echo
ok "Aetherium OS uninstalled successfully!"
echo
echo "Summary of Restoration:"
echo "  • KDE Plasma Lock Screen: Reverted to default"
echo "  • SDDM Display Manager:  Restored previous theme / removed drop-in"
echo "  • Session Environment:   Cleaned"
echo "  • Backups preserved at:  ${BACKUPS_DIR}"
echo
echo "To return to standard KDE Plasma, please log out and log back in."
echo
