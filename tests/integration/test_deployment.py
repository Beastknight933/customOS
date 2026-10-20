#!/usr/bin/env python3
"""
Integration Test: End-to-End Component Deployment & Verification Audit
Simulates complete deployment into a mock root filesystem and runs all 10 validator checks.
"""
import os
import sys
import shutil
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "installer"))

from backend.executor import InstallExecutor, InstallLogger
from backend.deployer import ComponentDeployer
from backend.validator import InstallationValidator

class TestIntegrationDeployment(unittest.TestCase):
    def setUp(self):
        self.mock_root = tempfile.mkdtemp(prefix="horizon_mock_root_")
        self.logger = InstallLogger(os.path.join(self.mock_root, "test-install.log"))
        self.executor = InstallExecutor(dry_run=False, target_root=self.mock_root, logger=self.logger)
        self.deployer = ComponentDeployer(executor=self.executor, repo_root=REPO_ROOT)

    def tearDown(self):
        self.logger.close()
        shutil.rmtree(self.mock_root, ignore_errors=True)

    def test_mock_end_to_end_deployment(self):
        # 1. Setup mock system binaries
        bin_dir = os.path.join(self.mock_root, "usr", "bin")
        lib_dir = os.path.join(self.mock_root, "usr", "lib", "systemd", "user")
        os.makedirs(bin_dir, exist_ok=True)
        os.makedirs(lib_dir, exist_ok=True)

        # Mock core binaries
        for b in ["plasmashell", "kwin_wayland", "sddm", "quickshell", "caelestia-autostart"]:
            p = os.path.join(bin_dir, b)
            with open(p, "w") as f:
                f.write("#!/bin/sh\nexit 0\n")
            os.chmod(p, 0o755)

        # Mock systemd user unit
        unit_p = os.path.join(lib_dir, "caelestia-shell.service")
        with open(unit_p, "w") as f:
            f.write("[Unit]\nDescription=Caelestia Shell\n")

        # 2. Deploy Ryoku SDDM Theme
        self.deployer.deploy_ryoku_sddm()

        # 3. Deploy Overload Splash Screen
        self.deployer.deploy_overload_splash()

        # 4. Deploy Candy Bar Icons
        self.deployer.deploy_candy_icons()

        # 5. Deploy KDE & Visual Identity Defaults
        self.deployer.deploy_horizon_kde_defaults()

        # 6. Deploy Caelestia Shell Configurations
        self.deployer.deploy_caelestia_shell(username="testuser")

        # 7. Run Comprehensive Post-Installation Audit
        validator = InstallationValidator(target_root=self.mock_root)
        results = validator.verify_all()

        passed = [r for r in results if r.passed]
        failed = [r for r in results if not r.passed]

        if failed:
            print("\nFailed checks in mock integration:")
            for f in failed:
                print(f"  - {f.title}: {f.details}")

        self.assertEqual(len(passed), 10, f"All 10 integration checks must pass. Passed: {len(passed)}/10")

if __name__ == "__main__":
    unittest.main()
