# Aetherium OS — Installation Guide

## 1. Prerequisites

Before installing Aetherium OS, ensure your system meets the minimum specifications:
- **Operating System:** Arch Linux, CachyOS, Fedora 40+, or Debian 13 / Ubuntu 24.04+.
- **Desktop Session:** KDE Plasma 6.0+ running on **Wayland** (`XDG_SESSION_TYPE=wayland`).
- **Display Server:** Wayland compositor with `wlr-layer-shell` and `ext-session-lock-v1` protocol support (standard in KWin 6).
- **Core Runtime:** `quickshell` (>= 0.0.12), `python3`, `qt6-declarative`, `qt6-5compat`.

---

## 2. Interactive Installation

Run the interactive installer from the repository root:
```bash
./install.sh
```

You will be presented with a profile selection:
1. **desktop:** Installs the Aetherium Desktop Shell, widgets, launcher, dynamic schemes, and autostart entries.
2. **desktop-lockscreen (Default):** Desktop shell + the coordinated `aetherium.desktop` Plasma lock screen.
3. **full:** Complete Aetherium experience including the SDDM greeter theme.
4. **custom:** Interactive toggles for each component.

---

## 3. Unattended / Scripted Installation

For automated or scripted deployments, supply the profile name as an argument:
```bash
NON_INTERACTIVE=1 ./install.sh full
```

---

## 4. Post-Installation Verification

Run the built-in diagnostic engine to verify system health:
```bash
aetherium-doctor
```
Or check configuration file syntax:
```bash
aetherium-doctor --validate-configs
```

---

## 5. Starting the Shell

To launch the desktop shell immediately without logging out:
```bash
nohup aetherium-autostart >/dev/null 2>&1 &
```
The shell will automatically autostart on all subsequent Wayland Plasma sessions via `~/.config/autostart/aetherium-autostart.desktop` or `aetherium-shell.service`.
