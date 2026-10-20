# Horizon OS — System Architecture Specification

## 1. Executive Summary

Horizon OS is an Arch Linux-based distribution engineered around KDE Plasma 6 and KWin, delivering a cohesive, dark, atmospheric desktop aesthetic influenced by Celestia, Lord of the Mysteries (LOTM), and Dishonored / Steampunk visual concepts.

The core architecture preserves KDE Plasma 6 and KWin as the underlying window management and system framework, while integrating a customized build of the Caelestia KDE port (`caelestia-kde` v2.6.3) as the interactive desktop shell.

```
┌────────────────────────────────────────────────────────┐
│                      SDDM Greeter                      │
│        (Horizon Ryoku Orbital SDDM Theme - Pure Black)  │
└──────────────────────────┬─────────────────────────────┘
                           │ Authenticates User Session
                           ▼
┌────────────────────────────────────────────────────────┐
│                   KDE Plasma 6 / KWin                  │
│       • Wayland Compositor (KWin)                      │
│       • KScreenLocker (Atmospheric Dishonored Art)     │
│       • KDE Services & Audio (PipeWire / WirePlumber)  │
│       • Candy Bar Icon Theme (candy-icons)             │
│       • Overload Splash Screen                         │
└──────────────────────────┬─────────────────────────────┘
                           │ Manages Desktop Windows & Bridge
                           ▼
┌────────────────────────────────────────────────────────┐
│                 Caelestia Desktop Shell                │
│       • Quickshell Engine & Native C++ Plugins         │
│       • KWin Workspace-Tracker Effect Plugin           │
│       • Top Bar with Auto-Hide / Hover Activation      │
│       • Uncluttered Center Dock (No Default Pinned)    │
│       • Restrained Transparency & Pitch-Black Theme    │
│       • KDE Plasma Desktop Widgets Preserved           │
└────────────────────────────────────────────────────────┘
```

## 2. Desktop Environment & Shell Architecture

### Foundation: KDE Plasma 6 and KWin
- **Window Management**: KWin running native Wayland compositor.
- **Session Manager**: KDE Plasma 6 session (`plasma-workspace`).
- **Desktop Widgets**: Retained. Caelestia's background canvas and wallpaper drawing are explicitly disabled (`background.enabled: false`) to ensure KDE desktop icons and plasma widgets operate without collision.
- **Lock Screen**: Managed by KScreenLocker. The upstream Caelestia lockscreen greeter (`caelestia.desktop`) is explicitly disabled via Horizon patches.

### Custom Shell: Caelestia KDE Port (Quickshell)
- **Engine**: Quickshell (Qt 6.9+ Declarative QML runtime).
- **Native C++ Plugins**: Direct KWin Wayland bridge and IPC plugins (`shell/plugin/`).
- **Workspace Tracker**: Custom KWin effect plugin compiled from `shell/kwin-effects/workspace-tracker/`.
- **Autostart**: Governed by `caelestia-shell.service` (systemd user unit) and launcher `/usr/bin/caelestia-autostart`.

## 3. Display Manager: SDDM & Horizon Ryoku Theme

- **Daemon**: Simple Desktop Display Manager (SDDM).
- **Theme**: Horizon Ryoku Orbital Clockwork SDDM Theme (`/usr/share/sddm/themes/ryoku`).
- **Color Modification**: Patched `Main.qml` ensures both light and dark branches resolve `bgColor` to pure black (`#000000`).
- **Configuration**: Pinned via `/etc/sddm.conf.d/99-ryoku.conf` with `[Theme] Current=ryoku`.
- **Exclusion**: Upstream Caelestia SDDM theme (`zz-caelestia.conf`) is stripped from builds and package recipes.

## 4. Kernel & Performance Layer: CachyOS

- **Kernel**: `linux-cachyos` with BORE (Burst-Oriented Response Enhancer) and `sched-ext` schedulers.
- **Auto-Nice Daemon**: `ananicy-cpp` with `cachyos-ananicy-rules`.
- **Settings**: `cachyos-settings` tuning sysctl, udev, and zram.
- **Architecture**: `x86_64_v3` AVX2/BMI2 optimized packages with fallback to standard `x86_64`.
