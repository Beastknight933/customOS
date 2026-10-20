#!/usr/bin/env python3
"""
Unit Test: Pacman Configuration, Architecture Compatibility, and Fallback Mirrors
"""
import os
import unittest
import tempfile
from installer.backend.hardware import detect_cpu_info

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestPacmanConf(unittest.TestCase):
    def test_arch_base_pacman_conf_exists(self):
        conf_path = os.path.join(REPO_ROOT, "packages", "arch-base", "pacman.conf")
        self.assertTrue(os.path.exists(conf_path))
        with open(conf_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Verify repository definitions
        self.assertIn("[cachyos-v3]", content)
        self.assertIn("[cachyos]", content)
        self.assertIn("[core]", content)
        self.assertIn("[extra]", content)
        self.assertIn("[multilib]", content)
        
        # Verify fallback Server directives
        self.assertIn("Server = https://mirror.cachyos.org/repo/x86_64_v3/$repo", content)
        self.assertIn("Server = https://mirror.cachyos.org/repo/$arch/$repo", content)
        self.assertIn("Server = https://geo.mirror.pkgbuild.com/$repo/os/$arch", content)

    def test_cpu_detection_structure(self):
        info = detect_cpu_info()
        self.assertIn("model", info)
        self.assertIn("cores", info)
        self.assertIn("arch", info)
        self.assertIn("v3_supported", info)
        self.assertIn("v4_supported", info)
        self.assertIsInstance(info["v3_supported"], bool)

    def test_tui_pacman_generator_v3_supported(self):
        sys_path = os.path.join(REPO_ROOT, "installer")
        import sys
        if sys_path not in sys.path:
            sys.path.insert(0, sys_path)
        from importlib.machinery import SourceFileLoader
        tui_module = SourceFileLoader("horizon_tui", os.path.join(sys_path, "horizon-tui.py")).load_module()
        installer = tui_module.HorizonInstallerApp(dry_run=True)
        conf_path = installer._generate_installer_pacman_conf(v3_supported=True)
        self.assertTrue(os.path.exists(conf_path))
        with open(conf_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("[cachyos-v3]", content)
        self.assertIn("[cachyos]", content)
        self.assertIn("x86_64_v3", content)
        if os.path.exists(conf_path):
            os.remove(conf_path)

    def test_tui_pacman_generator_v3_unsupported(self):
        sys_path = os.path.join(REPO_ROOT, "installer")
        import sys
        if sys_path not in sys.path:
            sys.path.insert(0, sys_path)
        from importlib.machinery import SourceFileLoader
        tui_module = SourceFileLoader("horizon_tui", os.path.join(sys_path, "horizon-tui.py")).load_module()
        installer = tui_module.HorizonInstallerApp(dry_run=True)
        conf_path = installer._generate_installer_pacman_conf(v3_supported=False)
        self.assertTrue(os.path.exists(conf_path))
        with open(conf_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("[cachyos-v3]", content)
        self.assertNotIn("[cachyos-core-v3]", content)
        self.assertNotIn("[cachyos-extra-v3]", content)
        self.assertIn("[cachyos]", content)
        self.assertIn("[core]", content)
        if os.path.exists(conf_path):
            os.remove(conf_path)

if __name__ == "__main__":
    unittest.main()
