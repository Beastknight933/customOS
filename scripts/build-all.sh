#!/usr/bin/env bash
# Horizon OS - Build All Custom Components
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================================="
echo "  Horizon OS — Building All Components"
echo "=========================================================="

# 1. Ryoku SDDM Theme
echo "==> [1/4] Preparing Horizon Ryoku SDDM Theme..."
cd "$REPO_ROOT/custom-components/ryoku-sddm"
if [[ -f "patches/0001-force-black-background.patch" ]]; then
    echo "    Ryoku patch verified."
fi

# 2. Splash Screen
echo "==> [2/4] Verifying Overload Splash Screen..."
if [[ -f "$REPO_ROOT/custom-components/splash/metadata.json" ]]; then
    echo "    Overload splash screen package verified."
fi

# 3. Candy Bar Icon Theme
echo "==> [3/4] Verifying Candy Bar Icon Theme..."
if [[ -f "$REPO_ROOT/custom-components/icons/candy-icons/index.theme" ]]; then
    echo "    Candy Bar (candy-icons) package verified."
fi

# 4. Caelestia KDE & Workspace-Tracker Build
echo "==> [4/4] Building Caelestia KDE Shell Suite..."
cd "$REPO_ROOT/custom-components/caelestia-kde"
if [[ -f "build/build.sh" ]]; then
    bash "build/build.sh"
fi

echo "=========================================================="
echo "  All Horizon OS Custom Components Built Successfully!"
echo "=========================================================="
