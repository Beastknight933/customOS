# Aetherium OS — Developer Guide

## 1. Project Directory Layout

```text
customOS/
├── desktop/                # Aetherium Desktop Shell & C++ Qt6 Plugin
│   ├── config/             # Authoritative design tokens & shell settings
│   ├── modules/            # QML modules: bar, launcher, overview, drawers, osd
│   ├── components/         # Reusable QML components & animations
│   ├── services/           # Platform bridges & AetheriumTheme singleton
│   ├── schemes/            # Atmospheric M3 color schemes
│   └── plugin/             # C++ Qt6 extension plugin (Caelestia / Aetherium)
├── themes/
│   ├── sddm/               # Aetherium SDDM theme baseline
│   └── lockscreen/         # Aetherium Plasma lockscreen package (aetherium.desktop)
├── core/
│   ├── bin/                # aetherium-doctor, aetherium-autostart
│   └── sddm-adapter/       # Transactional SDDM configuration engine
├── installer/              # Safe transactional installer, updater, and uninstaller
├── packaging/              # PKGBUILD, systemd user services, autostart entries
├── tests/                  # Automated test suites
└── docs/                   # System architecture and technical guides
```

---

## 2. Local Development & Testing

Run unit and integration tests:
```bash
make test
```

Validate design tokens and configuration schemas:
```bash
make validate
```

Inspect environment diagnostics:
```bash
make doctor
```
