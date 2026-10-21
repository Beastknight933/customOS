# Horizon OS — Installation Manual

This guide covers installing Horizon OS using the official Horizon OS Live ISO or an Arch Linux live image, on bare metal or within a virtual machine.

---

## 1. Quick Start from Horizon OS Live ISO (Recommended)

1. Boot your machine from the Horizon OS Live ISO in UEFI mode.
2. Establish network connectivity (Ethernet or `nmtui` / `nmcli` for Wi-Fi):
   ```bash
   ping -c 3 archlinux.org
   ```
3. Launch the installer:
   ```bash
   horizon-installer
   # Or run python directly:
   sudo python3 /opt/horizon-os/installer/horizon-tui.py
   ```

---

## 2. Alternative Installation from Arch Linux Live ISO

1. Boot the standard Arch Linux ISO in UEFI mode.
2. Connect to the network:
   ```bash
   iwctl  # for Wi-Fi
   ```
3. Clone the Horizon OS repository:
   ```bash
   git clone https://github.com/Beastknight933/customOS.git /root/horizon-os
   cd /root/horizon-os
   ```
4. Run the installer:
   ```bash
   ./install.sh
   ```

---

## 3. Interactive Installation Stages

The installer guides you through 5 stages:

1. **Hardware Probing**: Automatically detects UEFI firmware, CPU microarchitecture (`x86-64-v3`/`v4`), system RAM, and GPU devices.
2. **Storage Selection**: Choose target disk, filesystem scheme (Btrfs with optimized subvolumes `@`, `@home`, `@snapshots`, `@cache`, `@log` or Ext4), and swap size.
3. **System Identity & Account Security**:
   - Validate RFC 1123 hostname and POSIX username.
   - Set primary user password via non-echoing prompt with confirmation.
   - Choose root account policy: **Locked root account (Recommended)** or dedicated administrator password.
   - Select bootloader: **Limine (Recommended)**, GRUB, or systemd-boot.
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

---

## 4. Testing in a Virtual Machine (Safe Sandbox)

To safely test the installer without modifying host disks:

```bash
# Provision a disposable 32 GiB qcow2 virtual disk and boot the Horizon ISO:
qemu-system-x86_64 \
  -enable-kvm \
  -cpu host \
  -m 4G \
  -smp 4 \
  -bios /usr/share/ovmf/OVMF.fd \
  -cdrom dist/horizon-os-2026.10.21-x86_64.iso \
  -drive file=/var/tmp/horizon-test-vm.qcow2,format=qcow2,if=virtio \
  -boot d \
  -vga virtio \
  -display gtk
```

---

## 5. Post-Installation Verification

After installation, the verification audit can be rerun at any time:

```bash
./scripts/verify-installation.sh /mnt
```
