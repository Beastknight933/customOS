#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Installer Subsystem: Update Wrapper
# Bridges to root update.sh while preserving backwards-compatible CLI entry
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
AETHERIUM_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ -f "$AETHERIUM_ROOT/update.sh" ]]; then
    exec bash "$AETHERIUM_ROOT/update.sh" "$@"
fi

echo "  [ERR]   update.sh not found." >&2
exit 1
