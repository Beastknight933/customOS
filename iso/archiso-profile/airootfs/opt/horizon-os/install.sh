#!/usr/bin/env bash
#
# Horizon OS Master Installation Entrypoint
# Automates deployment from Arch Linux live ISO or direct host execution.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/var/log/horizon-install.log"

# Fallback log path if non-root dry-run
if [[ $EUID -ne 0 ]]; then
    LOG_FILE="$SCRIPT_DIR/horizon-install.log"
fi

echo "=========================================================="
echo "  Horizon OS Installer — Singularity Release"
echo "  Arch Linux + KDE Plasma 6 + Caelestia Shell"
echo "=========================================================="
echo "Log file: $LOG_FILE"

# Check for Python 3
if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is required to run the Horizon OS installer." >&2
    exit 1
fi

# Execute the TUI installer
exec python3 "$SCRIPT_DIR/installer/horizon-tui.py" "$@"
