# Aetherium OS — Technical Architecture & Engineering Specification

## 1. System Overview & Vision

**Aetherium OS** is an integrated, unified Linux desktop shell and visual system built on top of KDE Plasma 6 and Wayland. Rather than functioning as a disparate collection of dotfiles, themes, or uncoordinated scripts, Aetherium is engineered as a cohesive desktop product that transforms a compatible Linux installation into a sophisticated, atmospheric operating environment.

### Core Design Philosophy
- **Atmospheric & Cinematic:** Restrained deep obsidian and twilight slate foundations accented with celestial blues, ethereal cyan, and subtle gold/amber highlights.
- **Purposeful Motion:** Expressive yet rapid easing curves that communicate window hierarchy and navigation state without introducing input latency. Full reduced-motion mode for accessibility.
- **Architectural Separation:** Strict decoupling between desktop session execution (Quickshell Layer-Shell), pre-session display manager (SDDM), and session locking (KScreenLocker), ensuring the system remains completely recoverable even if a graphical component encounters an error.
- **Non-Destructive & Reversible:** Every configuration change, theme assignment, and system unit is tracked with transactional backup manifests, enabling clean rollbacks and complete uninstallation.

---

## 2. Upstream Source Audit & Reconnaissance Findings

A thorough inspection of the upstream reference sources (`caelestia-kde` and `qylock`) established the following technical foundation:

1. **Shell Entry Point & Lifecycle:**
   - The primary shell entry point is `shell/shell.qml`, executed via `quickshell -n -p <entrypoint>`.
   - Startup utilizes an initial 250ms deferred initialization timer before loading C++ plugins (`PluginLoader`), establishing IPC handlers (`region`, `lock`), and launching background services (Audio, GameMode, DiscordRPC, QuickShare).
2. **QML Module Registration:**
   - Compiled as Qt 6 QML modules via CMake (`qml-module.cmake`): `Caelestia` (root plugin), `Caelestia.Config` (declarative settings and design tokens), and `Caelestia.Services` (native platform bridges).
   - Component directories map to canonical QML namespace imports (`qs.components`, `qs.modules`, `qs.services`, `qs.utils`).
3. **C++ & Native Libraries:**
   - Core stack: Qt 6.6+ (`QtCore`, `QtGui`, `QtQml`, `QtQuick`, `QtMultimedia`, `Qt5Compat`), KDE Frameworks 6 (`KF6WindowSystem`, `KF6GuiAddons`, `KF6GlobalAccel`, `KF6Config`, `KF6CoreAddons`).
   - Native audio & hardware: `aubio`, `libcava`, `libpipewire`, `wireplumber`, `networkmanager-qt`, `pulseaudio-qt`, `libqalculate` (`qalc`), `ddcutil`, `brightnessctl`.
4. **Desktop Environment & Service Communication:**
   - Communicates with KWin and Wayland compositors via Wayland layer-shell protocols (`WlrLayershell`) and KWin DBus interfaces (`org.kde.KWin`).
   - Interacts with system services via DBus: `UPower` for battery/power profiles, `NetworkManager` for networking, `BlueZ` for Bluetooth, and systemd/loginctl for session control.
5. **Panels, Widgets & Overlays:**
   - Wayland LayerShell anchors panels to screen edges (`modules/bar`). Configurable zones (`left`, `middle`, `right`) host dynamic widgets (Clock, Workspaces, Performance, Status, Tray).
   - Drawers (`modules/drawers`) provide sliding sheets for notifications, dashboard, and quick settings without window occlusion conflicts.
   - Launcher (`modules/launcher`) provides keyboard-driven fuzzy searching across applications, windows, and calculation inputs.
   - Overview (`modules/overview`) displays virtual desktop layouts and window previews.
6. **Configuration & State Persistence:**
   - Strongly typed C++ `ObjectNode` hierarchy (`Caelestia.Config`) persisted to JSON:
     - `~/.config/aetherium/shell.json` (layout, widgets, drawer behavior).
     - `~/.config/aetherium/tokens.json` (design tokens: padding, rounding, font sizes, animation speeds).
7. **Wallpaper & Dynamic Color Generation:**
   - Algorithmic color extraction powered by `matugen` (Material Design 3 tokens).
   - Native `PaletteManager` and `Colours.qml` calculate surface luminance and transparency in C++, dynamically animating active palette transitions across all UI components without shell restarts.
8. **Motion & Animation Architecture:**
   - Centralized tokens in `tokens.hpp` define standard and expressive cubic bézier curves (`emphasized`, `standard`, `expressiveDefaultSpatial`, `expressiveFastEffects`).
   - QML behaviors wrap `Anim.qml` and `CAnim.qml` to enforce consistent timing.
9. **Keyboard Shortcuts:**
   - Managed via `Shortcuts.qml` using `KF6GlobalAccel` and DBus bindings for global compositor shortcuts (Super for Launcher, Super+Tab for Overview, Super+L for Session Lock).
10. **Installer Distribution & Dependency Detection:**
    - Detects distro family via `/etc/os-release` (Arch Linux / CachyOS / EndeavourOS, Fedora, Debian / Ubuntu).
    - Verifies package availability via native package manager queries (`pacman -Qq`, `rpm -q`, `dpkg -s`).
11. **Installation, Upgrades & Backups:**
    - Step-based installer scripts (`scripts/00-*` to `10-*`). Creates timestamped state backups in `~/.local/state/` before touching KDE or SDDM configuration.
12. **Platform Constraints:**
    - Strictly Wayland (`ext-session-lock-v1` and `wlr-layer-shell`). Qt 6.6+ required.
13. **External Utilities:**
    - Required: `matugen`, `quickshell`, `cava`, `brightnessctl`, `libqalculate`.
14. **Directly Reusable Components:**
    - Core layer-shell architecture, workspace tracking, native Qt6 C++ plugin infrastructure, and PAM session authentication abstractions.
15. **Required New Aetherium Components:**
    - Centralized Aetherium Design System (Layer A).
    - Transactional SDDM Adapter with Qt6 greeter validation and backup recovery (Layer D).
    - In-session Plasma Lockscreen package `aetherium.desktop` (Layer E).
    - Diagnostics and health verification engine `aetherium-doctor` (Layer C).
    - Granular profile-based installer with complete rollback metadata (Layer F).

---

## 3. Target Multi-Layer Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        AETHERIUM DESKTOP UX                           │
├────────────────────────────────────────────────────────────────────────┤
│ Layer A: Aetherium Design System (Tokens, Themes, Motion, Typography)   │
├────────────────────────────────────────────────────────────────────────┤
│ Layer B: Aetherium Shell (Bar, Launcher, Overview, Drawers, OSD)       │
├────────────────────────────────────────────────────────────────────────┤
│ Layer C: Aetherium Integration Services & aetherium-doctor CLI         │
├───────────────────────────────────┬────────────────────────────────────┤
│ Layer D: SDDM Integration Adapter │ Layer E: Plasma Lock Screen Package│
├───────────────────────────────────┴────────────────────────────────────┤
│ Layer F: Safe Installer, Rollback Engine & System Recovery             │
└────────────────────────────────────────────────────────────────────────┘
```

### Layer A: Aetherium Design System
- **Single Source of Truth:** Centralized design tokens located in `desktop/config/tokens.json` and mirrored in C++ headers.
- **Semantic Color Tokens:**
  - `surface.base`: `#0a0d14` (Deep obsidian void)
  - `surface.panel`: `#101522` (Translucent twilight slate)
  - `surface.elevated`: `#161d2f` (Elevated card container)
  - `text.primary`: `#e8edf5` (Crisp starlight silver)
  - `text.secondary`: `#8b9bb4` (Muted celestial mist)
  - `accent.primary`: `#569cd6` (Aetherium azure)
  - `accent.secondary`: `#4ec9b0` (Ethereal cyan)
  - `border.subtle`: `rgba(255, 255, 255, 0.08)`
  - `border.focused`: `rgba(86, 156, 214, 0.45)`
- **Motion Profiles:**
  - `motion.fast`: 150ms (Button presses, hover effects, tooltip popouts)
  - `motion.normal`: 300ms (Drawer open/close, launcher reveal, window highlights)
  - `motion.slow`: 500ms (Workspace transitions, overview zoom)
  - `motion.reduced`: 0ms / 50ms fade (Instantaneous changes when accessibility prefers reduced motion)

### Layer B: Aetherium Desktop Shell
- Hosted under `desktop/shell/`.
- Runs via Quickshell 0.0.12+ under KDE Plasma 6 Wayland session.
- Handles top/bottom/left/right panels, application searching, workspace navigation, system tray, notifications, and media controls.
- Configured via `~/.config/aetherium/shell.json`.

### Layer C: Integration Services & Diagnostics (`aetherium-doctor`)
- Lightweight CLI diagnostic and verification utility: `aetherium-doctor`.
- Verifies display server session type, Qt version, KDE Frameworks version, required packages, SDDM theme drop-in integrity, and user permissions.
- Collects non-sensitive system status for rapid troubleshooting without root privileges.

### Layer D: Aetherium SDDM Integration Framework
- Independent system-level integration decoupled from user desktop runtime.
- Installs to `/usr/share/sddm/themes/aetherium/`.
- Configures drop-in `/etc/sddm.conf.d/zz-aetherium.conf`.
- Inspects `/etc/sddm.conf` and all existing drop-ins, creates atomic backups in `/var/backups/aetherium/sddm/` or `~/.local/state/aetherium/backups/`, and verifies `sddm-greeter-qt6` presence before activation.
- Default baseline: Clean, high-contrast, atmospheric Aetherium login theme with static/animated fallback, password masking, user selection, session selection, and power management.
- Accommodates future integration of the 600MB Ryoku theme archive via the documented adapter contract.

### Layer E: In-Session Lock Screen Integration
- Packaged as a standard KDE Plasma Shell Package: `themes/lockscreen/aetherium.desktop/`.
- Configured via `plasmashellrc` (`[Shell] ShellPackage=aetherium.desktop`).
- Interacts strictly with KDE's secure `kscreenlocker_greet` and PAM `authenticator` target.
- Employs identical atmospheric design tokens, typography, and clock presentation as the desktop shell while preserving full PAM security.

### Layer F: Safe Installer, Updater, Rollback & Uninstallation
- Interactive and automated installation workflows.
- Four distinct profiles:
  1. `desktop`: Installs shell, design system, autostart, and desktop configs.
  2. `desktop-lockscreen`: Desktop shell + KDE Plasma lockscreen package.
  3. `full`: Complete Aetherium experience (Desktop, lockscreen, and SDDM theme).
  4. `custom`: Granular component selection.
- Atomic state tracking: Every modified file is recorded in an installation manifest (`install-manifest.json`).
- Immediate rollback capability on pre-flight or installation failure.
- Complete uninstallation that cleanly reverts KDE settings, removes Aetherium files, restores prior SDDM configuration, and verifies system health.

---

## 4. Ryoku SDDM Integration Contract

When the external 600MB Ryoku SDDM theme archive is made available, it must satisfy the following integration contract:
1. **Entry Point & Metadata:** Must provide a valid `metadata.desktop` declaring `QtVersion=6` and `MainScript=Main.qml`.
2. **QML Dependency Boundary:** All QML imports must be satisfied by standard Qt 6 modules (`QtQuick`, `QtQuick.Layouts`, `Qt5Compat.GraphicalEffects`, `QtMultimedia`, `SddmComponents 2.0`). Custom native C++ plugins are prohibited in the SDDM greeter sandbox.
3. **Authentication Integrity:** Must interface exclusively with the standard SDDM greeter context: `sddm.login(username, password, sessionIndex)`. Passwords must never be stored in plain text or emitted to logs.
4. **Resilience & Fallback:** Any background video or animation must provide a static fallback image (`background.png` / `bg.png`). If multimedia playback fails or codecs are missing, the greeter must remain responsive and functional.
5. **Portability:** File paths must be resolved relatively via `Qt.resolvedUrl()` rather than machine-specific absolute filesystem paths.

---

## 5. Compatibility Matrix

| Component | Minimum Version | Reference Target | Fallback / Notes |
| :--- | :--- | :--- | :--- |
| **Linux Distribution** | Arch / CachyOS / Fedora 40 / Debian 13 | Arch Linux / CachyOS | Modular package mappings |
| **Desktop Session** | KDE Plasma 6.0 | KDE Plasma 6.2+ | Plasma 5 unsupported |
| **Display Server** | Wayland 1.22+ | Wayland (KWin) | X11 unsupported (LayerShell requirement) |
| **Qt Runtime** | Qt 6.6 | Qt 6.7+ | Qt 6 declarative & 5compat required |
| **Quickshell** | 0.0.12 | 0.0.12+ | Pre-requisite for desktop shell |
| **Display Manager** | SDDM 0.20+ | SDDM with Qt6 greeter | Plasma-login compatible fallback |
| **Screen Locker** | KScreenLocker 6.0+ | KScreenLocker 6.2+ | Uses official ShellPackage API |

---

## 6. Implementation Milestones

1. **Phase 0:** Audit & Architecture (Completed).
2. **Phase 1:** Aetherium Identity & Design System (Tokens, schemas, palettes, typography).
3. **Phase 2:** Aetherium Desktop Shell (Adapted QML shell, C++ plugin, panel, launcher, overview, bar widgets).
4. **Phase 3:** Integration Services & Diagnostics (`aetherium-doctor` CLI and system checks).
5. **Phase 4:** SDDM Framework & Baseline Theme (Transactional adapter, config preservation, baseline theme).
6. **Phase 5:** In-Session Lock Screen Integration (Plasma shell package `aetherium.desktop`).
7. **Phase 6:** Safe Installer, Profile Engine, Rollback & Uninstaller.
8. **Phase 7:** Automated Test Suites & Verification (Unit tests, static linting, config validation).

---

## 7. Implementation & Verification Status

### 7.1 Implemented & Verified Components
- **Diagnostic Engine (`aetherium-doctor`):** Supports `--json` and `--validate-configs`. Semantic validation of `shell.json` and `tokens.json`. Adheres to exit codes (`0` ready, `1` config error, `2` missing deps, `3` unsupported env). Tested via unit tests with zero privilege escalation and zero sensitive credential leaks.
- **SDDM Integration Framework:** Staged atomic directory swapping on the same filesystem (`/usr/share/sddm/themes/.aetherium.staging-$$`), non-destructive backup of pre-existing themes and `/etc/sddm.conf.d/` drop-ins, and verified rollback without automatic display manager restarts.
- **Installer & Rollback Engine:** JSON-formatted manifest tracking (`install-manifest.json`) recording pre-existence status (`existed_before`), strict path traversal and whitelist safety enforcement, exact KConfig rollback (`plasmashellrc` and `kscreenlockerrc` restored or deleted), and clean removal of newly created files.
- **Design System & Metadata:** Complete schema and token verification for Aetherium dark/light schemes, lockscreen package metadata, and SDDM `metadata.desktop`.
- **Automated Test Suite:** 25 automated unit tests executed and passing cleanly via Python's standard `unittest` framework.

### 7.2 Implemented (Pending Native Linux Toolchain / Runtime Verification)
- **Desktop Shell Native C++ Plugins:** The CMake build configuration and C++ source code adapted from Caelestia are present in `desktop/`. Compiling and linking these plugins (`libCaelestia.so`, `libCaelestiaConfig.so`, `libCaelestiaServices.so`) requires a native Linux toolchain with Qt 6.6+ and KF6 development packages (`KF6WindowSystem`, `KF6GuiAddons`, `KF6GlobalAccel`, `pipewire`, `wireplumber`).
- **Live Wayland Compositor Session:** Full graphical execution under KWin Wayland using `wlr-layer-shell` and `ext-session-lock-v1` requires a running Linux graphical session.

### 7.3 Pending External Artifacts
- **Ryoku SDDM Theme Archive (600MB):** The external theme archive remains pending upstream delivery. The baseline Aetherium SDDM theme, adapter staging logic, verification hooks, and architectural contract are fully prepared to receive and validate the archive once provided.
