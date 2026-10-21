# Horizon OS — Third-Party Software & Component Licenses

Horizon OS bundles and integrates several open-source third-party components to provide a cohesive desktop experience. This document records upstream provenance, authors, licenses, and modifications for each component.

---

## 1. Component Inventory

| Component | Upstream Source & Author | License | Horizon OS Modifications | Redistribution Status |
| :--- | :--- | :--- | :--- | :--- |
| **Caelestia KDE** | [`ladybug-me/caelestia-kde`](https://github.com/ladybug-me/caelestia-kde) | **GPL-3.0-or-later** | Patched to remove SDDM override, disable lockscreen hijacking, and apply Horizon paths and systemd autostart. | Permitted (Source offers & patches provided) |
| **M3Shapes** | [`caelestia-dots/M3Shapes`](https://github.com/caelestia-dots/M3Shapes) | **MIT** | Pinned Qt6-compatible submodule for Caelestia shell widgets. | Permitted |
| **Yet Another Monochrome Icon Set** | Caelestia project contributors | **GPL-3.0** | Bundled inside Caelestia shell assets for system status icons. | Permitted |
| **Ryoku SDDM Theme** | Derived from Clockwork / Qylock Orbital by Darkkal44 | **GPL-3.0-or-later** | Patched background to pure black (`#000000`), renamed theme identifier to `ryoku`, added Horizon metadata. | Permitted |
| **Overload Splash Screen** | KDE Plasma Look-and-Feel Community | **LGPL-3.0-or-later** / **GPL-2.0+** | Packaged for Plasma 6 look-and-feel engine. | Permitted |
| **Candy Bar (`candy-icons`)** | Sweet / Candy Icons by EliverLara | **GPL-3.0** | Packaged under `/usr/share/icons/candy-icons`. | Permitted |
| **Google Sans Flex / Material Symbols** | Google Fonts | **OFL-1.1** / **Apache-2.0** | Font assets utilized by Caelestia QML interfaces. | Permitted |
| **Horizon Wallpaper Suite** | Horizon OS Design Contributors | **CC-BY-SA 4.0** | Custom artwork placed in `/usr/share/wallpapers/horizon/`. | Permitted |

---

## 2. License Texts & Upstream Notices

### 2.1 Caelestia KDE Port (GNU General Public License v3.0)
Caelestia KDE is licensed under the GNU General Public License v3.0 or later. Full source code, submodules, and applied patches are distributed in `custom-components/caelestia-kde/`.

Applied patches:
- `0001-horizon-remove-sddm-override.patch`: Prevents Caelestia from overwriting `/etc/sddm.conf.d/`.
- `0002-horizon-disable-lockscreen-hijack.patch`: Keeps native KScreenLocker active and disables duplicate Caelestia lockscreen handler.
- `0003-horizon-branding-and-paths.patch`: Sets `/etc/xdg/quickshell/caelestia` search paths and systemd user unit configuration.

### 2.2 M3Shapes (MIT License)
Copyright (c) Caelestia Contributors  
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction...

### 2.3 Ryoku SDDM Theme (GNU General Public License v3.0)
Copyright (c) Darkkal44 / Horizon OS Contributors  
Distributed under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.

### 2.4 Candy Bar (`candy-icons`) (GNU General Public License v3.0)
Copyright (c) EliverLara  
Icons are distributed under GPL-3.0. Full license file is available at `custom-components/icons/candy-icons/LICENSE`.

### 2.5 Fonts (SIL Open Font License 1.1)
Fonts bundled within shell assets are licensed under the SIL Open Font License, Version 1.1.
