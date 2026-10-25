#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Step 03: Deploy Configurations & Design Tokens
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=scripts/lib/log.sh
source "$SCRIPT_DIR/lib/log.sh"
# shellcheck source=scripts/lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"
# shellcheck source=scripts/lib/backup.sh
source "$SCRIPT_DIR/lib/backup.sh"

info "Deploying Aetherium configuration files and design tokens..."

CFG_TARGET="$HOME/.config/aetherium"
mkdir -p "$CFG_TARGET" "$CFG_TARGET/schemes"

if [[ -f "$BUNDLE_DIR/desktop/config/shell.json" ]]; then
    track_target "$CFG_TARGET/shell.json" "created"
    cp "$BUNDLE_DIR/desktop/config/shell.json" "$CFG_TARGET/shell.json"
fi

if [[ -f "$BUNDLE_DIR/desktop/config/tokens.json" ]]; then
    track_target "$CFG_TARGET/tokens.json" "created"
    cp "$BUNDLE_DIR/desktop/config/tokens.json" "$CFG_TARGET/tokens.json"
fi

if [[ -d "$BUNDLE_DIR/desktop/schemes" ]]; then
    track_target "$CFG_TARGET/schemes" "created"
    cp -r "$BUNDLE_DIR/desktop/schemes/"* "$CFG_TARGET/schemes/" 2>/dev/null || true
fi

ok "Aetherium configuration deployed to $CFG_TARGET."
