#!/usr/bin/env python3
"""
Unit Test: Theme & Desktop Configuration Validity
"""
import os
import json
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestConfigs(unittest.TestCase):
    def test_shell_json_schema(self):
        cfg_path = os.path.join(REPO_ROOT, "defaults", "shell", "shell.json")
        self.assertTrue(os.path.exists(cfg_path))
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        bar = data.get("bar", {})
        bg = data.get("background", {})
        dock = bar.get("dock", {})
        app = data.get("appearance", {})

        # Rule 1: Panel at top
        self.assertEqual(bar.get("position"), "top")
        # Rule 2: Panel visibility on hover
        self.assertTrue(bar.get("showOnHover"))
        self.assertFalse(bar.get("persistent"))
        # Rule 3: No pinned applications in dock
        self.assertEqual(dock.get("pinnedApps"), [])
        # Rule 4: Background layer disabled for KDE Plasma widgets
        self.assertFalse(bg.get("enabled"))
        # Rule 5: Desktop clock disabled
        self.assertFalse(bg.get("desktopClock", {}).get("enabled"))
        # Rule 6: Dark theme and controlled opacity
        self.assertTrue(app.get("pitchBlack"))
        self.assertTrue(app.get("transparency", {}).get("enabled"))

    def test_ryoku_sddm_patch(self):
        qml_path = os.path.join(REPO_ROOT, "custom-components", "ryoku-sddm", "Main.qml")
        self.assertTrue(os.path.exists(qml_path))
        with open(qml_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Both branches must use black
        self.assertIn('readonly property color bgColor: isLight ? "#000000" : "#000000"', content)

    def test_overload_splash_metadata(self):
        meta_path = os.path.join(REPO_ROOT, "custom-components", "splash", "metadata.json")
        self.assertTrue(os.path.exists(meta_path))
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data.get("KPlugin", {}).get("Id"), "Overload")

    def test_candy_icons_index(self):
        index_path = os.path.join(REPO_ROOT, "custom-components", "icons", "candy-icons", "index.theme")
        self.assertTrue(os.path.exists(index_path))
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Name=candy-icons", content)

    def test_kde_defaults(self):
        ksplashrc = os.path.join(REPO_ROOT, "defaults", "kde", "ksplashrc")
        kdeglobals = os.path.join(REPO_ROOT, "defaults", "kde", "kdeglobals")

        with open(ksplashrc, "r", encoding="utf-8") as f:
            self.assertIn("Theme=Overload", f.read())

        with open(kdeglobals, "r", encoding="utf-8") as f:
            self.assertIn("Theme=candy-icons", f.read())

if __name__ == "__main__":
    unittest.main()
