# Horizon OS — Singularity Edition
### Custom Arch Linux-Based Operating System, Terminal Installer, Caelestia KDE Port, Ryoku SDDM & Unified Desktop Integration

```
  ██╗  ██╗ ██████╗ ██████╗ ██╗███████╗ ██████╗ ███╗   ██╗     ██████╗ ███████╗
  ██║  ██║██╔═══██╗██╔══██╗██║╚══███╔╝██╔═══██╗████╗  ██║    ██╔═══██╗██╔════╝
  ███████║██║   ██║██████╔╝██║  ███╔╝ ██║   ██║██╔██╗ ██║    ██║   ██║███████╗
  ██╔══██║██║   ██║██╔══██╗██║ ███╔╝  ██║   ██║██║╚██╗██║    ██║   ██║╚════██║
  ██║  ██║╚██████╔╝██║  ██║██║███████╗╚██████╔╝██║ ╚████║    ╚██████╔╝███████║
  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝     ╚═════╝ ╚══════╝
```

---

## 1. Product Overview

**Horizon OS** is a custom Arch Linux-based operating system designed for maximum desktop immersion, speed, and aesthetics. Built around **KDE Plasma 6** and **KWin**, it combines an automated full-screen Terminal User Interface (TUI) installer with a customized integration of the **Caelestia KDE shell port**, the **Ryoku Orbital Clockwork SDDM theme**, the **Overload splash screen**, and the **Candy Bar (`candy-icons`)** icon suite.

### Key Highlights
- **KDE Plasma 6 & KWin Foundation**: KWin runs as the native Wayland compositor. Plasma desktop widgets and services are fully preserved.
- **Caelestia Shell Integration**: Custom-built from the `caelestia-kde` port (`v2.6.3`) powered by Quickshell, C++ plugins, and a native KWin workspace-tracker effect.
- **Atmospheric Visual Identity**: Deep dark aesthetic fusing Celestia geometric indicators, Lord of the Mysteries (LOTM) Victorian occult tones, and Dishonored / Steampunk clockwork mechanisms.
- **Pure Black Ryoku SDDM Greeter**: Custom Qylock/Clockwork Orbital login theme patched to enforce pitch black background across all branches.
- **CachyOS Performance Layer**: CPU-optimized `linux-cachyos` BORE kernel, auto-nice daemon (`ananicy-cpp`), and `x86_64_v3` AVX2/BMI2 binary repositories.
- **Full-Screen Terminal Installer**: Automated interactive TUI with disk detection, partition planning (Btrfs with optimized subvolumes or Ext4), user setup, and verification.

---

## 2. Desktop Architecture

```
┌────────────────────────────────────────────────────────┐
│                   SDDM Login Greeter                   │
│        (Horizon Ryoku Orbital SDDM Theme - Pure Black) │
└──────────────────────────┬─────────────────────────────┘
                           │ Authenticates User Session
                           ▼
┌────────────────────────────────────────────────────────┐
│                   KDE Plasma 6 / KWin                  │
│       • Wayland Compositor (KWin)                      │
│       • KScreenLocker (Atmospheric Dishonored Art)     │
│       • KDE Services & Audio (PipeWire / WirePlumber)  │
│       • Candy Bar Icon Theme (candy-icons)             │
│       • Overload Splash Screen                         │
└──────────────────────────┬─────────────────────────────┘
                           │ Manages Desktop Windows & Bridge
                           ▼
┌────────────────────────────────────────────────────────┐
│                 Caelestia Desktop Shell                │
│       • Quickshell Engine & Native C++ Plugins         │
│       • KWin Workspace-Tracker Effect Plugin           │
│       • Top Bar with Auto-Hide / Hover Activation      │
│       • Uncluttered Center Dock (No Default Pinned)    │
│       • Restrained Transparency & Pitch-Black Theme    │
│       • KDE Plasma Desktop Widgets Preserved           │
└────────────────────────────────────────────────────────┘
```

### Critical Architectural Invariants
1. **No Caelestia SDDM Theme**: Upstream Caelestia attempts to install `Current=caelestia` in `/etc/sddm.conf.d/zz-caelestia.conf`. Horizon OS strictly strips this override; the Ryoku Orbital SDDM theme remains active.
2. **Preserved KScreenLocker**: Upstream Caelestia scripts attempt to dynamically rewrite `plasmashellrc` and `kscreenlockerrc`. Horizon OS disables this hijack via patches to protect the intended atmospheric lockscreen.
3. **Plasma Widgets Functional**: Caelestia's background canvas and wallpaper drawing are disabled (`background.enabled: false`) so KDE Plasma desktop widgets, folders, and icons function without collision.

---

## 3. Repository Layout

```text
horizon-os/
├── README.md                          # Master documentation
├── LICENSE                            # GPL-3.0-or-later
├── CONTRIBUTING.md                     # Contribution guidelines
├── SECURITY.md                       # Security policy
├── .gitignore                         # Build artifact ignore rules
├── install.sh                         # Master installation entrypoint
├── installer/                         # TUI installer engine
│   ├── horizon-tui.py                 # Full-screen Python TUI installer
│   ├── horizon-installer              # Compiled standalone static Linux binary
│   ├── backend/
│   │   ├── hardware.py                # CPU, RAM, GPU, UEFI probing
│   │   ├── storage.py                 # Disk discovery & partition planning
│   │   ├── executor.py                # Command runner with dry-run support
│   │   ├── deployer.py                # Component deployment runner
│   │   └── validator.py               # 10-point post-install verification suite
│   └── tui-go/                        # Standalone Go TUI source
├── profiles/
│   ├── horizon-desktop.yaml           # Desktop architecture & visual profile
│   └── cachyos-kde-profile.yaml       # Full package manifest & CachyOS repos
├── packages/
│   ├── arch-base/                     # Base system package list & pacman.conf
│   ├── kde-desktop/                   # KDE Plasma & Caelestia runtime packages
│   └── caelestia-kde/                 # Horizon PKGBUILD, unit, autostart
├── custom-components/
│   ├── ryoku-sddm/                    # Patched Clockwork Orbital SDDM theme
│   ├── splash/                        # Overload Plasma 6 splash screen
│   ├── icons/                         # Candy Bar (candy-icons) icon suite
│   └── caelestia-kde/
│       ├── upstream/                  # Extracted upstream source (v2.6.3)
│       ├── patches/                   # Horizon OS integration patches
│       ├── packaging/                 # PKGBUILD & service files
│       ├── configuration/             # Horizon shell.json & shell-tokens.json
│       ├── build/                     # CMake build driver (build.sh)
│       ├── provenance.json            # Pinned upstream hashes & gitlinks
│       └── README.md
├── defaults/
│   ├── kde/                           # kdeglobals, ksplashrc, kwinrc, kscreenlockerrc
│   ├── shell/                         # shell.json, shell-tokens.json
│   ├── sddm/                          # 99-ryoku.conf
│   └── visual-identity/               # Wallpapers, palette & styling guide
├── scripts/
│   ├── build-all.sh                   # Build driver for all components
│   ├── deploy-horizon.sh              # Standalone deployment runner
│   ├── verify-installation.sh         # Compliance verification runner
│   └── run-vm-test.sh                 # Disposable QEMU test VM launcher
├── tests/
│   ├── unit/                          # Manifest, config, storage & exclusion tests
│   └── integration/                   # End-to-end simulated deployment test
├── docs/
│   ├── architecture.md                # System architecture documentation
│   ├── installation.md                # Installation manual (ISO, VM, bare-metal)
│   ├── component-builds.md            # Build instructions for each component
│   ├── asset-requirements.md          # Asset inventory & missing assets registry
│   ├── recovery.md                    # Emergency recovery & chroot guide
│   └── troubleshooting.md             # Diagnostics, journals & common solutions
└── iso/
    └── archiso-profile/               # archiso profile for building Horizon ISO
```

---

## 4. Provenance & Submodule Audit

The Caelestia KDE shell port used in Horizon OS is pinned to official upstream release `v2.6.3`:

- **Upstream Repository**: `https://github.com/ladybug-me/caelestia-kde`
- **Git Commit**: `c0cfd04d5b9da3fbf7b5f47016822888468e9829`
- **Release Tarball SHA256**: `e6c2d0deea7abafa6ffda48a94bc8f5d6871639815912767a28461b523e790ac`
- **Recovered Submodule `src/dots`**: Commit `639dd6e55b8d0e95aec12499720fb6c434548022`
- **Recovered Submodule `src/yet-another-monochrome-icon-set`**: Commit `227359bea788d55d202d9aad5f2daf63fe644cc3`
- **Pinned M3Shapes Revision**: `bdc327b29f95394a732baf3c9b19658ba23755b6`

Full details are recorded in [`custom-components/caelestia-kde/provenance.json`](./custom-components/caelestia-kde/provenance.json).

---

## 5. Quick Installation Instructions

### Launch from Arch Linux Live ISO
```bash
git clone https://github.com/Beastknight933/customOS.git /root/horizon-os
cd /root/horizon-os
./install.sh
```

### Dry-Run Simulation (Safe Test)
```bash
./install.sh --dry-run
```

### Post-Installation Verification
```bash
./scripts/verify-installation.sh /mnt
```

### Test in Disposable QEMU Virtual Machine
```bash
./scripts/run-vm-test.sh path/to/archlinux-latest-x86_64.iso
```

---

## 6. Running the Automated Test Suite

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

All 17 unit and integration tests validate package manifests, configuration schemas, Ryoku patches, component exclusions, storage calculations, and mock end-to-end deployments.
