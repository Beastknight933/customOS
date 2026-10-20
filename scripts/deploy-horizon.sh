#!/usr/bin/env bash
# Horizon OS - Standalone Desktop Deployment Script
set -euo pipefail

TARGET_ROOT="${1:-/}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================================="
echo "  Horizon OS — Deploying Desktop Environment"
echo "  Target: $TARGET_ROOT"
echo "=========================================================="

python3 - <<EOF
import sys
sys.path.insert(0, "$REPO_ROOT/installer")
from backend.executor import InstallExecutor
from backend.deployer import ComponentDeployer

executor = InstallExecutor(dry_run=False, target_root="$TARGET_ROOT")
deployer = ComponentDeployer(executor=executor, repo_root="$REPO_ROOT")

print("Deploying Ryoku SDDM...")
deployer.deploy_ryoku_sddm(print)

print("Deploying Overload Splash...")
deployer.deploy_overload_splash(print)

print("Deploying Candy Bar Icons...")
deployer.deploy_candy_icons(print)

print("Deploying KDE & Visual Identity Defaults...")
deployer.deploy_horizon_kde_defaults(print)

print("Deploying Caelestia Shell Configs...")
deployer.deploy_caelestia_shell(username="", on_output=print)
EOF

echo "==> Horizon desktop deployment finished successfully!"
