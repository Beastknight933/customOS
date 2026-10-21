#!/usr/bin/env python3
"""
Unit Test: Source-to-Staging Consistency Suite
Verifies that canonical files and their staged counterparts in the
Archiso airootfs profile are strictly synchronized without drift.
"""
import os
import filecmp
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STAGED_ROOT = os.path.join(REPO_ROOT, "iso", "archiso-profile", "airootfs", "opt", "horizon-os")

class TestStagingConsistency(unittest.TestCase):
    def test_staged_root_exists(self):
        self.assertTrue(os.path.isdir(STAGED_ROOT), f"Staged root must exist at {STAGED_ROOT}")

    def test_installer_backend_consistency(self):
        """Verify all installer engine modules match between repo and ISO staging."""
        installer_files = [
            "horizon-tui.py",
            "backend/account.py",
            "backend/bootloader.py",
            "backend/deployer.py",
            "backend/executor.py",
            "backend/hardware.py",
            "backend/storage.py",
            "backend/validator.py",
        ]
        for rel_p in installer_files:
            canonical = os.path.join(REPO_ROOT, "installer", rel_p)
            staged = os.path.join(STAGED_ROOT, "installer", rel_p)
            self.assertTrue(os.path.exists(canonical), f"Canonical {rel_p} missing")
            self.assertTrue(os.path.exists(staged), f"Staged {rel_p} missing")
            with open(canonical, "r", encoding="utf-8") as f1, open(staged, "r", encoding="utf-8") as f2:
                c1 = f1.read().replace("\r\n", "\n")
                c2 = f2.read().replace("\r\n", "\n")
                self.assertEqual(c1, c2, f"Drift detected between canonical and staged {rel_p}")

    def test_packages_and_profiles_consistency(self):
        """Verify package manifests and desktop profiles match canonical sources."""
        files = [
            ("packages/kde-desktop/packages.list", "packages/kde-desktop/packages.list"),
            ("packages/arch-base/packages.list", "packages/arch-base/packages.list"),
            ("packages/arch-base/pacman.conf", "packages/arch-base/pacman.conf"),
            ("packages/release-manifest.json", "packages/release-manifest.json"),
            ("profiles/cachyos-kde-profile.yaml", "profiles/cachyos-kde-profile.yaml"),
            ("profiles/horizon-desktop.yaml", "profiles/horizon-desktop.yaml"),
        ]
        for c_rel, s_rel in files:
            canonical = os.path.join(REPO_ROOT, c_rel)
            staged = os.path.join(STAGED_ROOT, s_rel)
            self.assertTrue(os.path.exists(canonical), f"Canonical {c_rel} missing")
            self.assertTrue(os.path.exists(staged), f"Staged {s_rel} missing")
            with open(canonical, "r", encoding="utf-8") as f1, open(staged, "r", encoding="utf-8") as f2:
                c1 = f1.read().replace("\r\n", "\n")
                c2 = f2.read().replace("\r\n", "\n")
                self.assertEqual(c1, c2, f"Drift detected between canonical and staged {c_rel}")

    def test_documentation_and_licenses_consistency(self):
        """Verify root docs, security policies, and third-party notices match."""
        for fname in ["README.md", "SECURITY.md", "THIRD_PARTY_LICENSES.md", "LICENSE", "install.sh"]:
            canonical = os.path.join(REPO_ROOT, fname)
            staged = os.path.join(STAGED_ROOT, fname)
            self.assertTrue(os.path.exists(canonical), f"Canonical {fname} missing")
            self.assertTrue(os.path.exists(staged), f"Staged {fname} missing")
            with open(canonical, "r", encoding="utf-8") as f1, open(staged, "r", encoding="utf-8") as f2:
                c1 = f1.read().replace("\r\n", "\n")
                c2 = f2.read().replace("\r\n", "\n")
                self.assertEqual(c1, c2, f"Drift detected in {fname}")

    def test_custom_components_and_defaults_consistency(self):
        """Verify key custom component metadata and defaults match."""
        files = [
            ("defaults/kde/kdeglobals", "defaults/kde/kdeglobals"),
            ("defaults/kde/ksplashrc", "defaults/kde/ksplashrc"),
            ("defaults/sddm/99-ryoku.conf", "defaults/sddm/99-ryoku.conf"),
            ("defaults/shell/shell.json", "defaults/shell/shell.json"),
            ("custom-components/ryoku-sddm/Main.qml", "custom-components/ryoku-sddm/Main.qml"),
            ("custom-components/splash/metadata.json", "custom-components/splash/metadata.json"),
            ("custom-components/caelestia-kde/provenance.json", "custom-components/caelestia-kde/provenance.json"),
        ]
        for c_rel, s_rel in files:
            canonical = os.path.join(REPO_ROOT, c_rel)
            staged = os.path.join(STAGED_ROOT, s_rel)
            self.assertTrue(os.path.exists(canonical), f"Canonical {c_rel} missing")
            self.assertTrue(os.path.exists(staged), f"Staged {s_rel} missing")
            with open(canonical, "r", encoding="utf-8") as f1, open(staged, "r", encoding="utf-8") as f2:
                c1 = f1.read().replace("\r\n", "\n")
                c2 = f2.read().replace("\r\n", "\n")
                self.assertEqual(c1, c2, f"Drift detected in {c_rel}")

    def test_no_invalid_arch_package_names(self):
        """Ensure non-existent package targets (libpipewire, libcava, ttf-rubik-vf) are not present."""
        forbidden = ["libpipewire", "libcava", "ttf-rubik-vf"]
        pkg_list = os.path.join(REPO_ROOT, "packages", "kde-desktop", "packages.list")
        profile = os.path.join(REPO_ROOT, "profiles", "cachyos-kde-profile.yaml")

        with open(pkg_list, "r", encoding="utf-8") as f:
            content_pkg = f.read()
        with open(profile, "r", encoding="utf-8") as f:
            content_prof = f.read()

        for pkg in forbidden:
            self.assertNotIn(pkg, content_pkg, f"Invalid package '{pkg}' must not be in packages.list")
            self.assertNotIn(pkg, content_prof, f"Invalid package '{pkg}' must not be in cachyos-kde-profile.yaml")

if __name__ == "__main__":
    unittest.main()
