#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Unified System Installer (Hardened)
# Safe, transactional deployment of Aetherium Desktop, Lock Screen, and SDDM
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
AETHERIUM_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load library modules
# shellcheck source=installer/lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"
# shellcheck source=installer/lib/detect.sh
source "${SCRIPT_DIR}/lib/detect.sh"
# shellcheck source=installer/lib/backup.sh
source "${SCRIPT_DIR}/lib/backup.sh"
# shellcheck source=installer/lib/rollback.sh
source "${SCRIPT_DIR}/lib/rollback.sh"

PROFILE="${1:-}"

header() {
    clear 2>/dev/null || true
    echo -e "${C_BLUE}${C_BOLD}"
    echo " ╭─────────────────────────────────────────────────────────╮"
    echo " │                 󰓅 AETHERIUM OS INSTALLER                │"
    echo " │      Unified KDE Plasma 6 Desktop Shell & System Integration│"
    echo " ╰─────────────────────────────────────────────────────────╯"
    echo -e "${C_RESET}"
}

header

# 1. Environment & Distro Detection
log_info "Step 1/15: Inspecting Host Environment..."
detect_distro
detect_session
detect_versions
check_dependencies

log_step "Detected Distribution: ${DISTRO_NAME} (${BASE_DISTRO})"
log_step "Desktop Session: ${CURRENT_DESKTOP} (${SESSION_TYPE})"
log_step "KDE Plasma: ${PLASMA_VER} | Qt Runtime: ${QT_VER}"

if [[ $IS_WAYLAND -ne 1 ]]; then
    log_err "Aetherium OS strictly requires a Wayland session (WlrLayershell & ExtSessionLock protocols)."
    log_err "Current session is '${SESSION_TYPE}'. Installation cannot continue."
    exit 1
fi

if [[ ${#MISSING_REQUIRED[@]} -gt 0 ]]; then
    log_err "Missing mandatory package dependencies: ${MISSING_REQUIRED[*]}"
    exit 1
fi
log_ok "Host environment verified."

# 2. Profile Selection
if [[ -z "$PROFILE" ]]; then
    echo
    echo -e "${C_CYAN}${C_BOLD}Select an Installation Profile:${C_RESET}"
    echo "  1) desktop            — Aetherium Shell, panels, launcher & themes"
    echo "  2) desktop-lockscreen — Desktop Shell + Plasma In-Session Lock Screen"
    echo "  3) full               — Complete Experience (Desktop + Lock Screen + SDDM Theme)"
    echo "  4) custom             — Granular component selection"
    echo
    echo -ne "${C_YELLOW}Choose profile [1-4] (default: 2): ${C_RESET}"
    read -r choice
    case "${choice:-2}" in
        1) PROFILE="desktop" ;;
        2) PROFILE="desktop-lockscreen" ;;
        3) PROFILE="full" ;;
        4) PROFILE="custom" ;;
        *) PROFILE="desktop-lockscreen" ;;
    esac
fi
log_info "Selected Installation Profile: '${PROFILE}'"

INSTALL_SHELL=1
INSTALL_LOCKSCREEN=0
INSTALL_SDDM=0

case "$PROFILE" in
    desktop)
        INSTALL_LOCKSCREEN=0; INSTALL_SDDM=0 ;;
    desktop-lockscreen)
        INSTALL_LOCKSCREEN=1; INSTALL_SDDM=0 ;;
    full)
        INSTALL_LOCKSCREEN=1; INSTALL_SDDM=1 ;;
    custom)
        confirm_prompt "Install Desktop Shell?" "Y" && INSTALL_SHELL=1 || INSTALL_SHELL=0
        confirm_prompt "Install Lock Screen Theme?" "Y" && INSTALL_LOCKSCREEN=1 || INSTALL_LOCKSCREEN=0
        confirm_prompt "Install SDDM Login Theme?" "N" && INSTALL_SDDM=1 || INSTALL_SDDM=0
        ;;
esac

# 3. Present Planned Actions
echo
log_info "Planned Changes for Profile '${PROFILE}':"
[[ $INSTALL_SHELL -eq 1 ]]      && log_step "• Deploy ~/.config/aetherium/ configurations & schemes"
[[ $INSTALL_SHELL -eq 1 ]]      && log_step "• Register environment.d and plasma-workspace session environment"
[[ $INSTALL_SHELL -eq 1 ]]      && log_step "• Register Aetherium Desktop Shell autostart"
[[ $INSTALL_LOCKSCREEN -eq 1 ]] && log_step "• Deploy and activate 'aetherium.desktop' Plasma lock screen"
[[ $INSTALL_SDDM -eq 1 ]]       && log_step "• Install SDDM theme and configure drop-in at /etc/sddm.conf.d/zz-aetherium.conf"
echo

confirm_prompt "Proceed with installation?" "Y" || {
    log_warn "Installation cancelled by user."
    exit 0
}

# 4. Transactional Backup
log_info "Step 8/15: Creating Pre-Installation State Backup..."
init_backup

# Trap errors for automatic rollback
trap 'log_err "An error occurred during installation. Initiating automatic rollback..."; rollback_installation; exit 1' ERR

# 5. Deploy User Configurations
log_info "Step 9/15: Deploying Aetherium Configurations & Tokens..."
CFG_TARGET="$HOME/.config/aetherium"
mkdir -p "$CFG_TARGET" "$CFG_TARGET/schemes"

track_target "$CFG_TARGET/shell.json" "created"
cp "$AETHERIUM_ROOT/desktop/config/shell.json" "$CFG_TARGET/shell.json"

track_target "$CFG_TARGET/tokens.json" "created"
cp "$AETHERIUM_ROOT/desktop/config/tokens.json" "$CFG_TARGET/tokens.json"

track_target "$CFG_TARGET/schemes" "created"
cp -r "$AETHERIUM_ROOT/desktop/schemes/"* "$CFG_TARGET/schemes/" 2>/dev/null || true
log_ok "Configuration deployed to $CFG_TARGET."

# 6. Deploy Session Environment
log_info "Step 10/15: Establishing Session Environment Variables..."
ENV_D="$HOME/.config/environment.d"
PLASMA_ENV_D="$HOME/.config/plasma-workspace/env"
mkdir -p "$ENV_D" "$PLASMA_ENV_D"

ENV_CONF="$ENV_D/aetherium.conf"
track_target "$ENV_CONF" "created"
cat > "$ENV_CONF" << EOF
# Written by Aetherium OS. Sourced by systemd user session.
QML2_IMPORT_PATH=$HOME/.local/lib/aetherium/qt6/qml:/usr/lib/qt6/qml
AETHERIUM_LIB_DIR=$HOME/.local/lib/aetherium
AETHERIUM_BIN_DIR=$HOME/.local/bin
AETHERIUM_SHELL_CONFIG=$HOME/.config/aetherium/shell.qml
EOF

PLASMA_ENV_SH="$PLASMA_ENV_D/aetherium.sh"
track_target "$PLASMA_ENV_SH" "created"
cat > "$PLASMA_ENV_SH" << EOF
#!/bin/sh
# Written by Aetherium OS. Sourced by KDE Plasma for KWin and session processes.
export PATH="\$HOME/.local/bin:\${PATH:+:\$PATH}"
export QML2_IMPORT_PATH="\$HOME/.local/lib/aetherium/qt6/qml:/usr/lib/qt6/qml\${QML2_IMPORT_PATH:+:\$QML2_IMPORT_PATH}"
export AETHERIUM_LIB_DIR="\$HOME/.local/lib/aetherium"
export AETHERIUM_BIN_DIR="\$HOME/.local/bin"
export AETHERIUM_SHELL_CONFIG="\$HOME/.config/aetherium/shell.qml"
EOF
chmod +x "$PLASMA_ENV_SH"
log_ok "Session environment written."

# 7. Deploy Shell & Autostart
if [[ $INSTALL_SHELL -eq 1 ]]; then
    log_info "Step 11/15: Establishing Desktop Shell Integration..."
    BIN_DIR="$HOME/.local/bin"
    AUTOSTART_DIR="$HOME/.config/autostart"
    mkdir -p "$BIN_DIR" "$AUTOSTART_DIR"

    track_target "$BIN_DIR/aetherium-autostart" "created"
    cp "$AETHERIUM_ROOT/core/bin/aetherium-autostart" "$BIN_DIR/aetherium-autostart"
    chmod +x "$BIN_DIR/aetherium-autostart"

    track_target "$BIN_DIR/aetherium-doctor" "created"
    cp "$AETHERIUM_ROOT/core/bin/aetherium-doctor" "$BIN_DIR/aetherium-doctor"
    chmod +x "$BIN_DIR/aetherium-doctor"

    track_target "$AUTOSTART_DIR/aetherium-autostart.desktop" "created"
    cp "$AETHERIUM_ROOT/packaging/aetherium-autostart.desktop" "$AUTOSTART_DIR/aetherium-autostart.desktop"
    log_ok "Desktop Shell autostart established."
fi

# 8. Configure Lock Screen
if [[ $INSTALL_LOCKSCREEN -eq 1 ]]; then
    log_info "Step 12/15: Configuring In-Session Plasma Lock Screen..."
    LOCAL_PLASMA_SHELLS="$HOME/.local/share/plasma/shells/aetherium.desktop"
    mkdir -p "$(dirname "$LOCAL_PLASMA_SHELLS")"

    track_target "$LOCAL_PLASMA_SHELLS" "created"
    rm -rf "$LOCAL_PLASMA_SHELLS"
    mkdir -p "$LOCAL_PLASMA_SHELLS"
    cp -r "$AETHERIUM_ROOT/themes/lockscreen/aetherium.desktop/"* "$LOCAL_PLASMA_SHELLS/"

    if command -v kwriteconfig6 &>/dev/null; then
        kwriteconfig6 --file plasmashellrc --group "Shell" --key "ShellPackage" "aetherium.desktop"
        kwriteconfig6 --file kscreenlockerrc --group "Greeter" --key "Theme" --delete
        log_ok "KScreenLocker configured with 'aetherium.desktop'."
    else
        log_warn "kwriteconfig6 not found in PATH; please register 'aetherium.desktop' manually in plasmashellrc."
    fi
fi

# 9. Configure SDDM
if [[ $INSTALL_SDDM -eq 1 ]]; then
    log_info "Step 13/15: Installing and Configuring SDDM Greeter Theme..."
    bash "$AETHERIUM_ROOT/core/sddm-adapter/aetherium-sddm-adapter.sh" --install "$AETHERIUM_ROOT/themes/sddm/aetherium"
    log_ok "SDDM Greeter configured."
fi

# 10. Validation
log_info "Step 14/15: Running Post-Installation Validation..."
python3 "$AETHERIUM_ROOT/core/bin/aetherium-doctor" --validate-configs
log_ok "Validation passed."

# 11. Summary
echo
echo -e "${C_GREEN}${C_BOLD}╔════════════════════════════════════════════════════════════════╗${C_RESET}"
echo -e "${C_GREEN}${C_BOLD}║              AETHERIUM OS INSTALLED SUCCESSFULLY              ║${C_RESET}"
echo -e "${C_GREEN}${C_BOLD}╚════════════════════════════════════════════════════════════════╝${C_RESET}"
echo
echo -e "Profile: ${C_CYAN}${PROFILE}${C_RESET}"
echo -e "To start the Aetherium Shell immediately without logging out:"
echo -e "  ${C_YELLOW}nohup aetherium-autostart >/dev/null 2>&1 &${C_RESET}"
echo
echo -e "To verify system state at any time:"
echo -e "  ${C_YELLOW}aetherium-doctor${C_RESET}"
echo
echo -e "To uninstall cleanly and restore prior settings:"
echo -e "  ${C_YELLOW}bash ${SCRIPT_DIR}/uninstall.sh${C_RESET}"
echo
