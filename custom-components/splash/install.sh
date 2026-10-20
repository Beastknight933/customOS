#!/usr/bin/env bash
# Horizon OS - Overload Splash Screen Installation Script
set -euo pipefail

TARGET_ROOT="${1:-/}"
SPLASH_DIR="$TARGET_ROOT/usr/share/plasma/look-and-feel/Overload"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing Overload KDE Plasma splash screen..."
mkdir -p "$SPLASH_DIR"
cp -a "$SRC_DIR/metadata.json" "$SPLASH_DIR/"
cp -a "$SRC_DIR/contents" "$SPLASH_DIR/"

echo "==> Overload splash screen installed to $SPLASH_DIR"
