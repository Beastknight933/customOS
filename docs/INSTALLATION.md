# Aetherium OS — Installation & Lifecycle Guide

## 1. Architecture & Design Principles

Aetherium OS employs the installation architecture pioneered by `ladybug-me/caelestia-kde`:
- **Single Root Entry Point:** Run `bash install.sh` to install, `bash update.sh` to update, and `bash uninstall.sh` to revert.
- **Interactive TUI / CLI Selection:** Choose between preconfigured profiles or customize components interactively.
- **Zero Manual Compilation Required:** Native C++ plugins are built automatically during the installation process via CMake, or run in QML compatibility mode if development packages are absent.
- **Safe & Non-Destructive:** Every modified configuration file and theme is backed up to a timestamped state snapshot before changes are written.

---

## 2. Prerequisites

| Component | Minimum Requirement | Notes |
| :--- | :--- | :--- |
| **Operating System** | Arch Linux / CachyOS, Fedora 40+, Debian 13 / Ubuntu 24.04+ | Supported package managers: `pacman`/`yay`, `dnf`, `apt-get` |
| **Desktop Session** | KDE Plasma 6.0+ | Plasma 5 is unsupported |
| **Display Server** | Wayland 1.22+ (`XDG_SESSION_TYPE=wayland`) | `wlr-layer-shell` and `ext-session-lock-v1` |
| **Core Runtime** | `quickshell` (>= 0.0.12), `python3` | Qt 6.6+ Declarative & 5Compat |

---

## 3. Installation Workflows

### 3.1 Local Checkout (Standard)

```bash
git clone https://github.com/Beastknight933/customOS.git
cd customOS
bash install.sh
```

### 3.2 One-Command Remote Execution

Aetherium supports one-command installation via curl:

```bash
curl -fsSL https://raw.githubusercontent.com/Beastknight933/customOS/main/install.sh | bash
```

The script detects piped execution, reconnects standard input and output to `/dev/tty`, clones or updates the repository into `~/customOS`, and runs the interactive setup.

---

## 4. Installation Profiles & Options

During installation, select from four profiles:

1. **Aetherium Desktop:**
   - Installs the Wayland desktop shell, bar zones, fuzzy application search launcher, overview, and design system tokens.
   - Deploys session environment variables to `~/.config/environment.d/aetherium.conf` and `~/.config/plasma-workspace/env/aetherium.sh`.
   - Registers user autostart units.
2. **Desktop + Lock Screen (Recommended):**
   - Installs the full desktop shell.
   - Installs and activates the matching `aetherium.desktop` Plasma lockscreen package.
3. **Full Aetherium Experience:**
   - Desktop shell + Plasma lockscreen package.
   - Transactional SDDM Greeter theme (`aetherium` or `clockwork`).
4. **Custom Installation:**
   - Interactive toggles for each component, theme variant, and system package upgrade.

### Scripted / Non-Interactive Flags

Pass CLI arguments to bypass prompts:

```bash
# Install Desktop + Lock Screen profile without prompts
bash install.sh --profile desktop-lockscreen --non-interactive --skip-update

# Install Full profile with Clockwork SDDM theme
bash install.sh --profile full --sddm-theme clockwork --non-interactive --skip-update
```

---

## 5. Updating Aetherium OS

Update your installation at any time using:

```bash
bash update.sh
```

The updater:
1. Loads persistent user settings from `~/.config/aetherium/install.env`.
2. Stashes local git changes safely before pulling latest remote commits.
3. Creates a pre-update configuration snapshot.
4. Rebuilds native plugins and syncs updated configuration files.
5. Refreshes the running shell seamlessly via `aetherium-autostart` without logging out.

---

## 6. Uninstallation & Rollback

To revert changes and restore prior configurations:

```bash
bash uninstall.sh
```

The uninstaller:
- Prompts for confirmation.
- Discovers existing snapshots in `~/.local/state/aetherium/backups/` and allows restoring to any prior snapshot.
- Reverts `plasmashellrc` and `kscreenlockerrc` lockscreen settings.
- Reverts SDDM drop-in configurations.
- Cleans up session environment files and autostart units.
- Leaves unrelated user applications and data intact.

---

## 7. Diagnostics & Troubleshooting

Run the diagnostic utility at any time:

```bash
# Comprehensive diagnostic summary
aetherium-doctor

# Configuration syntax & semantic validation
aetherium-doctor --validate-configs

# Machine-readable JSON report
aetherium-doctor --json
```

If the display manager encounters an issue, switch to a text console (`Ctrl + Alt + F3`), log in, and execute:

```bash
sudo ./core/sddm-adapter/aetherium-sddm-adapter.sh --rollback
sudo systemctl restart sddm.service
```
