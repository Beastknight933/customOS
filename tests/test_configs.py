import os
import json
import unittest

class TestAetheriumConfigs(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.shell_path = os.path.join(self.root_dir, "desktop", "config", "shell.json")
        self.schemes_dir = os.path.join(self.root_dir, "desktop", "schemes", "aetherium", "default")

    def test_shell_json_valid(self):
        self.assertTrue(os.path.exists(self.shell_path))
        with open(self.shell_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for section in ["general", "bar", "background", "appearance", "launcher", "dashboard", "utilities"]:
            self.assertIn(section, data, f"Missing section: {section}")

        self.assertIn(data["bar"]["position"], ["top", "bottom", "left", "right"])
        self.assertIsInstance(data["bar"]["scale"], (int, float))

    def test_aetherium_schemes(self):
        dark_txt = os.path.join(self.schemes_dir, "dark.txt")
        light_txt = os.path.join(self.schemes_dir, "light.txt")

        self.assertTrue(os.path.exists(dark_txt), f"Missing dark.txt: {dark_txt}")
        self.assertTrue(os.path.exists(light_txt), f"Missing light.txt: {light_txt}")

        with open(dark_txt, "r", encoding="utf-8") as f:
            content = f.read()

        required_tokens = ["background", "surface", "primary", "onPrimary", "secondary", "tertiary", "error"]
        for token in required_tokens:
            self.assertIn(token, content, f"Missing Material Design 3 token '{token}' in dark.txt")


if __name__ == "__main__":
    unittest.main()
