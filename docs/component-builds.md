# Horizon OS — Component Builds & Packaging Guide

This guide details how each custom component is compiled, patched, and staged for installation.

## 1. Caelestia KDE Main Shell & KWin Workspace Tracker

- **Source Location**: `custom-components/caelestia-kde/upstream/`
- **Source Revision**: `v2.6.3` (commit `c0cfd04d5b9da3fbf7b5f47016822888468e9829`)
- **Build Driver**: `custom-components/caelestia-kde/build/build.sh`

### Building the Main Shell
```bash
cmake -B build -S shell -G Ninja \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DCMAKE_INSTALL_PREFIX=/ \
  -DVERSION="2.6.3" \
  -DINSTALL_DATADIR=usr/share/caelestia \
  -DCAELESTIA_PACKAGE=ON \
  -DREQUIRE_CAVA=ON \
  -DDISTRIBUTOR="Horizon OS"

cmake --build build
```

### Building the KWin Workspace-Tracker Effect
```bash
cmake -B effect-build \
  -S shell/kwin-effects/workspace-tracker \
  -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=/usr

cmake --build effect-build
```

### Horizon Patches Applied
1. `patches/0001-horizon-remove-sddm-override.patch`: Excludes upstream SDDM theme installation.
2. `patches/0002-horizon-disable-lockscreen-hijack.patch`: Prevents overwriting `kscreenlockerrc`.
3. `patches/0003-horizon-branding-and-paths.patch`: Sets distributor identity and ensures predictable environment variables.

---

## 2. Ryoku SDDM Theme (Orbital Clockwork Pure Black)

- **Source Location**: `custom-components/ryoku-sddm/`
- **Target Path**: `/usr/share/sddm/themes/ryoku`
- **Configuration**: `/etc/sddm.conf.d/99-ryoku.conf`
- **Modifications**:
  - `patches/0001-force-black-background.patch`:
    ```qml
    - readonly property color bgColor: isLight ? "#ffffff" : "#000000"
    + readonly property color bgColor: isLight ? "#000000" : "#000000"
    ```
- **Deployment**:
  ```bash
  bash custom-components/ryoku-sddm/install.sh /target
  ```

---

## 3. Overload Splash Screen

- **Source Location**: `custom-components/splash/`
- **KPackage ID**: `Overload` (Version `2.0.2` by kloud / dgudim)
- **Target Path**: `/usr/share/plasma/look-and-feel/Overload`
- **Configuration**: `/etc/xdg/ksplashrc`:
  ```ini
  [KSplash]
  Engine=KSplashQML
  Theme=Overload
  ```

---

## 4. Candy Bar Icon Theme (candy-icons)

- **Source Location**: `custom-components/icons/candy-icons/`
- **Internal ID**: `candy-icons` (by EliverLara)
- **Target Path**: `/usr/share/icons/candy-icons`
- **Configuration**: `/etc/xdg/kdeglobals`:
  ```ini
  [Icons]
  Theme=candy-icons
  ```
