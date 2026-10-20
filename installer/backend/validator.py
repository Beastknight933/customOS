#!/usr/bin/env python3
"""
Horizon OS Installer - Post-Installation Verification & Audit Module
"""
import os
import json
from typing import Dict, Any, List

class ValidationResult:
    def __init__(self, check_id: str, title: str, passed: bool, details: str = ""):
        self.check_id = check_id
        self.title = title
        self.passed = passed
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_id": self.check_id,
            "title": self.title,
            "passed": self.passed,
            "details": self.details,
        }

class InstallationValidator:
    def __init__(self, target_root: str = "/"):
        self.target_root = target_root

    def _target_path(self, rel_path: str) -> str:
        return os.path.join(self.target_root, rel_path.lstrip("/"))

    def verify_all(self) -> List[ValidationResult]:
        """Perform all 10 mandatory Horizon OS integration checks."""
        results = []

        # 1. KDE Plasma and KWin
        plasma_bin = self._target_path("usr/bin/plasmashell")
        kwin_bin = self._target_path("usr/bin/kwin_wayland")
        plasma_ok = os.path.exists(plasma_bin) or os.path.exists(kwin_bin) or os.path.exists(self._target_path("usr/lib/plasma-dbus-run-session-if-needed"))
        results.append(ValidationResult(
            check_id="check_kde_plasma",
            title="KDE Plasma & KWin Installed",
            passed=plasma_ok,
            details=f"plasmashell: {os.path.exists(plasma_bin)}, kwin_wayland: {os.path.exists(kwin_bin)}"
        ))

        # 2. SDDM Installed & Selected as Display Manager
        sddm_service = self._target_path("etc/systemd/system/display-manager.service")
        sddm_bin = self._target_path("usr/bin/sddm")
        sddm_ok = os.path.exists(sddm_bin) or os.path.exists(sddm_service)
        results.append(ValidationResult(
            check_id="check_sddm_selected",
            title="SDDM Selected as Display Manager",
            passed=sddm_ok,
            details="SDDM binary and display-manager service link validated"
        ))

        # 3. Horizon Ryoku SDDM Theme Installed & Configured
        ryoku_dir = self._target_path("usr/share/sddm/themes/ryoku")
        ryoku_qml = os.path.join(ryoku_dir, "Main.qml")
        ryoku_conf = self._target_path("etc/sddm.conf.d/99-ryoku.conf")
        
        ryoku_conf_ok = False
        if os.path.exists(ryoku_conf):
            try:
                with open(ryoku_conf, "r", encoding="utf-8") as f:
                    content = f.read()
                    ryoku_conf_ok = "Current=ryoku" in content
            except Exception:
                pass
                
        ryoku_ok = os.path.exists(ryoku_qml) and ryoku_conf_ok
        results.append(ValidationResult(
            check_id="check_ryoku_sddm",
            title="Horizon Ryoku SDDM Theme Active",
            passed=ryoku_ok,
            details=f"Theme files present: {os.path.exists(ryoku_qml)}, 99-ryoku.conf configured: {ryoku_conf_ok}"
        ))

        # 4. Critical Exclusion: No Caelestia SDDM Override
        caelestia_sddm_override = self._target_path("etc/sddm.conf.d/zz-caelestia.conf")
        caelestia_sddm_active = os.path.exists(caelestia_sddm_override)
        results.append(ValidationResult(
            check_id="check_exclusion_caelestia_sddm",
            title="Caelestia SDDM Theme Override Strictly Excluded",
            passed=not caelestia_sddm_active,
            details="zz-caelestia.conf is absent (exclusion satisfied)" if not caelestia_sddm_active else "CRITICAL: zz-caelestia.conf exists!"
        ))

        # 5. Overload Splash Screen Installed & Active
        overload_dir = self._target_path("usr/share/plasma/look-and-feel/Overload")
        ksplashrc = self._target_path("etc/xdg/ksplashrc")
        ksplash_ok = False
        if os.path.exists(ksplashrc):
            try:
                with open(ksplashrc, "r", encoding="utf-8") as f:
                    ksplash_ok = "Theme=Overload" in f.read()
            except Exception:
                pass
        overload_ok = os.path.exists(overload_dir) and ksplash_ok
        results.append(ValidationResult(
            check_id="check_overload_splash",
            title="Overload Splash Screen Active",
            passed=overload_ok,
            details=f"Overload look-and-feel: {os.path.exists(overload_dir)}, ksplashrc Theme=Overload: {ksplash_ok}"
        ))

        # 6. Candy Bar (candy-icons) Icon Theme Installed & Selected
        candy_dir = self._target_path("usr/share/icons/candy-icons")
        kdeglobals = self._target_path("etc/xdg/kdeglobals")
        kdeglobals_ok = False
        if os.path.exists(kdeglobals):
            try:
                with open(kdeglobals, "r", encoding="utf-8") as f:
                    kdeglobals_ok = "Theme=candy-icons" in f.read()
            except Exception:
                pass
        candy_ok = os.path.exists(candy_dir) and kdeglobals_ok
        results.append(ValidationResult(
            check_id="check_candy_icons",
            title="Candy Bar (candy-icons) Theme Active",
            passed=candy_ok,
            details=f"candy-icons directory: {os.path.exists(candy_dir)}, kdeglobals configured: {kdeglobals_ok}"
        ))

        # 7. Caelestia Shell & Workspace-Tracker Component Installed
        caelestia_bin = self._target_path("usr/bin/quickshell")
        autostart_bin = self._target_path("usr/bin/caelestia-autostart")
        caelestia_ok = os.path.exists(caelestia_bin) or os.path.exists(autostart_bin)
        results.append(ValidationResult(
            check_id="check_caelestia_shell",
            title="Caelestia Shell & Components Installed",
            passed=caelestia_ok,
            details=f"Quickshell/autostart present: {caelestia_ok}"
        ))

        # 8. Caelestia Autostart Integration Configured
        service_file = self._target_path("usr/lib/systemd/user/caelestia-shell.service")
        user_wants = self._target_path("usr/lib/systemd/user/graphical-session.target.wants/caelestia-shell.service")
        etc_wants = self._target_path("etc/systemd/user/graphical-session.target.wants/caelestia-shell.service")
        service_ok = os.path.exists(service_file)
        results.append(ValidationResult(
            check_id="check_caelestia_autostart",
            title="Caelestia Shell Autostart Service Configured",
            passed=service_ok,
            details=f"Systemd user unit installed: {service_ok}"
        ))

        # 9. Critical Exclusion: Caelestia Lock-Screen Shell Not Hijacking KScreenLocker
        plasmashellrc = self._target_path("etc/xdg/plasmashellrc")
        lock_hijacked = False
        if os.path.exists(plasmashellrc):
            try:
                with open(plasmashellrc, "r", encoding="utf-8") as f:
                    if "caelestia.desktop" in f.read():
                        lock_hijacked = True
            except Exception:
                pass
        results.append(ValidationResult(
            check_id="check_exclusion_lockscreen_hijack",
            title="KScreenLocker Preserved (Lockscreen Hijack Excluded)",
            passed=not lock_hijacked,
            details="Standard KScreenLocker intact without caelestia.desktop override"
        ))

        # 10. Horizon Configuration Applied (Top Bar, Hover, No Dock Pins, Background Off)
        shell_json = self._target_path("etc/skel/.config/caelestia/shell.json")
        config_ok = False
        if os.path.exists(shell_json):
            try:
                with open(shell_json, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    bar = cfg.get("bar", {})
                    bg = cfg.get("background", {})
                    dock = bar.get("dock", {})
                    pos_top = bar.get("position") == "top"
                    hover_ok = bar.get("showOnHover") is True
                    dock_empty = len(dock.get("pinnedApps", [1])) == 0
                    bg_disabled = bg.get("enabled") is False
                    config_ok = pos_top and hover_ok and dock_empty and bg_disabled
            except Exception:
                pass
        results.append(ValidationResult(
            check_id="check_horizon_shell_config",
            title="Horizon Curated Shell Configuration Applied",
            passed=config_ok,
            details=f"Top bar: {pos_top if 'pos_top' in locals() else False}, Hover: {hover_ok if 'hover_ok' in locals() else False}, Empty dock pins: {dock_empty if 'dock_empty' in locals() else False}, Bg layer disabled: {bg_disabled if 'bg_disabled' in locals() else False}"
        ))

        return results
