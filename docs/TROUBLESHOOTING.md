# Aetherium OS — Troubleshooting & Diagnostics

## 1. Quick Diagnostics

Run the integrated environment verification engine:
```bash
aetherium-doctor
```

To validate configuration syntax:
```bash
aetherium-doctor --validate-configs
```

To inspect raw JSON state:
```bash
aetherium-doctor --json
```

---

## 2. Common Issues & Solutions

### A. Shell Does Not Appear on Login
- **Cause:** Session is running under X11 rather than Wayland.
- **Resolution:** Select "Plasma (Wayland)" from your display manager session selector before logging in. Quickshell layer-shell windows require Wayland.

### B. SDDM Login Screen Reverts to Default Theme
- **Cause:** Missing Qt 6 SDDM greeter (`sddm-greeter-qt6`).
- **Resolution:**
  - On Arch / CachyOS: `sudo pacman -S qt6-declarative qt6-5compat qt6-svg`
  - On Fedora: `sudo dnf install qt6-qtdeclarative qt6-qt5compat`
  - Re-run verification: `sudo aetherium-sddm-adapter --verify`

### C. Lock Screen Displays Blank Background
- **Cause:** Missing background asset or misconfigured theme path.
- **Resolution:** Verify that `~/.local/state/aetherium/scheme.json` or default scheme exists. Re-run `aetherium-doctor --validate-configs`.

### D. Audio Visualizer Inactive
- **Cause:** `cava` or `aubio` not installed.
- **Resolution:** Install optional dependencies (`sudo pacman -S cava aubio` / `sudo dnf install cava`). The shell continues to operate normally without audio visualization.
