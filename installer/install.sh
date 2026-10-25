#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Installer Subsystem: Install Wrapper
# Bridges to scripts/setup.sh while preserving backwards-compatible CLI entry
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
AETHERIUM_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ -f "$AETHERIUM_ROOT/scripts/setup.sh" ]]; then
    exec bash "$AETHERIUM_ROOT/scripts/setup.sh" "$@"
fi

echo "  [ERR]   scripts/setup.sh not found." >&2
exit 1
