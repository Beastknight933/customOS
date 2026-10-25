#!/usr/bin/env python3
"""
Tests for Aetherium OS Caelestia-style installation workflow:
Root entry points, scripts modularity, TUI data schemas, and Clockwork integration.
"""

import unittest
import os
import json
import subprocess
import tempfile
import shutil

class TestCaelestiaWorkflow(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def test_root_entry_points(self):
        """Root-level entry points must exist, be executable, and syntactically clean."""
        entry_points = ["install.sh", "update.sh", "uninstall.sh", "Makefile"]
        for ep in entry_points:
            p = os.path.join(self.root_dir, ep)
            self.assertTrue(os.path.isfile(p), f"Missing root entry point: {ep}")

        for ep in ["install.sh", "update.sh", "uninstall.sh"]:
            p = os.path.join(self.root_dir, ep)
            rel_p = os.path.relpath(p, self.root_dir).replace("\\", "/")
            res = subprocess.run(["bash", "-n", rel_p], cwd=self.root_dir, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"Syntax error in {ep}: {res.stderr}")

    def test_modular_scripts_exist(self):
        """Scripts directory must provide all modular phase steps matching upstream architecture."""
        required_scripts = [
            "setup.sh",
            "00-backup-themes.sh",
            "00a-system-update.sh",
            "01-ensure-prereqs.sh",
            "02-all-packages.sh",
            "03-deploy-configs.sh",
            "04-deploy-session.sh",
            "05-sddm-theme.sh",
            "06-lockscreen.sh",
            "08-build-shell.sh",
            "10-autostart.sh"
        ]
        for s in required_scripts:
            p = os.path.join(self.root_dir, "scripts", s)
            self.assertTrue(os.path.isfile(p), f"Missing script: scripts/{s}")

        required_lib = [
            "log.sh",
            "privileges.sh",
            "packages.sh",
            "toolchain.sh",
            "backup.sh",
            "rollback.sh",
            "detect.sh"
        ]
        for l in required_lib:
            p = os.path.join(self.root_dir, "scripts", "lib", l)
            self.assertTrue(os.path.isfile(p), f"Missing script lib: scripts/lib/{l}")

    def test_installer_data_menu_and_theme(self):
        """installer/data/menu.json and theme.json must be valid JSON and contain Aetherium specs."""
        menu_path = os.path.join(self.root_dir, "installer", "data", "menu.json")
        self.assertTrue(os.path.isfile(menu_path), "menu.json missing")
        with open(menu_path, "r", encoding="utf-8") as f:
            menu_data = json.load(f)
        self.assertIn("menu", menu_data)

        # Check for profile options and component keys
        menu_str = json.dumps(menu_data)
        self.assertIn("INSTALL_PROFILE", menu_str)
        self.assertIn("desktop-lockscreen", menu_str)
        self.assertIn("full", menu_str)
        self.assertIn("INSTALL_SHELL", menu_str)
        self.assertIn("APPLY_LOCKSCREEN", menu_str)
        self.assertIn("INSTALL_SDDM", menu_str)
        self.assertIn("SDDM_THEME_VARIANT", menu_str)

        theme_path = os.path.join(self.root_dir, "installer", "data", "theme.json")
        self.assertTrue(os.path.isfile(theme_path), "theme.json missing")
        with open(theme_path, "r", encoding="utf-8") as f:
            theme_data = json.load(f)
        self.assertIn("palette", theme_data)
        self.assertIn("splash_screen", theme_data)
        self.assertIn("glyphs", theme_data)

    def test_clockwork_sddm_theme_integration(self):
        """Qylock Clockwork SDDM theme must be integrated and conform to SDDM Qt6 contract."""
        clockwork_dir = os.path.join(self.root_dir, "themes", "sddm", "clockwork")
        self.assertTrue(os.path.isdir(clockwork_dir), "clockwork theme directory missing")

        meta_path = os.path.join(clockwork_dir, "metadata.desktop")
        main_qml = os.path.join(clockwork_dir, "Main.qml")
        conf_path = os.path.join(clockwork_dir, "theme.conf")
        font_path = os.path.join(clockwork_dir, "font", "Outfit-Black.ttf")
        bg_path = os.path.join(clockwork_dir, "bg.png")

        self.assertTrue(os.path.isfile(meta_path), "clockwork metadata.desktop missing")
        self.assertTrue(os.path.isfile(main_qml), "clockwork Main.qml missing")
        self.assertTrue(os.path.isfile(conf_path), "clockwork theme.conf missing")
        self.assertTrue(os.path.isfile(font_path), "clockwork font missing")
        self.assertTrue(os.path.isfile(bg_path), "clockwork fallback background missing")

        with open(meta_path, "r", encoding="utf-8") as f:
            meta_content = f.read()
        self.assertIn("QtVersion=6", meta_content)
        self.assertIn("MainScript=Main.qml", meta_content)

    def test_tui_cmake_target_name(self):
        """installer/tui/CMakeLists.txt must build aetherium-install."""
        cmake_file = os.path.join(self.root_dir, "installer", "tui", "CMakeLists.txt")
        self.assertTrue(os.path.isfile(cmake_file))
        with open(cmake_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("aetherium-install", content)

    def test_setup_help_flag(self):
        """scripts/setup.sh --help must return 0 and list options."""
        rel_setup = "scripts/setup.sh"
        res = subprocess.run(["bash", rel_setup, "--help"], cwd=self.root_dir, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"setup.sh failed: {res.stderr}")
        self.assertIn("Aetherium OS Installer", res.stdout)
        self.assertIn("--profile", res.stdout)
        self.assertIn("--sddm-theme", res.stdout)
        self.assertIn("--skip-update", res.stdout)

    def test_non_interactive_desktop_install_workflow(self):
        """Non-interactive desktop profile installation in sandbox environment."""
        with tempfile.TemporaryDirectory() as temp_home:
            # Under WSL/Windows, convert Windows drive path to POSIX /mnt/<drive>/...
            drive, rest = os.path.splitdrive(temp_home)
            if drive:
                temp_home_posix = f"/mnt/{drive[0].lower()}{rest.replace(os.sep, '/')}"
            else:
                temp_home_posix = temp_home.replace(os.sep, '/')

            cmd = (
                f"export HOME='{temp_home_posix}' "
                f"export XDG_STATE_HOME='{temp_home_posix}/.local/state' "
                f"export XDG_CONFIG_HOME='{temp_home_posix}/.config' "
                f"export XDG_SESSION_TYPE='wayland' "
                f"export XDG_CURRENT_DESKTOP='KDE' "
                f"export AETHERIUM_TEST_ENV='1' "
                f"export AETHERIUM_SKIP_BUILD='1' "
                f"export BASE_DISTRO='arch'; "
                f"bash scripts/setup.sh --profile desktop --skip-update --non-interactive --cli"
            )
            res = subprocess.run(
                ["bash", "-c", cmd],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            self.assertEqual(res.returncode, 0, f"setup.sh non-interactive failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")

            # Verify deployed files
            cfg_dir = os.path.join(temp_home, ".config", "aetherium")
            self.assertTrue(os.path.isfile(os.path.join(cfg_dir, "shell.json")), "shell.json missing after install")
            self.assertTrue(os.path.isfile(os.path.join(cfg_dir, "tokens.json")), "tokens.json missing after install")
            self.assertTrue(os.path.isfile(os.path.join(cfg_dir, "install.env")), "install.env missing after install")

            # Verify manifest
            manifest_file = os.path.join(temp_home, ".local", "state", "aetherium", "install-manifest.json")
            self.assertTrue(os.path.isfile(manifest_file), "install-manifest.json missing")
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
            self.assertGreater(len(manifest_data), 0)

            # Verify session environment
            env_conf = os.path.join(temp_home, ".config", "environment.d", "aetherium.conf")
            self.assertTrue(os.path.isfile(env_conf), "environment.d/aetherium.conf missing")

            # Verify autostart entries
            autostart_desk = os.path.join(temp_home, ".config", "autostart", "aetherium-autostart.desktop")
            self.assertTrue(os.path.isfile(autostart_desk), "aetherium-autostart.desktop missing")

            # Test uninstallation workflow
            uninst_cmd = (
                f"export HOME='{temp_home_posix}' "
                f"export XDG_STATE_HOME='{temp_home_posix}/.local/state' "
                f"export XDG_CONFIG_HOME='{temp_home_posix}/.config'; "
                f"printf 'y\\n0\\ny\\n' | bash uninstall.sh"
            )
            res_uninst = subprocess.run(
                ["bash", "-c", uninst_cmd],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            self.assertEqual(res_uninst.returncode, 0, f"uninstall.sh failed:\n{res_uninst.stderr}")

            # Verify files were removed
            self.assertFalse(os.path.isfile(autostart_desk), "autostart desktop file not cleaned up")
            self.assertFalse(os.path.isfile(env_conf), "environment.d file not cleaned up")
            self.assertFalse(os.path.isdir(cfg_dir), "aetherium config dir was not removed after user confirmation")

if __name__ == "__main__":
    unittest.main()
