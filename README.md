# Horizon OS — Singularity Edition
### Custom Arch Linux-Based Operating System, Terminal Installer, Caelestia KDE Port, Ryoku SDDM & Unified Desktop Integration

```text
  ██╗  ██╗ ██████╗ ██████╗ ██╗███████╗ ██████╗ ███╗   ██╗     ██████╗ ███████╗
  ██║  ██║██╔═══██╗██╔══██╗██║╚══███╔╝██╔═══██╗████╗  ██║    ██╔═══██╗██╔════╝
  ███████║██║   ██║██████╔╝██║  ███╔╝ ██║   ██║██╔██╗ ██║    ██║   ██║███████╗
  ██╔══██║██║   ██║██╔══██╗██║ ███╔╝  ██║   ██║██║╚██╗██║    ██║   ██║╚════██║
  ██║  ██║╚██████╔╝██║  ██║██║███████╗╚██████╔╝██║ ╚████║    ╚██████╔╝███████║
  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝     ╚═════╝ ╚══════╝
```

---

## 1. Product Overview

**Horizon OS** is an Arch Linux and CachyOS-based operating system providing a cohesive desktop experience centered around **KDE Plasma 6** and **KWin Wayland**.

It combines an automated full-screen Terminal User Interface (TUI) installer with a customized integration of the **Caelestia KDE desktop shell**, the **Ryoku Orbital Clockwork SDDM theme**, the **Overload splash screen**, and the **Candy Bar (`candy-icons`)** icon suite.

### Key Highlights
- **KDE Plasma 6 & KWin Foundation**: KWin runs as the native Wayland compositor. Plasma desktop widgets and services are fully preserved.
- **Caelestia Shell Integration**: Built from the `caelestia-kde` port (`v2.6.3`) powered by Quickshell, C++ plugins, and a native KWin workspace-tracker effect.
- **Atmospheric Visual Identity**: Deep dark aesthetic fusing Celestia geometric indicators, Lord of the Mysteries (LOTM) Victorian occult tones, and Dishonored / Steampunk clockwork mechanisms.
- **Pure Black Ryoku SDDM Greeter**: Custom Qylock/Clockwork Orbital login theme patched to enforce a pitch-black background.
- **CachyOS Performance Core**: CPU-optimized `linux-cachyos` (`7.2.11-1-cachyos`) kernel with BORE scheduler, auto-nice daemon (`ananicy-cpp`), and `x86_64_v3` AVX2/BMI2 binary repositories.
- **Terminal User Interface Installer**: Full-screen interactive installer with disk safety guards, partition planning (Btrfs with optimized subvolumes or Ext4), unprivileged account setup, and post-installation validation.

---

## 2. Desktop Architecture

```text
┌────────────────────────────────────────────────────────┐
│                   SDDM Login Greeter                   │
│        (Horizon Ryoku Orbital SDDM Theme - Pure Black) │
└──────────────────────────┬─────────────────────────────┘
                           │ Authenticates User Session
                           ▼
┌────────────────────────────────────────────────────────┐
│                   KDE Plasma 6 / KWin                  │
│       • Wayland Compositor (KWin 6.8.0)                │
│       • KScreenLocker (Atmospheric Lockscreen)         │
│       • KDE Services & Audio (PipeWire / WirePlumber)  │
│       • Candy Bar Icon Theme (candy-icons)             │
│       • Overload Splash Screen                         │
└──────────────────────────┬─────────────────────────────┘
                           │ Manages Desktop Windows & Bridge
                           ▼
┌────────────────────────────────────────────────────────┐
│                 Caelestia Desktop Shell                │
│       • Quickshell Engine & Native C++ Plugins         │
│       • KWin Workspace-Tracker Effect Plugin           │
│       • Top Bar with Auto-Hide / Hover Activation      │
│       • Uncluttered Center Dock (No Default Pinned)    │
│       • Restrained Transparency & Pitch-Black Theme    │
│       • KDE Plasma Desktop Widgets Preserved           │
└────────────────────────────────────────────────────────┘
```

### Critical Architectural Invariants
1. **No Caelestia SDDM Theme**: Upstream Caelestia attempts to install `Current=caelestia` in `/etc/sddm.conf.d/zz-caelestia.conf`. Horizon OS strictly strips this override; the Ryoku Orbital SDDM theme remains active.
2. **Preserved KScreenLocker**: Upstream Caelestia scripts attempt to dynamically rewrite `plasmashellrc` and `kscreenlockerrc`. Horizon OS disables this hijack via patches to protect the intended lockscreen.
3. **Plasma Widgets Functional**: Caelestia's background canvas and wallpaper drawing are disabled (`background.enabled: false`) so KDE Plasma desktop widgets, folders, and icons function without collision.

---

## 3. Hardware Requirements & Network Connectivity

### Hardware Requirements
- **Architecture**: `x86_64` (Intel/AMD 64-bit). Processors supporting `x86-64-v3` (AVX2, BMI1/2) automatically utilize performance-optimized CachyOS repositories.
- **Firmware**: UEFI firmware required (OVMF supported in virtual machines).
- **RAM**: Minimum 4 GiB (8 GiB or more recommended for development and multitasking).
- **Storage**: Minimum 30 GiB available storage on SSD, NVMe, or virtual disk.
- **Graphics**: Vulkan / OpenGL accelerated graphics (Intel Iris/Xe, AMD Radeon, NVIDIA with proprietary or open-source driver, or `virtio-gpu` in QEMU).

### Network Connectivity
- **Bundled Custom Components**: Caelestia KDE package (`caelestia-kde-2.6.3-1`), Ryoku SDDM theme, Overload splash, and Candy Bar icons are bundled offline in the ISO.
- **Live Base Packages**: Base system packages, kernel, and KDE Plasma are fetched live from Arch Linux and CachyOS mirrors during `pacstrap`. **An active network connection (Ethernet or Wi-Fi via `nmtui` / `nmcli`) is required during installation.**

---

## 4. Building the ISO

To build the bootable Horizon OS ISO on an Arch Linux or Arch-based build host:

```bash
# 1. Install archiso
sudo pacman -S --needed archiso git

# 2. Clone the repository
git clone https://github.com/Beastknight933/customOS.git ~/horizon-os
cd ~/horizon-os

# 3. Build the ISO using archiso profile
sudo mkarchiso -v -w /tmp/horizon-work -o dist/ iso/archiso-profile/
```

The resulting ISO will be placed in `dist/horizon-os-<version>-x86_64.iso`.

---

## 5. Verifying the ISO Checksum

Verify the cryptographic SHA-256 checksum of the release image before writing to installation media:

```bash
# Verify using sha256sum
sha256sum -c dist/SHA256SUMS

# Or calculate checksum directly:
sha256sum dist/horizon-os-2026.10.21-x86_64.iso
# Expected SHA-256: fcf39c344e0303fa8f4081132cc8fc1855eaf6dec48d32a5aa686c5cbdc8d0a7
```

---

## 6. Testing the ISO Safely in QEMU

Test the live environment and installer inside an isolated QEMU virtual machine without risking host disks:

```bash
# Create a 32GB disposable virtual test disk
qemu-img create -f qcow2 /var/tmp/horizon-test-vm.qcow2 32G

# Boot the ISO in UEFI mode
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

### Cold-Booting the Installed System
After running the installer, exit QEMU and boot directly from the virtual disk:
```bash
qemu-system-x86_64 \
  -enable-kvm \
  -cpu host \
  -m 4G \
  -smp 4 \
  -bios /usr/share/ovmf/OVMF.fd \
  -drive file=/var/tmp/horizon-test-vm.qcow2,format=qcow2,if=virtio \
  -boot c \
  -vga virtio \
  -display gtk
```

---

## 7. Installing onto a Target Disk

1. Boot the Horizon OS Live ISO on the target machine.
2. Ensure network connectivity:
   ```bash
   # Test connectivity
   ping -c 3 archlinux.org
   # If Wi-Fi is needed:
   nmtui
   ```
3. Launch the full-screen terminal installer:
   ```bash
   horizon-installer
   # Or run via Python:
   sudo python3 /opt/horizon-os/installer/horizon-tui.py
   ```
4. Follow the interactive prompts:
   - Select the target storage device.
   - Choose filesystem (Btrfs with `@`, `@home`, `@snapshots`, `@cache`, `@log` subvolumes or Ext4).
   - Configure hostname, user account, and account password.
   - Select root policy: **Locked root account (Recommended)** or dedicated administrator password.
   - Select bootloader (Limine, GRUB, or systemd-boot).
   - Type `YES` to confirm and begin installation.

---

## 8. Failure Recovery & Emergency Operations

If an installation step fails:
1. The installer automatically initiates safe cleanup, unmounting all target mountpoints (`@`, `@home`, ESP) and disabling any target swap.
2. Inspect the detailed installation log:
   ```bash
   less /var/log/horizon-install.log
   ```
3. To manually chroot into an installed system for repair:
   ```bash
   mount -o subvol=@ /dev/sdX3 /mnt
   mount -o subvol=@home /dev/sdX3 /mnt/home
   mount /dev/sdX1 /mnt/boot/efi
   arch-chroot /mnt
   ```
4. For comprehensive recovery procedures, see [`docs/recovery.md`](./docs/recovery.md).

---

## 9. Verified Features & Known Limitations

| Feature / Subsystem | Status | Verification Evidence |
| :--- | :--- | :--- |
| **UEFI Cold Boot** | **Verified** | OVMF UEFI cold-boot into Limine bootloader |
| **Btrfs Subvolumes** | **Verified** | Subvolumes `@`, `@home`, `@snapshots`, `@cache`, `@log` mounted by UUID |
| **SDDM Greeter** | **Verified** | Ryoku Orbital theme rendered; PAM graphical login succeeded |
| **KDE Plasma Wayland** | **Verified** | KWin 6.8.0 compositor and plasmashell running |
| **Caelestia Shell** | **Verified** | Quickshell service running; top panel and clock rendered |
| **KWin Workspace Tracker** | **Verified** | D-Bus query returns `true` (`isEffectLoaded kwin_workspace_tracker`) |
| **Shell Resilience** | **Verified** | Intentional SIGKILL auto-restarts Quickshell without crashing KWin |
| **Offline Custom Assets** | **Verified** | Prebuilt Caelestia package, Ryoku, and Candy Bar installed locally |
| **Offline Pacstrap** | *Limitation* | Base packages require active Internet connection during installation |
| **Legacy BIOS / MBR** | *Limitation* | Live ISO and installer require modern UEFI firmware |

---

## 10. Automated Test Suite

Horizon OS maintains a unit test suite covering account security, disk guards, failure recovery, manifest validity, and configuration schemas:

```bash
python3 -m unittest discover -s tests/unit
```

Output:
```text
Ran 41 tests in 0.332s
OK
```

---

## 11. Security & Vulnerability Reporting

Please review [`SECURITY.md`](./SECURITY.md) for details on security policies, account models, and vulnerability reporting protocols.
