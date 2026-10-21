# Horizon OS 2026.10.21 (Singularity Edition) — Release Notes

**Release Date:** October 21, 2026  
**Target Architecture:** `x86_64` (optimized for `x86_64_v3` with generic fallback)  
**Distribution Base:** Arch Linux + CachyOS Performance Core  
**Desktop Environment:** KDE Plasma 6.8.0 (Wayland) + Caelestia Desktop Shell 2.6.3  

---

## 1. Release Files & Checksums

| File | Size (Bytes) | SHA-256 Checksum |
| :--- | :--- | :--- |
| `horizon-os-2026.10.21-x86_64.iso` | `1,768,718,336` | `fcf39c344e0303fa8f4081132cc8fc1855eaf6dec48d32a5aa686c5cbdc8d0a7` |
| `SHA256SUMS` | `98` | Verification text file |
| `packages/release-manifest.json` | `37,605` | Complete 740-package machine-readable inventory |

Verification command:
```bash
sha256sum -c SHA256SUMS
```

---

## 2. Core Stack Versions

- **Live ISO Kernel:** `7.2.11-arch1-1`
- **Installed Kernel:** `7.2.11-1-cachyos` (BORE scheduler, CPU-optimized v3 repos)
- **KDE Plasma:** `6.8.0-1.1`
- **KWin Wayland:** `6.8.0-1.1`
- **Qt Framework:** `6.12.0-3.1`
- **Quickshell Engine:** `0.3.2-1.1`
- **Caelestia Shell Port:** `2.6.3-1`
- **SDDM Greeter:** `0.21.0-8` (with Horizon Ryoku Orbital theme)
- **Bootloader (Default):** `limine-12.9.3-2`
- **Audio Stack:** PipeWire `1.6.9-1` + WirePlumber `0.5.18-1`
- **Mesa Drivers:** `26.2.4-1`

---

## 3. Security & Safety Hardening

- **Zero Insecure Defaults:** No hardcoded passwords in scripts, configs, or installer source code.
- **Masked Password Prompts:** All password inputs in the installer use non-echoing prompts with mandatory verification.
- **Root Policy:** Default configuration locks the root account (`passwd -l root`) and provides administrative access via `sudo` for `%wheel`.
- **Subprocess Safety:** All system commands are executed with argument arrays to prevent shell injection. Passwords are piped strictly via stdin to `chpasswd` and are sanitized from logs.
- **Storage Safety:** Active host disks and installer live media are filtered and protected against accidental overwrites. All partition operations require explicit confirmation.

---

## 4. QEMU Verification

To boot the live ISO in an isolated environment:
```bash
qemu-system-x86_64 \
  -enable-kvm \
  -cpu host \
  -m 4G \
  -smp 4 \
  -bios /usr/share/ovmf/OVMF.fd \
  -cdrom horizon-os-2026.10.21-x86_64.iso \
  -drive file=test-vm.qcow2,format=qcow2,if=virtio \
  -boot d \
  -vga virtio \
  -display gtk
```

---

## 5. Known Limitations

1. **Network Requirement during Installation:** While custom components (Caelestia, Ryoku theme, Candy Bar icons) are bundled offline in the ISO, `pacstrap` requires an active Internet connection to download base Arch/CachyOS packages and KDE Plasma.
2. **UEFI Only:** Horizon OS requires UEFI firmware (OVMF in virtual machines). Legacy BIOS (MBR) boot is not supported.
