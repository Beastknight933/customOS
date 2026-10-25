# Aetherium OS — Backup, Rollback & Recovery Guide

## 1. Non-Destructive Principles

Aetherium OS strictly prohibits destructive in-place replacements of system configuration.
Every installation, update, and configuration modification creates an isolated, timestamped state snapshot before touching a single file.

---

## 2. Backup Structure

Backups are preserved in:
`${XDG_STATE_HOME:-$HOME/.local/state}/aetherium/backups/backup-<YYYYMMDD_HHMMSS>/`

Snapshots capture:
1. `config_aetherium/`: Previous user configuration if present.
2. `plasma_state.txt`: Prior `ShellPackage` and `Theme` keys from `plasmashellrc` and `kscreenlockerrc`. If a key was unset in the initial state, the rollback engine deletes it via `kwriteconfig6 --delete` rather than assigning an arbitrary default.
3. `sddm.conf` / `zz-aetherium.conf`: Prior display manager configuration and backup theme directory.
4. `install-manifest.json`: A structured JSON inventory of every target installed or modified, recording `target`, `backup_path`, and `existed_before` (boolean).

---

## 3. Security & Path Safety Whitelist

During rollback or uninstallation, the rollback engine enforces a strict path security whitelist:
- Targets must reside within approved directories:
  - `${XDG_CONFIG_HOME:-$HOME/.config}/aetherium`
  - `${XDG_CONFIG_HOME:-$HOME/.config}/plasma-workspace/env/aetherium.sh`
  - `${XDG_CONFIG_HOME:-$HOME/.config}/environment.d/aetherium.conf`
  - `${XDG_DATA_HOME:-$HOME/.local/share}/plasma/look-and-feel/aetherium.desktop`
  - `${XDG_DATA_HOME:-$HOME/.local/share}/plasma/shells/aetherium.desktop`
  - `${HOME}/.local/bin/aetherium-*`
  - `${XDG_CONFIG_HOME:-$HOME/.config}/autostart/aetherium-autostart.desktop`
  - `${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user/aetherium-shell.service`
- Targets containing `..` or residing outside the approved prefixes are strictly rejected to prevent directory traversal.
- Files recorded with `"existed_before": false` are safely deleted (`rm -rf`).
- Files recorded with `"existed_before": true` are restored from their exact snapshot copies.

---

## 4. Emergency TTY Recovery

If the graphical environment encounters an issue, you can restore your prior configuration from any text console without a working GUI:

1. Switch to a TTY:
   `Ctrl + Alt + F3`
2. Log in with your standard username and password.
3. Run the automated uninstaller:
   ```bash
   cd /path/to/customOS
   ./uninstall.sh
   ```
4. Or trigger manual SDDM rollback:
   ```bash
   sudo ./core/sddm-adapter/aetherium-sddm-adapter.sh --rollback
   # Review restored configuration, then restart SDDM when ready:
   sudo systemctl restart sddm.service
   ```
5. Or revert the Plasma lockscreen manually:
   ```bash
   # If ShellPackage was previously unset (KDE default):
   kwriteconfig6 --file plasmashellrc --group "Shell" --key "ShellPackage" --delete
   # Or if a specific package was previously in use:
   kwriteconfig6 --file plasmashellrc --group "Shell" --key "ShellPackage" "<previous-package>"
   ```
6. Return to your graphical session:
   `Ctrl + Alt + F1` (or `F2`).
