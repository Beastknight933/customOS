#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — SDDM Integration Adapter (Safety Hardened)
# Transactional, staged deployment and reliable rollback of SDDM greeter themes
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
THEME_NAME="aetherium"
DEFAULT_THEME_SRC="${SCRIPT_DIR}/../../themes/sddm/${THEME_NAME}"
SYSTEM_THEMES_DIR="/usr/share/sddm/themes"
TARGET_THEME_DIR="${SYSTEM_THEMES_DIR}/${THEME_NAME}"
SDDM_CONF_DIR="/etc/sddm.conf.d"
DROPIN_CONF="${SDDM_CONF_DIR}/zz-aetherium.conf"

# State and backup directory
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/aetherium/sddm"
BACKUP_MANIFEST="${STATE_DIR}/backup-manifest.json"

# Color formatting
C_BLUE='\033[38;2;96;165;250m'
C_CYAN='\033[38;2;45;212;191m'
C_GREEN='\033[38;2;74;222;128m'
C_YELLOW='\033[38;2;251;191;36m'
C_RED='\033[38;2;248;113;113m'
C_DIM='\033[38;2;148;163;184m'
C_RESET='\033[0m'

log_info()  { echo -e "${C_BLUE}[INFO]${C_RESET} $*"; }
log_step()  { echo -e "${C_CYAN}[STEP]${C_RESET} $*"; }
log_ok()    { echo -e "${C_GREEN}[OK]${C_RESET} $*"; }
log_warn()  { echo -e "${C_YELLOW}[WARN]${C_RESET} $*"; }
log_err()   { echo -e "${C_RED}[ERROR]${C_RESET} $*" >&2; }

require_root() {
    if [[ $EUID -ne 0 ]]; then
        if command -v sudo &>/dev/null; then
            exec sudo bash "$0" "$@"
        else
            log_err "Elevated privileges (root or sudo) required for SDDM operations."
            exit 1
        fi
    fi
}

detect_sddm() {
    if ! command -v sddm &>/dev/null && [[ ! -d "$SYSTEM_THEMES_DIR" ]]; then
        log_warn "SDDM does not appear to be installed on this system."
        return 1
    fi
    return 0
}

find_qt6_greeter() {
    local greeter=""
    for bin in sddm-greeter-qt6 /usr/lib/sddm/sddm-greeter-qt6 /usr/libexec/sddm/sddm-greeter-qt6 sddm-greeter; do
        if command -v "$bin" &>/dev/null || [[ -x "$bin" ]]; then
            greeter="$bin"
            break
        fi
    done
    printf '%s' "$greeter"
}

get_current_theme_info() {
    local theme=""
    local source_file="default"

    # Precedence 1: User/Admin Drop-in files in /etc/sddm.conf.d/ (reverse alphanumerical)
    if [[ -d "$SDDM_CONF_DIR" ]]; then
        # Check files other than zz-aetherium if we want to know what was active before us
        for f in $(find "$SDDM_CONF_DIR" -maxdepth 1 -name "*.conf" 2>/dev/null | sort -r); do
            [[ "$f" == "$DROPIN_CONF" ]] && continue
            local t
            t="$(grep -E '^[[:space:]]*Current[[:space:]]*=' "$f" 2>/dev/null | tail -n 1 | cut -d'=' -f2 | tr -d ' ' || true)"
            if [[ -n "$t" ]]; then
                theme="$t"
                source_file="$f"
                break
            fi
        done
    fi

    # Precedence 2: Legacy system configuration in /etc/sddm.conf
    if [[ -z "$theme" && -f "/etc/sddm.conf" ]]; then
        local t
        t="$(grep -E '^[[:space:]]*Current[[:space:]]*=' "/etc/sddm.conf" 2>/dev/null | tail -n 1 | cut -d'=' -f2 | tr -d ' ' || true)"
        if [[ -n "$t" ]]; then
            theme="$t"
            source_file="/etc/sddm.conf"
        fi
    fi

    # Precedence 3: Distribution vendor drop-ins in /usr/lib/sddm/sddm.conf.d/
    if [[ -z "$theme" && -d "/usr/lib/sddm/sddm.conf.d" ]]; then
        for f in $(find "/usr/lib/sddm/sddm.conf.d" -maxdepth 1 -name "*.conf" 2>/dev/null | sort -r); do
            local t
            t="$(grep -E '^[[:space:]]*Current[[:space:]]*=' "$f" 2>/dev/null | tail -n 1 | cut -d'=' -f2 | tr -d ' ' || true)"
            if [[ -n "$t" ]]; then
                theme="$t"
                source_file="$f"
                break
            fi
        done
    fi

    printf '%s|%s' "${theme:-breeze}" "$source_file"
}

validate_theme_directory() {
    local dir="$1"
    local missing=0

    for req in "metadata.desktop" "theme.conf" "Main.qml"; do
        if [[ ! -f "$dir/$req" ]]; then
            log_err "Missing mandatory theme component in $dir: $req"
            missing=$((missing + 1))
        fi
    done

    # Validate QtVersion=6 in metadata.desktop
    if [[ -f "$dir/metadata.desktop" ]]; then
        local qtv
        qtv="$(grep -E '^[[:space:]]*QtVersion[[:space:]]*=' "$dir/metadata.desktop" | cut -d'=' -f2 | tr -d ' ' || true)"
        if [[ "$qtv" != "6" ]]; then
            log_warn "metadata.desktop does not specify QtVersion=6 (found: '${qtv}'). Theme may fail under Qt 6 greeters."
        fi
    fi

    # Check greeter binary
    local greeter
    greeter="$(find_qt6_greeter)"
    if [[ -z "$greeter" ]]; then
        log_warn "No SDDM Qt6 greeter binary detected on system."
    fi

    if [[ $missing -gt 0 ]]; then
        return 1
    fi
    return 0
}

backup_pre_installation_state() {
    mkdir -p "$STATE_DIR"
    local theme_info
    theme_info="$(get_current_theme_info)"
    local prev_theme="${theme_info%%|*}"
    local prev_source="${theme_info##*|}"

    local timestamp
    timestamp="$(date +%Y%m%d_%H%M%S)"
    local theme_backup_dir="${STATE_DIR}/backups/theme-aetherium-${timestamp}"

    # Preserve existing theme directory if present
    local theme_existed=0
    if [[ -d "$TARGET_THEME_DIR" ]]; then
        log_step "Preserving existing theme at $TARGET_THEME_DIR -> $theme_backup_dir"
        mkdir -p "$theme_backup_dir"
        cp -a "$TARGET_THEME_DIR"/* "$theme_backup_dir/"
        theme_existed=1
    fi

    # Preserve drop-in state
    local dropin_existed=0
    local dropin_backup="${STATE_DIR}/backups/dropin-${timestamp}.conf"
    if [[ -f "$DROPIN_CONF" ]]; then
        mkdir -p "$(dirname "$dropin_backup")"
        cp -a "$DROPIN_CONF" "$dropin_backup"
        dropin_existed=1
    fi

    cat > "$BACKUP_MANIFEST" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "previous_theme": "${prev_theme}",
  "previous_source": "${prev_source}",
  "target_theme_dir": "${TARGET_THEME_DIR}",
  "theme_existed_before": ${theme_existed},
  "theme_backup_dir": "$([[ $theme_existed -eq 1 ]] && echo "$theme_backup_dir" || echo "")",
  "dropin_conf": "${DROPIN_CONF}",
  "dropin_existed_before": ${dropin_existed},
  "dropin_backup": "$([[ $dropin_existed -eq 1 ]] && echo "$dropin_backup" || echo "")"
}
EOF
    log_ok "Pre-installation state recorded in: $BACKUP_MANIFEST"
}

staged_install_theme() {
    local src_dir="${1:-$DEFAULT_THEME_SRC}"
    THEME_NAME="$(basename "$src_dir")"
    TARGET_THEME_DIR="${SYSTEM_THEMES_DIR}/${THEME_NAME}"
    require_root

    log_info "Step 1/5: Validating source theme files at: $src_dir"
    validate_theme_directory "$src_dir" || {
        log_err "Source theme validation failed. Aborting installation."
        exit 1
    }

    log_info "Step 2/5: Creating transactional backup of existing SDDM state..."
    backup_pre_installation_state

    # Stage files on the same filesystem
    mkdir -p "$SYSTEM_THEMES_DIR"
    local staging_dir="${SYSTEM_THEMES_DIR}/.aetherium.staging-$$"
    local backup_old_dir="${SYSTEM_THEMES_DIR}/.aetherium.old-$$"
    rm -rf "$staging_dir" "$backup_old_dir"

    log_info "Step 3/5: Staging theme files in $staging_dir..."
    mkdir -p "$staging_dir"
    cp -r "$src_dir"/* "$staging_dir/"

    # Set canonical permissions in staging
    find "$staging_dir" -type d -exec chmod 755 {} +
    find "$staging_dir" -type f -exec chmod 644 {} +

    log_step "Verifying staged files..."
    if ! validate_theme_directory "$staging_dir"; then
        log_err "Staged theme validation failed. Cleaning up staging without modifying active theme."
        rm -rf "$staging_dir"
        exit 1
    fi

    log_info "Step 4/5: Atomically swapping staged theme to $TARGET_THEME_DIR..."
    if [[ -d "$TARGET_THEME_DIR" ]]; then
        mv "$TARGET_THEME_DIR" "$backup_old_dir"
    fi

    if mv "$staging_dir" "$TARGET_THEME_DIR"; then
        # Swap succeeded; remove temporary old directory
        rm -rf "$backup_old_dir"
        log_ok "Theme directory deployed successfully."
    else
        log_err "Swap failed. Restoring original theme directory..."
        if [[ -d "$backup_old_dir" ]]; then
            mv "$backup_old_dir" "$TARGET_THEME_DIR"
        fi
        rm -rf "$staging_dir"
        exit 1
    fi

    log_info "Step 5/5: Configuring SDDM drop-in configuration at $DROPIN_CONF..."
    mkdir -p "$SDDM_CONF_DIR"
    cat > "$DROPIN_CONF" << EOF
# Generated by Aetherium OS SDDM Integration Adapter
[General]
GreeterEnvironment=QML_XHR_ALLOW_FILE_READ=1

[Theme]
Current=${THEME_NAME}
EOF
    chmod 644 "$DROPIN_CONF"
    log_ok "Aetherium SDDM theme activated via drop-in configuration."
}

safe_rollback() {
    require_root
    log_info "Initiating safe rollback of Aetherium SDDM configuration..."

    if [[ ! -f "$BACKUP_MANIFEST" ]]; then
        log_warn "No backup manifest found at $BACKUP_MANIFEST."
        log_info "Falling back to standard removal of Aetherium drop-in..."
        rm -f "$DROPIN_CONF"
        if [[ -d "$TARGET_THEME_DIR" ]]; then
            rm -rf "$TARGET_THEME_DIR"
        fi
        log_ok "Aetherium drop-in and theme directory removed."
        return 0
    fi

    # Parse manifest using Python
    python3 - "$BACKUP_MANIFEST" << 'PYEOF'
import sys, json, os, shutil

manifest_path = sys.argv[1]
try:
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    dropin_conf = data.get("dropin_conf")
    dropin_existed = data.get("dropin_existed_before", False)
    dropin_backup = data.get("dropin_backup")

    target_dir = data.get("target_theme_dir")
    theme_existed = data.get("theme_existed_before", False)
    theme_backup = data.get("theme_backup_dir")

    # Restore or delete drop-in
    if dropin_conf:
        if dropin_existed and dropin_backup and os.path.exists(dropin_backup):
            shutil.copy2(dropin_backup, dropin_conf)
            print(f"Restored original drop-in config: {dropin_conf}")
        elif os.path.exists(dropin_conf):
            os.remove(dropin_conf)
            print(f"Removed Aetherium drop-in: {dropin_conf}")

    # Restore or delete theme directory
    if target_dir:
        if theme_existed and theme_backup and os.path.exists(theme_backup):
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir, ignore_errors=True)
            shutil.copytree(theme_backup, target_dir)
            print(f"Restored original theme directory: {target_dir}")
        elif os.path.exists(target_dir):
            shutil.rmtree(target_dir, ignore_errors=True)
            print(f"Removed Aetherium theme directory: {target_dir}")

except Exception as e:
    print(f"Rollback error: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF

    log_ok "SDDM restoration completed successfully."
}

show_status() {
    log_info "=== Aetherium SDDM Integration Status ==="
    echo "  Installed Theme Path : $TARGET_THEME_DIR"
    echo "  Theme Exists         : $([[ -d "$TARGET_THEME_DIR" ]] && echo "Yes" || echo "No")"
    
    local info
    info="$(get_current_theme_info)"
    echo "  Resolved Theme       : ${info%%|*} (from ${info##*|})"
    echo "  Drop-in Active       : $([[ -f "$DROPIN_CONF" ]] && echo "Yes ($DROPIN_CONF)" || echo "No")"
    echo "  Qt6 Greeter Binary   : $(find_qt6_greeter)"
    echo "  Backup Manifest      : $([[ -f "$BACKUP_MANIFEST" ]] && echo "Yes ($BACKUP_MANIFEST)" || echo "None")"
    echo
}

case "${1:-status}" in
    --install|-i)
        staged_install_theme "${2:-$DEFAULT_THEME_SRC}"
        ;;
    --verify|-v)
        validate_theme_directory "${2:-$DEFAULT_THEME_SRC}"
        ;;
    --rollback|-r|--uninstall|-u)
        safe_rollback
        ;;
    --status|-s|status)
        show_status
        ;;
    *)
        echo "Usage: $0 [--install [src_path] | --verify [src_path] | --rollback | --status]"
        exit 1
        ;;
esac
