# Aetherium OS — Compatibility & System Requirements

## 1. Operating Systems Matrix

| Distribution | Compatibility Status | Tested Package Names / Notes |
| :--- | :--- | :--- |
| **Arch Linux / CachyOS** | **Tier 1 (Reference)** | Full native support via standard Arch repositories & AUR |
| **EndeavourOS / Manjaro** | **Tier 1** | Identical package mappings to Arch Linux |
| **Fedora 40+** | **Tier 2** | Supported; requires `dnf install qt6-qtdeclarative qt6-qt5compat` |
| **Debian 13 (Trixie) / Ubuntu 24.04** | **Tier 2** | Supported; requires Plasma 6 backports / PPA |

---

## 2. Desktop Environment & Display Protocols

| Component | Minimum Version | Recommended | Notes |
| :--- | :--- | :--- | :--- |
| **KDE Plasma** | 6.0 | 6.2+ | Plasma 5 is unsupported due to API breakages in KScreenLocker and KWin. |
| **Display Protocol** | Wayland 1.22+ | Wayland (KWin) | **X11 is unsupported.** Quickshell's Layer-Shell architecture requires Wayland. |
| **Qt Framework** | 6.6 | 6.7+ | `qt6-base`, `qt6-declarative`, `qt6-5compat`, `qt6-multimedia`. |
| **Quickshell** | 0.0.12 | 0.0.12+ | Shell runtime engine. |
| **Display Manager** | SDDM 0.20+ | SDDM with Qt6 greeter | Supports fallback to standard Plasma-Login. |

---

## 3. Hardware & Peripheral Integrations

- **Audio Visualizer:** Powered by `cava` and `aubio`. Falls back gracefully to static indicators if unavailable.
- **Display Brightness:** Controlled via `brightnessctl` (laptops/internal) and `ddcutil` (external DDC/CI monitors).
- **Power Management:** Interacts with `power-profiles-daemon` via DBus.
- **Biometric Unlock:** Honors system PAM configuration (Fingerprint `fprintd` / Face unlock `howdy`).
