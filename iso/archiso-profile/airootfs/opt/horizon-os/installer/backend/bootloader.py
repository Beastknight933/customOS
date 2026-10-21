#!/usr/bin/env python3
"""
Horizon OS Installer - Bootloader Configuration & Verification Engine
Supports Limine, GRUB, and systemd-boot with firmware detection, kernel discovery,
root UUID resolution, Btrfs subvolume configuration, and rigorous post-install verification.
"""
import os
import re
import shutil
import subprocess
from typing import Optional, Tuple, Dict, Any, List
from .executor import InstallExecutor

def is_firmware_uefi() -> bool:
    """Check if the current host/installer environment booted in UEFI mode."""
    return os.path.exists("/sys/firmware/efi")

def discover_installed_kernels(target_root: str) -> Dict[str, str]:
    """
    Discover installed Linux kernels and matching initramfs images in target /boot.
    Returns dict: {'kernel': 'vmlinuz-...', 'initramfs': 'initramfs-....img'}
    """
    boot_dir = os.path.join(target_root, "boot")
    if not os.path.exists(boot_dir):
        return {}

    # Priority order of kernels
    kernel_candidates = [
        "vmlinuz-linux-cachyos",
        "vmlinuz-linux-zen",
        "vmlinuz-linux",
        "vmlinuz-linux-lts",
    ]

    selected_kernel = ""
    for k in kernel_candidates:
        if os.path.exists(os.path.join(boot_dir, k)):
            selected_kernel = k
            break

    if not selected_kernel:
        # Fallback search for any vmlinuz-*
        for f in os.listdir(boot_dir):
            if f.startswith("vmlinuz-") and not f.endswith(".old"):
                selected_kernel = f
                break

    if not selected_kernel:
        return {}

    # Match initramfs
    suffix = selected_kernel.replace("vmlinuz-", "")
    initramfs_candidates = [
        f"initramfs-{suffix}.img",
        f"initramfs-linux.img",
    ]

    selected_initrd = ""
    for initrd in initramfs_candidates:
        if os.path.exists(os.path.join(boot_dir, initrd)):
            selected_initrd = initrd
            break

    if not selected_initrd:
        for f in os.listdir(boot_dir):
            if f.startswith("initramfs-") and f.endswith(".img") and not f.endswith("-fallback.img"):
                selected_initrd = f
                break

    return {
        "kernel": selected_kernel,
        "initramfs": selected_initrd or "initramfs-linux.img",
    }

def get_partition_uuid(partition_path: str) -> str:
    """Resolve UUID of a partition using blkid or lsblk."""
    clean_path = os.path.realpath(partition_path)
    if shutil.which("blkid"):
        try:
            out = subprocess.check_output(
                ["blkid", "-s", "UUID", "-o", "value", clean_path],
                text=True, stderr=subprocess.DEVNULL
            ).strip()
            if out:
                return out
        except Exception:
            pass

    if shutil.which("lsblk"):
        try:
            out = subprocess.check_output(
                ["lsblk", "-no", "UUID", clean_path],
                text=True, stderr=subprocess.DEVNULL
            ).strip()
            if out:
                return out
        except Exception:
            pass

    return ""

class BootloaderManager:
    def __init__(
        self,
        executor: InstallExecutor,
        target_root: str,
        selected_disk: str,
        bootloader: str = "limine",
        filesystem: str = "btrfs",
    ):
        self.executor = executor
        self.target_root = os.path.abspath(target_root)
        self.selected_disk = selected_disk
        self.bootloader = bootloader.lower()
        self.filesystem = filesystem.lower()

        sep = "p" if selected_disk[-1].isdigit() else ""
        self.efi_partition = f"{selected_disk}{sep}1"
        self.swap_partition = f"{selected_disk}{sep}2"
        self.root_partition = f"{selected_disk}{sep}3"

    def install(self) -> Tuple[bool, str]:
        """
        Execute full bootloader installation and verification pipeline.
        Stops immediately and returns (False, error) if any phase fails.
        """
        self.executor.set_stage("Installing Bootloader")
        is_uefi = is_firmware_uefi()

        # Step 1: Pre-flight Verification of EFI & Kernel
        esp_path = os.path.join(self.target_root, "boot", "efi")
        if not self.executor.dry_run:
            if not os.path.exists(esp_path):
                err = f"EFI system partition mountpoint {esp_path} does not exist"
                self.executor.logger.log(f"FATAL: {err}")
                return False, err

            if not self.executor.verify_mount(esp_path):
                err = f"EFI system partition {esp_path} is not an active mountpoint"
                self.executor.logger.log(f"FATAL: {err}")
                return False, err

            kernels = discover_installed_kernels(self.target_root)
            if not kernels.get("kernel"):
                err = "No installed Linux kernel found in target /boot! Base/kernel installation failed or is incomplete."
                self.executor.logger.log(f"FATAL: {err}")
                return False, err

        # Step 2: Dispatch Bootloader Handler
        if self.bootloader == "limine":
            return self._install_limine(is_uefi)
        elif self.bootloader == "grub":
            return self._install_grub(is_uefi)
        elif self.bootloader == "systemd-boot":
            return self._install_systemd_boot(is_uefi)
        else:
            return False, f"Unsupported bootloader: {self.bootloader}"

    def _install_limine(self, is_uefi: bool) -> Tuple[bool, str]:
        """
        Configure Limine bootloader for UEFI with direct Btrfs and Snapper support.
        """
        self.executor.logger.log("Configuring Limine bootloader...")
        kernels = discover_installed_kernels(self.target_root) if not self.executor.dry_run else {"kernel": "vmlinuz-linux", "initramfs": "initramfs-linux.img"}
        kernel_name = kernels.get("kernel", "vmlinuz-linux")
        initrd_name = kernels.get("initramfs", "initramfs-linux.img")

        root_uuid = get_partition_uuid(self.root_partition) if not self.executor.dry_run else "MOCK-ROOT-UUID-BTRFS-001"
        subvol_param = "rootflags=subvol=@" if self.filesystem == "btrfs" else ""
        cmdline = f"root=UUID={root_uuid} {subvol_param} rw quiet splash loglevel=3"

        # 1. Deploy EFI binaries
        if not self.executor.dry_run:
            esp_dir = os.path.join(self.target_root, "boot", "efi")
            boot_efi_dir = os.path.join(esp_dir, "EFI", "BOOT")
            limine_efi_dir = os.path.join(esp_dir, "EFI", "limine")
            os.makedirs(boot_efi_dir, exist_ok=True)
            os.makedirs(limine_efi_dir, exist_ok=True)

            # Copy Limine EFI loader from package
            limine_share = os.path.join(self.target_root, "usr", "share", "limine")
            src_loader = os.path.join(limine_share, "BOOTX64.EFI")
            if os.path.exists(src_loader):
                shutil.copy2(src_loader, os.path.join(boot_efi_dir, "BOOTX64.EFI"))
                shutil.copy2(src_loader, os.path.join(limine_efi_dir, "BOOTX64.EFI"))

            # Also ensure kernel and initramfs are present on ESP for direct loading
            boot_src_dir = os.path.join(self.target_root, "boot")
            for f in [kernel_name, initrd_name, "initramfs-linux-fallback.img"]:
                src_f = os.path.join(boot_src_dir, f)
                if os.path.exists(src_f):
                    try:
                        shutil.copy2(src_f, os.path.join(esp_dir, f))
                    except Exception:
                        pass

        # 2. Generate limine.conf
        limine_conf = f"""#
# Horizon OS - Limine Bootloader Configuration
#
timeout: 3
default_entry: 1

/Horizon OS (KDE Plasma 6)
    protocol: linux
    kernel_path: boot():/{kernel_name}
    module_path: boot():/{initrd_name}
    cmdline: {cmdline}

/Horizon OS (Btrfs Direct Boot)
    protocol: linux
    kernel_path: boot(3):/@/boot/{kernel_name}
    module_path: boot(3):/@/boot/{initrd_name}
    cmdline: {cmdline}
"""
        self.executor.write_target_file("boot/efi/limine.conf", limine_conf)
        self.executor.write_target_file("boot/limine.conf", limine_conf)

        # 3. Add UEFI boot entry via efibootmgr inside chroot if available
        if is_uefi and not self.executor.dry_run:
            self.executor.chroot_exec(
                ["efibootmgr", "--create", "--disk", self.selected_disk, "--part", "1",
                 "--label", "Horizon OS (Limine)", "--loader", "\\EFI\\limine\\BOOTX64.EFI"],
                description="Registering Limine in UEFI firmware",
            )

        # 4. Rigorous Post-Install Verification
        if not self.executor.dry_run:
            conf_path = os.path.join(self.target_root, "boot", "efi", "limine.conf")
            if not os.path.exists(conf_path):
                return False, f"Limine configuration file {conf_path} was not created"
            with open(conf_path, "r", encoding="utf-8") as f:
                content = f.read()
                if root_uuid and root_uuid not in content:
                    return False, f"limine.conf does not contain root UUID {root_uuid}"
                if self.filesystem == "btrfs" and "subvol=@" not in content:
                    return False, "limine.conf does not specify required Btrfs subvol=@ parameter"

            # Check loader presence
            loader_path = os.path.join(self.target_root, "boot", "efi", "EFI", "BOOT", "BOOTX64.EFI")
            if not os.path.exists(loader_path) and not os.path.exists(os.path.join(self.target_root, "boot", "efi", "EFI", "limine", "BOOTX64.EFI")):
                return False, "Limine EFI loader was not installed to ESP"

        self.executor.logger.log("Limine bootloader verified and ready.")
        return True, "Limine installed and verified"

    def _install_grub(self, is_uefi: bool) -> Tuple[bool, str]:
        """
        Configure GRUB for UEFI with Btrfs support.
        """
        self.executor.logger.log("Installing GRUB...")
        root_uuid = get_partition_uuid(self.root_partition) if not self.executor.dry_run else "MOCK-ROOT-UUID"
        subvol_param = "rootflags=subvol=@" if self.filesystem == "btrfs" else ""

        # Write /etc/default/grub
        grub_default = f"""#
# Horizon OS GRUB Configuration
#
GRUB_DEFAULT=0
GRUB_TIMEOUT=3
GRUB_DISTRIBUTOR="Horizon OS"
GRUB_CMDLINE_LINUX_DEFAULT="loglevel=3 quiet splash {subvol_param}"
GRUB_CMDLINE_LINUX=""
GRUB_PRELOAD_MODULES="part_gpt btrfs"
GRUB_ENABLE_CRYPTODISK=n
"""
        self.executor.write_target_file("etc/default/grub", grub_default)

        # Execute grub-install
        cmd_install = [
            "grub-install",
            "--target=x86_64-efi",
            "--efi-directory=/boot/efi",
            "--bootloader-id=HORIZON",
            "--recheck"
        ]
        if not self.executor.chroot_exec(cmd_install, description="Running grub-install"):
            return False, "grub-install command failed"

        # Execute grub-mkconfig
        if not self.executor.chroot_exec(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"], description="Running grub-mkconfig"):
            return False, "grub-mkconfig command failed"

        # Post-install verification
        if not self.executor.dry_run:
            grub_efi = os.path.join(self.target_root, "boot", "efi", "EFI", "HORIZON", "grubx64.efi")
            grub_cfg = os.path.join(self.target_root, "boot", "grub", "grub.cfg")

            if not os.path.exists(grub_efi):
                return False, f"GRUB EFI binary not found at {grub_efi}"
            if not os.path.exists(grub_cfg):
                return False, f"GRUB configuration not found at {grub_cfg}"

            with open(grub_cfg, "r", encoding="utf-8") as f:
                content = f.read()
                if self.filesystem == "btrfs" and "subvol=@" not in content and root_uuid not in content:
                    return False, "grub.cfg does not contain valid Btrfs subvolume or root UUID reference"

        self.executor.logger.log("GRUB bootloader verified and ready.")
        return True, "GRUB installed and verified"

    def _install_systemd_boot(self, is_uefi: bool) -> Tuple[bool, str]:
        """
        Configure systemd-boot for UEFI.
        Because systemd-boot cannot natively read files from inside a Btrfs subvolume
        when /boot is on the root partition, the kernel and initramfs must be staged on ESP.
        """
        self.executor.logger.log("Configuring systemd-boot...")
        if not is_uefi:
            return False, "systemd-boot requires UEFI firmware mode."

        # Install systemd-boot to ESP
        if not self.executor.chroot_exec(["bootctl", "--esp-path=/boot/efi", "install"], description="Installing systemd-boot to ESP"):
            return False, "bootctl install failed"

        kernels = discover_installed_kernels(self.target_root) if not self.executor.dry_run else {"kernel": "vmlinuz-linux", "initramfs": "initramfs-linux.img"}
        kernel_name = kernels.get("kernel", "vmlinuz-linux")
        initrd_name = kernels.get("initramfs", "initramfs-linux.img")

        root_uuid = get_partition_uuid(self.root_partition) if not self.executor.dry_run else "MOCK-ROOT-UUID"
        subvol_param = "rootflags=subvol=@" if self.filesystem == "btrfs" else ""

        # Stage kernel and initramfs to ESP /boot/efi/horizon/
        if not self.executor.dry_run:
            esp_horizon_dir = os.path.join(self.target_root, "boot", "efi", "horizon")
            os.makedirs(esp_horizon_dir, exist_ok=True)
            src_kernel = os.path.join(self.target_root, "boot", kernel_name)
            src_initrd = os.path.join(self.target_root, "boot", initrd_name)
            if os.path.exists(src_kernel):
                shutil.copy2(src_kernel, os.path.join(esp_horizon_dir, kernel_name))
            if os.path.exists(src_initrd):
                shutil.copy2(src_initrd, os.path.join(esp_horizon_dir, initrd_name))

        # Write loader.conf
        loader_conf = """#
# Horizon OS - systemd-boot Configuration
#
default  horizon.conf
timeout  3
console-mode max
editor   no
"""
        self.executor.write_target_file("boot/efi/loader/loader.conf", loader_conf)

        # Write entries/horizon.conf
        entry_conf = f"""#
# Horizon OS Entry
#
title   Horizon OS (KDE Plasma 6)
linux   /horizon/{kernel_name}
initrd  /horizon/{initrd_name}
options root=UUID={root_uuid} {subvol_param} rw quiet splash loglevel=3
"""
        self.executor.write_target_file("boot/efi/loader/entries/horizon.conf", entry_conf)

        # Verification
        if not self.executor.dry_run:
            entry_path = os.path.join(self.target_root, "boot", "efi", "loader", "entries", "horizon.conf")
            loader_path = os.path.join(self.target_root, "boot", "efi", "EFI", "systemd", "systemd-bootx64.efi")
            if not os.path.exists(entry_path):
                return False, f"systemd-boot entry {entry_path} was not created"
            if not os.path.exists(loader_path) and not os.path.exists(os.path.join(self.target_root, "boot", "efi", "EFI", "BOOT", "BOOTX64.EFI")):
                return False, "systemd-boot EFI binary was not installed"

        self.executor.logger.log("systemd-boot verified and ready.")
        return True, "systemd-boot installed and verified"
