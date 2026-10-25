import os
import subprocess
import json
import unittest

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


if __name__ == "__main__":
    unittest.main()
