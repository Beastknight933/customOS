#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Installer Subsystem: Uninstall Wrapper
# Bridges to root uninstall.sh while preserving backwards-compatible CLI entry
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
AETHERIUM_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ -f "$AETHERIUM_ROOT/uninstall.sh" ]]; then
    exec bash "$AETHERIUM_ROOT/uninstall.sh" "$@"
fi

echo "  [ERR]   uninstall.sh not found." >&2
exit 1
