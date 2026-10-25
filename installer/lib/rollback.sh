#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Installer Library: Rollback & Recovery Engine
# ==============================================================================

set -euo pipefail

rollback_installation() {
    log_warn "Executing rollback of Aetherium OS installation..."
    local state_root="${XDG_STATE_HOME:-$HOME/.local/state}/aetherium"
    local manifest="${state_root}/install-manifest.json"

    if [[ ! -f "$manifest" ]]; then
        log_err "No installation manifest found at $manifest. Unable to automatically roll back."
        return 1
    fi

    # Read installed files from manifest and remove them
    if command -v python3 &>/dev/null; then
        python3 - "$manifest" << 'PYEOF'
import sys, json, os, shutil

manifest_path = sys.argv[1]
try:
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for fpath in reversed(data.get("installed_files", [])):
        if os.path.exists(fpath):
            if os.path.isdir(fpath):
                shutil.rmtree(fpath, ignore_errors=True)
            else:
                os.remove(fpath)
            print(f"Removed: {fpath}")
except Exception as e:
    print(f"Rollback file removal warning: {e}", file=sys.stderr)
PYEOF
    fi

    # Revert Plasma Lockscreen to prior state
    local backup_dir
    backup_dir="$(python3 -c "import json; print(json.load(open('$manifest')).get('backup_dir', ''))" 2>/dev/null || true)"
    if [[ -n "$backup_dir" && -f "$backup_dir/plasma_state.txt" ]]; then
        local prev_shell prev_theme
        prev_shell="$(grep -E '^PREVIOUS_SHELL_PACKAGE=' "$backup_dir/plasma_state.txt" | cut -d'=' -f2 || true)"
        prev_theme="$(grep -E '^PREVIOUS_GREETER_THEME=' "$backup_dir/plasma_state.txt" | cut -d'=' -f2 || true)"

        if command -v kwriteconfig6 &>/dev/null; then
            if [[ -n "$prev_shell" ]]; then
                kwriteconfig6 --file plasmashellrc --group "Shell" --key "ShellPackage" "$prev_shell" 2>/dev/null || true
            fi
            if [[ -n "$prev_theme" && "$prev_theme" != "#none" ]]; then
                kwriteconfig6 --file kscreenlockerrc --group "Greeter" --key "Theme" "$prev_theme" 2>/dev/null || true
            else
                kwriteconfig6 --file kscreenlockerrc --group "Greeter" --key "Theme" --delete 2>/dev/null || true
            fi
        fi
        log_step "Reverted KDE Plasma lock screen settings to: $prev_shell"
    fi

    # Revert SDDM drop-in if present
    if [[ -f "/etc/sddm.conf.d/zz-aetherium.conf" ]]; then
        if [[ $EUID -eq 0 ]]; then
            rm -f "/etc/sddm.conf.d/zz-aetherium.conf"
        elif command -v sudo &>/dev/null; then
            sudo rm -f "/etc/sddm.conf.d/zz-aetherium.conf" 2>/dev/null || true
        fi
        log_step "Removed Aetherium SDDM drop-in"
    fi

    log_ok "Rollback sequence completed successfully."
}
