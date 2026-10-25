import os
import subprocess
import json
import unittest
import sys
from importlib.machinery import SourceFileLoader

doctor_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "core", "bin", "aetherium-doctor"))
aetherium_doctor = SourceFileLoader("aetherium_doctor", doctor_file).load_module()


class TestAetheriumDoctor(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.doctor_script = os.path.join(self.root_dir, "core", "bin", "aetherium-doctor")

    def test_doctor_json_mode(self):
        res = subprocess.run(
            ["python", self.doctor_script, "--json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        self.assertEqual(res.returncode, 0, f"doctor --json failed: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertIn("os", data)
        self.assertIn("session", data)
        self.assertIn("plasma_version", data)
        self.assertIn("qt_version", data)
        self.assertIn("quickshell", data)
        self.assertIn("sddm", data)
        self.assertIn("lockscreen", data)
        self.assertIn("utilities", data)
        self.assertIn("config", data)

    def test_doctor_validate_configs(self):
        res = subprocess.run(
            ["python", self.doctor_script, "--validate-configs"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        self.assertEqual(res.returncode, 0, f"doctor --validate-configs failed: {res.stderr}")
        self.assertIn("[VALID]", res.stdout)
        self.assertIn("shell.json", res.stdout)
        self.assertIn("tokens.json", res.stdout)

    def test_semantic_validation_catches_invalid_configs(self):
        # Invalid shell config: bad position and negative scale
        bad_shell = {
            "general": {},
            "bar": {"position": "invalid_diagonal", "scale": -1}
        }
        errs = aetherium_doctor.validate_shell_config(bad_shell)
        self.assertTrue(len(errs) > 0)
        self.assertTrue(any("position" in e for e in errs))

        # Invalid tokens config: bad color format
        bad_tokens = {
            "appearance": {},
            "semantics": {
                "color": {"accentPrimary": "not-a-color-value"}
            }
        }
        errs = aetherium_doctor.validate_tokens_config(bad_tokens)
        self.assertTrue(len(errs) > 0)
        self.assertTrue(any("accentPrimary" in e for e in errs))


if __name__ == "__main__":
    unittest.main()
