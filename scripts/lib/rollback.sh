#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Installer Library: Rollback & Recovery Engine (Hardened)
# Restores previous system and user state with strict path safety validation
# ==============================================================================

set -euo pipefail

rollback_installation() {
    log_warn "Executing transactional rollback of Aetherium OS installation..."
    local state_root="${XDG_STATE_HOME:-$HOME/.local/state}/aetherium"
    local manifest="${state_root}/install-manifest.json"

    if [[ ! -f "$manifest" ]]; then
        log_err "No installation manifest found at $manifest. Unable to automatically roll back."
        return 1
    fi

    # Execute safe restoration using Python with strict path whitelist checking
    python3 - "$manifest" << 'PYEOF'
import sys, json, os, shutil

manifest_path = sys.argv[1]
try:
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception as e:
    print(f"Error reading manifest: {e}", file=sys.stderr)
    sys.exit(1)

home = os.path.expanduser("~")
allowed_prefixes = [
    os.path.join(home, ".config", "aetherium"),
    os.path.join(home, ".config", "autostart", "aetherium-"),
    os.path.join(home, ".config", "environment.d", "aetherium.conf"),
    os.path.join(home, ".config", "plasma-workspace", "env", "aetherium.sh"),
    os.path.join(home, ".local", "bin", "aetherium-"),
    os.path.join(home, ".local", "share", "plasma", "shells", "aetherium.desktop"),
    "/usr/share/sddm/themes/aetherium",
    "/etc/sddm.conf.d/zz-aetherium.conf"
]

def is_safe_target(path: str) -> bool:
    norm = os.path.normpath(os.path.abspath(path))
    # Disallow path traversal
    if ".." in path.split(os.sep):
        return False
    # Must match at least one allowed prefix
    for pref in allowed_prefixes:
        norm_pref = os.path.normpath(os.path.abspath(pref))
        if norm == norm_pref or norm.startswith(norm_pref):
            return True
    return False

# 1. Process tracked items in reverse order
tracked = data.get("tracked_items", [])
for item in reversed(tracked):
    target = item.get("target")
    if not target:
        continue

    if not is_safe_target(target):
        print(f"SECURITY WARNING: Target '{target}' outside allowed prefixes. Skipping deletion.", file=sys.stderr)
        continue

    existed = item.get("existed_before", False)
    backup_path = item.get("backup_path")

    if existed and backup_path and os.path.exists(backup_path):
        # Restore pre-existing file or directory
        try:
            if os.path.isdir(backup_path):
                if os.path.exists(target):
                    shutil.rmtree(target, ignore_errors=True)
                shutil.copytree(backup_path, target)
            else:
                shutil.copy2(backup_path, target)
            print(f"Restored original: {target}")
        except Exception as e:
            print(f"Warning: Failed to restore {target}: {e}", file=sys.stderr)
    elif not existed and os.path.exists(target):
        # Cleanly remove newly created item
        try:
            if os.path.isdir(target):
                shutil.rmtree(target, ignore_errors=True)
            else:
                os.remove(target)
            print(f"Removed Aetherium file: {target}")
        except Exception as e:
            print(f"Warning: Failed to remove {target}: {e}", file=sys.stderr)

# 2. Revert exact plasma configs if backup files exist
backup_dir = data.get("backup_dir")
if backup_dir and os.path.exists(backup_dir):
    for f in ["plasmashellrc", "kscreenlockerrc"]:
        bkp_f = os.path.join(backup_dir, f)
        target_f = os.path.join(home, ".config", f)
        if os.path.exists(bkp_f):
            try:
                shutil.copy2(bkp_f, target_f)
                print(f"Restored exact configuration file: {target_f}")
            except Exception as e:
                print(f"Warning: Failed to restore {target_f}: {e}", file=sys.stderr)

PYEOF

    # 3. Precise KConfig key restoration
    local backup_dir
    backup_dir="$(python3 -c "import json; print(json.load(open('$manifest')).get('backup_dir', ''))" 2>/dev/null || true)"
    if command -v kwriteconfig6 &>/dev/null; then
        local shell_was_set shell_package theme_was_set greeter_theme
        shell_was_set="$(python3 -c "import json; print(json.load(open('$manifest')).get('plasma_state', {}).get('shell_package_was_set', 0))" 2>/dev/null || true)"
        shell_package="$(python3 -c "import json; print(json.load(open('$manifest')).get('plasma_state', {}).get('shell_package', ''))" 2>/dev/null || true)"
        theme_was_set="$(python3 -c "import json; print(json.load(open('$manifest')).get('plasma_state', {}).get('greeter_theme_was_set', 0))" 2>/dev/null || true)"
        greeter_theme="$(python3 -c "import json; print(json.load(open('$manifest')).get('plasma_state', {}).get('greeter_theme', ''))" 2>/dev/null || true)"

        if [[ "$shell_was_set" == "1" && -n "$shell_package" ]]; then
            kwriteconfig6 --file plasmashellrc --group "Shell" --key "ShellPackage" "$shell_package" 2>/dev/null || true
            log_step "Restored ShellPackage key to '$shell_package'"
        else
            kwriteconfig6 --file plasmashellrc --group "Shell" --key "ShellPackage" --delete 2>/dev/null || true
            log_step "Deleted ShellPackage override (reverted to KDE default)"
        fi

        if [[ "$theme_was_set" == "1" && -n "$greeter_theme" ]]; then
            kwriteconfig6 --file kscreenlockerrc --group "Greeter" --key "Theme" "$greeter_theme" 2>/dev/null || true
            log_step "Restored lock screen Theme key to '$greeter_theme'"
        else
            kwriteconfig6 --file kscreenlockerrc --group "Greeter" --key "Theme" --delete 2>/dev/null || true
            log_step "Deleted lock screen Theme override"
        fi
    fi

    # 4. Rollback SDDM Theme if installed
    local sddm_adapter="${SCRIPT_DIR}/../../core/sddm-adapter/aetherium-sddm-adapter.sh"
    if [[ -x "$sddm_adapter" && -f "/etc/sddm.conf.d/zz-aetherium.conf" ]]; then
        log_info "Invoking SDDM adapter rollback..."
        bash "$sddm_adapter" --rollback 2>/dev/null || true
    fi

    log_ok "Transactional rollback sequence completed successfully."
}
