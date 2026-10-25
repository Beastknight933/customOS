#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Step 08: Build & Install Desktop Shell
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=scripts/lib/log.sh
source "$SCRIPT_DIR/lib/log.sh"
# shellcheck source=scripts/lib/toolchain.sh
source "$SCRIPT_DIR/lib/toolchain.sh"

DESKTOP_DIR="$BUNDLE_DIR/desktop"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/aetherium"
BUILD_LOG="$CACHE_DIR/shell-build.log"
mkdir -p "$CACHE_DIR"

info "Preparing Aetherium Desktop Shell..."

if [[ ! -d "$DESKTOP_DIR" ]]; then
    err "Desktop directory not found at $DESKTOP_DIR"
    exit 1
fi

# Deploy QML shell source tree to ~/.config/quickshell/aetherium
QS_TARGET="$HOME/.config/quickshell/aetherium"
mkdir -p "$QS_TARGET"
if [[ -d "$DESKTOP_DIR/shell" ]]; then
    info "Syncing QML shell components to $QS_TARGET..."
    cp -r "$DESKTOP_DIR/shell/"* "$QS_TARGET/" 2>/dev/null || true
fi

# Native C++ plugin compilation
CAN_BUILD=1
if ! toolchain_has_compiler; then
    CAN_BUILD=0
    warn "C++ compiler (g++ / clang++) not available."
fi
if ! toolchain_has_cmake; then
    CAN_BUILD=0
    warn "CMake not available."
fi
if ! toolchain_has_qt6_dev; then
    CAN_BUILD=0
    info "Qt6 development headers not detected on host."
fi

if [[ $CAN_BUILD -eq 1 && "${AETHERIUM_SKIP_BUILD:-0}" != "1" ]]; then
    info "Configuring and compiling native C++ plugins via CMake..."
    BUILD_DIR="$DESKTOP_DIR/build"
    rm -rf "$BUILD_DIR"
    mkdir -p "$BUILD_DIR"

    CMAKE_GEN="Unix Makefiles"
    if toolchain_has_ninja; then
        CMAKE_GEN="Ninja"
    fi

    (
        cd "$BUILD_DIR" || exit 1
        cmake -G "$CMAKE_GEN" \
            -DCMAKE_BUILD_TYPE=Release \
            -DCMAKE_INSTALL_PREFIX="$HOME/.local" \
            -DINSTALL_BINDIR="bin" \
            -DINSTALL_DATADIR="lib/aetherium" \
            -DINSTALL_LIBDIR="lib/aetherium" \
            -DINSTALL_QMLDIR="lib/aetherium/qt6/qml" \
            .. >"$BUILD_LOG" 2>&1
        cmake --build . -j"$(nproc 2>/dev/null || echo 2)" >>"$BUILD_LOG" 2>&1
        cmake --install . >>"$BUILD_LOG" 2>&1
    ) || {
        warn "Native C++ plugin build encountered issues. Full log: $BUILD_LOG"
        warn "The shell will operate in QML compatibility mode."
    }
    ok "C++ plugin step completed."
else
    info "Skipping native C++ compilation (pre-requisite dev packages missing or build skipped)."
    info "QML shell components installed to $QS_TARGET."
fi

ok "Desktop shell setup completed."
