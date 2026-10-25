#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Installer Library: Transactional Backup Engine (Hardened)
# ==============================================================================

set -euo pipefail

STATE_ROOT="${XDG_STATE_HOME:-$HOME/.local/state}/aetherium"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="${STATE_ROOT}/backups/backup-${TIMESTAMP}"
MANIFEST_FILE="${STATE_ROOT}/install-manifest.json"

init_backup() {
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$STATE_ROOT"
    log_info "Initializing pre-installation snapshot at: $BACKUP_DIR"

    # Backup existing configuration directories if present
    local config_existed=0
    if [[ -d "$HOME/.config/aetherium" ]]; then
        cp -a "$HOME/.config/aetherium" "$BACKUP_DIR/config_aetherium"
        config_existed=1
        log_step "Preserved existing ~/.config/aetherium"
    fi

    # Backup exact KDE Plasma config files
    local plasmashellrc_existed=0
    local prev_shell=""
    local shell_was_set=0
    if [[ -f "$HOME/.config/plasmashellrc" ]]; then
        cp -a "$HOME/.config/plasmashellrc" "$BACKUP_DIR/plasmashellrc"
        plasmashellrc_existed=1
    fi
    if command -v kreadconfig6 &>/dev/null; then
        prev_shell="$(kreadconfig6 --file plasmashellrc --group "Shell" --key "ShellPackage" 2>/dev/null || true)"
        if [[ -n "$prev_shell" ]]; then
            shell_was_set=1
        fi
    fi

    local kscreenlockerrc_existed=0
    local prev_theme=""
    local theme_was_set=0
    if [[ -f "$HOME/.config/kscreenlockerrc" ]]; then
        cp -a "$HOME/.config/kscreenlockerrc" "$BACKUP_DIR/kscreenlockerrc"
        kscreenlockerrc_existed=1
    fi
    if command -v kreadconfig6 &>/dev/null; then
        prev_theme="$(kreadconfig6 --file kscreenlockerrc --group "Greeter" --key "Theme" 2>/dev/null || true)"
        if [[ -n "$prev_theme" ]]; then
            theme_was_set=1
        fi
    fi

    # Backup existing environment and session files if present
    local env_conf_existed=0
    if [[ -f "$HOME/.config/environment.d/aetherium.conf" ]]; then
        cp -a "$HOME/.config/environment.d/aetherium.conf" "$BACKUP_DIR/aetherium-env.conf"
        env_conf_existed=1
    fi

    local plasma_env_existed=0
    if [[ -f "$HOME/.config/plasma-workspace/env/aetherium.sh" ]]; then
        cp -a "$HOME/.config/plasma-workspace/env/aetherium.sh" "$BACKUP_DIR/aetherium-plasma-env.sh"
        plasma_env_existed=1
    fi

    # Initialize structured JSON manifest
    cat > "$MANIFEST_FILE" << EOF
{
  "version": "1.1",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "backup_dir": "${BACKUP_DIR}",
  "profile": "${PROFILE:-unknown}",
  "plasma_state": {
    "plasmashellrc_existed": ${plasmashellrc_existed},
    "shell_package": "${prev_shell}",
    "shell_package_was_set": ${shell_was_set},
    "kscreenlockerrc_existed": ${kscreenlockerrc_existed},
    "greeter_theme": "${prev_theme}",
    "greeter_theme_was_set": ${theme_was_set}
  },
  "tracked_items": []
}
EOF
    log_ok "Backup initialized and manifest created: $MANIFEST_FILE"
}

track_target() {
    local target_path="$1"
    local action="${2:-created}" # created | modified
    local existed_before=0
    local backup_item=""

    if [[ -e "$target_path" ]]; then
        existed_before=1
        local rel_name
        rel_name="$(echo "$target_path" | tr '/' '_')"
        backup_item="${BACKUP_DIR}/item${rel_name}"
        if [[ -d "$target_path" ]]; then
            cp -a "$target_path" "$backup_item"
        else
            cp -a "$target_path" "$backup_item"
        fi
    fi

    # Update manifest via Python
    if command -v python3 &>/dev/null; then
        python3 - "$MANIFEST_FILE" "$target_path" "$action" "$existed_before" "$backup_item" << 'PYEOF'
import sys, json

manifest_path, target, action, existed_str, bkp = sys.argv[1:6]
existed = (existed_str == "1")

try:
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Avoid duplicate entries
    existing_targets = [x["target"] for x in data.get("tracked_items", [])]
    if target not in existing_targets:
        data.setdefault("tracked_items", []).append({
            "target": target,
            "action": action,
            "existed_before": existed,
            "backup_path": bkp if existed else None
        })

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
except Exception:
    pass
PYEOF
    fi
}
