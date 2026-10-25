import os
import unittest

class TestAetheriumSddmTheme(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.sddm_dir = os.path.join(self.root_dir, "themes", "sddm", "aetherium")

    def test_sddm_files_exist(self):
        for req in ["metadata.desktop", "theme.conf", "Main.qml"]:
            path = os.path.join(self.sddm_dir, req)
            self.assertTrue(os.path.exists(path), f"Missing SDDM file: {path}")

    def test_metadata_desktop_contract(self):
        meta_path = os.path.join(self.sddm_dir, "metadata.desktop")
        with open(meta_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("[SddmGreeterTheme]", content)
        self.assertIn("QtVersion=6", content)
        self.assertIn("MainScript=Main.qml", content)

    def test_main_qml_contains_auth_and_session(self):
        qml_path = os.path.join(self.sddm_dir, "Main.qml")
        with open(qml_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check critical imports and components
        self.assertIn("import QtQuick", content)
        self.assertIn("import SddmComponents 2.0", content)
        self.assertIn("sddm.login(", content)
        self.assertIn("passInput", content)
        self.assertIn("sessionModel", content)
        self.assertIn("userModel", content)


if __name__ == "__main__":
    unittest.main()
