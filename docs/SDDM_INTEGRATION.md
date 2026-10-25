# Aetherium OS — SDDM Integration & Ryoku Adapter Contract

## 1. Overview & Architectural Decoupling

Display Manager (SDDM) integration in Aetherium OS is strictly decoupled from the desktop session lifecycle:
- The SDDM greeter executes before any user logs in, within an unprivileged system sandbox (`sddm` user).
- Desktop session shells (`quickshell`) execute after user authentication inside the graphical Wayland session.
- Consequently, SDDM themes must never rely on shell runtime singletons, private user settings, or desktop daemons.

---

## 2. SDDM Safety & Transactional Lifecycle

The Aetherium SDDM Adapter (`core/sddm-adapter/aetherium-sddm-adapter.sh`) guarantees zero disruption to working display setups through an 8-step safety lifecycle:

1. **Pre-flight Detection:** Queries whether SDDM or Plasma-Login is the active display manager.
2. **Current State Discovery:** Reads `/etc/sddm.conf` and drop-ins (`/etc/sddm.conf.d/*.conf`, `/usr/lib/sddm/sddm.conf.d/*.conf`) to determine the currently active theme.
3. **Atomic Backup & Theme Preservation:** Copies any pre-existing Aetherium theme directory to `${XDG_STATE_HOME:-$HOME/.local/state}/aetherium/sddm/theme-backup/` and records previous drop-in state in `backup-theme-state.txt` and `backup_manifest.json`.
4. **Theme Verification:** Validates that `metadata.desktop`, `theme.conf`, and `Main.qml` are present and valid before touching system directories.
5. **Greeter Verification:** Checks for `sddm-greeter-qt6` to ensure the Qt 6 runtime can execute the QML markup.
6. **Staged Same-Filesystem Deployment:** Stages theme files into `/usr/share/sddm/themes/.aetherium.staging-$$` with standard permissions (`0755` for directories, `0644` for files), verifies content integrity, and performs an atomic directory swap on the same filesystem. The prior directory is preserved as `.aetherium.old-$$` until swap completion.
7. **Clean Drop-in Configuration:** Writes `/etc/sddm.conf.d/zz-aetherium.conf` without touching or destroying unrelated system settings.
8. **Safe Rollback (No Auto-Restart):** Enables clean rollbacks from any virtual terminal without automatically killing or restarting the active display manager, preventing unexpected session loss. The operator is prompted to restart `sddm.service` when ready.

---

## 3. Ryoku Theme Integration Contract

When the external 600MB Ryoku source archive is made available, it must be integrated via this formal contract:

### 3.1 Metadata & Compatibility Requirements
- **Descriptor:** Must contain a valid `metadata.desktop` declaring:
  ```ini
  [SddmGreeterTheme]
  Name=Ryoku
  QtVersion=6
  MainScript=Main.qml
  ConfigFile=theme.conf
  ```
- **Runtime:** Must run under Qt 6 SDDM greeters. Any legacy Qt 5 components must be converted or run via compatible Qt 6 shims.

### 3.2 QML & Component Boundaries
- **Permitted Imports:**
  - `QtQuick` (>= 2.15 / Qt 6)
  - `QtQuick.Window`
  - `Qt5Compat.GraphicalEffects`
  - `QtMultimedia`
  - `SddmComponents 2.0`
- **Forbidden:** Custom compiled C++ plugins that require installation outside standard Qt QML import paths.

### 3.3 Media & Animated Backgrounds
- **Resilience:** If the theme utilizes an MP4/WebM video or dynamic GL canvas background, it **must** supply a static fallback image (`bg.png` or `assets/background.png`).
- **Graceful Failure:** If media playback errors occur (e.g. missing GStreamer or FFmpeg plugins in the SDDM greeter environment), the theme must catch `MediaPlayer.Error` and smoothly fade into the static background. The user must never be prevented from typing credentials.

### 3.4 Authentication Protocol
- Theme QML must invoke:
  ```qml
  sddm.login(username, password, sessionIndex)
  ```
- Must handle both `onLoginSucceeded` and `onLoginFailed` signals.
- Passwords must use `TextInput.Password` masking and never be logged.

---

## 4. Emergency Recovery Procedures

If the display manager encounters an error or fails to start the graphical interface:

1. Switch to a text console (TTY) by pressing:
   `Ctrl + Alt + F3` (or `F2`–`F6`).
2. Log in with your standard user account.
3. Run the Aetherium SDDM rollback command:
   ```bash
   sudo /path/to/customOS/core/sddm-adapter/aetherium-sddm-adapter.sh --rollback
   ```
4. Restart the display manager service:
   ```bash
   sudo systemctl restart sddm.service
   ```
5. Your previous working display theme will be restored immediately.
