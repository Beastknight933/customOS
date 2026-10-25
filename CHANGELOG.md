# Aetherium OS Changelog

All notable changes to the Aetherium OS project will be documented in this file.

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
