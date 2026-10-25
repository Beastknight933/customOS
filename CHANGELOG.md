# Aetherium OS Changelog

All notable changes to the Aetherium OS project will be documented in this file.

## [1.1.0] - 2026-10-25 — Caelestia KDE Installation Model Rework

### Added & Reworked
- **Authoritative Root Entry Points (`install.sh`, `update.sh`, `uninstall.sh`):**
  - `install.sh`: Supports local execution (`bash install.sh`) and piped remote execution (`curl -fsSL ... | bash`), automatically reconnecting to `/dev/tty` for interactive wizard mode.
  - `update.sh`: Single-command updater that preserves user preferences (`install.env`), safely stashes uncommitted local git changes, pulls latest branch commits, creates pre-update backup snapshots, rebuilds components, updates active integrations, and reloads the desktop shell live without losing session state.
  - `uninstall.sh`: Single-command uninstaller offering snapshot restoration from `~/.local/state/aetherium/backups/`, reverting Plasma lockscreen configuration, safely removing SDDM drop-ins, and cleaning session environments and autostart units while preserving user applications and personal data.
- **Modular Step Script Architecture (`scripts/`):**
  - Restructured installation lifecycle into numbered modular step scripts matching Caelestia KDE:
    - `00-backup-themes.sh`: Transactional state snapshot creation.
    - `00a-system-update.sh`: Distribution package upgrades (optional/skippable).
    - `01-ensure-prereqs.sh`: Build toolchain and package manager verification (`yay`, `dnf`, `apt`).
    - `02-all-packages.sh`: Distribution package resolution.
    - `03-deploy-configs.sh`: Deployment of `~/.config/aetherium/` schemas and tokens.
    - `04-deploy-session.sh`: Registration of `environment.d` and `plasma-workspace/env` drop-ins.
    - `05-sddm-theme.sh`: Transactional SDDM greeter installation.
    - `06-lockscreen.sh`: Plasma `aetherium.desktop` lockscreen package deployment.
    - `08-build-shell.sh`: CMake compilation of native C++ plugins with build logging and QML fallback.
    - `10-autostart.sh`: Systemd user service, autostart entries, and CLI utilities installation.
    - `setup.sh`: Master setup runner coordinating interactive TUI, CLI wizard, and non-interactive profiles.
- **Interactive TUI & Data Schemas (`installer/`):**
  - Integrated C++ TUI installer source (`installer/tui/`) adapted for Aetherium OS (`aetherium-install`).
  - Added `installer/data/menu.json` and `installer/data/theme.json` with Aetherium obsidian/azure palette and ASCII art.
  - Added distribution package mappings (`installer/distro/arch`, `fedora`, `debian`).
- **Qylock Clockwork SDDM Theme Integration:**
  - Integrated `themes/sddm/clockwork` (neo-orbital clockwork theme from Qylock) as a first-class selectable SDDM option alongside the baseline Aetherium theme.
  - Validated Qt6 SDDM contract (`metadata.desktop`, `Main.qml`, `font/`, fallback `bg.png`).
- **Developer Makefile:**
  - Added targets: `install`, `update`, `uninstall`, `build-shell`, `installer`, `doctor`, `validate`, `test`, `check`, `clean`.
- **Automated Test Suite Expansion:**
  - Expanded test suite from 25 to 32 unit tests, verifying root entry points, script modularity, TUI data schemas, Clockwork theme contract, and full non-interactive desktop installation & uninstallation workflow.

## [1.0.1] - 2026-10-25 — Safety Hardening & Verification Audit

### Hardened & Fixed
- **Diagnostic Engine (`aetherium-doctor`):**
  - Implemented semantic validation for `shell.json` and `tokens.json` verifying required keys, layout structures, and styling values.
  - Implemented formal exit codes (`EXIT_READY=0`, `EXIT_CONFIG_ERROR=1`, `EXIT_MISSING_DEPS=2`, `EXIT_UNSUPPORTED_ENV=3`).
  - Added structured JSON reporting (`--json`) outputting operating system, desktop session, Plasma/Qt versions, Quickshell, SDDM, lockscreen, utilities, and configuration checks.
  - Enforced unprivileged execution without requiring root and eliminated any risk of leaking sensitive environment variables or secrets.
- **SDDM Adapter (`aetherium-sddm-adapter.sh`):**
  - Replaced destructive directory deletion with staged deployment on the same filesystem (`/usr/share/sddm/themes/.aetherium.staging-$$`).
  - Implemented atomic directory swap preserving prior installation (`.aetherium.old-$$`) until validation succeeds.
  - Created complete backup manifest of existing theme and `/etc/sddm.conf.d/` drop-ins prior to replacement.
  - Hardened rollback to restore prior theme and drop-in configuration without automatically killing or restarting `sddm.service`.
- **Installer & Rollback Engine (`installer/lib/backup.sh`, `installer/lib/rollback.sh`):**
  - Upgraded backup manifest to structured JSON (`install-manifest.json`) tracking target path, backup location, and `existed_before` flag.
  - Implemented strict path security whitelist preventing directory traversal or manipulation of unintended paths.
  - Updated rollback to delete files that did not exist before installation (`"existed_before": false`) rather than leaving empty or dangling files.
  - Restored KDE Plasma lockscreen configuration accurately: if `ShellPackage` or `Theme` was previously unset, rollback deletes the key via `kwriteconfig6 --delete` rather than setting an arbitrary default.
  - Integrated session environment variables into `~/.config/environment.d/aetherium.conf` and `~/.config/plasma-workspace/env/aetherium.sh` ensuring `QML2_IMPORT_PATH` is exported for `kscreenlocker_greet` and Quickshell.
- **Automated Verification:**
  - Expanded automated test suite to 25 unit tests covering token validity, config schemas, diagnostic output, semantic error handling, SDDM staged installation/rollback, and installer path whitelist safety.
  - Verified bash script syntax across all 15 shell scripts.

## [1.0.0] - 2026-10-25

### Added
- **Aetherium Design System (Layer A):** Centralized semantic tokens, atmospheric dark and light palettes (`desktop/schemes/aetherium`), and `AetheriumTheme` QML singleton.
- **Aetherium Desktop Shell (Layer B):** Integrated Wayland desktop shell foundation adapted from Caelestia KDE, supporting bar zones, floating dock, workspace indicators, and fuzzy application searching.
- **Integration Services & Diagnostics (Layer C):** Standalone `aetherium-doctor` CLI utility for system health checking and configuration validation.
- **SDDM Integration Framework (Layer D):** Transactional SDDM adapter (`aetherium-sddm-adapter`) with 8-step safety lifecycle, pre-flight verification, atomic backups, and the baseline Aetherium SDDM theme.
- **Ryoku Integration Contract:** Documented architectural and technical contract in `docs/SDDM_INTEGRATION.md` for seamless ingestion of external 600MB theme archive.
- **In-Session Plasma Lock Screen (Layer E):** Native KDE Plasma shell package (`aetherium.desktop`) interfacing with `org.kde.kscreenlocker` and PAM authenticator.
- **Safe Installer & Rollback Engine (Layer F):** Modular installer supporting 4 distinct deployment profiles (`desktop`, `desktop-lockscreen`, `full`, `custom`), atomic manifest tracking, and clean uninstallation.
- **Comprehensive Test Suite:** Automated Python unit test suite verifying tokens, configuration files, SDDM metadata, and installer mechanics.
