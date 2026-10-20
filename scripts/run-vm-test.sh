#!/usr/bin/env bash
# Horizon OS - Virtual Machine Test Harness
# Spawns a disposable QEMU virtual machine to safely test the installer without risking host disks.
set -euo pipefail

DISK_IMG="horizon-test-vm.qcow2"
DISK_SIZE="32G"
RAM="4096"
CPUS="4"
ARCH_ISO="${1:-archlinux-latest-x86_64.iso}"

echo "=========================================================="
echo "  Horizon OS — Disposable Virtual Machine Test"
echo "=========================================================="

if ! command -v qemu-system-x86_64 >/dev/null 2>&1; then
    echo "ERROR: qemu-system-x86_64 is not installed."
    echo "To test on Arch Linux host: pacman -S qemu-desktop edk2-ovmf"
    exit 1
fi

if [[ ! -f "$DISK_IMG" ]]; then
    echo "==> Creating disposable $DISK_SIZE virtual disk ($DISK_IMG)..."
    qemu-img create -f qcow2 "$DISK_IMG" "$DISK_SIZE"
fi

OVMF_CODE="/usr/share/edk2-ovmf/x64/OVMF_CODE.fd"
OVMF_VARS="/usr/share/edk2-ovmf/x64/OVMF_VARS.fd"

if [[ ! -f "$OVMF_CODE" ]]; then
    # Fallback paths for Ubuntu / Debian / Fedora
    for path in "/usr/share/OVMF/OVMF_CODE.fd" "/usr/share/edk2/ovmf/OVMF_CODE.fd"; do
        if [[ -f "$path" ]]; then
            OVMF_CODE="$path"
            break
        fi
    done
fi

echo "==> Booting VM with QEMU (UEFI enabled)..."
qemu-system-x86_64 \
    -enable-kvm \
    -m "$RAM" \
    -smp "$CPUS" \
    -cpu host \
    -drive if=pflash,format=raw,readonly=on,file="$OVMF_CODE" \
    -drive file="$DISK_IMG",format=qcow2,if=virtio \
    -cdrom "$ARCH_ISO" \
    -boot d \
    -net nic,model=virtio \
    -net user \
    -vga virtio \
    -display gtk,gl=on
