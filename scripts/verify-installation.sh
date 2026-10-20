#!/usr/bin/env bash
# Horizon OS - Installation Verification & Compliance Audit
set -euo pipefail

TARGET_ROOT="${1:-/}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================================="
echo "  Horizon OS — Post-Installation Verification Audit"
echo "  Target: $TARGET_ROOT"
echo "=========================================================="

python3 "$REPO_ROOT/installer/horizon-tui.py" --target "$TARGET_ROOT" --verify-only
