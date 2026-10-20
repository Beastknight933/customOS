# Horizon OS — Troubleshooting & Diagnostics

This guide covers common diagnostic steps, log locations, and solutions for potential issues.

## 1. Key Log Locations

- **Installer Execution Log**: `/var/log/horizon-install.log` (or `./horizon-install.log` in dry-run mode)
- **Caelestia Shell Journal**: `journalctl --user -u caelestia-shell.service -f`
- **SDDM Login Greeter Log**: `journalctl -u sddm.service -b`
- **KWin Wayland Compositor**: `journalctl --user -u plasma-kwin_wayland -b`
- **XDG Portal Log**: `journalctl --user -u xdg-desktop-portal-kde -b`

---

## 2. Common Issues & Solutions

### A. Caelestia Shell Not Launching on Login
- **Symptom**: You see the KDE Plasma wallpaper and widgets, but no top bar or launcher.
- **Check**:
  ```bash
  systemctl --user status caelestia-shell.service
  ```
- **Fix**: Check if quickshell is on PATH:
  ```bash
  which quickshell
  ```
  If Quickshell was not found, install it or run `/usr/bin/caelestia-autostart` manually in a terminal to view debugging output.

### B. SDDM Theme Shows White or Default Theme
- **Symptom**: SDDM displays the default breeze theme instead of Ryoku Orbital.
- **Check**:
  ```bash
  cat /etc/sddm.conf.d/99-ryoku.conf
  ls -la /usr/share/sddm/themes/ryoku/Main.qml
  ```
- **Fix**: Verify that no `/etc/sddm.conf.d/zz-caelestia.conf` exists which might override `Current=ryoku`.

### C. Quickshell Hyprland IPC Warning
- **Symptom**: Journal prints `quickshell.hyprland.ipc.warning: Failed to connect to Hyprland socket`.
- **Reason**: Quickshell includes Hyprland IPC compatibility by default. In Horizon OS, the native KWin Wayland bridge is active. This warning is completely harmless and suppressed via `QT_LOGGING_RULES="quickshell.hyprland.ipc.warning=false"` in `caelestia-autostart`.

### D. Btrfs Snapshot Management with Snapper
- **Check snapshots**:
  ```bash
  snapper list
  ```
- **Roll back to previous snapshot**:
  ```bash
  snapper undochange 1..2
  ```
