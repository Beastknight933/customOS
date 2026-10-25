# Aetherium OS — Unified KDE Plasma 6 Desktop Shell & System Integration

<p align="center">
  <b>A cohesive, atmospheric, and transactional desktop environment built on KDE Plasma 6 and Wayland.</b>
</p>

---

## Overview

**Aetherium OS** transforms a compatible Linux installation into a unified operating experience. Built upon the Caelestia KDE foundation and incorporating an independent SDDM greeter adapter, Aetherium provides an atmospheric visual identity, purposeful motion design, and rigorous transactional installation safety.

### Key Highlights
- **Atmospheric Visual Identity:** Deep obsidian and twilight slate base palette with celestial azure, ethereal cyan, and subtle amber accents.
- **Wayland Native:** Built on Quickshell and KDE Plasma 6 utilizing `wlr-layer-shell` and `ext-session-lock-v1`.
- **Decoupled Architecture:** Strict separation between user desktop sessions, pre-session SDDM greeter, and in-session lock screen.
- **Safety & Reversibility:** Transactional backups, atomic manifest logging, immediate rollback on error, and clean uninstallation.
- **Ryoku-Ready SDDM Adapter:** Transactional SDDM adapter supporting pre-flight checks, backup/rollback, and an architectural contract for external theme integration.
- **Diagnostic Engine:** Integrated `aetherium-doctor` CLI for rapid environment verification and configuration validation.

---

## Architecture

```text
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

For complete architectural details, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## Installation Quickstart

### Prerequisites
- **OS:** Arch Linux / CachyOS, Fedora 40+, or Debian 13 / Ubuntu 24.04+.
- **Desktop Session:** KDE Plasma 6.0+ running under Wayland.
- **Core Dependencies:** `quickshell` (>= 0.0.12), `python3`, `qt6-declarative`, `qt6-5compat`.

### Running the Installer
```bash
./install.sh
```

Choose from four installation profiles:
1. `desktop`: Shell, panels, widgets, and themes.
2. `desktop-lockscreen` (Recommended): Desktop shell + coordinated Plasma lock screen.
3. `full`: Complete experience including SDDM greeter theme.
4. `custom`: Interactive component toggles.

### Health Check
```bash
aetherium-doctor
```

---

## Implementation & Verification Status

| Component | Status | Details / Verification Method |
| :--- | :--- | :--- |
| **Design System & Tokens** | **Verified** | Semantic color palettes, motion timings, spacing, and schema validated via automated tests (`test_tokens.py`, `test_configs.py`). |
| **Diagnostic Engine (`aetherium-doctor`)** | **Verified** | JSON output, semantic configuration validation, and meaningful exit codes validated via `test_doctor.py`. Zero secret exposure; runs unprivileged. |
| **SDDM Greeter Adapter** | **Verified** | Staged atomic replacement, pre-flight backup, rollback, and theme validation verified via unit tests (`test_sddm_adapter.py`, `test_sddm_theme.py`). |
| **Baseline SDDM Theme** | **Verified** | QML syntax, PAM auth contract, session selection, and static fallback verified. |
| **Plasma Lock Screen Package** | **Verified** | `metadata.json`, QML component structure, and PAM contract verified via `test_lockscreen.py`. |
| **Installer & Rollback Engine** | **Verified** | Staged installation manifests, pre-existing vs new file tracking, path whitelist security, and exact KConfig rollbacks verified via `test_manifest_and_rollback.py` and `test_installer_logic.py`. |
| **Desktop Shell QML Modules** | **Implemented** | Complete QML codebase adapted from Caelestia KDE (`desktop/shell/`). |
| **C++ Desktop Shell Plugins** | **Implemented (Pending Runtime)** | CMake configuration and C++ source code ready; compilation and live session execution require native Linux environment with Qt 6.6+ and KDE Frameworks 6 headers. |
| **Ryoku SDDM Theme (600MB Archive)** | **Pending Upstream** | The external 600MB theme archive is pending delivery. The adapter contract (`docs/SDDM_INTEGRATION.md`), baseline theme, and staging engine are in place ready to ingest it. |

---

## Documentation Index

- [Architecture & Reconnaissance](docs/ARCHITECTURE.md)
- [Installation Guide](docs/INSTALLATION.md)
- [System Compatibility Matrix](docs/COMPATIBILITY.md)
- [SDDM Integration & Ryoku Contract](docs/SDDM_INTEGRATION.md)
- [In-Session Lock Screen Integration](docs/LOCKSCREEN_INTEGRATION.md)
- [Backup, Rollback & Recovery](docs/BACKUP_AND_RECOVERY.md)
- [Troubleshooting & Diagnostics](docs/TROUBLESHOOTING.md)
- [Developer Guide](docs/DEVELOPMENT.md)
- [Third-Party Licenses & Notices](THIRD_PARTY_LICENSES.md)

---

## License

Aetherium OS is licensed under the **GNU General Public License version 3 (GPL-3.0)**.
Upstream components are subject to their respective licenses. See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for details.
