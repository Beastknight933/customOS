#!/usr/bin/env bash
# Horizon OS - Ryoku SDDM Theme Installation Script
set -euo pipefail

TARGET_ROOT="${1:-/}"
THEME_DIR="$TARGET_ROOT/usr/share/sddm/themes/ryoku"
CONF_DIR="$TARGET_ROOT/etc/sddm.conf.d"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing Horizon Ryoku SDDM theme..."
mkdir -p "$THEME_DIR"
cp -a "$SRC_DIR/Main.qml" "$THEME_DIR/"
cp -a "$SRC_DIR/metadata.desktop" "$THEME_DIR/"
cp -a "$SRC_DIR/theme.conf" "$THEME_DIR/"
cp -a "$SRC_DIR/preview.gif" "$THEME_DIR/"
cp -a "$SRC_DIR/font" "$THEME_DIR/"
cp -a "$SRC_DIR/i18n" "$THEME_DIR/"

echo "==> Configuring SDDM to use ryoku theme..."
mkdir -p "$CONF_DIR"
cat > "$CONF_DIR/99-ryoku.conf" <<'EOF'
[Theme]
Current=ryoku
EOF

# Ensure no Caelestia SDDM override exists
rm -f "$CONF_DIR/zz-caelestia.conf"

echo "==> Ryoku SDDM theme installed successfully at $THEME_DIR"
