#!/usr/bin/env python3
"""
Unit Test: Storage Planning, Live Media Protection, and Safe Unmounting
"""
import os
import unittest
import tempfile
from installer.backend.storage import BlockDevice, plan_partition_table, is_device_live_media, unmount_target_disk

class TestStorage(unittest.TestCase):
    def test_block_device_properties(self):
        dev = BlockDevice(
            name="nvme0n1",
            path="/dev/nvme0n1",
            size="512.0 GiB",
            size_bytes=512 * 1024**3,
            model="Samsung SSD 980 PRO",
            tran="nvme",
            is_rotational=False,
            partitions=[],
            is_live_media=False,
        )
        data = dev.to_dict()
        self.assertEqual(data["name"], "nvme0n1")
        self.assertEqual(data["path"], "/dev/nvme0n1")
        self.assertFalse(data["is_live_media"])

    def test_live_media_flag(self):
        dev_live = BlockDevice(
            name="sdb",
            path="/dev/sdb",
            size="32.0 GiB",
            size_bytes=32 * 1024**3,
            model="SanDisk Ultra USB",
            tran="usb",
            is_rotational=False,
            partitions=[],
            is_live_media=True,
        )
        data = dev_live.to_dict()
        self.assertTrue(data["is_live_media"])

    def test_btrfs_partition_plan(self):
        plan = plan_partition_table("/dev/vda", fs_type="btrfs", swap_size_gib=4, efi_size_mib=1024)
        self.assertEqual(plan["disk"], "/dev/vda")
        self.assertEqual(plan["filesystem"], "btrfs")
        self.assertEqual(len(plan["partitions"]), 3)
        self.assertEqual(plan["partitions"][0]["name"], "HORIZON_EFI")
        self.assertEqual(plan["partitions"][1]["name"], "HORIZON_SWAP")
        self.assertEqual(plan["partitions"][2]["name"], "HORIZON_ROOT")
        self.assertEqual(len(plan["btrfs_subvolumes"]), 5)
        subvol_names = [s["name"] for s in plan["btrfs_subvolumes"]]
        self.assertEqual(subvol_names, ["@", "@home", "@snapshots", "@cache", "@log"])

    def test_ext4_partition_plan(self):
        plan = plan_partition_table("/dev/vda", fs_type="ext4", swap_size_gib=8, efi_size_mib=1024)
        self.assertEqual(plan["disk"], "/dev/vda")
        self.assertEqual(plan["filesystem"], "ext4")
        self.assertEqual(len(plan["partitions"]), 3)
        self.assertEqual(plan["partitions"][1]["size_mib"], 8192)
        self.assertEqual(len(plan["btrfs_subvolumes"]), 0)

    def test_is_device_live_media_nonexistent(self):
        self.assertFalse(is_device_live_media("/dev/nonexistent_disk_xyz"))

    def test_unmount_target_disk_safe_nonexistent(self):
        # Must execute cleanly without exception
        res = unmount_target_disk("/dev/nonexistent_disk_xyz")
        self.assertTrue(res)

if __name__ == "__main__":
    unittest.main()
