import os
import json
import unittest

class TestAetheriumLockscreen(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.lock_dir = os.path.join(self.root_dir, "themes", "lockscreen", "aetherium.desktop")

    def test_metadata_json(self):
        meta_path = os.path.join(self.lock_dir, "metadata.json")
        self.assertTrue(os.path.exists(meta_path))

        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data.get("KPackageStructure"), "Plasma/Shell")
        self.assertEqual(data.get("KPlugin", {}).get("Id"), "aetherium.desktop")

    def test_qml_components_exist(self):
        contents = os.path.join(self.lock_dir, "contents", "lockscreen")
        self.assertTrue(os.path.exists(os.path.join(contents, "LockScreen.qml")))
        self.assertTrue(os.path.exists(os.path.join(contents, "LockScreenUi.qml")))
        self.assertTrue(os.path.exists(os.path.join(contents, "components", "AuthHandler.qml")))


if __name__ == "__main__":
    unittest.main()
