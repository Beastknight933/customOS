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
2. `plasma_state.txt`: Prior `ShellPackage` and `Theme` keys from `plasmashellrc` and `kscreenlockerrc`.
3. `sddm.conf` / `zz-aetherium.conf`: Prior display manager configuration.
4. `install-manifest.json`: An inventory of every file installed or modified during the session.

---

## 3. Emergency TTY Recovery

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
   sudo systemctl restart sddm.service
   ```
5. Or revert the Plasma lockscreen:
   ```bash
   kwriteconfig6 --file plasmashellrc --group "Shell" --key "ShellPackage" "org.kde.plasma.desktop"
   ```
6. Return to your graphical session:
   `Ctrl + Alt + F1` (or `F2`).
