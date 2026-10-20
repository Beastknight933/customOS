#!/usr/bin/env python3
"""
Horizon OS Installer - Storage & Partitioning Planner
"""
import os
import json
import subprocess
import shutil
from typing import List, Dict, Any, Optional

class BlockDevice:
    def __init__(self, name: str, path: str, size: str, size_bytes: int, model: str, tran: str, is_rotational: bool, partitions: List[Dict[str, Any]], is_live_media: bool = False):
        self.name = name
        self.path = path
        self.size = size
        self.size_bytes = size_bytes
        self.model = model
        self.tran = tran
        self.is_rotational = is_rotational
        self.partitions = partitions
        self.is_live_media = is_live_media

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
        }

def is_device_live_media(device_path: str) -> bool:
    """Check if the given device holds active live ISO mounts."""
    try:
        # Check /proc/mounts
        if os.path.exists("/proc/mounts"):
            with open("/proc/mounts", "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        src, target = parts[0], parts[1]
                        if "/run/archiso" in target or (target == "/" and "airootfs" in src):
                            if src.startswith(device_path):
                                return True
        # Check findmnt for archiso bootmnt
        if shutil.which("findmnt"):
            try:
                out = subprocess.check_output(
                    ["findmnt", "-n", "-o", "SOURCE", "/run/archiso/bootmnt"],
                    text=True, stderr=subprocess.DEVNULL
                ).strip()
                if out and out.startswith(device_path):
                    return True
            except Exception:
                pass
    except Exception:
        pass
    return False

def unmount_target_disk(disk_path: str) -> bool:
    """Safely unmount all mounted partitions and deactivate swap on the target disk before partitioning."""
    try:
        if shutil.which("swapoff"):
            subprocess.run(["swapoff", "-a"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Check /proc/mounts for any mounts on disk_path
        if os.path.exists("/proc/mounts"):
            with open("/proc/mounts", "r", encoding="utf-8") as f:
                mounted = [line.split()[1] for line in f if line.startswith(disk_path)]
            # Unmount in reverse order (deepest path first)
            for m in sorted(mounted, key=len, reverse=True):
                subprocess.run(["umount", "-f", "-R", m], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        return False
    return True

def list_disks() -> List[BlockDevice]:
    """List candidate installation disks using lsblk."""
    disks = []
    if shutil.which("lsblk"):
        try:
            cmd = ["lsblk", "-J", "-b", "-o", "NAME,PATH,TYPE,SIZE,MODEL,TRAN,ROTA,MOUNTPOINT"]
            out = subprocess.check_output(cmd, text=True)
            data = json.loads(out)
            for dev in data.get("blockdevices", []):
                if dev.get("type") == "disk":
                    # Filter out read-only / loop devices
                    if dev.get("name", "").startswith("loop") or dev.get("name", "").startswith("airoot"):
                        continue
                    
                    parts = []
                    for child in dev.get("children", []):
                        parts.append({
                            "name": child.get("name"),
                            "path": child.get("path"),
                            "size": child.get("size"),
                            "mountpoint": child.get("mountpoint"),
                        })
                    
                    # Human readable size
                    bytes_val = int(dev.get("size", 0))
                    gib = round(bytes_val / (1024**3), 1)
                    size_str = f"{gib} GiB"

                    dev_path = dev.get("path", f"/dev/{dev.get('name')}")
                    is_live = is_device_live_media(dev_path)

                    disks.append(BlockDevice(
                        name=dev.get("name", ""),
                        path=dev_path,
                        size=size_str,
                        size_bytes=bytes_val,
                        model=dev.get("model") or "Generic Drive",
                        tran=dev.get("tran") or "internal",
                        is_rotational=bool(dev.get("rota", False)),
                        partitions=parts,
                        is_live_media=is_live,
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
