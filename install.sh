#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Primary Installation Entry Point
# Supports direct checkout execution (bash install.sh) and piped curl execution:
#   curl -fsSL https://raw.githubusercontent.com/Beastknight933/customOS/main/install.sh | bash
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
    else
        echo "  [ERR]   stdin is not a terminal and no TTY is available." >&2
        echo "  [INFO]  Please run the installer directly: bash install.sh" >&2
        exit 1
    fi
fi

REPO="${AETHERIUM_REPO:-https://github.com/Beastknight933/customOS.git}"
BRANCH="${AETHERIUM_BRANCH:-main}"
DEST="${AETHERIUM_DIR:-$HOME/customOS}"

unset CDPATH
SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"

# Run setup from this checkout if available
if [ -f "$SCRIPT_DIR/scripts/setup.sh" ]; then
    if [ ! -t 0 ] && [ -c /dev/tty ]; then
        exec bash "$SCRIPT_DIR/scripts/setup.sh" </dev/tty "$@"
    fi
    exec bash "$SCRIPT_DIR/scripts/setup.sh" "$@"
fi

# Fallback to installer directory in local checkout if present
if [ -f "$SCRIPT_DIR/installer/install.sh" ]; then
    exec bash "$SCRIPT_DIR/installer/install.sh" "$@"
fi

# Piped remote execution: clone or update repository
if ! command -v git >/dev/null 2>&1; then
    echo "  [ERR]   git is required for installation but not installed." >&2
    exit 1
fi

if [ -d "$DEST/.git" ]; then
    echo "  [INFO]  Updating existing checkout at $DEST..."
    git -C "$DEST" pull --ff-only --recurse-submodules 2>/dev/null || {
        echo "  [WARN]  git pull encountered warnings; proceeding with existing checkout." >&2
    }
elif [ -e "$DEST" ]; then
    echo "  [ERR]   $DEST already exists and is not a git repository; aborting." >&2
    exit 1
else
    echo "  [INFO]  Cloning Aetherium OS from $REPO ($BRANCH) into $DEST..."
    git clone -b "$BRANCH" --single-branch --depth 1 --recurse-submodules "$REPO" "$DEST"
fi

if [ -f "$DEST/scripts/setup.sh" ]; then
    if [ ! -t 0 ] && [ -c /dev/tty ]; then
        exec bash "$DEST/scripts/setup.sh" </dev/tty "$@"
    fi
    exec bash "$DEST/scripts/setup.sh" "$@"
fi

echo "  [ERR]   Could not locate scripts/setup.sh in $DEST" >&2
exit 1
