import os
import tempfile
import json
import shutil
import unittest

class TestAetheriumSddmAdapterLogic(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.themes_dir = os.path.join(self.test_dir, "usr_share_sddm_themes")
        self.sddm_conf_dir = os.path.join(self.test_dir, "etc_sddm_conf_d")
        self.state_dir = os.path.join(self.test_dir, "state")
        os.makedirs(self.themes_dir, exist_ok=True)
        os.makedirs(self.sddm_conf_dir, exist_ok=True)
        os.makedirs(self.state_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_dummy_theme(self, dir_path, complete=True):
        os.makedirs(dir_path, exist_ok=True)
        with open(os.path.join(dir_path, "metadata.desktop"), "w") as f:
            f.write("[SddmGreeterTheme]\nQtVersion=6\nMainScript=Main.qml\n")
        with open(os.path.join(dir_path, "theme.conf"), "w") as f:
            f.write("[General]\nthemeMode=dark\n")
        if complete:
            with open(os.path.join(dir_path, "Main.qml"), "w") as f:
                f.write("import QtQuick\nRectangle {}\n")

    def test_theme_validation(self):
        valid_dir = os.path.join(self.test_dir, "valid_theme")
        invalid_dir = os.path.join(self.test_dir, "invalid_theme")

        self.create_dummy_theme(valid_dir, complete=True)
        self.create_dummy_theme(invalid_dir, complete=False)

        def validate(path):
            for req in ["metadata.desktop", "theme.conf", "Main.qml"]:
                if not os.path.exists(os.path.join(path, req)):
                    return False
            return True

        self.assertTrue(validate(valid_dir))
        self.assertFalse(validate(invalid_dir))

    def test_staged_atomic_replacement(self):
        target_dir = os.path.join(self.themes_dir, "aetherium")
        staging_dir = os.path.join(self.themes_dir, ".aetherium.staging")
        old_dir = os.path.join(self.themes_dir, ".aetherium.old")

        # 1. Target pre-exists with old version
        os.makedirs(target_dir, exist_ok=True)
        with open(os.path.join(target_dir, "version.txt"), "w") as f:
            f.write("v0.9")

        # 2. Stage new version
        os.makedirs(staging_dir, exist_ok=True)
        with open(os.path.join(staging_dir, "version.txt"), "w") as f:
            f.write("v1.0")

        # 3. Atomic swap
        if os.path.exists(target_dir):
            os.rename(target_dir, old_dir)
        os.rename(staging_dir, target_dir)
        if os.path.exists(old_dir):
            shutil.rmtree(old_dir)

        # 4. Verify target now has v1.0
        with open(os.path.join(target_dir, "version.txt"), "r") as f:
            ver = f.read().strip()
        self.assertEqual(ver, "v1.0")
        self.assertFalse(os.path.exists(staging_dir))
        self.assertFalse(os.path.exists(old_dir))

    def test_sddm_rollback_restores_pre_existing_theme(self):
        target_dir = os.path.join(self.themes_dir, "aetherium")
        backup_theme_dir = os.path.join(self.state_dir, "backup_theme")
        dropin_conf = os.path.join(self.sddm_conf_dir, "zz-aetherium.conf")
        dropin_backup = os.path.join(self.state_dir, "dropin.conf.bak")

        # Scenario: Pre-existing theme was backed up
        os.makedirs(backup_theme_dir, exist_ok=True)
        with open(os.path.join(backup_theme_dir, "marker.txt"), "w") as f:
            f.write("ORIGINAL_THEME_FILES")

        # Dropin was previously absent
        manifest = {
            "target_theme_dir": target_dir,
            "theme_existed_before": True,
            "theme_backup_dir": backup_theme_dir,
            "dropin_conf": dropin_conf,
            "dropin_existed_before": False,
            "dropin_backup": ""
        }

        # Active installation has deployed files
        os.makedirs(target_dir, exist_ok=True)
        with open(os.path.join(target_dir, "marker.txt"), "w") as f:
            f.write("NEW_THEME_FILES")
        with open(dropin_conf, "w") as f:
            f.write("[Theme]\nCurrent=aetherium\n")

        # Rollback execution
        if os.path.exists(dropin_conf):
            os.remove(dropin_conf)
        if manifest["theme_existed_before"] and os.path.exists(backup_theme_dir):
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            shutil.copytree(backup_theme_dir, target_dir)

        self.assertFalse(os.path.exists(dropin_conf), "Dropin should be removed as it was absent before")
        self.assertTrue(os.path.exists(target_dir))
        with open(os.path.join(target_dir, "marker.txt"), "r") as f:
            content = f.read().strip()
        self.assertEqual(content, "ORIGINAL_THEME_FILES")


if __name__ == "__main__":
    unittest.main()
