#!/usr/bin/env python3
"""
Unit Test: Package Manifest & Profile Integrity
"""
import os
import unittest
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestManifests(unittest.TestCase):
    def test_cachyos_profile_yaml(self):
        profile_path = os.path.join(REPO_ROOT, "profiles", "cachyos-kde-profile.yaml")
        self.assertTrue(os.path.exists(profile_path), "cachyos-kde-profile.yaml must exist")
        with open(profile_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        self.assertIn("packages", data)
        self.assertIn("cachyos_kernel_and_perf", data["packages"])
        self.assertIn("linux-cachyos", data["packages"]["cachyos_kernel_and_perf"])
        self.assertIn("kde_plasma_desktop", data["packages"])
        self.assertIn("plasma-workspace", data["packages"]["kde_plasma_desktop"])
        self.assertIn("kwin", data["packages"]["kde_plasma_desktop"])
        self.assertIn("sddm", data["packages"]["display_manager"])
        self.assertIn("caelestia_runtime", data["packages"])
        self.assertIn("quickshell", data["packages"]["caelestia_runtime"])

    def test_horizon_desktop_yaml(self):
        desktop_path = os.path.join(REPO_ROOT, "profiles", "horizon-desktop.yaml")
        self.assertTrue(os.path.exists(desktop_path), "horizon-desktop.yaml must exist")
        with open(desktop_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertEqual(data["desktop"]["login_manager"], "SDDM")
        self.assertEqual(data["desktop"]["lock_screen"], "KScreenLocker")
        self.assertEqual(data["components"]["sddm"]["theme"], "ryoku")
        self.assertEqual(data["components"]["splash"]["theme"], "Overload")
        self.assertEqual(data["components"]["icons"]["theme"], "candy-icons")
        self.assertIn("exclusions", data)
        self.assertIn("caelestia_sddm_theme", data["exclusions"])
        self.assertIn("caelestia_lockscreen_shell", data["exclusions"])

    def test_arch_base_packages_list(self):
        pkg_file = os.path.join(REPO_ROOT, "packages", "arch-base", "packages.list")
        self.assertTrue(os.path.exists(pkg_file))
        with open(pkg_file, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        self.assertIn("base", lines)
        self.assertIn("linux-cachyos", lines)
        self.assertIn("limine", lines)

    def test_kde_packages_list(self):
        pkg_file = os.path.join(REPO_ROOT, "packages", "kde-desktop", "packages.list")
        self.assertTrue(os.path.exists(pkg_file))
        with open(pkg_file, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        self.assertIn("plasma-desktop", lines)
        self.assertIn("sddm", lines)
        self.assertIn("quickshell", lines)
        self.assertIn("matugen", lines)

    def test_release_manifest_json(self):
        import json
        manifest_path = os.path.join(REPO_ROOT, "packages", "release-manifest.json")
        self.assertTrue(os.path.exists(manifest_path), "release-manifest.json must exist")
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["distribution"], "Horizon OS")
        self.assertEqual(data["base_system"]["target_kernel"], "7.2.11-1-cachyos")
        self.assertEqual(data["base_system"]["live_kernel"], "7.2.11-arch1-1")
        self.assertEqual(data["desktop_environment"]["plasma"], "6.8.0-1.1")
        self.assertIn("caelestia-kde", data["installed_packages"])

if __name__ == "__main__":
    unittest.main()
