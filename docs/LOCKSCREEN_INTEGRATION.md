# Aetherium OS — In-Session Lock Screen Integration

## 1. Overview & Security Architecture

The Aetherium in-session lock screen is engineered as an official KDE Plasma Shell Package (`themes/lockscreen/aetherium.desktop/`).

### Security Guarantees
- **KScreenLocker Native Integration:** Executes directly inside the system's `kscreenlocker_greet` process, interfacing with the authentic KDE `ScreenLocker` authenticator API (`org.kde.kscreenlocker`).
- **No PAM Hijacking:** Does not introduce custom or external PAM binaries. Authentication is processed exclusively by the privileged system daemon.
- **Grace-Lock & Lockout Compliance:** Fully honors KDE's configured grace period (unlock without password within $N$ seconds of screen blank) and exponential failed-attempt lockouts (`%1 min left`).
- **Zero Secret Leakage:** Password strings are handled via secure memory buffers in Qt, never logged to syslog/journald, and purged from memory immediately upon unlock signal.

---

## 2. Shell Package Configuration & Activation

To activate the Aetherium lock screen in KDE Plasma 6:

1. **Package Placement:**
   Installed to:
   - System-wide: `/usr/share/plasma/shells/aetherium.desktop/`
   - Or user local: `~/.local/share/plasma/shells/aetherium.desktop/`

2. **KDE Plasma Configuration:**
   KDE's lock screen greeter chooses the active theme based on the `ShellPackage` key in `plasmashellrc`:
   ```bash
   kwriteconfig6 --file plasmashellrc --group "Shell" --key "ShellPackage" "aetherium.desktop"
   kwriteconfig6 --file kscreenlockerrc --group "Greeter" --key "Theme" --delete
   ```

3. **Reversion to Default Plasma Greeter:**
   ```bash
   kwriteconfig6 --file plasmashellrc --group "Shell" --key "ShellPackage" "org.kde.plasma.desktop"
   ```

---

## 3. Visual & Aesthetic Coordination

The lock screen coordinates directly with the Aetherium Desktop Shell:
- **Typography:** Outfit & Rubik fonts matching the desktop panel clock and widget displays.
- **Dynamic Palette:** Reads dynamic color schemes from `~/.local/state/aetherium/scheme.json`, automatically matching wallpaper colors without restarting the session.
- **Atmospheric Cards:** Displays media playback info, weather status, system resources, and pending notifications with subtle frosted glass surfaces.
- **Keyboard-First Focus:** Pressing any alphanumeric key immediately focuses the password entry field.
- **Multi-Monitor Handling:** Primary display presents the interactive login pill and cards; auxiliary monitors present ambient cinematic artwork without clutter.
