import os
import tempfile
import json
import shutil
import unittest

class TestAetheriumManifestAndRollback(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.manifest_path = os.path.join(self.test_dir, "install-manifest.json")
        self.backup_dir = os.path.join(self.test_dir, "backup")
        os.makedirs(self.backup_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_path_safety_whitelist(self):
        # Python implementation of the whitelist validation
        home = os.path.expanduser("~")
        allowed_prefixes = [
            os.path.join(home, ".config", "aetherium"),
            os.path.join(home, ".config", "autostart", "aetherium-"),
            os.path.join(home, ".config", "environment.d", "aetherium.conf"),
            os.path.join(home, ".config", "plasma-workspace", "env", "aetherium.sh"),
            os.path.join(home, ".local", "bin", "aetherium-"),
            os.path.join(home, ".local", "share", "plasma", "shells", "aetherium.desktop"),
            "/usr/share/sddm/themes/aetherium",
            "/etc/sddm.conf.d/zz-aetherium.conf"
        ]

        def is_safe_target(path: str) -> bool:
            norm = os.path.normpath(os.path.abspath(path))
            if ".." in path.split(os.sep):
                return False
            for pref in allowed_prefixes:
                norm_pref = os.path.normpath(os.path.abspath(pref))
                if norm == norm_pref or norm.startswith(norm_pref):
                    return True
            return False

        # Safe targets
        self.assertTrue(is_safe_target(os.path.join(home, ".config", "aetherium", "shell.json")))
        self.assertTrue(is_safe_target(os.path.join(home, ".local", "bin", "aetherium-doctor")))
        self.assertTrue(is_safe_target("/etc/sddm.conf.d/zz-aetherium.conf"))

        # Dangerous / traversal targets
        self.assertFalse(is_safe_target("/etc/shadow"))
        self.assertFalse(is_safe_target("/usr/bin/bash"))
        self.assertFalse(is_safe_target(os.path.join(home, ".bashrc")))
        self.assertFalse(is_safe_target(os.path.join(home, ".config", "aetherium", "..", "important.txt")))

    def test_previously_absent_files_are_deleted_not_restored(self):
        # Target that did not exist before
        created_file = os.path.join(self.test_dir, "new_file.json")
        with open(created_file, "w") as f:
            f.write("{}")

        manifest = {
            "version": "1.1",
            "backup_dir": self.backup_dir,
            "tracked_items": [
                {
                    "target": created_file,
                    "action": "created",
                    "existed_before": False,
                    "backup_path": None
                }
            ]
        }
        with open(self.manifest_path, "w") as f:
            json.dump(manifest, f)

        # Execute rollback logic
        with open(self.manifest_path, "r") as f:
            data = json.load(f)

        for item in reversed(data.get("tracked_items", [])):
            target = item["target"]
            existed = item["existed_before"]
            if not existed and os.path.exists(target):
                os.remove(target)

        self.assertFalse(os.path.exists(created_file), "Newly created file should be removed on rollback")

    def test_previously_existing_files_are_restored(self):
        # Target that existed before and was modified
        target_file = os.path.join(self.test_dir, "existing.conf")
        original_content = "ORIGINAL_SETTING=1"
        modified_content = "MODIFIED_SETTING=2"

        # Backup copy
        backup_copy = os.path.join(self.backup_dir, "existing.conf.bak")
        with open(backup_copy, "w") as f:
            f.write(original_content)

        # Overwritten target
        with open(target_file, "w") as f:
            f.write(modified_content)

        manifest = {
            "version": "1.1",
            "backup_dir": self.backup_dir,
            "tracked_items": [
                {
                    "target": target_file,
                    "action": "modified",
                    "existed_before": True,
                    "backup_path": backup_copy
                }
            ]
        }
        with open(self.manifest_path, "w") as f:
            json.dump(manifest, f)

        # Execute rollback logic
        with open(self.manifest_path, "r") as f:
            data = json.load(f)

        for item in reversed(data.get("tracked_items", [])):
            target = item["target"]
            existed = item["existed_before"]
            bkp = item["backup_path"]
            if existed and bkp and os.path.exists(bkp):
                shutil.copy2(bkp, target)

        with open(target_file, "r") as f:
            restored = f.read()

        self.assertEqual(restored, original_content, "Pre-existing file should be restored to original content")


if __name__ == "__main__":
    unittest.main()
