#!/usr/bin/env bash
# Horizon OS - Deterministic Archiso Staging Script
# Synchronizes canonical repository files to the Archiso airootfs staging directory.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
STAGING_DIR="$REPO_ROOT/iso/archiso-profile/airootfs/opt/horizon-os"

echo "=========================================================="
echo "  Horizon OS — Deterministic Archiso Staging Pipeline"
echo "=========================================================="
echo "Canonical Root: $REPO_ROOT"
echo "Staging Target: $STAGING_DIR"

mkdir -p "$STAGING_DIR"

# 1. Root documentation & licenses
echo "==> [1/6] Staging root documentation & licenses..."
cp -p "$REPO_ROOT/README.md" "$STAGING_DIR/"
cp -p "$REPO_ROOT/SECURITY.md" "$STAGING_DIR/"
cp -p "$REPO_ROOT/THIRD_PARTY_LICENSES.md" "$STAGING_DIR/"
cp -p "$REPO_ROOT/LICENSE" "$STAGING_DIR/"
cp -p "$REPO_ROOT/install.sh" "$STAGING_DIR/"

# 2. Installer engine
echo "==> [2/6] Staging installer engine..."
mkdir -p "$STAGING_DIR/installer/backend"
cp -p "$REPO_ROOT/installer/horizon-tui.py" "$STAGING_DIR/installer/"
if [[ -f "$REPO_ROOT/installer/horizon-installer" ]]; then
    cp -p "$REPO_ROOT/installer/horizon-installer" "$STAGING_DIR/installer/"
fi
cp -p "$REPO_ROOT/installer/backend/"*.py "$STAGING_DIR/installer/backend/"

# 3. Package definitions & manifests
echo "==> [3/6] Staging package definitions and release manifest..."
mkdir -p "$STAGING_DIR/packages/arch-base"
mkdir -p "$STAGING_DIR/packages/kde-desktop"
mkdir -p "$STAGING_DIR/packages/caelestia-kde"

cp -p "$REPO_ROOT/packages/arch-base/"* "$STAGING_DIR/packages/arch-base/"
cp -p "$REPO_ROOT/packages/kde-desktop/"* "$STAGING_DIR/packages/kde-desktop/"
cp -p "$REPO_ROOT/packages/release-manifest.json" "$STAGING_DIR/packages/"
cp -p "$REPO_ROOT/packages/caelestia-kde/"* "$STAGING_DIR/packages/caelestia-kde/"

# 4. Desktop profiles
echo "==> [4/6] Staging desktop profiles..."
mkdir -p "$STAGING_DIR/profiles"
cp -p "$REPO_ROOT/profiles/"*.yaml "$STAGING_DIR/profiles/"

# 5. Desktop defaults
echo "==> [5/6] Staging desktop defaults and visual identity..."
mkdir -p "$STAGING_DIR/defaults/kde"
mkdir -p "$STAGING_DIR/defaults/sddm"
mkdir -p "$STAGING_DIR/defaults/shell"
mkdir -p "$STAGING_DIR/defaults/visual-identity/wallpapers"

cp -p "$REPO_ROOT/defaults/kde/"* "$STAGING_DIR/defaults/kde/"
cp -p "$REPO_ROOT/defaults/sddm/"* "$STAGING_DIR/defaults/sddm/"
cp -p "$REPO_ROOT/defaults/shell/"* "$STAGING_DIR/defaults/shell/"
cp -p "$REPO_ROOT/defaults/visual-identity/README.md" "$STAGING_DIR/defaults/visual-identity/"
cp -p "$REPO_ROOT/defaults/visual-identity/wallpapers/"* "$STAGING_DIR/defaults/visual-identity/wallpapers/"

# 6. Custom components (excluding uncompiled upstream git checkout)
echo "==> [6/6] Staging custom components..."
mkdir -p "$STAGING_DIR/custom-components/ryoku-sddm"
mkdir -p "$STAGING_DIR/custom-components/splash"
mkdir -p "$STAGING_DIR/custom-components/caelestia-kde"

cp -rp "$REPO_ROOT/custom-components/ryoku-sddm/"* "$STAGING_DIR/custom-components/ryoku-sddm/"
cp -rp "$REPO_ROOT/custom-components/splash/"* "$STAGING_DIR/custom-components/splash/"
cp -p "$REPO_ROOT/custom-components/caelestia-kde/provenance.json" "$STAGING_DIR/custom-components/caelestia-kde/"
cp -p "$REPO_ROOT/custom-components/caelestia-kde/README.md" "$STAGING_DIR/custom-components/caelestia-kde/"
cp -rp "$REPO_ROOT/custom-components/caelestia-kde/configuration" "$STAGING_DIR/custom-components/caelestia-kde/"
cp -rp "$REPO_ROOT/custom-components/caelestia-kde/packaging" "$STAGING_DIR/custom-components/caelestia-kde/"
cp -rp "$REPO_ROOT/custom-components/caelestia-kde/patches" "$STAGING_DIR/custom-components/caelestia-kde/"

echo "=========================================================="
echo "  ✓ Archiso Staging Completed Successfully!"
echo "=========================================================="
