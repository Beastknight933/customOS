#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Step 04: Deploy Session Environment
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=scripts/lib/log.sh
source "$SCRIPT_DIR/lib/log.sh"
# shellcheck source=scripts/lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"
# shellcheck source=scripts/lib/backup.sh
source "$SCRIPT_DIR/lib/backup.sh"

info "Establishing Aetherium session environment variables..."

ENV_D="$HOME/.config/environment.d"
PLASMA_ENV_D="$HOME/.config/plasma-workspace/env"
mkdir -p "$ENV_D" "$PLASMA_ENV_D"

ENV_CONF="$ENV_D/aetherium.conf"
track_target "$ENV_CONF" "created"
cat > "$ENV_CONF" << EOF
# Written by Aetherium OS. Sourced by systemd user session.
QML2_IMPORT_PATH=$HOME/.local/lib/aetherium/qt6/qml:/usr/lib/qt6/qml
AETHERIUM_LIB_DIR=$HOME/.local/lib/aetherium
AETHERIUM_BIN_DIR=$HOME/.local/bin
AETHERIUM_SHELL_CONFIG=$HOME/.config/aetherium/shell.qml
EOF

PLASMA_ENV_SH="$PLASMA_ENV_D/aetherium.sh"
track_target "$PLASMA_ENV_SH" "created"
cat > "$PLASMA_ENV_SH" << EOF
#!/bin/sh
# Written by Aetherium OS. Sourced by KDE Plasma for KWin and session processes.
export PATH="\$HOME/.local/bin:\${PATH:+:\$PATH}"
export QML2_IMPORT_PATH="\$HOME/.local/lib/aetherium/qt6/qml:/usr/lib/qt6/qml\${QML2_IMPORT_PATH:+:\$QML2_IMPORT_PATH}"
export AETHERIUM_LIB_DIR="\$HOME/.local/lib/aetherium"
export AETHERIUM_BIN_DIR="\$HOME/.local/bin"
export AETHERIUM_SHELL_CONFIG="\$HOME/.config/aetherium/shell.qml"
EOF
chmod +x "$PLASMA_ENV_SH"

ok "Session environment configured."
