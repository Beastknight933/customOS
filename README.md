# Aetherium OS — Unified KDE Plasma 6 Desktop Shell & System Integration

<p align="center">
  <b>A cohesive, atmospheric, and transactional desktop environment built on KDE Plasma 6 and Wayland.</b><br>
  <i>Follows the upstream Caelestia KDE interactive installation, update, and uninstallation model.</i>
</p>

---

## 1. Overview

**Aetherium OS** transforms a compatible Linux installation into a unified operating experience. Engineered on the Caelestia KDE technical foundation, Aetherium provides an atmospheric visual identity, purposeful motion design, an independent transactional SDDM greeter adapter, and reliable system safety.

### Key Highlights
- **Atmospheric Visual Identity:** Deep obsidian and twilight slate foundations accented with celestial azure (`#569cd6`) and ethereal cyan (`#4ec9b0`).
- **Wayland Native:** Built on Quickshell and KDE Plasma 6 using `wlr-layer-shell` and `ext-session-lock-v1`.
- **Caelestia-Modeled Workflow:** Single interactive installer, single updater, and single uninstaller at the repository root.
- **Transactional Safety:** Pre-installation backups, JSON manifest logging (`install-manifest.json`), path whitelist security barrier, and immediate automatic rollback on error.
- **Dual SDDM Themes:** Includes both the baseline Aetherium theme and the integrated Qylock Clockwork neo-orbital theme with atomic same-filesystem staging.
- **Diagnostic Engine:** Integrated `aetherium-doctor` CLI for environment verification, configuration validation, and health checks.

---

## 2. System Requirements & Compatibility

| Component | Minimum Requirement | Recommended Target | Notes |
| :--- | :--- | :--- | :--- |
| **Operating System** | Arch Linux / CachyOS, Fedora 40+, Debian 13 / Ubuntu 24.04+ | Arch Linux / CachyOS | Tested across distro family package managers |
| **Desktop Session** | KDE Plasma 6.0 | KDE Plasma 6.2+ | Plasma 5 is unsupported |
| **Display Server** | Wayland 1.22+ (KWin) | Wayland | Strictly Wayland (Layer-Shell & ExtSessionLock) |
| **Qt Runtime** | Qt 6.6 | Qt 6.7+ | `qt6-declarative`, `qt6-5compat`, `qt6-multimedia` |
| **Core Utilities** | `quickshell` (>= 0.0.12), `python3` | `quickshell`, `matugen` | Matugen for dynamic palette derivation |
| **Display Manager** | SDDM 0.20+ with Qt6 greeter | SDDM Qt6 | Optional (selected during installation) |

---

## 3. Installation

The installation follows the upstream Caelestia KDE repository experience: clone the repository, run `install.sh`, follow the interactive installer, and log in to your transformed desktop.

### 3.1 Local Checkout Installation (Recommended)

```bash
git clone https://github.com/aetherium-os/aetherium-desktop.git
cd aetherium-desktop
bash install.sh
```

### 3.2 One-Command Installation (Remote Pipeline)

Once published to a remote release repository, Aetherium OS supports one-command remote installation via piped bash. The installer automatically detects piped execution, reconnects to the user's terminal TTY, and launches the interactive installer:

```bash
curl -fsSL https://raw.githubusercontent.com/aetherium-os/aetherium-desktop/main/install.sh | bash
```

*(Note: Prior to public release, execute from a local repository clone as described in 3.1).*

### 3.3 Installation Profiles

The interactive installer offers four pre-configured profiles:

1. **Aetherium Desktop:** Installs the desktop shell, bar zones, fuzzy application launcher, overview, design tokens, and session environment.
2. **Desktop + Lock Screen (Recommended):** Complete desktop shell + coordinated KDE Plasma lock screen package (`aetherium.desktop`).
3. **Full Aetherium Experience:** Desktop shell + Plasma lock screen + transactional SDDM login greeter theme.
4. **Custom Installation:** Granular component-level toggles (desktop shell, lockscreen, SDDM variant, system upgrade).

### 3.4 SDDM Greeter Theme Selection

When SDDM integration is selected, the installer lets you choose between:
- **`aetherium`:** Deep obsidian, twilight slate, celestial azure highlights, and starlight typography.
- **`clockwork`:** The Qylock neo-orbital clockwork theme with animated time engine, date indicators, and static wallpaper fallback.

The SDDM adapter stages themes on the same filesystem (`/usr/share/sddm/themes/.aetherium.staging-$$`), creates a transactional backup of pre-existing themes and drop-ins, and **never restarts the active display manager automatically** while your graphical session is running.

### 3.5 Non-Interactive / Scripted Installation

For automated deployments or container setups, pass flags directly to `install.sh`:

```bash
# Scripted install with Desktop + Lock Screen profile
bash install.sh --profile desktop-lockscreen --non-interactive --skip-update

# Full install with Clockwork SDDM theme
bash install.sh --profile full --sddm-theme clockwork --non-interactive --skip-update
```

### 3.6 Post-Installation

Once the installer completes:
1. **Log out and log back in** to your KDE Plasma Wayland session to initialize the shell.
2. Alternatively, start the shell immediately in your running session without logging out:
   ```bash
   nohup aetherium-autostart >/dev/null 2>&1 &
   ```

---

## 4. Updating

Updating Aetherium OS is performed through a single root entry point:

```bash
bash update.sh
```

The updater executes a safe, non-destructive lifecycle:
1. **Preserves User Settings:** Reads your existing installation profile and preferences from `~/.config/aetherium/install.env`.
2. **Safe Git Synchronization:** Detects local uncommitted modifications and stashes them automatically before pulling the latest branch changes.
3. **Pre-Update Snapshot:** Generates a timestamped backup snapshot before modifying files.
4. **Rebuilds Components:** Automatically recompiles shell plugins and updates configuration schemes.
5. **Updates Integrations:** Refreshes lockscreen and SDDM themes if they were previously activated.
6. **Live Shell Reload:** Restarts the running desktop shell smoothly via `aetherium-autostart` without interrupting your active applications or graphical session.

---

## 5. Uninstallation & System Recovery

Uninstallation removes Aetherium-owned components and restores your prior system state:

```bash
bash uninstall.sh
```

### 5.1 What Uninstallation Does
- **Restores KDE Plasma Lock Screen:** Reverts `plasmashellrc` and `kscreenlockerrc` to their exact pre-installation states (or deletes keys if they were unset in default KDE).
- **Restores SDDM Greeter:** Safely removes `/etc/sddm.conf.d/zz-aetherium.conf` and restores the previously active display manager theme.
- **Cleans Session Environment:** Removes `~/.config/environment.d/aetherium.conf` and `~/.config/plasma-workspace/env/aetherium.sh`.
- **Removes User Services & Autostart:** Removes `aetherium-autostart` and `aetherium-shell.service`.
- **Offers Snapshot Selection:** Allows restoring any previous configuration snapshot from `~/.local/state/aetherium/backups/`.
- **Preserves Unrelated Data:** Leaves your applications, personal files, and unrelated KDE settings intact.

### 5.2 Emergency TTY Recovery

If an issue occurs with your graphical display manager:
1. Switch to a text console (TTY) by pressing `Ctrl + Alt + F3`.
2. Log in with your standard user credentials.
3. Revert the SDDM display manager theme:
   ```bash
   sudo ./core/sddm-adapter/aetherium-sddm-adapter.sh --rollback
   sudo systemctl restart sddm.service
   ```
4. Or run the full uninstaller:
   ```bash
   bash ./uninstall.sh
   ```
5. Return to your graphical session with `Ctrl + Alt + F1` or `F2`.

---

## 6. Diagnostics & System Health Checks

Aetherium includes a dedicated diagnostic utility: `aetherium-doctor`.

```bash
# Run interactive diagnostic report
aetherium-doctor

# Emit machine-readable JSON report
aetherium-doctor --json

# Validate configuration tokens and shell schema
aetherium-doctor --validate-configs
```

The diagnostic utility:
- Requires no root privileges.
- Exposes zero passwords, tokens, or private environment variables.
- Semantically validates `~/.config/aetherium/shell.json` and `tokens.json`.
- Returns formal exit codes (`0` ready, `1` config error, `2` missing deps, `3` unsupported env).

---

## 7. Developer Commands

The root `Makefile` provides standard developer targets:

```bash
make help          # Show available targets
make install       # Run interactive installer (bash install.sh)
make update        # Run system updater (bash update.sh)
make uninstall     # Run uninstaller (bash uninstall.sh)
make test          # Run automated test suite (32 tests)
make doctor        # Run system diagnostics
make validate      # Validate design tokens and configuration schemas
make build-shell   # Build native C++ plugins via CMake
make check         # Syntax check all shell scripts (bash -n)
make clean         # Remove temporary build artifacts
```

---

## 8. Implementation & Verification Status

| Component | Status | Details / Verification Method |
| :--- | :--- | :--- |
| **Interactive Installer Workflow** | **Verified** | Caelestia-modeled `install.sh`, modular `scripts/` (`00-*` to `10-*`), profile selection, and non-interactive mode verified via unit tests. |
| **System Updater (`update.sh`)** | **Verified** | Git auto-stash, preference persistence (`install.env`), pre-update backup, and live shell reload verified. |
| **Uninstaller (`uninstall.sh`)** | **Verified** | Snapshot restoration, SDDM rollback, lockscreen KConfig key deletion, and clean removal verified. |
| **SDDM Greeter Adapter** | **Verified** | Same-filesystem atomic staging, dual themes (`aetherium`, `clockwork`), and no-auto-restart safety verified. |
| **Clockwork SDDM Theme** | **Verified** | Qylock neo-orbital theme (`metadata.desktop`, `Main.qml`, `font/`, fallback `bg.png`) integrated and contract-validated. |
| **Plasma Lock Screen Package** | **Verified** | `metadata.json`, QML components, and PAM authenticator integration verified via `test_lockscreen.py`. |
| **Diagnostic Engine (`aetherium-doctor`)** | **Verified** | JSON reporting, exit codes, and semantic schema validation verified via `test_doctor.py`. |
| **C++ Desktop Shell Plugins** | **Implemented (Pending Runtime)** | CMake configuration and C++ source code in `desktop/`; native compilation verified when Qt6/KF6 dev packages are present. |

---

## 9. Documentation Index

- [Architecture & Reconnaissance](docs/ARCHITECTURE.md)
- [Installation Guide](docs/INSTALLATION.md)
- [System Compatibility Matrix](docs/COMPATIBILITY.md)
- [SDDM Integration & Ryoku / Clockwork Contract](docs/SDDM_INTEGRATION.md)
- [In-Session Lock Screen Integration](docs/LOCKSCREEN_INTEGRATION.md)
- [Backup, Rollback & Recovery](docs/BACKUP_AND_RECOVERY.md)
- [Troubleshooting & Diagnostics](docs/TROUBLESHOOTING.md)
- [Developer Guide](docs/DEVELOPMENT.md)
- [Third-Party Licenses & Notices](THIRD_PARTY_LICENSES.md)

---

## 10. License

Aetherium OS is licensed under the **GNU General Public License version 3 (GPL-3.0)**.
Upstream components are subject to their respective licenses. See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for details.
