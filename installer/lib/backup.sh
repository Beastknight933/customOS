#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Installer Library: Transactional Backup Engine
# ==============================================================================

set -euo pipefail

STATE_ROOT="${XDG_STATE_HOME:-$HOME/.local/state}/aetherium"
BACKUP_DIR="${STATE_ROOT}/backups/backup-$(date +%Y%m%d_%H%M%S)"
MANIFEST_FILE="${STATE_ROOT}/install-manifest.json"

init_backup() {
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$STATE_ROOT"
    log_info "Initializing transaction backup directory at: $BACKUP_DIR"

    # Backup existing configuration directories if present
    if [[ -d "$HOME/.config/aetherium" ]]; then
        cp -r "$HOME/.config/aetherium" "$BACKUP_DIR/config_aetherium"
        log_step "Archived pre-existing ~/.config/aetherium"
    fi

    # Backup KDE Plasma shell and lockscreen keys
    if command -v kreadconfig6 &>/dev/null; then
        local prev_shell prev_theme
        prev_shell="$(kreadconfig6 --file plasmashellrc --group "Shell" --key "ShellPackage" 2>/dev/null || true)"
        prev_theme="$(kreadconfig6 --file kscreenlockerrc --group "Greeter" --key "Theme" 2>/dev/null || true)"
        cat > "$BACKUP_DIR/plasma_state.txt" << EOF
PREVIOUS_SHELL_PACKAGE=${prev_shell:-org.kde.plasma.desktop}
PREVIOUS_GREETER_THEME=${prev_theme:-#none}
EOF
        log_step "Archived KDE Plasma shell & lock screen configuration keys"
    fi

    # Backup SDDM configuration state if SDDM is installed
    if [[ -f "/etc/sddm.conf" ]]; then
        cp "/etc/sddm.conf" "$BACKUP_DIR/sddm.conf" 2>/dev/null || true
    fi
    if [[ -f "/etc/sddm.conf.d/zz-aetherium.conf" ]]; then
        cp "/etc/sddm.conf.d/zz-aetherium.conf" "$BACKUP_DIR/zz-aetherium.conf" 2>/dev/null || true
    fi

    # Initialize empty install manifest
    cat > "$MANIFEST_FILE" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "backup_dir": "$BACKUP_DIR",
  "installed_files": [],
  "modified_configs": []
}
EOF
    log_ok "Backup initialized and state manifest generated."
}

record_installed_file() {
    local file_path="$1"
    if [[ -f "$MANIFEST_FILE" ]] && command -v python3 &>/dev/null; then
        python3 - "$MANIFEST_FILE" "$file_path" << 'PYEOF'
import sys, json, os

manifest_path, target = sys.argv[1], sys.argv[2]
try:
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if target not in data["installed_files"]:
        data["installed_files"].append(target)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
except Exception:
    pass
PYEOF
    fi
}
