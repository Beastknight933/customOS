# Aetherium OS Changelog

All notable changes to the Aetherium OS project will be documented in this file.

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
