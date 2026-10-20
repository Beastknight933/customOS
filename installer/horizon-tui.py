#!/usr/bin/env python3
"""
Horizon OS — Full-Screen Terminal User Interface (TUI) Installer
Operates cleanly on Arch Linux live ISOs, virtual machines, and installation environments.
"""

import os
import sys
import time
import json
import argparse
from typing import Dict, Any, List, Optional

# Ensure installer backend is importable
INSTALLER_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(INSTALLER_DIR)
sys.path.insert(0, INSTALLER_DIR)

from backend.hardware import probe_all_hardware, detect_cpu_info
from backend.storage import list_disks, plan_partition_table, is_device_live_media, unmount_target_disk
from backend.executor import InstallExecutor, InstallLogger
from backend.deployer import ComponentDeployer
from backend.validator import InstallationValidator

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
BG_DARK = f"{ESC}48;5;234m"

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
        self.target_root = target_root
        self.logger = InstallLogger()
        self.executor = InstallExecutor(dry_run=dry_run, target_root=target_root, logger=self.logger)
        self.deployer = ComponentDeployer(executor=self.executor, repo_root=REPO_ROOT)
        
        # State
        self.hardware: Dict[str, Any] = {}
        self.available_disks: List[Any] = []
        self.selected_disk: Optional[str] = None
        self.filesystem: str = "btrfs"
        self.swap_size_gib: int = 4
        self.bootloader: str = "limine"
        
        # User Configuration
        self.hostname: str = "horizon-pc"
        self.root_password: str = "horizon"
        self.username: str = "horizon"
        self.user_fullname: str = "Horizon Operator"
        self.user_password: str = "horizon"
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
            status_tag = f" {RED}[LIVE MEDIA - CANNOT INSTALL]{RESET}" if disk_info.get("is_live_media") else ""
            print(f"    [{BOLD}{i}{RESET}] {BRIGHT_CYAN}{disk_info['path']}{RESET} — {disk_info['size']} ({rot}, {disk_info['model']}){status_tag}")

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
                print(f"  {RED}ERROR: {chosen['path']} is the active boot media and cannot be partitioned! Choose another device.{RESET}")
                continue
            break

        self.selected_disk = chosen["path"]
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

        # Hostname
        print(f"  Enter Hostname [default '{self.hostname}']: ", end="")
        try:
            h = input().strip()
            if h:
                self.hostname = h
        except EOFError:
            pass

        # Username
        print(f"  Enter Primary User Login [default '{self.username}']: ", end="")
        try:
            u = input().strip()
            if u:
                self.username = u
        except EOFError:
            pass

        # User Password
        print(f"  Enter User Password [default '{self.user_password}']: ", end="")
        try:
            pw = input().strip()
            if pw:
                self.user_password = pw
                self.root_password = pw
        except EOFError:
            pass

        # Bootloader
        print(f"\n  {BOLD}Select Bootloader:{RESET}")
        print(f"    [1] Limine (Recommended: Modern, fast, full CachyOS & Snapper snapshot integration)")
        print(f"    [2] systemd-boot (Simple UEFI native loader)")
        print(f"    [3] GRUB (Classic multi-boot)")
        print(f"  Choice [1-3, default 1]: ", end="")
        try:
            b_choice = input().strip()
            if b_choice == "2":
                self.bootloader = "systemd-boot"
            elif b_choice == "3":
                self.bootloader = "grub"
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

    def stage_execute_installation(self):
        self.print_header("Stage 5 of 5: Installation Execution & Component Deployment")
        print(f"  {CYAN}Executing installation pipeline...{RESET}\n")

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
            print(f"  [{i}/{total_steps}] {BOLD}{WHITE}{title}...{RESET}")
            success = func()
            if not success:
                print(f"  {BRIGHT_RED}❌ FAILED at step {i}: {title}{RESET}")
                print(f"  Inspect /var/log/horizon-install.log for error details.")
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
        
        # Ensure mirrorlists exist or provide inline fallback
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
            if not os.path.exists(mirror_arch):
                with open(mirror_arch, "w", encoding="utf-8") as f:
                    f.write("Server = https://geo.mirror.pkgbuild.com/$repo/os/$arch\n")
                    f.write("Server = https://mirror.rackspace.com/archlinux/$repo/os/$arch\n")

        v3_repos = ""
        if v3_supported:
            v3_repos = """
[cachyos-v3]
Include = /etc/pacman.d/cachyos-v3-mirrorlist
Server = https://mirror.cachyos.org/repo/x86_64_v3/$repo

[cachyos-core-v3]
Include = /etc/pacman.d/cachyos-v3-mirrorlist
Server = https://mirror.cachyos.org/repo/x86_64_v3/$repo

[cachyos-extra-v3]
Include = /etc/pacman.d/cachyos-v3-mirrorlist
Server = https://mirror.cachyos.org/repo/x86_64_v3/$repo
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
SigLevel    = TrustAll DatabaseOptional
LocalFileSigLevel = Optional
{v3_repos}
[cachyos]
Include = /etc/pacman.d/cachyos-mirrorlist
Server = https://mirror.cachyos.org/repo/$arch/$repo

[core]
Include = /etc/pacman.d/mirrorlist
Server = https://geo.mirror.pkgbuild.com/$repo/os/$arch

[extra]
Include = /etc/pacman.d/mirrorlist
Server = https://geo.mirror.pkgbuild.com/$repo/os/$arch

[multilib]
Include = /etc/pacman.d/mirrorlist
Server = https://geo.mirror.pkgbuild.com/$repo/os/$arch
"""
        with open(conf_path, "w", encoding="utf-8") as f:
            f.write(content)
        return conf_path

    # Execution Steps
    def _step_partition_and_format(self) -> bool:
        self.executor.logger.log(f"Pre-flight partition validation on {self.selected_disk}")
        if is_device_live_media(self.selected_disk):
            self.executor.logger.log(f"FATAL: Target disk {self.selected_disk} is detected as live media!")
            return False
            
        unmount_target_disk(self.selected_disk)
        cmd_wipe = ["parted", "-s", self.selected_disk, "mklabel", "gpt"]
        self.executor.run_cmd(cmd_wipe, description="Wiping disk label")
        
        # Partition 1: EFI
        cmd_p1 = ["parted", "-s", self.selected_disk, "mkpart", "HORIZON_EFI", "fat32", "1MiB", "1025MiB"]
        self.executor.run_cmd(cmd_p1, description="Creating EFI partition")
        self.executor.run_cmd(["parted", "-s", self.selected_disk, "set", "1", "esp", "on"], description="Setting ESP flag")

        # Partition 2: Swap
        swap_end = 1025 + (self.swap_size_gib * 1024)
        cmd_p2 = ["parted", "-s", self.selected_disk, "mkpart", "HORIZON_SWAP", "linux-swap", "1025MiB", f"{swap_end}MiB"]
        self.executor.run_cmd(cmd_p2, description="Creating Swap partition")

        # Partition 3: Root
        cmd_p3 = ["parted", "-s", self.selected_disk, "mkpart", "HORIZON_ROOT", self.filesystem, f"{swap_end}MiB", "100%"]
        self.executor.run_cmd(cmd_p3, description="Creating Root partition")

        # Formatting
        sep = "p" if self.selected_disk[-1].isdigit() else ""
        efi_dev = f"{self.selected_disk}{sep}1"
        swap_dev = f"{self.selected_disk}{sep}2"
        root_dev = f"{self.selected_disk}{sep}3"

        self.executor.run_cmd(["mkfs.fat", "-F32", "-n", "HORIZON_EFI", efi_dev], description="Formatting EFI partition")
        self.executor.run_cmd(["mkswap", "-L", "HORIZON_SWAP", swap_dev], description="Formatting Swap partition")
        
        if self.filesystem == "btrfs":
            self.executor.run_cmd(["mkfs.btrfs", "-f", "-L", "HORIZON_ROOT", root_dev], description="Formatting Btrfs root")
        else:
            self.executor.run_cmd(["mkfs.ext4", "-F", "-L", "HORIZON_ROOT", root_dev], description="Formatting Ext4 root")
        return True

    def _step_mount_target(self) -> bool:
        sep = "p" if self.selected_disk[-1].isdigit() else ""
        root_dev = f"{self.selected_disk}{sep}3"
        efi_dev = f"{self.selected_disk}{sep}1"

        if self.filesystem == "btrfs":
            # Mount root temporarily to create subvolumes
            self.executor.run_cmd(["mount", root_dev, self.target_root], description="Mounting root for subvolume creation")
            for sub in ["@", "@home", "@snapshots", "@cache", "@log"]:
                self.executor.run_cmd(["btrfs", "subvolume", "create", f"{self.target_root}/{sub}"], description=f"Creating subvolume {sub}")
            self.executor.run_cmd(["umount", self.target_root], description="Unmounting root")

            # Mount with subvolumes
            btrfs_opts = "noatime,compress=zstd:1,space_cache=v2"
            self.executor.run_cmd(["mount", "-o", f"subvol=@,{btrfs_opts}", root_dev, self.target_root], description="Mounting @ to /mnt")
            
            os.makedirs(f"{self.target_root}/home", exist_ok=True)
            os.makedirs(f"{self.target_root}/.snapshots", exist_ok=True)
            os.makedirs(f"{self.target_root}/var/cache", exist_ok=True)
            os.makedirs(f"{self.target_root}/var/log", exist_ok=True)
            os.makedirs(f"{self.target_root}/boot/efi", exist_ok=True)

            self.executor.run_cmd(["mount", "-o", f"subvol=@home,{btrfs_opts}", root_dev, f"{self.target_root}/home"])
            self.executor.run_cmd(["mount", "-o", f"subvol=@snapshots,{btrfs_opts}", root_dev, f"{self.target_root}/.snapshots"])
            self.executor.run_cmd(["mount", "-o", f"subvol=@cache,{btrfs_opts}", root_dev, f"{self.target_root}/var/cache"])
            self.executor.run_cmd(["mount", "-o", f"subvol=@log,{btrfs_opts}", root_dev, f"{self.target_root}/var/log"])
        else:
            self.executor.run_cmd(["mount", root_dev, self.target_root], description="Mounting ext4 root")
            os.makedirs(f"{self.target_root}/boot/efi", exist_ok=True)

        self.executor.run_cmd(["mount", efi_dev, f"{self.target_root}/boot/efi"], description="Mounting EFI system partition")
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

        # Remove duplicates
        packages = list(dict.fromkeys(packages))
        cpu_info = detect_cpu_info()
        pacman_conf = self._generate_installer_pacman_conf(v3_supported=cpu_info.get("v3_supported", False))
        cmd = ["pacstrap", "-C", pacman_conf, "-K", self.target_root] + packages
        return self.executor.run_cmd(cmd, description=f"Pacstrapping {len(packages)} packages to target")

    def _step_configure_chroot(self) -> bool:
        # Write fstab
        self.executor.run_cmd(["genfstab", "-U", self.target_root], description="Generating fstab")
        
        # Configure pacman inside target
        cpu_info = detect_cpu_info()
        v3_supported = cpu_info.get("v3_supported", False)
        target_pacman_conf = self._generate_installer_pacman_conf(v3_supported)
        try:
            with open(target_pacman_conf, "r", encoding="utf-8") as f:
                target_conf_content = f.read().replace("SigLevel    = TrustAll DatabaseOptional", "SigLevel    = Required DatabaseOptional")
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

        # Initialize pacman keys inside chroot
        self.executor.chroot_exec(["pacman-key", "--init"], description="Initializing pacman keyring")
        self.executor.chroot_exec(["pacman-key", "--populate", "archlinux"], description="Populating Arch Linux keyring")
        
        # Configure hostname
        self.executor.write_target_file("etc/hostname", f"{self.hostname}\n")
        self.executor.write_target_file("etc/hosts", f"127.0.0.1 localhost\n::1 localhost\n127.0.1.1 {self.hostname}.localdomain {self.hostname}\n")

        # Configure locale
        self.executor.write_target_file("etc/locale.gen", f"{self.locale} UTF-8\n")
        self.executor.write_target_file("etc/locale.conf", f"LANG={self.locale}\n")
        self.executor.write_target_file("etc/vconsole.conf", f"KEYMAP={self.keymap}\n")

        # Run locale-gen in chroot
        self.executor.chroot_exec(["locale-gen"], description="Generating locales")

        # Set root password
        self.executor.chroot_exec(["sh", "-c", f"echo 'root:{self.root_password}' | chpasswd"], description="Setting root password")

        # Create user
        self.executor.chroot_exec(["useradd", "-m", "-G", "wheel,video,audio,input", "-s", "/bin/bash", self.username], description="Creating user")
        self.executor.chroot_exec(["sh", "-c", f"echo '{self.username}:{self.user_password}' | chpasswd"], description="Setting user password")

        # Sudoers
        sudoers_dropin = "%wheel ALL=(ALL:ALL) ALL\n"
        self.executor.write_target_file("etc/sudoers.d/10-wheel", sudoers_dropin, mode=0o440)

        # Enable core services
        for s in ["NetworkManager", "sddm", "bluetooth", "avahi-daemon", "ananicy-cpp"]:
            self.executor.chroot_exec(["systemctl", "enable", f"{s}.service"], description=f"Enabling {s}.service")

        return True

    def _step_install_bootloader(self) -> bool:
        if self.bootloader == "limine":
            # Limine UEFI installation
            self.executor.chroot_exec(["limine", "bios-install", self.selected_disk], description="Installing Limine bootloader")
        elif self.bootloader == "systemd-boot":
            self.executor.chroot_exec(["bootctl", "install"], description="Installing systemd-boot")
        else:
            self.executor.chroot_exec(["grub-install", "--target=x86_64-efi", "--efi-directory=/boot/efi", "--bootloader-id=HORIZON"], description="Installing GRUB")
            self.executor.chroot_exec(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"], description="Generating grub.cfg")
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
            print(f"    [{mark}] {BOLD}{r.title}{RESET}")
            if r.details:
                print(f"           {DIM}{r.details}{RESET}")

        return passed_count == total_count

    def run(self):
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
            print(f"  [{mark}] {r.title}: {r.details}")
        print(f"\nScore: {passed}/{len(results)} checks passed.")
        sys.exit(0 if passed == len(results) else 1)

    app = HorizonInstallerApp(dry_run=args.dry_run, target_root=args.target)
    sys.exit(app.run())

if __name__ == "__main__":
    main()
