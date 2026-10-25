#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Unified System Updater
# Safely updates shell, configuration, themes, and integrations
# ==============================================================================

set -uo pipefail
export PATH="$HOME/.local/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_DIR="$SCRIPT_DIR"
export BUNDLE_DIR

# shellcheck source=scripts/lib/log.sh
source "$BUNDLE_DIR/scripts/lib/log.sh" 2>/dev/null || source "$BUNDLE_DIR/installer/lib/common.sh"
# shellcheck source=scripts/lib/privileges.sh
source "$BUNDLE_DIR/scripts/lib/privileges.sh" 2>/dev/null || true
# shellcheck source=scripts/lib/backup.sh
source "$BUNDLE_DIR/scripts/lib/backup.sh" 2>/dev/null || source "$BUNDLE_DIR/installer/lib/backup.sh"

section() {
    local title="$1"
    echo
    echo "-------------------------------------------------------------"
    echo "  $title"
    echo "-------------------------------------------------------------"
}

# Concurrency lock
if command -v flock >/dev/null 2>&1; then
    exec 9>"${XDG_RUNTIME_DIR:-/tmp}/aetherium-update.lock"
    flock -n 9 || { err "Another Aetherium update process is currently running."; exit 1; }
fi

section "Step 1: Inspecting Installation & Source Tree"

if [ -d "$BUNDLE_DIR/.git" ] && command -v git >/dev/null 2>&1; then
    info "Git repository detected. Checking remote updates..."
    git -C "$BUNDLE_DIR" fetch origin 2>/dev/null || warn "Failed to fetch from remote origin (network offline?)"

    STASHED=0
    if ! git -C "$BUNDLE_DIR" diff-index --quiet HEAD -- 2>/dev/null; then
        warn "Local uncommitted modifications detected."
        info "Creating automatic safety stash before update..."
        git -C "$BUNDLE_DIR" stash -m "Auto-stash before Aetherium update" || warn "Stash command returned warnings."
        STASHED=1
    fi

    CURRENT_BRANCH=$(git -C "$BUNDLE_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
    info "Pulling latest changes for branch '${CURRENT_BRANCH}'..."
    git -C "$BUNDLE_DIR" pull origin "$CURRENT_BRANCH" 2>/dev/null || warn "Could not pull latest changes; continuing with local source."

    if [ "$STASHED" -eq 1 ]; then
        info "Local modifications were preserved in git stash."
    fi
else
    info "Stand-alone tree checkout (not a Git repository); updating local components..."
fi

# Read existing installation preferences
INSTALL_ENV="$HOME/.config/aetherium/install.env"
if [ -f "$INSTALL_ENV" ]; then
    info "Loading persistent installation preferences from $INSTALL_ENV..."
    set -a
    # shellcheck disable=SC1090
    . "$INSTALL_ENV"
    set +a
else
    info "No install.env found; defaulting to desktop-lockscreen configuration."
    INSTALL_SHELL="true"
    INSTALL_LOCKSCREEN="true"
    INSTALL_SDDM="false"
    SDDM_THEME_VARIANT="aetherium"
fi

section "Step 2: Pre-Update Transactional Backup"
init_backup
ok "Pre-update state snapshot created."

section "Step 3: Updating Core Components"

info "Updating Aetherium configuration files..."
bash "$BUNDLE_DIR/scripts/03-deploy-configs.sh" || die "Configuration deployment failed."

info "Updating session environment definitions..."
bash "$BUNDLE_DIR/scripts/04-deploy-session.sh" || warn "Session environment update encountered warnings."

info "Rebuilding desktop shell..."
bash "$BUNDLE_DIR/scripts/08-build-shell.sh" || warn "Shell build reported warnings; operating in QML compatibility mode."

info "Updating autostart and background service units..."
bash "$BUNDLE_DIR/scripts/10-autostart.sh" || warn "Autostart update encountered warnings."

if [[ "${INSTALL_LOCKSCREEN:-false}" == "true" ]]; then
    section "Step 4: Updating Plasma Lock Screen"
    bash "$BUNDLE_DIR/scripts/06-lockscreen.sh" || warn "Lock screen update encountered warnings."
fi

if [[ "${INSTALL_SDDM:-false}" == "true" ]]; then
    section "Step 5: Updating SDDM Greeter Theme"
    bash "$BUNDLE_DIR/scripts/05-sddm-theme.sh" || warn "SDDM theme update encountered warnings."
fi

section "Step 6: Refreshing Desktop Session"

# Restart shell safely without killing user session
if command -v aetherium-autostart >/dev/null 2>&1; then
    info "Triggering graceful shell reload via aetherium-autostart..."
    pkill -f "quickshell.*aetherium/shell.qml" 2>/dev/null || true
    nohup aetherium-autostart >/dev/null 2>&1 &
elif pgrep -f "quickshell.*aetherium" >/dev/null 2>&1; then
    info "Restarting quickshell process..."
    pkill -f "quickshell.*aetherium" 2>/dev/null || true
fi

echo
ok "Aetherium OS updated successfully!"
info "If you updated the SDDM theme, changes will take effect at next login."
echo
