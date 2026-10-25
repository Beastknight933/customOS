#!/usr/bin/env bash
# ==============================================================================
# Aetherium OS — Toolchain and Development Header Checks
# ==============================================================================

toolchain_has_compiler() {
    command -v g++ >/dev/null 2>&1 || command -v clang++ >/dev/null 2>&1
}

toolchain_has_cmake() {
    command -v cmake >/dev/null 2>&1
}

toolchain_has_ninja() {
    command -v ninja >/dev/null 2>&1
}

toolchain_has_qt6_dev() {
    if command -v pkg-config >/dev/null 2>&1; then
        pkg-config --exists Qt6Core Qt6Quick Qt6Qml 2>/dev/null && return 0
    fi
    [[ -d /usr/include/qt6 || -d /usr/lib/qt6 || -d /usr/lib64/qt6 ]]
}

toolchain_has_kf6_dev() {
    if command -v pkg-config >/dev/null 2>&1; then
        pkg-config --exists KF6WindowSystem KF6GuiAddons 2>/dev/null && return 0
    fi
    [[ -d /usr/include/KF6 ]]
}
