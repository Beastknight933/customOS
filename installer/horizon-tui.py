#!/usr/bin/env python3
"""
Horizon OS — Full-Screen Terminal User Interface (TUI) Installer
Operates cleanly on Arch Linux live ISOs, virtual machines, and installation environments.
Includes strict account security, non-echoing credentials, failure cleanup,
storage validation guards, and verified bootloader configuration.
"""

import os
import sys
import re
import time
import json
import getpass
import argparse
import shutil
import subprocess
from typing import Dict, Any, List, Optional, Tuple

# Ensure installer backend is importable
INSTALLER_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(INSTALLER_DIR)
sys.path.insert(0, INSTALLER_DIR)

from backend.hardware import probe_all_hardware, detect_cpu_info
from backend.storage import (
    list_disks,
    plan_partition_table,
    is_device_live_media,
    unmount_target_disk,
    revalidate_target_disk,
    verify_partition_nodes,
    verify_filesystem,
    detect_host_system_disk,
)
from backend.executor import InstallExecutor, InstallLogger
from backend.deployer import ComponentDeployer
from backend.validator import InstallationValidator
from backend.bootloader import BootloaderManager, discover_installed_kernels
from backend.account import validate_username, validate_hostname, prompt_secure_password

# Colors and formatting
ESC = "\033["
RESET = f"{ESC}0m"
BOLD = f"{ESC}1m"
DIM = f"{ESC}2m"
CYAN = f"{ESC}36m"
BRIGHT_CYAN = f"{ESC}96m"
GREEN = f"{ESC}32m"
BRIGHT_GREEN = f"{ESC}92m"
YELLOW = f"{ESC}33m"
BRIGHT_YELLOW = f"{ESC}93m"
RED = f"{ESC}31m"
BRIGHT_RED = f"{ESC}91m"
MAGENTA = f"{ESC}35m"
BLUE = f"{ESC}34m"
WHITE = f"{ESC}97m"

BANNER = f"""
{BRIGHT_CYAN}  ██╗  ██╗ ██████╗ ██████╗ ██╗███████╗ ██████╗ ███╗   ██╗     ██████╗ ███████╗
  ██║  ██║██╔═══██╗██╔══██╗██║╚══███╔╝██╔═══██╗████╗  ██║    ██╔═══██╗██╔════╝
  ███████║██║   ██║██████╔╝██║  ███╔╝ ██║   ██║██╔██╗ ██║    ██║   ██║███████╗
  ██╔══██║██║   ██║██╔══██╗██║ ███╔╝  ██║   ██║██║╚██╗██║    ██║   ██║╚════██║
  ██║  ██║╚██████╔╝██║  ██║██║███████╗╚██████╔╝██║ ╚████║    ╚██████╔╝███████║
  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝     ╚═════╝ ╚══════╝{RESET}
{DIM}  KDE Plasma 6 • KWin • Caelestia Shell • Ryoku SDDM • CachyOS Performance Core{RESET}
"""

class HorizonInstallerApp:
    def __init__(self, dry_run: bool = False, target_root: str = "/mnt"):
        self.dry_run = dry_run
        self.target_root = os.path.abspath(target_root)
        self.logger = InstallLogger()
        self.executor = InstallExecutor(dry_run=dry_run, target_root=target_root, logger=self.logger)
        self.deployer = ComponentDeployer(executor=self.executor, repo_root=REPO_ROOT)
        
        # State
        self.hardware: Dict[str, Any] = {}
        self.available_disks: List[Any] = []
        self.selected_disk: Optional[str] = None
        self.selected_disk_size_bytes: int = 0
        self.filesystem: str = "btrfs"
        self.swap_size_gib: int = 4
        self.bootloader: str = "limine"
        
        # User Configuration (No hardcoded credentials)
        self.hostname: str = "horizon-pc"
        self.username: str = "horizon"
        self.user_fullname: str = "Horizon Operator"
        self.user_password: str = ""
        self.root_password: str = ""
        self.lock_root: bool = True
        self.timezone: str = "UTC"
        self.locale: str = "en_US.UTF-8"
        self.keymap: str = "us"

    def clear(self):
        os.system("clear" if os.name != "nt" else "cls")

    def print_header(self, stage_title: str):
        self.clear()
        print(BANNER)
        print(f"{BOLD}{WHITE}  ─── [ {BRIGHT_CYAN}{stage_title}{WHITE} ] ──────────────────────────────────────────────────────────{RESET}\n")

    def stage_welcome_and_hardware(self):
        self.print_header("Stage 1 of 5: Hardware Probing & Platform Detection")
        print(f"  {CYAN}Detecting system hardware capabilities...{RESET}")
        self.hardware = probe_all_hardware()
        cpu = self.hardware["cpu"]
        mem = self.hardware["memory"]
        uefi = self.hardware["uefi"]
        gpus = self.hardware["gpus"]

        print(f"\n  {BOLD}Hardware Probing Summary:{RESET}")
        print(f"    • {BOLD}Firmware:{RESET}       {'UEFI (Supported)' if uefi else 'BIOS / Legacy MBR'}")
        print(f"    • {BOLD}CPU Model:{RESET}      {cpu['model']} ({cpu['cores']} threads, {cpu['arch']})")
        print(f"    • {BOLD}x86-64-v3:{RESET}      {'YES (AVX2/BMI2 optimized CachyOS repos eligible)' if cpu['v3_supported'] else 'Standard x86-64'}")
        print(f"    • {BOLD}x86-64-v4:{RESET}      {'YES (AVX-512 eligible)' if cpu['v4_supported'] else 'No'}")
        print(f"    • {BOLD}System RAM:{RESET}     {mem['total_gb']} GiB ({mem['total_mb']} MiB)")
        for i, g in enumerate(gpus, 1):
            print(f"    • {BOLD}GPU {i}:{RESET}          {g}")

        print(f"\n  {GREEN}Platform successfully identified.{RESET}")
        print(f"  {DIM}Press Enter to proceed to Storage & Partitioning...{RESET}")
        try:
            input()
        except EOFError:
            pass

    def stage_storage_selection(self):
        self.print_header("Stage 2 of 5: Storage Selection & Partitioning Layout")
        self.available_disks = list_disks()
        
        print(f"  {BOLD}Available Storage Devices:{RESET}")
        for i, d in enumerate(self.available_disks, 1):
            disk_info = d.to_dict()
            rot = "HDD" if disk_info["is_rotational"] else "SSD/NVMe"
            status_tags = []
            if disk_info.get("is_live_media"):
                status_tags.append(f"{RED}[LIVE INSTALLER MEDIA]{RESET}")
            if disk_info.get("is_host_disk"):
                status_tags.append(f"{RED}[HOST OS DISK - PROTECTED]{RESET}")

            tag_str = " " + " ".join(status_tags) if status_tags else ""
            print(f"    [{BOLD}{i}{RESET}] {BRIGHT_CYAN}{disk_info['path']}{RESET} — {disk_info['size']} ({rot}, {disk_info['model']}){tag_str}")

        while True:
            print(f"\n  Select target disk number [1-{len(self.available_disks)}]: ", end="")
            try:
                choice = input().strip()
                idx = int(choice) - 1 if choice.isdigit() else 0
                idx = max(0, min(idx, len(self.available_disks) - 1))
            except (ValueError, EOFError):
                idx = 0
                
            chosen = self.available_disks[idx].to_dict()
            if chosen.get("is_live_media"):
                print(f"  {RED}ERROR: {chosen['path']} is the active installer media and cannot be partitioned! Choose another device.{RESET}")
                continue
            if chosen.get("is_host_disk"):
                print(f"  {RED}ERROR: {chosen['path']} contains the active running host system! Cannot destroy host disk.{RESET}")
                continue
            break

        self.selected_disk = chosen["path"]
        self.selected_disk_size_bytes = chosen.get("size_bytes", 0)
        print(f"  Selected target disk: {BRIGHT_GREEN}{self.selected_disk}{RESET} ({chosen['size']})")

        print(f"\n  {BOLD}Filesystem Scheme:{RESET}")
        print(f"    [1] Btrfs (Recommended: subvolumes @, @home, @snapshots, @cache, @log + zstd)")
        print(f"    [2] Ext4 (Classic robust Linux filesystem)")
        print(f"  Choice [1-2, default 1]: ", end="")
        try:
            fs_choice = input().strip()
            self.filesystem = "ext4" if fs_choice == "2" else "btrfs"
        except EOFError:
            self.filesystem = "btrfs"
        print(f"  Filesystem: {BRIGHT_GREEN}{self.filesystem}{RESET}")

        print(f"  Swap partition size in GiB [default 4]: ", end="")
        try:
            swap_input = input().strip()
            self.swap_size_gib = int(swap_input) if swap_input.isdigit() else 4
        except EOFError:
            self.swap_size_gib = 4

        print(f"\n  {DIM}Press Enter to proceed to System Configuration...{RESET}")
        try:
            input()
        except EOFError:
            pass

    def stage_system_configuration(self):
        self.print_header("Stage 3 of 5: System Identity & Accounts")
        print(f"  Configure identity, user account, and bootloader options.\n")

        # Hostname validation loop
        while True:
            print(f"  Enter Hostname [default '{self.hostname}']: ", end="")
            try:
                h = input().strip()
                target_h = h if h else self.hostname
            except EOFError:
                target_h = self.hostname

            valid, err = validate_hostname(target_h)
            if valid:
                self.hostname = target_h
                break
            print(f"  {RED}Invalid hostname: {err}{RESET}")

        # Username validation loop
        while True:
            print(f"  Enter Primary User Login [default '{self.username}']: ", end="")
            try:
                u = input().strip()
                target_u = u if u else self.username
            except EOFError:
                target_u = self.username

            valid, err = validate_username(target_u)
            if valid:
                self.username = target_u
                break
            print(f"  {RED}Invalid username: {err}{RESET}")

        # Secure User Password Entry (Non-echoing)
        print(f"\n  {BOLD}Set Password for user '{self.username}':{RESET}")
        self.user_password = prompt_secure_password(f"Enter password for {self.username}")

        # Root Password Configuration (Explicit choice, non-echoing)
        print(f"\n  {BOLD}Root (Administrator) Account Policy:{RESET}")
        print(f"    [1] Lock root account (Recommended: administrative tasks use 'sudo')")
        print(f"    [2] Set a separate, dedicated root password")
        print(f"  Choice [1-2, default 1]: ", end="")
        try:
            root_choice = input().strip()
        except EOFError:
            root_choice = "1"

        if root_choice == "2":
            self.lock_root = False
            self.root_password = prompt_secure_password("Enter dedicated root password", "Confirm dedicated root password")
            print(f"  {GREEN}✓ Dedicated root password established.{RESET}")
        else:
            self.lock_root = True
            self.root_password = ""
            print(f"  {GREEN}✓ Root account will be locked; administrative access via 'sudo'.{RESET}")

        # Bootloader Selection
        print(f"\n  {BOLD}Select Bootloader:{RESET}")
        print(f"    [1] Limine (Recommended: Modern, fast, native Btrfs & snapshot support)")
        print(f"    [2] GRUB (Classic multi-boot with UEFI & Btrfs support)")
        print(f"    [3] systemd-boot (Simple UEFI native loader)")
        print(f"  Choice [1-3, default 1]: ", end="")
        try:
            b_choice = input().strip()
            if b_choice == "2":
                self.bootloader = "grub"
            elif b_choice == "3":
                self.bootloader = "systemd-boot"
            else:
                self.bootloader = "limine"
        except EOFError:
            self.bootloader = "limine"

        print(f"\n  Configuration captured for {BRIGHT_GREEN}{self.username}@{self.hostname}{RESET} (Bootloader: {self.bootloader}).")
        print(f"  {DIM}Press Enter to proceed to Summary...{RESET}")
        try:
            input()
        except EOFError:
            pass

    def stage_confirmation_summary(self) -> bool:
        self.print_header("Stage 4 of 5: Installation Summary & Destructive Safety Check")
        plan = plan_partition_table(self.selected_disk, fs_type=self.filesystem, swap_size_gib=self.swap_size_gib)

        print(f"  {BOLD}{BRIGHT_YELLOW}⚠️  WARNING: ALL DATA ON THE TARGET DISK WILL BE DESTROYED! ⚠️{RESET}\n")
        print(f"  {BOLD}Target Disk:{RESET}       {BRIGHT_RED}{self.selected_disk}{RESET}")
        print(f"  {BOLD}Partition Table:{RESET}   GPT")
        print(f"  {BOLD}Partitions:{RESET}")
        for p in plan["partitions"]:
            print(f"    • Partition {p['number']}: {p['name']} ({p['size_mib']} MiB, {p['fs']}) -> {p['mountpoint']}")
        if plan["btrfs_subvolumes"]:
            print(f"  {BOLD}Btrfs Subvolumes:{RESET}")
            for sub in plan["btrfs_subvolumes"]:
                print(f"    • Subvol {sub['name']} -> {sub['mountpoint']} ({sub['mount_opts']})")
        print(f"  {BOLD}Bootloader:{RESET}       {self.bootloader}")
        print(f"  {BOLD}Profile:{RESET}          CachyOS Performance Core + KDE Plasma 6 Desktop")
        print(f"  {BOLD}Desktop Shell:{RESET}    Horizon Caelestia KDE Port (Top Bar, Hover, Pure Black)")
        print(f"  {BOLD}SDDM Theme:{RESET}       Horizon Ryoku Orbital SDDM (Clockwork, Black)")
        print(f"  {BOLD}Splash Screen:{RESET}    Overload Plasma 6 Splash")
        print(f"  {BOLD}Icon Suite:{RESET}       Candy Bar (candy-icons)")
        print(f"  {BOLD}User Account:{RESET}     {self.username} (Hostname: {self.hostname})")
        print(f"  {BOLD}Dry-Run Mode:{RESET}     {'ACTIVE (No disk writes will occur)' if self.dry_run else 'NO (Live installation)'}")

        print(f"\n  {BOLD}Type 'YES' (all uppercase) to confirm and begin installation:{RESET} ", end="")
        try:
            confirmation = input().strip()
            return confirmation == "YES"
        except EOFError:
            return False

    def _validate_host_tools(self) -> Tuple[bool, List[str]]:
        """Validate required tools are available before attempting real disk operations."""
        required = ["parted", "mkfs.fat", "mount", "umount"]
        if self.filesystem == "btrfs":
            required.append("mkfs.btrfs")
        elif self.filesystem == "ext4":
            required.append("mkfs.ext4")
        if self.swap_size_gib > 0:
            required.extend(["mkswap", "swapon", "swapoff"])
        if not self.dry_run:
            required.extend(["pacstrap", "arch-chroot", "genfstab"])
        missing = [cmd for cmd in required if not shutil.which(cmd)]
        return len(missing) == 0, missing

    def stage_execute_installation(self) -> bool:
        self.print_header("Stage 5 of 5: Installation Execution & Component Deployment")
        print(f"  {CYAN}Executing installation pipeline...{RESET}\n")

        # 1. Immediate disk re-validation and safety check
        if not self.dry_run:
            valid_disk, disk_err = revalidate_target_disk(self.selected_disk)
            if not valid_disk:
                print(f"  {BRIGHT_RED}❌ Pre-Execution Disk Safety Check Failed:{RESET} {disk_err}")
                self.executor.logger.log(f"FATAL: Pre-execution disk safety check failed for {self.selected_disk}: {disk_err}")
                self.executor.last_error = disk_err
                return False

            tools_ok, missing_tools = self._validate_host_tools()
            if not tools_ok:
                missing_str = ", ".join(missing_tools)
                print(f"  {BRIGHT_RED}❌ Missing required host utilities:{RESET} {missing_str}")
                print(f"  {YELLOW}Please ensure you are running within the Arch Linux live environment.{RESET}\n")
                self.executor.logger.log(f"FATAL: Missing host utilities: {missing_tools}")
                self.executor.last_error = f"Missing required host utilities: {missing_str}"
                return False

        steps = [
            ("Partitioning and Formatting Disk", self._step_partition_and_format),
            ("Mounting Target Filesystem", self._step_mount_target),
            ("Pacstrapping Base System & Kernel", self._step_pacstrap_base),
            ("Configuring System Base & Chroot", self._step_configure_chroot),
            ("Installing Bootloader", self._step_install_bootloader),
            ("Deploying Horizon Ryoku SDDM Theme", self._step_deploy_sddm),
            ("Deploying Overload Splash Screen", self._step_deploy_splash),
            ("Deploying Candy Bar Icon Theme", self._step_deploy_icons),
            ("Deploying Horizon Caelestia Shell & Workspace Tracker", self._step_deploy_shell),
            ("Applying Horizon KDE & Visual Identity Defaults", self._step_deploy_defaults),
            ("Running Post-Installation Verification Audit", self._step_verify_installation),
        ]

        total_steps = len(steps)
        for i, (title, func) in enumerate(steps, 1):
            self.executor.set_stage(title)
            print(f"  [{i}/{total_steps}] {BOLD}{WHITE}{title}...{RESET}")
            success = func()
            if not success:
                err_detail = self.executor.last_error or "Stage reported failure"
                cmd_detail = self.executor.last_failed_command or "N/A"
                print(f"\n  {BRIGHT_RED}❌ FAILED at step {i}: {title}{RESET}")
                print(f"  {RED}Error Details:{RESET} {err_detail}")
                print(f"  {RED}Command:{RESET}       {cmd_detail}")
                print(f"\n  {YELLOW}Initiating emergency target unmount and safety cleanup...{RESET}")
                self.executor.cleanup_target_mounts(target_disk=self.selected_disk)
                print(f"  {YELLOW}Recovery instructions:{RESET}")
                print(f"    1. Inspect log file at: /var/log/horizon-install.log")
                print(f"    2. Verify disk state with: lsblk {self.selected_disk}")
                print(f"    3. Re-run installer once issues are resolved.\n")
                return False
            print(f"  {BRIGHT_GREEN}✓ Completed successfully.{RESET}\n")

        print(f"  {BOLD}{BRIGHT_GREEN}=========================================================={RESET}")
        print(f"  {BOLD}{BRIGHT_GREEN}  Horizon OS Installation Complete!{RESET}")
        print(f"  {BOLD}{BRIGHT_GREEN}=========================================================={RESET}")
        print(f"  All components, themes, services, and configurations have been deployed.")
        print(f"  You may now reboot into Horizon OS.\n")
        return True

    def _generate_installer_pacman_conf(self, v3_supported: bool) -> str:
        """Generate a validated pacman.conf for bootstrap with CPU architecture awareness and fallback mirrors."""
        conf_path = "/tmp/horizon-pacman.conf" if not self.dry_run else "horizon-pacman.conf"
        
        mirror_cachyos = "/etc/pacman.d/cachyos-mirrorlist"
        mirror_cachyos_v3 = "/etc/pacman.d/cachyos-v3-mirrorlist"
        mirror_arch = "/etc/pacman.d/mirrorlist"
        
        if not self.dry_run:
            os.makedirs("/etc/pacman.d", exist_ok=True)
            if not os.path.exists(mirror_cachyos):
                with open(mirror_cachyos, "w", encoding="utf-8") as f:
                    f.write("Server = https://mirror.cachyos.org/repo/$arch/$repo\n")
                    f.write("Server = https://eu.mirror.cachyos.org/repo/$arch/$repo\n")
            if not os.path.exists(mirror_cachyos_v3):
                with open(mirror_cachyos_v3, "w", encoding="utf-8") as f:
                    f.write("Server = https://mirror.cachyos.org/repo/x86_64_v3/$repo\n")
                    f.write("Server = https://eu.mirror.cachyos.org/repo/x86_64_v3/$repo\n")
        # Ensure /etc/pacman.d/mirrorlist has active mirrors if present
        mirror_arch = "/etc/pacman.d/mirrorlist"
        if os.path.exists(mirror_arch):
            try:
                with open(mirror_arch, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                has_active = any(line.strip().startswith("Server") for line in lines)
                if not has_active:
                    # Uncomment fast mirrors or prepend reliable defaults
                    with open(mirror_arch, "w", encoding="utf-8") as f:
                        f.write("Server = https://fastly.mirror.pkgbuild.com/$repo/os/$arch\n")
                        f.write("Server = https://mirror.rackspace.com/archlinux/$repo/os/$arch\n")
                        f.write("Server = https://geo.mirror.pkgbuild.com/$repo/os/$arch\n")
                        f.writelines(lines)
            except Exception:
                pass
        else:
            try:
                os.makedirs("/etc/pacman.d", exist_ok=True)
                with open(mirror_arch, "w", encoding="utf-8") as f:
                    f.write("Server = https://fastly.mirror.pkgbuild.com/$repo/os/$arch\n")
                    f.write("Server = https://mirror.rackspace.com/archlinux/$repo/os/$arch\n")
                    f.write("Server = https://geo.mirror.pkgbuild.com/$repo/os/$arch\n")
            except Exception:
                pass

        v3_repos = ""
        if v3_supported:
            v3_repos = """
[cachyos-v3]
Include = /etc/pacman.d/cachyos-v3-mirrorlist
Server = https://mirror.cachyos.org/repo/x86_64_v3/$repo
Server = https://eu.mirror.cachyos.org/repo/x86_64_v3/$repo
Server = https://us.mirror.cachyos.org/repo/x86_64_v3/$repo

[cachyos-core-v3]
Include = /etc/pacman.d/cachyos-v3-mirrorlist
Server = https://mirror.cachyos.org/repo/x86_64_v3/$repo
Server = https://eu.mirror.cachyos.org/repo/x86_64_v3/$repo
Server = https://us.mirror.cachyos.org/repo/x86_64_v3/$repo

[cachyos-extra-v3]
Include = /etc/pacman.d/cachyos-v3-mirrorlist
Server = https://mirror.cachyos.org/repo/x86_64_v3/$repo
Server = https://eu.mirror.cachyos.org/repo/x86_64_v3/$repo
Server = https://us.mirror.cachyos.org/repo/x86_64_v3/$repo
"""
        else:
            self.executor.logger.log("CPU does not support x86-64-v3 instructions. Omitting v3 optimized repositories.")

        content = f"""#
# Horizon OS - Installer Pacman Configuration
# Dynamic CPU architecture level: {'x86_64_v3' if v3_supported else 'x86_64'}
#

[options]
HoldPkg     = pacman glibc
Architecture = auto {'x86_64_v3' if v3_supported else ''}
Color
CheckSpace
VerbosePkgLists
ParallelDownloads = 5
SigLevel    = Optional TrustAll
LocalFileSigLevel = Optional
DisableDownloadTimeout
{v3_repos}
[cachyos]
Include = /etc/pacman.d/cachyos-mirrorlist
Server = https://mirror.cachyos.org/repo/$arch/$repo
Server = https://eu.mirror.cachyos.org/repo/$arch/$repo
Server = https://us.mirror.cachyos.org/repo/$arch/$repo

[core]
Include = /etc/pacman.d/mirrorlist
Server = https://fastly.mirror.pkgbuild.com/$repo/os/$arch
Server = https://mirror.rackspace.com/archlinux/$repo/os/$arch
Server = https://geo.mirror.pkgbuild.com/$repo/os/$arch

[extra]
Include = /etc/pacman.d/mirrorlist
Server = https://fastly.mirror.pkgbuild.com/$repo/os/$arch
Server = https://mirror.rackspace.com/archlinux/$repo/os/$arch
Server = https://geo.mirror.pkgbuild.com/$repo/os/$arch

[multilib]
Include = /etc/pacman.d/mirrorlist
Server = https://fastly.mirror.pkgbuild.com/$repo/os/$arch
Server = https://mirror.rackspace.com/archlinux/$repo/os/$arch
Server = https://geo.mirror.pkgbuild.com/$repo/os/$arch
"""
        with open(conf_path, "w", encoding="utf-8") as f:
            f.write(content)
        return conf_path

    # Execution Steps
    def _step_partition_and_format(self) -> bool:
        self.executor.logger.log(f"Pre-flight partition validation on {self.selected_disk}")
        
        # Rigorous Revalidation immediately before destruction
        valid, reason = revalidate_target_disk(self.selected_disk, self.selected_disk_size_bytes)
        if not valid:
            self.executor.logger.log(f"FATAL: Revalidation failed: {reason}")
            self.executor.last_error = reason
            return False

        # Clean unmount existing partitions and swap
        if not unmount_target_disk(self.selected_disk):
            self.executor.logger.log("WARNING: unmount_target_disk reported incomplete unmount")

        # 1. Wipe and create GPT
        if not self.executor.run_cmd(["parted", "-s", self.selected_disk, "mklabel", "gpt"], description="Wiping disk label"):
            return False
        
        # 2. Partition 1: EFI
        if not self.executor.run_cmd(["parted", "-s", self.selected_disk, "mkpart", "HORIZON_EFI", "fat32", "1MiB", "1025MiB"], description="Creating EFI partition"):
            return False
        if not self.executor.run_cmd(["parted", "-s", self.selected_disk, "set", "1", "esp", "on"], description="Setting ESP flag"):
            return False

        # 3. Partition 2: Swap
        swap_end = 1025 + (self.swap_size_gib * 1024)
        if not self.executor.run_cmd(["parted", "-s", self.selected_disk, "mkpart", "HORIZON_SWAP", "linux-swap", "1025MiB", f"{swap_end}MiB"], description="Creating Swap partition"):
            return False

        # 4. Partition 3: Root
        if not self.executor.run_cmd(["parted", "-s", self.selected_disk, "mkpart", "HORIZON_ROOT", self.filesystem, f"{swap_end}MiB", "100%"], description="Creating Root partition"):
            return False

        # 5. Verify partition device nodes
        if not self.dry_run:
            if not verify_partition_nodes(self.selected_disk, [1, 2, 3]):
                self.executor.logger.log(f"FATAL: Partition nodes for {self.selected_disk} were not created by kernel")
                self.executor.last_error = "Partition nodes not created by kernel"
                return False

        # 6. Formatting
        sep = "p" if self.selected_disk[-1].isdigit() else ""
        efi_dev = f"{self.selected_disk}{sep}1"
        swap_dev = f"{self.selected_disk}{sep}2"
        root_dev = f"{self.selected_disk}{sep}3"

        if not self.executor.run_cmd(["mkfs.fat", "-F32", "-n", "HORIZON_EFI", efi_dev], description="Formatting EFI partition"):
            return False
        if not self.executor.run_cmd(["mkswap", "-L", "HORIZON_SWAP", swap_dev], description="Formatting Swap partition"):
            return False
        
        if self.filesystem == "btrfs":
            if not self.executor.run_cmd(["mkfs.btrfs", "-f", "-L", "HORIZON_ROOT", root_dev], description="Formatting Btrfs root"):
                return False
        else:
            if not self.executor.run_cmd(["mkfs.ext4", "-F", "-L", "HORIZON_ROOT", root_dev], description="Formatting Ext4 root"):
                return False

        # Verify filesystems
        if not self.dry_run:
            if not verify_filesystem(efi_dev, "vfat"):
                self.executor.last_error = f"Filesystem on {efi_dev} is not valid FAT32"
                return False
            if not verify_filesystem(root_dev, self.filesystem):
                self.executor.last_error = f"Filesystem on {root_dev} is not valid {self.filesystem}"
                return False

        return True

    def _step_mount_target(self) -> bool:
        sep = "p" if self.selected_disk[-1].isdigit() else ""
        root_dev = f"{self.selected_disk}{sep}3"
        efi_dev = f"{self.selected_disk}{sep}1"

        if self.filesystem == "btrfs":
            # Mount root temporarily to create subvolumes
            if not self.executor.run_cmd(["mount", root_dev, self.target_root], description="Mounting root for subvolume creation"):
                return False
            for sub in ["@", "@home", "@snapshots", "@cache", "@log"]:
                if not self.executor.run_cmd(["btrfs", "subvolume", "create", f"{self.target_root}/{sub}"], description=f"Creating subvolume {sub}"):
                    return False
            if not self.executor.run_cmd(["umount", self.target_root], description="Unmounting root"):
                return False

            # Mount with subvolumes
            btrfs_opts = "noatime,compress=zstd:1,space_cache=v2"
            if not self.executor.run_cmd(["mount", "-o", f"subvol=@,{btrfs_opts}", root_dev, self.target_root], description="Mounting @ to /mnt"):
                return False
            
            os.makedirs(f"{self.target_root}/home", exist_ok=True)
            os.makedirs(f"{self.target_root}/.snapshots", exist_ok=True)
            os.makedirs(f"{self.target_root}/var/cache", exist_ok=True)
            os.makedirs(f"{self.target_root}/var/log", exist_ok=True)
            os.makedirs(f"{self.target_root}/boot/efi", exist_ok=True)

            if not self.executor.run_cmd(["mount", "-o", f"subvol=@home,{btrfs_opts}", root_dev, f"{self.target_root}/home"], description="Mounting @home"):
                return False
            if not self.executor.run_cmd(["mount", "-o", f"subvol=@snapshots,{btrfs_opts}", root_dev, f"{self.target_root}/.snapshots"], description="Mounting @snapshots"):
                return False
            if not self.executor.run_cmd(["mount", "-o", f"subvol=@cache,{btrfs_opts}", root_dev, f"{self.target_root}/var/cache"], description="Mounting @cache"):
                return False
            if not self.executor.run_cmd(["mount", "-o", f"subvol=@log,{btrfs_opts}", root_dev, f"{self.target_root}/var/log"], description="Mounting @log"):
                return False
        else:
            if not self.executor.run_cmd(["mount", root_dev, self.target_root], description="Mounting ext4 root"):
                return False
            os.makedirs(f"{self.target_root}/boot/efi", exist_ok=True)

        if not self.executor.run_cmd(["mount", efi_dev, f"{self.target_root}/boot/efi"], description="Mounting EFI system partition"):
            return False

        # Verify mounts active
        if not self.dry_run:
            if not self.executor.verify_mount(self.target_root):
                self.executor.last_error = f"Target root {self.target_root} is not an active mountpoint!"
                return False
            if not self.executor.verify_mount(f"{self.target_root}/boot/efi"):
                self.executor.last_error = f"Target EFI {self.target_root}/boot/efi is not an active mountpoint!"
                return False

        return True

    def _step_pacstrap_base(self) -> bool:
        pkg_file = os.path.join(REPO_ROOT, "packages", "arch-base", "packages.list")
        desktop_pkg_file = os.path.join(REPO_ROOT, "packages", "kde-desktop", "packages.list")
        
        packages = []
        for pf in [pkg_file, desktop_pkg_file]:
            if os.path.exists(pf):
                with open(pf, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            packages.append(line)

        packages = list(dict.fromkeys(packages))
        cpu_info = detect_cpu_info()
        pacman_conf = self._generate_installer_pacman_conf(v3_supported=cpu_info.get("v3_supported", False))
        cmd = ["pacstrap", "-C", pacman_conf, "-K", self.target_root] + packages
        if not self.executor.run_cmd(cmd, description=f"Pacstrapping {len(packages)} packages to target"):
            return False

        # Post-pacstrap kernel presence verification
        if not self.dry_run:
            kernels = discover_installed_kernels(self.target_root)
            if not kernels.get("kernel"):
                self.executor.last_error = "Pacstrap finished but no Linux kernel found in target /boot!"
                return False

        return True

    def _step_configure_chroot(self) -> bool:
        # Generate and write fstab
        if not self.dry_run:
            try:
                # Activate swap partition if configured so genfstab discovers it
                sep = "p" if self.selected_disk[-1].isdigit() else ""
                swap_dev = f"{self.selected_disk}{sep}2"
                self.executor.run_cmd(["swapon", swap_dev], description="Activating swap before genfstab")
                
                res = subprocess.run(["genfstab", "-U", self.target_root], capture_output=True, text=True, check=True)
                if res.stdout:
                    self.executor.write_target_file("etc/fstab", res.stdout)
                    self.executor.logger.log(f"fstab generated with {len(res.stdout.splitlines())} entries")
            except Exception as e:
                self.executor.logger.log(f"WARNING: genfstab execution failed: {e}")
        else:
            self.executor.logger.log("Simulating fstab generation")

        # Configure pacman inside target
        cpu_info = detect_cpu_info()
        v3_supported = cpu_info.get("v3_supported", False)
        target_pacman_conf = self._generate_installer_pacman_conf(v3_supported)
        try:
            with open(target_pacman_conf, "r", encoding="utf-8") as f:
                target_conf_content = f.read().replace("SigLevel    = Optional TrustAll", "SigLevel    = Required DatabaseOptional")
                self.executor.write_target_file("etc/pacman.conf", target_conf_content)
        except Exception:
            pass

        # Copy CachyOS mirrorlists into target /etc/pacman.d/
        for m in ["cachyos-mirrorlist", "cachyos-v3-mirrorlist"]:
            src_m = f"/etc/pacman.d/{m}"
            if os.path.exists(src_m):
                try:
                    with open(src_m, "r", encoding="utf-8") as f:
                        self.executor.write_target_file(f"etc/pacman.d/{m}", f.read())
                except Exception:
                    pass

        # Keyring initialization
        self.executor.chroot_exec(["pacman-key", "--init"], description="Initializing pacman keyring")
        self.executor.chroot_exec(["pacman-key", "--populate", "archlinux"], description="Populating Arch Linux keyring")
        
        # Configure hostname & hosts
        self.executor.write_target_file("etc/hostname", f"{self.hostname}\n")
        self.executor.write_target_file("etc/hosts", f"127.0.0.1 localhost\n::1 localhost\n127.0.1.1 {self.hostname}.localdomain {self.hostname}\n")

        # Configure locale
        self.executor.write_target_file("etc/locale.gen", f"{self.locale} UTF-8\n")
        self.executor.write_target_file("etc/locale.conf", f"LANG={self.locale}\n")
        self.executor.write_target_file("etc/vconsole.conf", f"KEYMAP={self.keymap}\n")

        if not self.executor.chroot_exec(["locale-gen"], description="Generating locales"):
            return False

        # Root Account Configuration (Locked by default, or dedicated password set)
        if getattr(self, "lock_root", True):
            if not self.executor.chroot_exec(["passwd", "-l", "root"], description="Locking root account"):
                return False
        else:
            if not self.executor.set_user_password("root", self.root_password, description="Setting dedicated root password"):
                return False

        # Create user
        if not self.executor.chroot_exec(["useradd", "-m", "-G", "wheel,video,audio,input", "-s", "/bin/bash", self.username], description=f"Creating user {self.username}"):
            return False

        # Secure User Password Setting
        if not self.executor.set_user_password(self.username, self.user_password, description=f"Setting password for user {self.username}"):
            return False

        # Sudoers dropin
        sudoers_dropin = "%wheel ALL=(ALL:ALL) ALL\n"
        self.executor.write_target_file("etc/sudoers.d/10-wheel", sudoers_dropin, mode=0o440)

        # Validate sudoers configuration with visudo
        visudo_bin = shutil.which("visudo")
        if visudo_bin and not self.dry_run:
            target_sudoers = os.path.join(self.target_root, "etc", "sudoers.d", "10-wheel")
            res = subprocess.run([visudo_bin, "-c", "-f", target_sudoers], capture_output=True, text=True)
            if res.returncode != 0:
                err_msg = f"visudo check failed on /etc/sudoers.d/10-wheel: {res.stderr.strip()}"
                self.executor.logger.log(f"ERROR: {err_msg}")
                self.executor.last_error = err_msg
                return False
            self.executor.logger.log("Sudoers configuration successfully verified with visudo")

        # Enable core services
        for s in ["NetworkManager", "sddm", "bluetooth", "avahi-daemon", "ananicy-cpp"]:
            success = self.executor.chroot_exec(["systemctl", "enable", f"{s}.service"], description=f"Enabling {s}.service")
            if not success and s in ["NetworkManager", "sddm"]:
                self.executor.last_error = f"Failed to enable critical service: {s}.service"
                return False

        return True

    def _step_install_bootloader(self) -> bool:
        manager = BootloaderManager(
            executor=self.executor,
            target_root=self.target_root,
            selected_disk=self.selected_disk,
            bootloader=self.bootloader,
            filesystem=self.filesystem,
        )
        success, message = manager.install()
        if not success:
            self.executor.last_error = message
            self.executor.logger.log(f"FATAL: Bootloader installation failed: {message}")
            return False
        return True

    def _step_deploy_sddm(self) -> bool:
        return self.deployer.deploy_ryoku_sddm()

    def _step_deploy_splash(self) -> bool:
        return self.deployer.deploy_overload_splash()

    def _step_deploy_icons(self) -> bool:
        return self.deployer.deploy_candy_icons()

    def _step_deploy_shell(self) -> bool:
        return self.deployer.deploy_caelestia_shell(username=self.username)

    def _step_deploy_defaults(self) -> bool:
        return self.deployer.deploy_horizon_kde_defaults()

    def _step_verify_installation(self) -> bool:
        validator = InstallationValidator(target_root=self.target_root)
        results = validator.verify_all()
        passed_count = sum(1 for r in results if r.passed)
        total_count = len(results)
        
        print(f"\n  {BOLD}Validation Audit Results ({passed_count}/{total_count} Passed):{RESET}")
        for r in results:
            mark = f"{BRIGHT_GREEN}✓ PASS{RESET}" if r.passed else f"{BRIGHT_RED}✗ FAIL{RESET}"
            tag = f" {YELLOW}[STUB]{RESET}" if r.is_placeholder else ""
            print(f"    [{mark}] {BOLD}{r.title}{RESET} ({r.category}){tag}")
            if r.details:
                print(f"           {DIM}{r.details}{RESET}")

        return passed_count == total_count

    def run(self) -> int:
        try:
            self.stage_welcome_and_hardware()
            self.stage_storage_selection()
            self.stage_system_configuration()
            confirmed = self.stage_confirmation_summary()
            if not confirmed:
                print(f"\n  {YELLOW}Installation cancelled by operator. No changes were made.{RESET}\n")
                return 0
            success = self.stage_execute_installation()
            return 0 if success else 1
        finally:
            self.logger.close()

def main():
    parser = argparse.ArgumentParser(description="Horizon OS Terminal User Interface (TUI) Installer")
    parser.add_argument("--dry-run", action="store_true", help="Simulate installation without touching disks")
    parser.add_argument("--target", default="/mnt", help="Installation mountpoint (default: /mnt)")
    parser.add_argument("--verify-only", action="store_true", help="Run validation checks on existing target")
    args = parser.parse_args()

    if args.verify_only:
        print(f"{BOLD}{CYAN}==> Running Horizon OS Verification Suite on {args.target}...{RESET}")
        validator = InstallationValidator(target_root=args.target)
        results = validator.verify_all()
        passed = sum(1 for r in results if r.passed)
        for r in results:
            mark = f"{BRIGHT_GREEN}✓ PASS{RESET}" if r.passed else f"{BRIGHT_RED}✗ FAIL{RESET}"
            tag = f" [STUB]" if r.is_placeholder else ""
            print(f"  [{mark}] [{r.category}] {r.title}{tag}: {r.details}")
        print(f"\nScore: {passed}/{len(results)} checks passed.")
        sys.exit(0 if passed == len(results) else 1)

    app = HorizonInstallerApp(dry_run=args.dry_run, target_root=args.target)
    sys.exit(app.run())

if __name__ == "__main__":
    main()
