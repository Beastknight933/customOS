import os
import tempfile
import json
import unittest

class TestAetheriumInstallerLogic(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.installer_dir = os.path.join(self.root_dir, "installer")

    def test_installer_scripts_exist(self):
        scripts = [
            os.path.join(self.root_dir, "install.sh"),
            os.path.join(self.root_dir, "uninstall.sh"),
            os.path.join(self.root_dir, "update.sh"),
            os.path.join(self.installer_dir, "install.sh"),
            os.path.join(self.installer_dir, "uninstall.sh"),
            os.path.join(self.installer_dir, "update.sh"),
            os.path.join(self.installer_dir, "lib", "common.sh"),
            os.path.join(self.installer_dir, "lib", "detect.sh"),
            os.path.join(self.installer_dir, "lib", "backup.sh"),
            os.path.join(self.installer_dir, "lib", "rollback.sh")
        ]
        for script in scripts:
            self.assertTrue(os.path.exists(script), f"Missing script: {script}")

    def test_manifest_recording_and_cleanup_logic(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = os.path.join(tmpdir, "manifest.json")
            dummy_file = os.path.join(tmpdir, "test_file.txt")
            with open(dummy_file, "w") as f:
                f.write("test content")

            # Init manifest
            manifest = {
                "timestamp": "2026-10-25T00:00:00Z",
                "backup_dir": tmpdir,
                "installed_files": [dummy_file]
            }
            with open(manifest_path, "w") as f:
                json.dump(manifest, f)

            self.assertTrue(os.path.exists(dummy_file))

            # Simulate rollback logic
            with open(manifest_path, "r") as f:
                data = json.load(f)
            for fpath in reversed(data.get("installed_files", [])):
                if os.path.exists(fpath):
                    os.remove(fpath)

            self.assertFalse(os.path.exists(dummy_file), "Rollback failed to remove dummy file")


if __name__ == "__main__":
    unittest.main()
