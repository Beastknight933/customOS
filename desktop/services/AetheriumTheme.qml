pragma Singleton
pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import Caelestia.Config
import qs.services

Singleton {
    id: root

    // Semantic Surfaces
    readonly property color surfaceBase: "#090c10"
    readonly property color surfacePanel: "#101522"
    readonly property color surfaceElevated: "#161d2f"
    readonly property color surfaceContainer: "#121824"

    // Semantic Typography
    readonly property color textPrimary: "#e8edf5"
    readonly property color textSecondary: "#8b9bb4"
    readonly property color textDim: "#5c6b84"

    // Semantic Accents
    readonly property color accentPrimary: "#60a5fa"
    readonly property color accentSecondary: "#38bdf8"
    readonly property color accentHighlight: "#2dd4bf"
    readonly property color accentAmber: "#f59e0b"

    // Borders & Outlines
    readonly property color borderSubtle: Qt.rgba(1, 1, 1, 0.08)
    readonly property color borderFocused: Qt.rgba(0.38, 0.65, 0.98, 0.45)
    readonly property color cardBorder: Qt.rgba(1, 1, 1, 0.06)

    // Motion Durations (ms)
    readonly property int motionFast: 150
    readonly property int motionNormal: 300
    readonly property int motionSlow: 500
    readonly property int motionReduced: 40

    // Reduced motion mode detection
    readonly property bool reducedMotion: !GlobalConfig.appearance.anim.enabled
}
