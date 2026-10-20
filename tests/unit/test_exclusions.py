#!/usr/bin/env python3
"""
Unit Test: Critical Component Exclusions (Caelestia SDDM & Lockscreen Hijack)
"""
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestExclusions(unittest.TestCase):
    def test_no_caelestia_sddm_in_packaging(self):
        pkgbuild_path = os.path.join(REPO_ROOT, "custom-components", "caelestia-kde", "packaging", "PKGBUILD")
        self.assertTrue(os.path.exists(pkgbuild_path))
        with open(pkgbuild_path, "r", encoding="utf-8") as f:
            content = f.read()

        # zz-caelestia.conf dropin must NOT be created
        self.assertNotIn("cat > \"$pkgdir/etc/sddm.conf.d/zz-caelestia.conf\"", content)
        self.assertNotIn("Current=caelestia", content)
        # Must explicitly delete any accidental sddm drop-ins
        self.assertIn("rm -rf \"$pkgdir/etc/sddm.conf.d\"", content)

    def test_sddm_override_patch_exists(self):
        patch_path = os.path.join(REPO_ROOT, "custom-components", "caelestia-kde", "patches", "0001-horizon-remove-sddm-override.patch")
        self.assertTrue(os.path.exists(patch_path))
        with open(patch_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("-        set(_SDDM_THEME_DIR", content)

    def test_lockscreen_hijack_patch_exists(self):
        patch_path = os.path.join(REPO_ROOT, "custom-components", "caelestia-kde", "patches", "0002-horizon-disable-lockscreen-hijack.patch")
        self.assertTrue(os.path.exists(patch_path))
        with open(patch_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn('-        current_shell=', content)
        self.assertIn('kwriteconfig6 --file plasmashellrc --group "Shell" --key "ShellPackage" "caelestia.desktop"', content)

    def test_sddm_configuration_selects_ryoku(self):
        sddm_conf = os.path.join(REPO_ROOT, "defaults", "sddm", "99-ryoku.conf")
        self.assertTrue(os.path.exists(sddm_conf))
        with open(sddm_conf, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Current=ryoku", content)
        self.assertNotIn("caelestia", content)

if __name__ == "__main__":
    unittest.main()
