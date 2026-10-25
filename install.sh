#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Primary Installation Entry Point
# Supports direct checkout execution (bash install.sh) and piped curl execution
# ==============================================================================

set -euo pipefail

# Redirect TTY if run via curl ... | bash
if [ ! -t 0 ]; then
    REAL_TTY=""
    if [ -t 1 ]; then
        REAL_TTY=$(tty 0>&1 2>/dev/null || true)
    elif [ -t 2 ]; then
        REAL_TTY=$(tty 0>&2 2>/dev/null || true)
    fi

    if [ -z "$REAL_TTY" ] || [ "$REAL_TTY" = "not a tty" ]; then
        _CTTY=$(ps -p $$ -o tty= 2>/dev/null | awk '{print $1}' || true)
        if [ -n "$_CTTY" ] && [ "$_CTTY" != "?" ]; then
            case "$_CTTY" in
                /*) REAL_TTY="$_CTTY" ;;
                *)  REAL_TTY="/dev/$_CTTY" ;;
            esac
        fi
    fi

    if [ -n "$REAL_TTY" ] && [ "$REAL_TTY" != "not a tty" ] && [ -c "$REAL_TTY" ]; then
        exec 0<>"$REAL_TTY" 1<>"$REAL_TTY" 2<>"$REAL_TTY"
    elif [ -c /dev/tty ]; then
        exec 0<>/dev/tty
    fi
fi

unset CDPATH
SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"

# Run setup from this checkout
if [ -f "$SCRIPT_DIR/scripts/setup.sh" ]; then
    exec bash "$SCRIPT_DIR/scripts/setup.sh" "$@"
fi

# Fallback to installer directory if present
if [ -f "$SCRIPT_DIR/installer/install.sh" ]; then
    exec bash "$SCRIPT_DIR/installer/install.sh" "$@"
fi

echo "  [ERR]   Could not locate scripts/setup.sh in $SCRIPT_DIR" >&2
exit 1
