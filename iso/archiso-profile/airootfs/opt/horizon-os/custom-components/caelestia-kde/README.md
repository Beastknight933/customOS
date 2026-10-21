# Caelestia KDE — Horizon OS Custom Component

This directory contains the Horizon OS-maintained build, provenance, patches, and integration rules for the Caelestia shell KDE Plasma port.

## 1. Provenance and Upstream Tracking

- **Upstream Repository**: [https://github.com/ladybug-me/caelestia-kde](https://github.com/ladybug-me/caelestia-kde)
- **Upstream Tag**: `v2.6.3`
- **Upstream Commit**: `c0cfd04d5b9da3fbf7b5f47016822888468e9829`
- **Release Archive**: `caelestia-kde-v2.6.3.tar.gz` (SHA256: `e6c2d0deea7abafa6ffda48a94bc8f5d6871639815912767a28461b523e790ac`)
- **Submodules Recovered**:
  - `src/dots`: [https://github.com/caelestia-dots/caelestia.git](https://github.com/caelestia-dots/caelestia.git) at commit `639dd6e55b8d0e95aec12499720fb6c434548022`
  - `src/yet-another-monochrome-icon-set`: [https://bitbucket.org/dirn-typo/yet-another-monochrome-icon-set](https://bitbucket.org/dirn-typo/yet-another-monochrome-icon-set) at commit `227359bea788d55d202d9aad5f2daf63fe644cc3`
  - `m3shapes`: [https://github.com/caelestia-dots/m3shapes.git](https://github.com/caelestia-dots/m3shapes.git) at revision `bdc327b29f95394a732baf3c9b19658ba23755b6`

Full machine-readable provenance is recorded in [`provenance.json`](./provenance.json).

## 2. Horizon OS Customizations and Exclusions

Horizon OS incorporates Caelestia as its primary desktop shell while preserving KDE Plasma 6 as the system desktop foundation and KWin as the window manager. To avoid architectural conflicts, the following rules and patches are maintained:

1. **SDDM Exclusion (`patches/0001-horizon-remove-sddm-override.patch`)**:
   Upstream Caelestia packages its own SDDM theme and attempts to install `/etc/sddm.conf.d/zz-caelestia.conf` with `Current=caelestia`. This is strictly stripped. Horizon OS exclusively runs the custom Ryoku Orbital SDDM theme configured via `/etc/sddm.conf.d/99-ryoku.conf`.

2. **Lockscreen Hijack Protection (`patches/0002-horizon-disable-lockscreen-hijack.patch`)**:
   Upstream scripts attempt to dynamically rewrite `plasmashellrc` and `kscreenlockerrc` to force `caelestia.desktop` as the lockscreen greeter. Horizon OS disables this mechanism so that the standard KScreenLocker greeter and Dishonored atmospheric wallpaper run uninterrupted.

3. **Horizon OS Branding (`patches/0003-horizon-branding-and-paths.patch`)**:
   Sets the distributor token to `Horizon OS` and establishes predictable paths for Quickshell configuration (`~/.config/caelestia/shell.json`).

4. **Curated Configuration**:
   - Bar located at screen `top`
   - Bar visibility set to `hover` (`persistent: false`, `showOnHover: true`)
   - Empty dock pinned apps (`pinnedApps: []`)
   - Caelestia background layer disabled (`background.enabled: false`) so KDE desktop widgets and icons function normally
   - Visual effects restrained with controlled transparency (`base: 0.15`, `layers: 0.25`)

## 3. Directory Structure

```text
custom-components/caelestia-kde/
├── upstream/             # Complete upstream source tree (v2.6.3)
├── patches/              # Horizon OS integration patches
├── configuration/        # Horizon default shell.json and shell-tokens.json
├── packaging/            # Horizon Arch PKGBUILD, systemd unit, autostart script
├── build/                # Reproducible CMake/Ninja build driver (build.sh)
├── provenance.json       # Pinned upstream hashes and provenance record
└── README.md             # This document
```

## 4. Building and Installation

To build and stage both the main shell and KWin workspace tracker:

```bash
./build/build.sh
```

Or package with `makepkg`:

```bash
cd packaging && makepkg -si
```
