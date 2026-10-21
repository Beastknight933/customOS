#!/usr/bin/env bash
# Horizon OS - Candy Bar (candy-icons) Icon Theme Installation Script
set -euo pipefail

TARGET_ROOT="${1:-/}"
ICONS_DIR="$TARGET_ROOT/usr/share/icons/candy-icons"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/candy-icons"

echo "==> Installing Candy Bar (candy-icons) icon theme..."
mkdir -p "$ICONS_DIR"
cp -a "$SRC_DIR/"* "$ICONS_DIR/"

echo "==> Candy Bar icon theme installed successfully to $ICONS_DIR"
