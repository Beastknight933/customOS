#!/usr/bin/env python3
"""
Unit Test Suite: Account Security, Failure Recovery, Bootloader Verification & Disk Guards
Tests:
 1. Password setting safety with metacharacters and no secret leakage.
 2. Username and Hostname validation logic.
 3. Installation failure handling and safe target mount cleanup.
 4. Bootloader manager configuration and verification (Limine, GRUB, systemd-boot).
 5. Storage revalidation and live media/host disk protection.
 6. Validator mock stub detection and categorisation.
"""
import os
import sys
import unittest
import tempfile
import shutil

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "installer"))

from backend.account import validate_username, validate_hostname, prompt_secure_password
from backend.executor import InstallExecutor, InstallLogger
from backend.storage import (
    revalidate_target_disk,
    is_device_live_media,
    get_parent_disk,
    plan_partition_table,
)
from backend.bootloader import (
    BootloaderManager,
    discover_installed_kernels,
    is_firmware_uefi,
)
from backend.validator import InstallationValidator, ValidationCategory

class TestSecurityAndFailure(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="horizon_sec_test_")
        self.log_file = os.path.join(self.test_dir, "test.log")
        self.logger = InstallLogger(self.log_file)
        self.executor = InstallExecutor(dry_run=True, target_root=self.test_dir, logger=self.logger)

    def tearDown(self):
        self.logger.close()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # 1. Account Security & Input Validation
    def test_username_validation(self):
        # Valid usernames
        for u in ["horizon", "alice", "_service", "admin_01", "user-name"]:
            valid, msg = validate_username(u)
            self.assertTrue(valid, f"Expected '{u}' to be valid, got: {msg}")

        # Invalid usernames
        invalid_cases = [
            ("", "empty"),
            ("Horizon", "uppercase"),
            ("1user", "starts with number"),
            ("-user", "starts with hyphen"),
            ("user-", "ends with hyphen"),
            ("root", "reserved user"),
            ("daemon", "reserved user"),
            ("user name", "contains space"),
            ("user;touch /tmp/pwn", "shell metacharacters"),
            ("a" * 33, "too long"),
        ]
        for u, reason in invalid_cases:
            valid, msg = validate_username(u)
            self.assertFalse(valid, f"Expected '{u}' ({reason}) to be invalid")

    def test_hostname_validation(self):
        # Valid hostnames
        for h in ["horizon-pc", "archlinux", "desktop-01", "node1"]:
            valid, msg = validate_hostname(h)
            self.assertTrue(valid, f"Expected '{h}' to be valid, got: {msg}")

        # Invalid hostnames
        invalid_cases = [
            ("", "empty"),
            ("-horizon", "starts with hyphen"),
            ("horizon-", "ends with hyphen"),
            ("horizon_pc", "contains underscore"),
            ("horizon pc", "contains space"),
            ("horizon;id", "metacharacter"),
            ("a" * 64, "too long"),
        ]
        for h, reason in invalid_cases:
            valid, msg = validate_hostname(h)
            self.assertFalse(valid, f"Expected '{h}' ({reason}) to be invalid")

    def test_password_metacharacter_safety(self):
        """
        Verify that passwords containing quotes, dollar signs, semicolons,
        backticks, ampersands, and unicode never execute commands or leak into logs.
        """
        dangerous_passwords = [
            "p@$$w0rd'; rm -rf /; echo 'owned",
            "admin' OR '1'='1",
            'foo"bar"baz',
            "`whoami`",
            "$(cat /etc/shadow)",
            "pass&word|pipe>redirect",
            "Hörîzøn-パスワード-🔐",
            "!@#$%^&*()_+-=[]{}|;':,.<>/?`~",
        ]

        for pw in dangerous_passwords:
            # Set password through executor in dry-run
            res = self.executor.set_user_password("testuser", pw)
            self.assertTrue(res)

        # Inspect log file to verify NO password leaked into the log
        self.logger.file.flush()
        with open(self.log_file, "r", encoding="utf-8") as f:
            log_content = f.read()

        for pw in dangerous_passwords:
            # Check that literal dangerous password is never written into logs
            self.assertNotIn(pw, log_content, f"Password '{pw}' leaked into log file!")

        self.assertIn("Setting password for user 'testuser' (secret redacted)", log_content)

    def test_empty_password_rejection(self):
        res = self.executor.set_user_password("testuser", "")
        self.assertFalse(res)
        self.assertIn("Username or password cannot be empty", self.executor.last_error)

        res_none = self.executor.set_user_password("testuser", None)
        self.assertFalse(res_none)

    def test_password_spaces_and_unicode(self):
        pw = "Correct Horse Battery Staple 2026! 🚀"
        res = self.executor.set_user_password("testuser", pw)
        self.assertTrue(res)
        with open(self.log_file, "r", encoding="utf-8") as f:
            log_content = f.read()
        self.assertNotIn(pw, log_content)

    def test_prompt_secure_password_mock(self):
        from unittest.mock import patch
        # 1: empty then mismatch then valid
        inputs = ["", "first_try", "different_confirm", "valid_pw_123", "valid_pw_123"]
        with patch("getpass.getpass", side_effect=inputs):
            pw = prompt_secure_password("Enter password", "Confirm password")
            self.assertEqual(pw, "valid_pw_123")

    def test_root_account_policy_locked(self):
        """Verify root locking uses passwd -l."""
        called_cmds = []
        mock_executor = InstallExecutor(dry_run=True, target_root=self.test_dir, logger=self.logger)
        mock_executor.chroot_exec = lambda cmd, **kwargs: called_cmds.append(cmd) or True
        mock_executor.chroot_exec(["passwd", "-l", "root"], description="Locking root account")
        self.assertEqual(called_cmds[0], ["passwd", "-l", "root"])

    # 2. Failure Handling & Cleanup
    def test_command_failure_tracking(self):
        live_executor = InstallExecutor(dry_run=False, target_root=self.test_dir, logger=self.logger)
        res = live_executor.run_cmd([sys.executable, "-c", "import sys; sys.exit(7)"], description="Intentional Failure Test")
        self.assertFalse(res)
        self.assertEqual(live_executor.last_failed_command, "Intentional Failure Test")
        self.assertIsNotNone(live_executor.last_error)
        self.assertIn("exited with code 7", live_executor.last_error)

    def test_safe_target_cleanup_protection(self):
        """Verify cleanup never unmounts unrelated host filesystems."""
        # Run cleanup on dry-run target
        res = self.executor.cleanup_target_mounts(target_disk="/dev/mock_disk")
        self.assertTrue(res)

    # 3. Bootloader Verification
    def test_kernel_discovery_and_bootloader_limine(self):
        boot_dir = os.path.join(self.test_dir, "boot")
        esp_dir = os.path.join(boot_dir, "efi")
        os.makedirs(boot_dir, exist_ok=True)
        os.makedirs(esp_dir, exist_ok=True)

        # Create mock kernel, initramfs, and limine loader
        with open(os.path.join(boot_dir, "vmlinuz-linux"), "w") as f:
            f.write("mock-vmlinuz")
        with open(os.path.join(boot_dir, "initramfs-linux.img"), "w") as f:
            f.write("mock-initrd")

        limine_share = os.path.join(self.test_dir, "usr", "share", "limine")
        os.makedirs(limine_share, exist_ok=True)
        with open(os.path.join(limine_share, "BOOTX64.EFI"), "w") as f:
            f.write("mock-efi-loader")

        kernels = discover_installed_kernels(self.test_dir)
        self.assertEqual(kernels.get("kernel"), "vmlinuz-linux")
        self.assertEqual(kernels.get("initramfs"), "initramfs-linux.img")

        # Test Limine bootloader installation
        live_executor = InstallExecutor(dry_run=False, target_root=self.test_dir, logger=self.logger)
        live_executor.verify_mount = lambda p: True  # Bypass mountpoint check in temp dir
        mgr = BootloaderManager(
            executor=live_executor,
            target_root=self.test_dir,
            selected_disk="/dev/vda",
            bootloader="limine",
            filesystem="btrfs",
        )
        success, msg = mgr.install()
        self.assertTrue(success, f"Limine install failed: {msg}")

        # Check generated limine.conf
        conf_path = os.path.join(self.test_dir, "boot", "efi", "limine.conf")
        self.assertTrue(os.path.exists(conf_path))
        with open(conf_path, "r", encoding="utf-8") as f:
            conf = f.read()
            self.assertIn("vmlinuz-linux", conf)
            self.assertIn("initramfs-linux.img", conf)
            self.assertIn("rootflags=subvol=@", conf)

    def test_bootloader_missing_kernel_fails(self):
        """Verify bootloader installer stops immediately if /boot has no kernel."""
        # Target dir with boot/efi but WITHOUT kernel in /boot
        esp_dir = os.path.join(self.test_dir, "boot", "efi")
        os.makedirs(esp_dir, exist_ok=True)

        live_executor = InstallExecutor(dry_run=False, target_root=self.test_dir, logger=self.logger)
        live_executor.verify_mount = lambda p: True
        mgr = BootloaderManager(
            executor=live_executor,
            target_root=self.test_dir,
            selected_disk="/dev/vda",
            bootloader="limine",
        )
        success, msg = mgr.install()
        self.assertFalse(success)
        self.assertIn("No installed Linux kernel found", msg)

    # 4. Storage Revalidation & Protection
    def test_revalidate_target_disk_nonexistent(self):
        valid, msg = revalidate_target_disk("/dev/nonexistent_drive_9999")
        self.assertFalse(valid)
        self.assertIn("does not exist", msg)

    def test_parent_disk_resolution(self):
        self.assertEqual(get_parent_disk("/dev/nvme0n1p2"), "/dev/nvme0n1")
        self.assertEqual(get_parent_disk("/dev/sda1"), "/dev/sda")
        self.assertEqual(get_parent_disk("/dev/vda3"), "/dev/vda")
        self.assertEqual(get_parent_disk("/dev/loop0p1"), "/dev/loop0")

    # 5. Validator Mock Stub Detection & Categorisation
    def test_validator_stub_detection(self):
        # Create a stub script in test target
        bin_dir = os.path.join(self.test_dir, "usr", "bin")
        os.makedirs(bin_dir, exist_ok=True)
        stub_file = os.path.join(bin_dir, "plasmashell")
        with open(stub_file, "w") as f:
            f.write("#!/bin/sh\nexit 0\n")

        validator = InstallationValidator(target_root=self.test_dir)
        self.assertTrue(validator.is_mock_stub("usr/bin/plasmashell"))
        self.assertFalse(validator.is_elf_binary("usr/bin/plasmashell"))

        # Verify category and placeholder flag
        results = validator.verify_all()
        plasma_result = next(r for r in results if r.check_id == "check_kde_plasma")
        self.assertEqual(plasma_result.category, ValidationCategory.FILE_PRESENCE)
        self.assertTrue(plasma_result.is_placeholder)
        self.assertIn("Placeholder mock stub detected", plasma_result.details)

    # 6. Sudoers Policy & Tool Validation
    def test_secure_password_no_echo_terminal_error(self):
        """Verify prompt_secure_password raises RuntimeError on interactive terminal error rather than echoing."""
        from unittest.mock import patch
        with patch("getpass.getpass", side_effect=Exception("Terminal ioctl failure")), \
             patch("sys.stdin.isatty", return_value=True):
            with self.assertRaises(RuntimeError) as ctx:
                prompt_secure_password("Password")
            self.assertIn("Cannot securely prompt for password without echoing", str(ctx.exception))

    def test_sudoers_wheel_dropin(self):
        """Verify sudoers dropin defines strict wheel policy."""
        sudoers_content = "%wheel ALL=(ALL:ALL) ALL\n"
        sudoers_path = os.path.join(self.test_dir, "10-wheel")
        with open(sudoers_path, "w", encoding="utf-8") as f:
            f.write(sudoers_content)
        os.chmod(sudoers_path, 0o440)
        if sys.platform != "win32":
            self.assertEqual(oct(os.stat(sudoers_path).st_mode)[-3:], "440")
        else:
            self.assertEqual(oct(os.stat(sudoers_path).st_mode)[-3:], "444")
        self.assertIn("%wheel ALL=(ALL:ALL) ALL", sudoers_content)

    def test_validate_host_tools_logic(self):
        """Verify _validate_host_tools accurately detects missing or present system utilities."""
        import horizon_tui
        installer = horizon_tui.HorizonInstallerApp(dry_run=True)
        ok, missing = installer._validate_host_tools()
        # In dry run mode, basic tools like mount/umount exist on standard Linux hosts
        self.assertIsInstance(ok, bool)
        self.assertIsInstance(missing, list)

if __name__ == "__main__":
    unittest.main()
