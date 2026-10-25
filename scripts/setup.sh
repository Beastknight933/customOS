#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Unified Interactive Setup & Installation Engine
# Follows the Caelestia KDE repository workflow and modular architecture
# ==============================================================================

set -euo pipefail
export AETHERIUM_SETUP_RUNNING=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
export BUNDLE_DIR
export SCRIPTS_DIR="$BUNDLE_DIR/scripts"
export PATH="$HOME/.local/bin:$PATH"

# shellcheck source=scripts/lib/log.sh
source "$SCRIPTS_DIR/lib/log.sh"
# shellcheck source=scripts/lib/privileges.sh
source "$SCRIPTS_DIR/lib/privileges.sh"
# shellcheck source=scripts/lib/packages.sh
source "$SCRIPTS_DIR/lib/packages.sh"
# shellcheck source=scripts/lib/common.sh
source "$SCRIPTS_DIR/lib/common.sh"
# shellcheck source=scripts/lib/detect.sh
source "$SCRIPTS_DIR/lib/detect.sh"
# shellcheck source=scripts/lib/backup.sh
source "$SCRIPTS_DIR/lib/backup.sh"
# shellcheck source=scripts/lib/rollback.sh
source "$SCRIPTS_DIR/lib/rollback.sh"

# Lock file to prevent concurrent setup runs
LOCK_FILE="${XDG_RUNTIME_DIR:-/tmp}/aetherium-setup.lock"
if command -v flock >/dev/null 2>&1; then
    exec 9>"$LOCK_FILE"
    flock -n 9 || { err "Another Aetherium setup process is currently running."; exit 1; }
fi

PROFILE=""
SDDM_VARIANT="aetherium"
SKIP_UPDATE="false"
NON_INTERACTIVE="false"
FORCE_CLI="false"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --profile)
            PROFILE="$2"; shift 2 ;;
        --sddm-theme)
            SDDM_VARIANT="$2"; shift 2 ;;
        --skip-update)
            SKIP_UPDATE="true"; shift ;;
        --non-interactive|-y)
            NON_INTERACTIVE="true"; shift ;;
        --cli)
            FORCE_CLI="true"; shift ;;
        --help|-h)
            echo "Aetherium OS Installer"
            echo "Usage: bash install.sh [options]"
            echo
            echo "Options:"
            echo "  --profile <name>      Choose profile: desktop, desktop-lockscreen, full, custom"
            echo "  --sddm-theme <name>   Choose SDDM theme variant: aetherium, clockwork"
            echo "  --skip-update         Skip distribution system package upgrade"
            echo "  --non-interactive, -y Run without interactive prompts using selected profile"
            echo "  --cli                 Run interactive CLI without compiling C++ TUI"
            echo "  --help, -h            Show this help text"
            exit 0
            ;;
        *)
            if [[ -z "$PROFILE" ]]; then
                PROFILE="$1"
                shift
            else
                shift
            fi
            ;;
    esac
done

# CRLF normalization for repository shell scripts
normalize_line_endings() {
    if command -v dos2unix >/dev/null 2>&1; then
        find "$BUNDLE_DIR" -maxdepth 3 -name '*.sh' -type f -exec dos2unix -q {} + 2>/dev/null || true
    fi
}
normalize_line_endings

banner() {
    clear 2>/dev/null || true
    echo -e "${C_CYAN}${C_BOLD}"
    echo "    ___         __   __               _                 ____   _____ "
    echo "   /   |  ___  / /__/ /_  ___   _____(_)__  ______ ___  / __ \ / ___/ "
    echo "  / /| | / _ \/ __/ __ \ / _ \ / ___/ / / / / __  __ \/ / / / \__ \  "
    echo " / ___ |/  __/ /_/ / / //  __// /  / / /_/ / / / / / / /_/ / ___/ /  "
    echo "/_/  |_|\___/\__/_/ /_/ \___//_/  /_/\__,_/_/ /_/ /_/\____(_)____/   "
    echo -e "${C_RESET}"
    echo -e "${C_BLUE}${C_BOLD}  Unified KDE Plasma 6 Desktop Shell & System Integration${C_RESET}"
    echo -e "${C_DIM}  Atmospheric Design System • Safe Transactional Deployment${C_RESET}"
    echo
}

banner

# Step 1: Detect Environment
info "Inspecting host system and desktop session..."
detect_distro
detect_session
detect_versions

echo -e "  • Distribution:  ${C_CYAN}${DISTRO_NAME} (${BASE_DISTRO})${C_RESET}"
echo -e "  • Session Type:  ${C_CYAN}${SESSION_TYPE} (Desktop: ${CURRENT_DESKTOP})${C_RESET}"
echo -e "  • KDE Plasma:    ${C_CYAN}${PLASMA_VER}${C_RESET} | Qt Runtime: ${C_CYAN}${QT_VER}${C_RESET}"
echo

if [[ "${IS_WAYLAND:-0}" -ne 1 && "${AETHERIUM_TEST_ENV:-0}" != "1" ]]; then
    err "Aetherium OS requires a KDE Plasma Wayland session."
    err "Active session is '${SESSION_TYPE}'. Layer-shell and session-lock protocols require Wayland."
    exit 1
fi

# Determine whether to attempt C++ TUI or proceed with interactive CLI
TUI_BIN="$BUNDLE_DIR/installer/build/aetherium-install"
TRY_TUI=1
if [[ "$FORCE_CLI" == "true" || "$NON_INTERACTIVE" == "true" || ! -t 0 ]]; then
    TRY_TUI=0
fi

if [[ $TRY_TUI -eq 1 ]]; then
    if [[ ! -x "$TUI_BIN" ]] && command -v cmake >/dev/null 2>&1 && command -v g++ >/dev/null 2>&1; then
        info "Compiling interactive terminal installer..."
        mkdir -p "$BUNDLE_DIR/installer/build"
        (
            cd "$BUNDLE_DIR/installer/build"
            cmake "$BUNDLE_DIR/installer/tui" -DCMAKE_BUILD_TYPE=Release >/dev/null 2>&1 && \
            cmake --build . -j"$(nproc 2>/dev/null || echo 1)" >/dev/null 2>&1
        ) || true
    fi

    if [[ -x "$TUI_BIN" ]]; then
        info "Launching Aetherium interactive installer TUI..."
        if "$TUI_BIN"; then
            ok "TUI installer finished cleanly."
            exit 0
        else
            warn "TUI session closed; continuing via standard terminal installer..."
        fi
    fi
fi

# Terminal Installer Workflow
if [[ -z "$PROFILE" ]]; then
    echo -e "${C_CYAN}${C_BOLD}Select an Installation Profile:${C_RESET}"
    echo "  1) desktop            — Aetherium Shell, panels, launcher & themes"
    echo "  2) desktop-lockscreen — Desktop Shell + Plasma In-Session Lock Screen (Recommended)"
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

export INSTALL_SHELL=true
export INSTALL_LOCKSCREEN=true
export INSTALL_SDDM=false
export SDDM_THEME_VARIANT="$SDDM_VARIANT"
export SKIP_SYSTEM_UPDATE="$SKIP_UPDATE"

case "$PROFILE" in
    desktop)
        INSTALL_SHELL=true
        INSTALL_LOCKSCREEN=false
        INSTALL_SDDM=false
        ;;
    desktop-lockscreen)
        INSTALL_SHELL=true
        INSTALL_LOCKSCREEN=true
        INSTALL_SDDM=false
        ;;
    full)
        INSTALL_SHELL=true
        INSTALL_LOCKSCREEN=true
        INSTALL_SDDM=true
        ;;
    custom)
        if [[ "$NON_INTERACTIVE" != "true" ]]; then
            confirm_prompt "Install Desktop Shell & Themes?" "Y" && INSTALL_SHELL=true || INSTALL_SHELL=false
            confirm_prompt "Install Plasma Lock Screen Theme?" "Y" && INSTALL_LOCKSCREEN=true || INSTALL_LOCKSCREEN=false
            confirm_prompt "Install SDDM Login Greeter Theme?" "N" && INSTALL_SDDM=true || INSTALL_SDDM=false
            if [[ "$INSTALL_SDDM" == "true" ]]; then
                echo "Select SDDM Theme Variant:"
                echo "  1) aetherium (Atmospheric Obsidian & Azure)"
                echo "  2) clockwork (Qylock Neo-Orbital Theme)"
                read -r -p "Choice [1-2] (default: 1): " _svar
                [[ "${_svar:-1}" == "2" ]] && SDDM_THEME_VARIANT="clockwork" || SDDM_THEME_VARIANT="aetherium"
            fi
        fi
        ;;
esac

echo
info "Planned Installation Plan (Profile: ${C_BOLD}${PROFILE}${C_RESET}):"
[[ "$INSTALL_SHELL" == "true" ]]      && echo -e "  ${C_GREEN}✔${C_RESET} Aetherium Desktop Shell, Bar Zones, Overview & Configs"
[[ "$INSTALL_LOCKSCREEN" == "true" ]] && echo -e "  ${C_GREEN}✔${C_RESET} Coordinated Plasma Lock Screen Package (aetherium.desktop)"
[[ "$INSTALL_SDDM" == "true" ]]       && echo -e "  ${C_GREEN}✔${C_RESET} SDDM Login Greeter (${SDDM_THEME_VARIANT} theme, staged replacement)"
[[ "$INSTALL_SDDM" == "false" ]]      && echo -e "  ${C_DIM}○${C_RESET} SDDM Login Greeter (not selected)"
echo

if [[ "$NON_INTERACTIVE" != "true" ]]; then
    confirm_prompt "Proceed with installation?" "Y" || {
        warn "Installation cancelled by user."
        exit 0
    }
fi

# Save answers for update.sh and persistence
mkdir -p "$HOME/.config/aetherium"
cat > "$HOME/.config/aetherium/install.env" << EOF
INSTALL_PROFILE='$PROFILE'
INSTALL_SHELL='$INSTALL_SHELL'
INSTALL_LOCKSCREEN='$INSTALL_LOCKSCREEN'
INSTALL_SDDM='$INSTALL_SDDM'
SDDM_THEME_VARIANT='$SDDM_THEME_VARIANT'
SKIP_SYSTEM_UPDATE='$SKIP_SYSTEM_UPDATE'
EOF

# Trap on failure for safe rollback
trap 'err "An error occurred during installation. Initiating automatic rollback..."; rollback_installation; exit 1' ERR

echo
info "Executing installation steps..."

bash "$SCRIPTS_DIR/00-backup-themes.sh"
bash "$SCRIPTS_DIR/00a-system-update.sh"
bash "$SCRIPTS_DIR/01-ensure-prereqs.sh"
bash "$SCRIPTS_DIR/02-all-packages.sh"

if [[ "$INSTALL_SHELL" == "true" ]]; then
    bash "$SCRIPTS_DIR/03-deploy-configs.sh"
    bash "$SCRIPTS_DIR/04-deploy-session.sh"
    bash "$SCRIPTS_DIR/08-build-shell.sh"
    bash "$SCRIPTS_DIR/10-autostart.sh"
fi

if [[ "$INSTALL_LOCKSCREEN" == "true" ]]; then
    bash "$SCRIPTS_DIR/06-lockscreen.sh"
fi

if [[ "$INSTALL_SDDM" == "true" ]]; then
    bash "$SCRIPTS_DIR/05-sddm-theme.sh"
fi

# Validation
if [[ -x "$BUNDLE_DIR/core/bin/aetherium-doctor" || -f "$BUNDLE_DIR/core/bin/aetherium-doctor" ]]; then
    info "Running post-installation health check..."
    python3 "$BUNDLE_DIR/core/bin/aetherium-doctor" --validate-configs || warn "Configuration check noted warnings."
fi

trap - ERR

echo
echo -e "${C_GREEN}${C_BOLD}╔════════════════════════════════════════════════════════════════╗${C_RESET}"
echo -e "${C_GREEN}${C_BOLD}║              AETHERIUM OS INSTALLED SUCCESSFULLY              ║${C_RESET}"
echo -e "${C_GREEN}${C_BOLD}╚════════════════════════════════════════════════════════════════╝${C_RESET}"
echo
echo -e "Profile: ${C_CYAN}${PROFILE}${C_RESET}"
echo -e "Next Steps:"
echo -e "  1. ${C_BOLD}Log Out and Log In${C_RESET} to your KDE Plasma Wayland session to start the shell."
echo -e "  2. Or start the shell immediately in your running session:"
echo -e "     ${C_YELLOW}nohup aetherium-autostart >/dev/null 2>&1 &${C_RESET}"
echo -e "  3. Verify system health at any time:"
echo -e "     ${C_YELLOW}aetherium-doctor${C_RESET}"
echo -e "  4. Update Aetherium at any time:"
echo -e "     ${C_YELLOW}bash update.sh${C_RESET}"
echo -e "  5. Uninstall and restore prior configuration:"
echo -e "     ${C_YELLOW}bash uninstall.sh${C_RESET}"
echo
