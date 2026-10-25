#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Step 00: Backup Current Setup
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

info "Creating transactional pre-installation state backup..."
init_backup
ok "Pre-installation backup completed successfully."
