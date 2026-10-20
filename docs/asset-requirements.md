# Horizon OS — Asset Requirements & Inventory

This document registers all visual, branding, and multimedia assets across the Horizon OS project, noting their current status, location, format, licensing, and any optional upstream assets.

## 1. Asset Inventory Summary

| Asset Name | Format | Status | Intended Path | Source / Attribution |
|------------|--------|--------|---------------|----------------------|
| **Caelestia KDE Shell Source** | Tarball/Tree | **Resolved & Extracted** | `custom-components/caelestia-kde/upstream/` | Upstream v2.6.3 (GPL-3.0) |
| **Caelestia Submodule: dots** | Git Tree | **Resolved & Extracted** | `custom-components/caelestia-kde/upstream/src/dots/` | Commit `639dd6e` |
| **Caelestia Submodule: icons**| SVG Tree | **Resolved & Extracted** | `custom-components/caelestia-kde/upstream/src/yet-another-monochrome-icon-set/` | Commit `227359b` |
| **Ryoku Orbital SDDM Theme** | QML/Fonts | **Integrated & Patched** | `custom-components/ryoku-sddm/` | Ryoku-dev / Darkkal44 |
| **Overload Splash Screen** | QML/WebP | **Integrated & Verified** | `custom-components/splash/` | dgudim / kloud (OCS 2124799) |
| **Candy Bar Icons (`candy-icons`)** | SVG Tree | **Integrated & Verified** | `custom-components/icons/candy-icons/` | EliverLara (GPL-3.0) |
| **Atmospheric Wallpapers** | JPEG | **Integrated (5 Images)** | `defaults/visual-identity/wallpapers/` | LOTM / Dishonored / Steampunk |

---

## 2. Optional Enhanced Artwork (Non-Blocking)

The operating system build, installer, packaging, and desktop integration are **100% operational** with the included assets. The following optional assets can be provided by the user to further polish the visual identity:

### 1. Horizon Vector Logo / Wordmark
- **Expected Format**: Scalable Vector Graphics (`.svg`), transparent background.
- **Intended Path**: `defaults/visual-identity/branding/horizon-logo.svg`
- **Why It Is Useful**: Displayed in the fastfetch / neofetch terminal greeting, desktop launcher watermark, and system settings About page.
- **Blocks Build**: No. A crisp ASCII art banner and Unicode glyphs are used currently.
- **How to Provide**: Drop `horizon-logo.svg` into `defaults/visual-identity/branding/`.

### 2. Animated Lockscreen Video Loop (Dishonored Theme)
- **Expected Format**: H.264 or VP9 `.mp4` / `.webm` (1080p or 4K, 30/60 fps, seamless loop, no audio track).
- **Intended Path**: `defaults/visual-identity/videos/dishonored-atmospheric-loop.mp4`
- **Why It Is Useful**: If using an animated video wallpaper plugin on KScreenLocker for a moving clockwork/fog aesthetic.
- **Blocks Build**: No. High-resolution static artwork (`dishonored-atmospheric.jpg`) is currently active.
- **How to Provide**: Place video in `defaults/visual-identity/videos/`.

### 3. Plymouth Boot Splash Theme
- **Expected Format**: Plymouth script and PNG sequence.
- **Intended Path**: `defaults/visual-identity/plymouth/horizon/`
- **Why It Is Useful**: Renders early boot animations before SDDM launches.
- **Blocks Build**: No. Standard kernel silent boot / text log is active.
