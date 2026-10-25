#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Step 05: Install SDDM Theme
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=scripts/lib/log.sh
source "$SCRIPT_DIR/lib/log.sh"

if [[ "${INSTALL_SDDM:-false}" != "true" ]]; then
    skip "SDDM theme installation not selected."
    exit 0
fi

VARIANT="${SDDM_THEME_VARIANT:-aetherium}"
info "Configuring SDDM Greeter theme (variant: $VARIANT)..."

THEME_PATH="$BUNDLE_DIR/themes/sddm/$VARIANT"
if [[ ! -d "$THEME_PATH" ]]; then
    warn "Theme directory not found at $THEME_PATH; falling back to 'aetherium'"
    THEME_PATH="$BUNDLE_DIR/themes/sddm/aetherium"
fi

if [[ ! -f "$THEME_PATH/metadata.desktop" || ! -f "$THEME_PATH/Main.qml" ]]; then
    err "Invalid SDDM theme at $THEME_PATH (missing metadata.desktop or Main.qml)."
    exit 1
fi

ADAPTER="$BUNDLE_DIR/core/sddm-adapter/aetherium-sddm-adapter.sh"
if [[ -x "$ADAPTER" || -f "$ADAPTER" ]]; then
    bash "$ADAPTER" --install "$THEME_PATH"
    ok "SDDM theme ($VARIANT) installed successfully."
else
    err "SDDM adapter script not found at $ADAPTER"
    exit 1
fi
