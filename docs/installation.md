# Horizon OS — Installation Manual

This guide covers installing Horizon OS using the official Arch Linux live ISO or within a virtual machine.

## 1. Quick Start from Arch Linux Live ISO

1. Download the official Arch Linux ISO from [https://archlinux.org/download/](https://archlinux.org/download/) and boot your machine in UEFI mode.
2. Establish network connectivity (Ethernet or `iwctl`).
3. Clone the Horizon OS repository:
   ```bash
   git clone https://github.com/Beastknight933/customOS.git /root/horizon-os
   cd /root/horizon-os
   ```
4. Launch the Horizon Terminal User Interface (TUI) installer:
   ```bash
   ./install.sh
   ```
   *(Or run the static binary directly: `./installer/horizon-installer`)*

## 2. Interactive Installation Stages

The installer guides you through 5 stages:

1. **Hardware Probing**: Automatically detects UEFI firmware, CPU microarchitecture (x86_64-v3/v4), system RAM, and GPU devices.
2. **Storage Selection**: Choose target disk, filesystem scheme (Btrfs with optimized subvolumes `@`, `@home`, `@snapshots`, `@cache`, `@log` or Ext4), and swap size.
3. **System Identity**: Set hostname, root password, primary user credentials, timezone, and preferred bootloader (Limine, systemd-boot, or GRUB).
4. **Safety Confirmation**: Detailed review of target disk and partition layout. Requires typing `YES` before any disk operations proceed.
5. **Execution Pipeline**:
   - Disk partitioning and filesystem formatting
   - Pacstrapping base packages and CachyOS kernel
   - Chroot user and network configuration
   - Bootloader installation
   - Ryoku SDDM theme deployment
   - Overload splash screen deployment
   - Candy Bar icon suite deployment
   - Caelestia KDE shell & workspace-tracker deployment
   - Post-install verification audit

## 3. Testing in a Virtual Machine (Safe Sandbox)

To safely test the installer without modifying host disks:

```bash
# On an Arch or Linux host with QEMU:
./scripts/run-vm-test.sh path/to/archlinux-latest-x86_64.iso
```

The script provisions a disposable 32 GiB qcow2 virtual disk and boots the ISO with UEFI OVMF firmware.

## 4. Verification

After installation, run the verification audit:

```bash
./scripts/verify-installation.sh /mnt
```
