#!/usr/bin/env python3
"""
Horizon OS Installer - Storage & Partitioning Planner
Provides block device discovery, live media protection, host disk guardrails,
partition layout generation, and pre/post-execution validation.
"""
import os
import re
import json
import subprocess
import shutil
import time
from typing import List, Dict, Any, Optional, Tuple

class BlockDevice:
    def __init__(
        self,
        name: str,
        path: str,
        size: str,
        size_bytes: int,
        model: str,
        tran: str,
        is_rotational: bool,
        partitions: List[Dict[str, Any]],
        is_live_media: bool = False,
        is_host_disk: bool = False,
    ):
        self.name = name
        self.path = path
        self.size = size
        self.size_bytes = size_bytes
        self.model = model
        self.tran = tran
        self.is_rotational = is_rotational
        self.partitions = partitions
        self.is_live_media = is_live_media
        self.is_host_disk = is_host_disk

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "size": self.size,
            "size_bytes": self.size_bytes,
            "model": self.model,
            "tran": self.tran,
            "is_rotational": self.is_rotational,
            "partitions": self.partitions,
            "is_live_media": self.is_live_media,
            "is_host_disk": self.is_host_disk,
        }

def get_parent_disk(device_path: str) -> str:
    """
    Given a partition path (e.g. /dev/nvme0n1p2 or /dev/sda1), return parent disk path.
    """
    clean_path = device_path.replace("\\", "/")
    if os.name != "nt" and os.path.exists(device_path):
        clean_path = os.path.realpath(device_path)
    # NVMe / eMMC / loop: /dev/nvme0n1p1 -> /dev/nvme0n1
    match_nvme = re.match(r"^(/dev/(?:nvme\d+n\d+|mmcblk\d+|loop\d+))p\d+$", clean_path)
    if match_nvme:
        return match_nvme.group(1)

    # Standard disks: /dev/sda1 -> /dev/sda
    match_sd = re.match(r"^(/dev/[a-zA-Z]+)\d+$", clean_path)
    if match_sd:
        return match_sd.group(1)

    return clean_path

def detect_host_system_disk() -> Optional[str]:
    """
    Detect the disk device currently backing the root (/) filesystem of the running system.
    If running on an installed host (e.g. dev workstation), returns the parent block device.
    If running in a live ISO (overlay/airootfs), returns None or the live backing device.
    """
    try:
        # Check mount source of /
        root_dev = ""
        if shutil.which("findmnt"):
            try:
                root_dev = subprocess.check_output(
                    ["findmnt", "-n", "-o", "SOURCE", "/"],
                    text=True, stderr=subprocess.DEVNULL
                ).strip()
            except Exception:
                pass

        if not root_dev and os.path.exists("/proc/mounts"):
            with open("/proc/mounts", "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] == "/":
                        root_dev = parts[0]
                        break

        if root_dev:
            # If root is a live RAM/overlay filesystem, not a permanent host disk
            if root_dev in ["airootfs", "cowspace", "overlay", "rootfs"] or "tmpfs" in root_dev:
                return None
            if root_dev.startswith("/dev/"):
                return get_parent_disk(root_dev)
    except Exception:
        pass
    return None

def is_device_live_media(device_path: str) -> bool:
    """
    Check if the given device holds active live ISO mounts or is the parent
    device of the live installation media.
    """
    clean_dev = os.path.realpath(device_path)
    parent_target = get_parent_disk(clean_dev)

    try:
        # Check /proc/mounts for /run/archiso and airootfs
        if os.path.exists("/proc/mounts"):
            with open("/proc/mounts", "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        src, target = parts[0], parts[1]
                        if "/run/archiso" in target or (target == "/" and "airootfs" in src):
                            src_real = os.path.realpath(src) if src.startswith("/dev") else src
                            src_parent = get_parent_disk(src_real) if src.startswith("/dev") else ""
                            if (src.startswith(clean_dev) or src_real.startswith(clean_dev) or
                                (src_parent and src_parent == parent_target)):
                                return True

        # Check findmnt for archiso bootmnt
        if shutil.which("findmnt"):
            try:
                out = subprocess.check_output(
                    ["findmnt", "-n", "-o", "SOURCE", "/run/archiso/bootmnt"],
                    text=True, stderr=subprocess.DEVNULL
                ).strip()
                if out:
                    out_real = os.path.realpath(out)
                    out_parent = get_parent_disk(out_real)
                    if out.startswith(clean_dev) or out_real.startswith(clean_dev) or out_parent == parent_target:
                        return True
            except Exception:
                pass

        # Check for iso9660 or ARCH_ label on device or child partitions
        if shutil.which("lsblk"):
            try:
                out = subprocess.check_output(
                    ["lsblk", "-no", "FSTYPE,LABEL", clean_dev],
                    text=True, stderr=subprocess.DEVNULL
                )
                if "iso9660" in out or "ARCH_" in out:
                    return True
            except Exception:
                pass

    except Exception:
        pass
    return False

def revalidate_target_disk(
    disk_path: str,
    expected_size_bytes: Optional[int] = None,
    allow_virtual_only: bool = False
) -> Tuple[bool, str]:
    """
    Rigorously revalidate the target disk immediately before destructive operations:
    1. Verify disk device node exists.
    2. Guard against wiping the active host OS disk.
    3. Guard against wiping the live installation media.
    4. Guard against drive enumeration shifts (size verification).
    """
    clean_path = os.path.realpath(disk_path)
    if not os.path.exists(clean_path):
        return False, f"Target disk '{disk_path}' does not exist as a block device node."

    # Guard against host disk wipe
    host_disk = detect_host_system_disk()
    if host_disk and (clean_path == host_disk or get_parent_disk(clean_path) == host_disk):
        return False, f"FATAL: Target disk '{disk_path}' is the host operating system disk! Destructive action blocked."

    # Guard against live media wipe
    if is_device_live_media(clean_path):
        return False, f"FATAL: Target disk '{disk_path}' contains active live installer media! Destructive action blocked."

    # Guard against size discrepancies
    if expected_size_bytes and expected_size_bytes > 0:
        try:
            actual_size = 0
            if shutil.which("blockdev"):
                actual_size = int(subprocess.check_output(["blockdev", "--getsize64", clean_path], text=True).strip())
            elif os.path.exists(f"/sys/class/block/{os.path.basename(clean_path)}/size"):
                with open(f"/sys/class/block/{os.path.basename(clean_path)}/size", "r") as f:
                    actual_size = int(f.read().strip()) * 512

            if actual_size > 0:
                # Discrepancy > 100MB indicates potential drive order swap
                if abs(actual_size - expected_size_bytes) > 100 * 1024 * 1024:
                    return False, f"FATAL: Disk size changed! Expected {expected_size_bytes} bytes, probed {actual_size} bytes."
        except Exception as e:
            return False, f"Could not verify disk size for '{disk_path}': {str(e)}"

    return True, "Revalidation passed"

def unmount_target_disk(disk_path: str) -> bool:
    """
    Safely unmount all mounted partitions and deactivate swap on the target disk before partitioning.
    """
    clean_path = os.path.realpath(disk_path)
    try:
        # Check active swap on target partitions
        if os.path.exists("/proc/swaps") and shutil.which("swapoff"):
            with open("/proc/swaps", "r", encoding="utf-8") as f:
                for line in f:
                    swap_dev = line.split()[0]
                    if swap_dev.startswith(clean_path):
                        subprocess.run(["swapoff", swap_dev], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Check /proc/mounts for any mounts on disk_path
        if os.path.exists("/proc/mounts"):
            with open("/proc/mounts", "r", encoding="utf-8") as f:
                mounted = [line.split()[1] for line in f if line.split()[0].startswith(clean_path)]
            # Unmount in reverse order (deepest path first)
            for m in sorted(mounted, key=len, reverse=True):
                subprocess.run(["umount", "-R", "-f", m], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        return False
    return True

def verify_partition_nodes(disk_path: str, partition_numbers: List[int]) -> bool:
    """
    Verify that expected partition device nodes exist after partitioning.
    """
    if shutil.which("partprobe"):
        subprocess.run(["partprobe", disk_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if shutil.which("udevadm"):
        subprocess.run(["udevadm", "settle"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.5)

    sep = "p" if disk_path[-1].isdigit() else ""
    for num in partition_numbers:
        part_dev = f"{disk_path}{sep}{num}"
        if not os.path.exists(part_dev):
            return False
    return True

def verify_filesystem(part_path: str, expected_fstype: str) -> bool:
    """
    Verify that a partition was formatted with the expected filesystem.
    """
    if not os.path.exists(part_path):
        return False

    if shutil.which("blkid"):
        try:
            out = subprocess.check_output(["blkid", "-s", "TYPE", "-o", "value", part_path], text=True).strip()
            if expected_fstype.lower() in out.lower() or (expected_fstype.lower() == "vfat" and "fat" in out.lower()):
                return True
        except Exception:
            pass

    if shutil.which("lsblk"):
        try:
            out = subprocess.check_output(["lsblk", "-no", "FSTYPE", part_path], text=True).strip()
            if expected_fstype.lower() in out.lower() or (expected_fstype.lower() == "vfat" and "fat" in out.lower()):
                return True
        except Exception:
            pass

    return False

def list_disks() -> List[BlockDevice]:
    """List candidate installation disks using lsblk with safety flags."""
    disks = []
    host_disk = detect_host_system_disk()

    if shutil.which("lsblk"):
        try:
            cmd = ["lsblk", "-J", "-b", "-o", "NAME,PATH,TYPE,SIZE,MODEL,TRAN,ROTA,MOUNTPOINT"]
            out = subprocess.check_output(cmd, text=True)
            data = json.loads(out)
            for dev in data.get("blockdevices", []):
                if dev.get("type") == "disk":
                    # Filter out read-only / loop devices (unless loop explicitly enabled)
                    name = dev.get("name", "")
                    if name.startswith("airoot") or name.startswith("zram"):
                        continue

                    parts = []
                    for child in dev.get("children", []):
                        parts.append({
                            "name": child.get("name"),
                            "path": child.get("path"),
                            "size": child.get("size"),
                            "mountpoint": child.get("mountpoint"),
                        })

                    bytes_val = int(dev.get("size", 0))
                    gib = round(bytes_val / (1024**3), 1)
                    size_str = f"{gib} GiB"

                    dev_path = dev.get("path", f"/dev/{name}")
                    is_live = is_device_live_media(dev_path)
                    is_host = bool(host_disk and (dev_path == host_disk or os.path.realpath(dev_path) == host_disk))

                    disks.append(BlockDevice(
                        name=name,
                        path=dev_path,
                        size=size_str,
                        size_bytes=bytes_val,
                        model=dev.get("model") or "Generic Drive",
                        tran=dev.get("tran") or "internal",
                        is_rotational=bool(dev.get("rota", False)),
                        partitions=parts,
                        is_live_media=is_live,
                        is_host_disk=is_host,
                    ))
        except Exception:
            pass

    # Fallback dummy disk for dry-run or when probing fails on non-Linux
    if not disks:
        disks.append(BlockDevice(
            name="vda",
            path="/dev/vda",
            size="64.0 GiB",
            size_bytes=64 * 1024**3,
            model="VirtIO Virtual Block Device",
            tran="virtio",
            is_rotational=False,
            partitions=[],
            is_live_media=False,
            is_host_disk=False,
        ))
    return disks

def plan_partition_table(disk_path: str, fs_type: str = "btrfs", swap_size_gib: int = 4, efi_size_mib: int = 1024) -> Dict[str, Any]:
    """Generate partition plan for a target disk."""
    plan = {
        "disk": disk_path,
        "label": "gpt",
        "partitions": [
            {
                "number": 1,
                "name": "HORIZON_EFI",
                "type": "C12A7328-F81F-11D2-BA4B-00A0C93EC93B",  # ESP GUID
                "size_mib": efi_size_mib,
                "fs": "vfat",
                "mountpoint": "/boot/efi",
                "flags": ["boot", "esp"],
            }
        ],
        "filesystem": fs_type,
        "btrfs_subvolumes": []
    }

    part_num = 2
    if swap_size_gib > 0:
        plan["partitions"].append({
            "number": part_num,
            "name": "HORIZON_SWAP",
            "type": "0657FD6D-A4AB-43C4-84E5-0933C84B4F4F",  # Linux Swap GUID
            "size_mib": swap_size_gib * 1024,
            "fs": "swap",
            "mountpoint": "[SWAP]",
        })
        part_num += 1

    plan["partitions"].append({
        "number": part_num,
        "name": "HORIZON_ROOT",
        "type": "4F68BCE3-E8CD-4DB1-96E7-FBCAF984B709",  # Linux x86-64 root GUID
        "size_mib": "REST",
        "fs": fs_type,
        "mountpoint": "/",
    })

    if fs_type == "btrfs":
        plan["btrfs_subvolumes"] = [
            {"name": "@", "mountpoint": "/", "mount_opts": "noatime,compress=zstd:1,space_cache=v2"},
            {"name": "@home", "mountpoint": "/home", "mount_opts": "noatime,compress=zstd:1,space_cache=v2"},
            {"name": "@snapshots", "mountpoint": "/.snapshots", "mount_opts": "noatime,compress=zstd:1,space_cache=v2"},
            {"name": "@cache", "mountpoint": "/var/cache", "mount_opts": "noatime,compress=zstd:1,space_cache=v2"},
            {"name": "@log", "mountpoint": "/var/log", "mount_opts": "noatime,compress=zstd:1,space_cache=v2"},
        ]

    return plan
