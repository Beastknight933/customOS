#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — SDDM Integration Adapter
# Safe, transactional management and verification of SDDM greeter themes
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
THEME_NAME="aetherium"
DEFAULT_THEME_SRC="${SCRIPT_DIR}/../../themes/sddm/${THEME_NAME}"
SYSTEM_THEMES_DIR="/usr/share/sddm/themes"
TARGET_THEME_DIR="${SYSTEM_THEMES_DIR}/${THEME_NAME}"
SDDM_CONF_DIR="/etc/sddm.conf.d"
DROPIN_CONF="${SDDM_CONF_DIR}/zz-aetherium.conf"
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/aetherium/sddm"
BACKUP_FILE="${STATE_DIR}/backup-theme-state.txt"

# Color formatting
C_BLUE='\033[38;2;96;165;250m'
C_CYAN='\033[38;2;45;212;191m'
C_GREEN='\033[38;2;74;222;128m'
C_YELLOW='\033[38;2;251;191;36m'
C_RED='\033[38;2;248;113;113m'
C_DIM='\033[38;2;148;163;184m'
C_RESET='\033[0m'

log_info()  { echo -e "${C_BLUE}[INFO]${C_RESET} $*"; }
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
    if ! command -v sddm &>/dev/null && [[ ! -d "/usr/share/sddm" ]]; then
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

get_current_theme() {
    local theme=""
    if [[ -f "$DROPIN_CONF" ]]; then
        theme="$(grep -E '^[[:space:]]*Current[[:space:]]*=' "$DROPIN_CONF" 2>/dev/null | tail -n 1 | cut -d'=' -f2 | tr -d ' ' || true)"
    fi
    if [[ -z "$theme" ]] && [[ -f "/etc/sddm.conf" ]]; then
        theme="$(grep -E '^[[:space:]]*Current[[:space:]]*=' "/etc/sddm.conf" 2>/dev/null | tail -n 1 | cut -d'=' -f2 | tr -d ' ' || true)"
    fi
    if [[ -z "$theme" ]]; then
        for f in /etc/sddm.conf.d/*.conf /usr/lib/sddm/sddm.conf.d/*.conf; do
            [[ -f "$f" ]] || continue
            [[ "$f" == "$DROPIN_CONF" ]] && continue
            local t
            t="$(grep -E '^[[:space:]]*Current[[:space:]]*=' "$f" 2>/dev/null | tail -n 1 | cut -d'=' -f2 | tr -d ' ' || true)"
            if [[ -n "$t" ]]; then
                theme="$t"
                break
            fi
        done
    fi
    printf '%s' "${theme:-breeze}"
}

verify_theme() {
    local src_dir="${1:-$DEFAULT_THEME_SRC}"
    log_info "Verifying SDDM theme at: $src_dir"

    local missing=0
    for req in "metadata.desktop" "theme.conf" "Main.qml"; do
        if [[ ! -f "$src_dir/$req" ]]; then
            log_err "Missing mandatory theme component: $req"
            missing=$((missing + 1))
        fi
    done

    # Check QtVersion in metadata.desktop
    if [[ -f "$src_dir/metadata.desktop" ]]; then
        local qtv
        qtv="$(grep -E '^[[:space:]]*QtVersion[[:space:]]*=' "$src_dir/metadata.desktop" | cut -d'=' -f2 | tr -d ' ' || true)"
        if [[ "$qtv" != "6" ]]; then
            log_warn "Theme declares QtVersion='$qtv', target standard is QtVersion=6."
        else
            log_ok "Theme declares QtVersion=6 compatibility."
        fi
    fi

    # Greeter check
    local greeter
    greeter="$(find_qt6_greeter)"
    if [[ -z "$greeter" ]]; then
        log_warn "No SDDM Qt6 greeter binary detected. Install qt6-declarative or sddm with Qt6 support."
    else
        log_ok "Greeter binary detected: $greeter"
    fi

    if [[ $missing -gt 0 ]]; then
        log_err "Theme verification failed with $missing missing file(s)."
        return 1
    fi

    log_ok "Theme verification successful."
    return 0
}

backup_state() {
    mkdir -p "$STATE_DIR"
    local curr
    curr="$(get_current_theme)"
    log_info "Recording pre-installation SDDM theme: '$curr'"
    cat > "$BACKUP_FILE" << EOF
PREVIOUS_THEME=${curr}
TIMESTAMP=$(date +%Y-%m-%dT%H:%M:%S)
DROPIN_WAS_PRESENT=$([[ -f "$DROPIN_CONF" ]] && echo "1" || echo "0")
EOF
    log_ok "Theme state preserved in: $BACKUP_FILE"
}

install_theme() {
    local src_dir="${1:-$DEFAULT_THEME_SRC}"
    require_root

    verify_theme "$src_dir" || {
        log_err "Pre-installation verification failed. Aborting installation."
        exit 1
    }

    backup_state

    log_info "Deploying theme files to ${TARGET_THEME_DIR}..."
    mkdir -p "$SYSTEM_THEMES_DIR"
    rm -rf "$TARGET_THEME_DIR"
    mkdir -p "$TARGET_THEME_DIR"
    cp -r "$src_dir"/* "$TARGET_THEME_DIR/"

    find "$TARGET_THEME_DIR" -type d -exec chmod 755 {} +
    find "$TARGET_THEME_DIR" -type f -exec chmod 644 {} +

    log_ok "Theme assets copied and permissions established."

    log_info "Activating SDDM configuration drop-in at ${DROPIN_CONF}..."
    mkdir -p "$SDDM_CONF_DIR"
    cat > "$DROPIN_CONF" << EOF
[General]
GreeterEnvironment=QML_XHR_ALLOW_FILE_READ=1

[Theme]
Current=${THEME_NAME}
EOF
    chmod 644 "$DROPIN_CONF"
    log_ok "Aetherium SDDM theme activated successfully."
}

rollback_or_uninstall() {
    require_root
    log_info "Reverting Aetherium SDDM configuration..."

    if [[ -f "$DROPIN_CONF" ]]; then
        rm -f "$DROPIN_CONF"
        log_ok "Removed drop-in: $DROPIN_CONF"
    fi

    if [[ -f "$BACKUP_FILE" ]]; then
        local prev
        prev="$(grep -E '^PREVIOUS_THEME=' "$BACKUP_FILE" | cut -d'=' -f2 || true)"
        if [[ -n "$prev" && "$prev" != "$THEME_NAME" ]]; then
            log_info "Restoring previous theme: '$prev'"
            if command -v kwriteconfig6 &>/dev/null; then
                kwriteconfig6 --file /etc/sddm.conf --group Theme --key Current "$prev" 2>/dev/null || true
            fi
        fi
    fi

    if [[ -d "$TARGET_THEME_DIR" ]]; then
        rm -rf "$TARGET_THEME_DIR"
        log_ok "Removed theme folder: $TARGET_THEME_DIR"
    fi

    log_ok "SDDM restoration completed."
}

show_status() {
    log_info "=== Aetherium SDDM Status ==="
    echo "  Installed Theme Path : $TARGET_THEME_DIR"
    echo "  Theme Exists         : $([[ -d "$TARGET_THEME_DIR" ]] && echo "Yes" || echo "No")"
    echo "  Active SDDM Theme    : $(get_current_theme)"
    echo "  Drop-in File         : $([[ -f "$DROPIN_CONF" ]] && echo "Active ($DROPIN_CONF)" || echo "None")"
    echo "  Qt6 Greeter Binary   : $(find_qt6_greeter)"
    echo "  Backup State Exists  : $([[ -f "$BACKUP_FILE" ]] && echo "Yes ($BACKUP_FILE)" || echo "No")"
}

case "${1:-status}" in
    --install|-i)
        install_theme "${2:-$DEFAULT_THEME_SRC}"
        ;;
    --verify|-v)
        verify_theme "${2:-$DEFAULT_THEME_SRC}"
        ;;
    --rollback|-r|--uninstall|-u)
        rollback_or_uninstall
        ;;
    --status|-s|status)
        show_status
        ;;
    *)
        echo "Usage: $0 [--install [path] | --verify [path] | --rollback | --status]"
        exit 1
        ;;
esac
