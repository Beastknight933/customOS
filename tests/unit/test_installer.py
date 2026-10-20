#!/usr/bin/env python3
"""
Unit Test: Installer Storage Planning, Hardware Probing & Dry-Run Execution
"""
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.insert(0, os.path.join(REPO_ROOT, "installer"))

from backend.storage import plan_partition_table, BlockDevice
from backend.hardware import probe_all_hardware
from backend.executor import InstallExecutor, InstallLogger

class TestInstaller(unittest.TestCase):
    def test_btrfs_partition_plan(self):
        plan = plan_partition_table("/dev/nvme0n1", fs_type="btrfs", swap_size_gib=8, efi_size_mib=1024)
        self.assertEqual(plan["disk"], "/dev/nvme0n1")
        self.assertEqual(plan["label"], "gpt")
        self.assertEqual(len(plan["partitions"]), 3)
        
        # Partition 1: EFI
        efi = plan["partitions"][0]
        self.assertEqual(efi["name"], "HORIZON_EFI")
        self.assertEqual(efi["fs"], "vfat")
        self.assertEqual(efi["size_mib"], 1024)

        # Partition 2: Swap
        swap = plan["partitions"][1]
        self.assertEqual(swap["name"], "HORIZON_SWAP")
        self.assertEqual(swap["fs"], "swap")
        self.assertEqual(swap["size_mib"], 8192)

        # Partition 3: Root
        root = plan["partitions"][2]
        self.assertEqual(root["name"], "HORIZON_ROOT")
        self.assertEqual(root["fs"], "btrfs")

        # Subvolumes
        subvol_names = [s["name"] for s in plan["btrfs_subvolumes"]]
        self.assertIn("@", subvol_names)
        self.assertIn("@home", subvol_names)
        self.assertIn("@snapshots", subvol_names)
        self.assertIn("@cache", subvol_names)
        self.assertIn("@log", subvol_names)

    def test_hardware_probing(self):
        hw = probe_all_hardware()
        self.assertIn("cpu", hw)
        self.assertIn("memory", hw)
        self.assertIn("uefi", hw)
        self.assertIn("gpus", hw)
        self.assertGreater(hw["cpu"]["cores"], 0)

    def test_executor_dry_run(self):
        log_path = os.path.join(REPO_ROOT, "tests", "test-dryrun.log")
        logger = InstallLogger(log_path)
        executor = InstallExecutor(dry_run=True, target_root="/tmp/horizon-mock", logger=logger)
        
        output_captured = []
        res = executor.run_cmd(["echo", "Horizon Test"], description="Testing Dry Run", on_output=output_captured.append)
        self.assertTrue(res)
        self.assertTrue(any("DRYRUN" in o for o in output_captured))
        logger.close()
        if os.path.exists(log_path):
            os.remove(log_path)

if __name__ == "__main__":
    unittest.main()
