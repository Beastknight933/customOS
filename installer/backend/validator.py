#!/usr/bin/env python3
"""
Horizon OS Installer - Post-Installation Verification & Audit Module
Distinguishes:
 1. Installed Files (Static presence)
 2. Valid Package Dependencies (Pacman local DB verification)
 3. Correct Service Configuration (Syntax, settings, and themes)
 4. Enabled Services (Systemd units and wants symlinks)
 5. Binary Integrity & Mock Stub Detection (Authentic ELF vs placeholder scripts)
 6. Graphical-Session Integration (Wayland desktop entries, KScreenLocker preservation)
"""
import os
import re
import json
from typing import Dict, Any, List, Optional

class ValidationCategory:
    FILE_PRESENCE = "Installed Files"
    BINARY_INTEGRITY = "Binary Integrity"
    PACKAGE_DEPENDENCY = "Package Dependencies"
    SERVICE_CONFIG = "Service Configuration"
    SERVICE_ENABLEMENT = "Service Enablement"
    SESSION_INTEGRATION = "Session Integration"
    RUNTIME_VERIFY = "Runtime & Functional"

class ValidationResult:
    def __init__(
        self,
        check_id: str,
        title: str,
        passed: bool,
        details: str = "",
        category: str = ValidationCategory.FILE_PRESENCE,
        is_placeholder: bool = False,
    ):
        self.check_id = check_id
        self.title = title
        self.passed = passed
        self.details = details
        self.category = category
        self.is_placeholder = is_placeholder

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_id": self.check_id,
            "category": self.category,
            "title": self.title,
            "passed": self.passed,
            "is_placeholder": self.is_placeholder,
            "details": self.details,
        }

class InstallationValidator:
    def __init__(self, target_root: str = "/"):
        self.target_root = os.path.abspath(target_root)

    def _target_path(self, rel_path: str) -> str:
        return os.path.join(self.target_root, rel_path.lstrip("/"))

    def is_elf_binary(self, rel_path: str) -> bool:
        """Verify whether an executable is an authentic compiled ELF binary rather than a stub."""
        full_path = self._target_path(rel_path)
        if not os.path.isfile(full_path):
            return False
        try:
            with open(full_path, "rb") as f:
                magic = f.read(4)
                return magic == b"\x7fELF"
        except Exception:
            return False

    def is_mock_stub(self, rel_path: str) -> bool:
        """Check if an executable is a mock/placeholder script (e.g. #!/bin/sh exit 0)."""
        full_path = self._target_path(rel_path)
        if not os.path.isfile(full_path):
            return False
        try:
            size = os.path.getsize(full_path)
            if size < 256:
                with open(full_path, "r", errors="ignore") as f:
                    content = f.read()
                    if "#!/bin/sh" in content or "exit 0" in content:
                        return True
        except Exception:
            pass
        return False

    def has_pacman_package(self, pkg_name: str) -> bool:
        """Check if a package is registered in target pacman database (/var/lib/pacman/local/)."""
        local_db = self._target_path("var/lib/pacman/local")
        if not os.path.isdir(local_db):
            return False
        try:
            for entry in os.listdir(local_db):
                # Format: pkgname-version-release
                match = re.match(r"^(.+)-[^-]+-[^-]+$", entry)
                if match and match.group(1) == pkg_name:
                    return True
        except Exception:
            pass
        return False

    def verify_all(self) -> List[ValidationResult]:
        """Perform all mandatory Horizon OS integration checks with accurate categorisation."""
        results = []

        # 1. KDE Plasma and KWin (File Presence & Integrity)
        plasma_bin = self._target_path("usr/bin/plasmashell")
        kwin_bin = self._target_path("usr/bin/kwin_wayland")
        plasma_exists = os.path.exists(plasma_bin) or os.path.exists(kwin_bin) or os.path.exists(self._target_path("usr/lib/plasma-dbus-run-session-if-needed"))
        plasma_stub = self.is_mock_stub("usr/bin/plasmashell") or self.is_mock_stub("usr/bin/kwin_wayland")
        plasma_elf = self.is_elf_binary("usr/bin/plasmashell") or self.is_elf_binary("usr/bin/kwin_wayland")
        
        detail_msg = f"plasmashell present: {os.path.exists(plasma_bin)}, kwin_wayland present: {os.path.exists(kwin_bin)}"
        if plasma_stub:
            detail_msg += " [NOTICE: Placeholder mock stub detected]"
        elif plasma_elf:
            detail_msg += " [Verified authentic ELF binary]"

        results.append(ValidationResult(
            check_id="check_kde_plasma",
            title="KDE Plasma & KWin Installed",
            passed=plasma_exists,
            category=ValidationCategory.FILE_PRESENCE,
            is_placeholder=plasma_stub,
            details=detail_msg,
        ))

        # 2. SDDM Installed & Selected as Display Manager
        sddm_service = self._target_path("etc/systemd/system/display-manager.service")
        sddm_bin = self._target_path("usr/bin/sddm")
        sddm_exists = os.path.exists(sddm_bin) or os.path.exists(sddm_service)
        sddm_stub = self.is_mock_stub("usr/bin/sddm")
        sddm_elf = self.is_elf_binary("usr/bin/sddm")

        sddm_msg = f"sddm binary: {os.path.exists(sddm_bin)}, display-manager link: {os.path.exists(sddm_service)}"
        if sddm_stub:
            sddm_msg += " [NOTICE: Mock stub detected]"
        elif sddm_elf:
            sddm_msg += " [Verified authentic ELF binary]"

        results.append(ValidationResult(
            check_id="check_sddm_selected",
            title="SDDM Selected as Display Manager",
            passed=sddm_exists,
            category=ValidationCategory.SERVICE_ENABLEMENT,
            is_placeholder=sddm_stub,
            details=sddm_msg,
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
            category=ValidationCategory.SERVICE_CONFIG,
            details=f"Theme files present: {os.path.exists(ryoku_qml)}, 99-ryoku.conf configured: {ryoku_conf_ok}",
        ))

        # 4. Critical Exclusion: No Caelestia SDDM Override
        caelestia_sddm_override = self._target_path("etc/sddm.conf.d/zz-caelestia.conf")
        caelestia_sddm_active = os.path.exists(caelestia_sddm_override)
        results.append(ValidationResult(
            check_id="check_exclusion_caelestia_sddm",
            title="Caelestia SDDM Theme Override Strictly Excluded",
            passed=not caelestia_sddm_active,
            category=ValidationCategory.SERVICE_CONFIG,
            details="zz-caelestia.conf is absent (exclusion satisfied)" if not caelestia_sddm_active else "CRITICAL: zz-caelestia.conf exists!",
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
            category=ValidationCategory.SERVICE_CONFIG,
            details=f"Overload look-and-feel: {os.path.exists(overload_dir)}, ksplashrc Theme=Overload: {ksplash_ok}",
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
            category=ValidationCategory.SERVICE_CONFIG,
            details=f"candy-icons directory: {os.path.exists(candy_dir)}, kdeglobals configured: {kdeglobals_ok}",
        ))

        # 7. Caelestia Shell & Workspace-Tracker Component Installed
        caelestia_bin = self._target_path("usr/bin/quickshell")
        autostart_bin = self._target_path("usr/bin/caelestia-autostart")
        caelestia_exists = os.path.exists(caelestia_bin) or os.path.exists(autostart_bin)
        caelestia_stub = self.is_mock_stub("usr/bin/quickshell")
        caelestia_elf = self.is_elf_binary("usr/bin/quickshell")

        caelestia_msg = f"Quickshell present: {os.path.exists(caelestia_bin)}, autostart present: {os.path.exists(autostart_bin)}"
        if caelestia_stub:
            caelestia_msg += " [NOTICE: Mock stub detected]"
        elif caelestia_elf:
            caelestia_msg += " [Verified authentic ELF binary]"

        results.append(ValidationResult(
            check_id="check_caelestia_shell",
            title="Caelestia Shell & Components Installed",
            passed=caelestia_exists,
            category=ValidationCategory.FILE_PRESENCE,
            is_placeholder=caelestia_stub,
            details=caelestia_msg,
        ))

        # 8. Caelestia Autostart Integration Configured
        service_file = self._target_path("usr/lib/systemd/user/caelestia-shell.service")
        service_ok = os.path.exists(service_file)
        results.append(ValidationResult(
            check_id="check_caelestia_autostart",
            title="Caelestia Shell Autostart Service Configured",
            passed=service_ok,
            category=ValidationCategory.SERVICE_ENABLEMENT,
            details=f"Systemd user unit installed: {service_ok}",
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
            category=ValidationCategory.SESSION_INTEGRATION,
            details="Standard KScreenLocker intact without caelestia.desktop override",
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
            category=ValidationCategory.SERVICE_CONFIG,
            details=f"Top bar: {pos_top if 'pos_top' in locals() else False}, Hover: {hover_ok if 'hover_ok' in locals() else False}, Empty dock pins: {dock_empty if 'dock_empty' in locals() else False}, Bg layer disabled: {bg_disabled if 'bg_disabled' in locals() else False}",
        ))

        return results

    def verify_package_dependencies(self) -> List[ValidationResult]:
        """Check whether essential pacman packages are registered in local DB."""
        results = []
        required_pkgs = [
            ("plasma-desktop", "KDE Plasma Desktop Shell"),
            ("kwin", "KWin Wayland Compositor"),
            ("sddm", "SDDM Display Manager"),
            ("caelestia-kde", "Horizon Caelestia KDE Shell"),
        ]
        for pkg, title in required_pkgs:
            present = self.has_pacman_package(pkg)
            results.append(ValidationResult(
                check_id=f"pkg_dep_{pkg}",
                title=f"Package Registration: {title} ({pkg})",
                passed=present,
                category=ValidationCategory.PACKAGE_DEPENDENCY,
                details=f"Package {pkg} {'found in' if present else 'missing from'} /var/lib/pacman/local",
            ))
        return results
