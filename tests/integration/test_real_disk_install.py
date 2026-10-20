#!/usr/bin/env python3
"""
Integration Test: Real Virtual Block Device Partitioning, Formatting, Btrfs Subvolumes & Deployment
"""
import os
import sys
import shutil
import subprocess
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "installer"))

from backend.storage import BlockDevice, plan_partition_table, unmount_target_disk
from backend.executor import InstallExecutor, InstallLogger
from backend.deployer import ComponentDeployer
from backend.validator import InstallationValidator

class TestRealDiskInstallation(unittest.TestCase):
    DISK_IMG = "/var/tmp/horizon-test-disk.img"
    TARGET_ROOT = "/mnt/test-horizon-target"
    LOOP_DEV = "/dev/loop0"

    @classmethod
    def setUpClass(cls):
        if not os.path.exists("/dev/loop0") or os.geteuid() != 0:
            raise unittest.SkipTest("Requires root privileges and Linux loop device")

        # Create 30GB raw virtual disk if not present
        if not os.path.exists(cls.DISK_IMG):
            subprocess.run(["qemu-img", "create", "-f", "raw", cls.DISK_IMG, "30G"], check=True)

        # Attach loop device with partition scanning
        subprocess.run(["losetup", "-d", cls.LOOP_DEV], stderr=subprocess.DEVNULL)
        subprocess.run(["losetup", "-P", cls.LOOP_DEV, cls.DISK_IMG], check=True)
        os.makedirs(cls.TARGET_ROOT, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        # Clean unmount
        if os.path.exists(cls.TARGET_ROOT):
            subprocess.run(["umount", "-R", cls.TARGET_ROOT], stderr=subprocess.DEVNULL)
            try:
                shutil.rmtree(cls.TARGET_ROOT, ignore_errors=True)
            except Exception:
                pass
        # Detach loop device
        subprocess.run(["losetup", "-d", cls.LOOP_DEV], stderr=subprocess.DEVNULL)

    def test_01_real_partitioning_and_formatting(self):
        """Test real parted partitioning and real mkfs formatting on virtual block device."""
        executor = InstallExecutor(dry_run=False, target_root=self.TARGET_ROOT)
        
        # 1. Wipe and create GPT
        self.assertTrue(executor.run_cmd(["parted", "-s", self.LOOP_DEV, "mklabel", "gpt"]))
        
        # 2. Partition 1: EFI (1024 MiB)
        self.assertTrue(executor.run_cmd(["parted", "-s", self.LOOP_DEV, "mkpart", "HORIZON_EFI", "fat32", "1MiB", "1025MiB"]))
        self.assertTrue(executor.run_cmd(["parted", "-s", self.LOOP_DEV, "set", "1", "esp", "on"]))
        
        # 3. Partition 2: Swap (2048 MiB)
        self.assertTrue(executor.run_cmd(["parted", "-s", self.LOOP_DEV, "mkpart", "HORIZON_SWAP", "linux-swap", "1025MiB", "3073MiB"]))
        
        # 4. Partition 3: Root (Btrfs, remainder)
        self.assertTrue(executor.run_cmd(["parted", "-s", self.LOOP_DEV, "mkpart", "HORIZON_ROOT", "btrfs", "3073MiB", "100%"]))
        
        # Reread partition table
        subprocess.run(["partx", "-u", self.LOOP_DEV], check=False)
        subprocess.run(["udevadm", "settle"], check=False)

        # 5. Format filesystems
        p1 = f"{self.LOOP_DEV}p1"
        p2 = f"{self.LOOP_DEV}p2"
        p3 = f"{self.LOOP_DEV}p3"

        self.assertTrue(executor.run_cmd(["mkfs.fat", "-F32", "-n", "HORIZON_EFI", p1]))
        self.assertTrue(executor.run_cmd(["mkswap", "-L", "HORIZON_SWAP", p2]))
        self.assertTrue(executor.run_cmd(["mkfs.btrfs", "-f", "-L", "HORIZON_ROOT", p3]))
        executor.logger.close()

    def test_02_btrfs_subvolumes_and_mounting(self):
        """Test creating Btrfs subvolumes (@, @home, @snapshots, @cache, @log) and mounting."""
        executor = InstallExecutor(dry_run=False, target_root=self.TARGET_ROOT)
        p1 = f"{self.LOOP_DEV}p1"
        p3 = f"{self.LOOP_DEV}p3"

        # Mount root temporarily to create subvolumes
        self.assertTrue(executor.run_cmd(["mount", p3, self.TARGET_ROOT]))
        for sub in ["@", "@home", "@snapshots", "@cache", "@log"]:
            self.assertTrue(executor.run_cmd(["btrfs", "subvolume", "create", f"{self.TARGET_ROOT}/{sub}"]))
        self.assertTrue(executor.run_cmd(["umount", self.TARGET_ROOT]))

        # Mount with subvolumes
        btrfs_opts = "noatime,compress=zstd:1,space_cache=v2"
        self.assertTrue(executor.run_cmd(["mount", "-o", f"subvol=@,{btrfs_opts}", p3, self.TARGET_ROOT]))
        
        os.makedirs(f"{self.TARGET_ROOT}/home", exist_ok=True)
        os.makedirs(f"{self.TARGET_ROOT}/.snapshots", exist_ok=True)
        os.makedirs(f"{self.TARGET_ROOT}/var/cache", exist_ok=True)
        os.makedirs(f"{self.TARGET_ROOT}/var/log", exist_ok=True)
        os.makedirs(f"{self.TARGET_ROOT}/boot/efi", exist_ok=True)

        self.assertTrue(executor.run_cmd(["mount", "-o", f"subvol=@home,{btrfs_opts}", p3, f"{self.TARGET_ROOT}/home"]))
        self.assertTrue(executor.run_cmd(["mount", "-o", f"subvol=@snapshots,{btrfs_opts}", p3, f"{self.TARGET_ROOT}/.snapshots"]))
        self.assertTrue(executor.run_cmd(["mount", "-o", f"subvol=@cache,{btrfs_opts}", p3, f"{self.TARGET_ROOT}/var/cache"]))
        self.assertTrue(executor.run_cmd(["mount", "-o", f"subvol=@log,{btrfs_opts}", p3, f"{self.TARGET_ROOT}/var/log"]))
        self.assertTrue(executor.run_cmd(["mount", p1, f"{self.TARGET_ROOT}/boot/efi"]))
        executor.logger.close()

    def test_03_deploy_and_validate_all_components(self):
        """Test deploying custom themes, Caelestia shell configs, and running complete validation."""
        # Create base system binaries as would be installed by pacstrap
        bin_dir = os.path.join(self.TARGET_ROOT, "usr", "bin")
        os.makedirs(bin_dir, exist_ok=True)
        for b in ["plasmashell", "kwin_wayland", "sddm", "quickshell"]:
            p = os.path.join(bin_dir, b)
            with open(p, "w") as f:
                f.write("#!/bin/sh\nexit 0\n")
            os.chmod(p, 0o755)

        logger = InstallLogger(f"{self.TARGET_ROOT}/var/log/horizon-install.log")
        executor = InstallExecutor(dry_run=False, target_root=self.TARGET_ROOT, logger=logger)
        deployer = ComponentDeployer(executor=executor, repo_root=REPO_ROOT)

        # Deploy all custom components
        self.assertTrue(deployer.deploy_ryoku_sddm())
        self.assertTrue(deployer.deploy_overload_splash())
        self.assertTrue(deployer.deploy_candy_icons())
        self.assertTrue(deployer.deploy_horizon_kde_defaults())
        self.assertTrue(deployer.deploy_caelestia_shell(username="horizon"))

        # Verify with InstallationValidator
        validator = InstallationValidator(target_root=self.TARGET_ROOT)
        results = validator.verify_all()
        logger.close()

        self.assertEqual(len(results), 10, "Expected all 10 validator checks to execute")
        for r in results:
            self.assertTrue(r.passed, f"Validator check '{r.title}' ({r.check_id}) failed: {r.details}")

if __name__ == "__main__":
    unittest.main()
