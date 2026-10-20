# Horizon OS — System Recovery & Emergency Operations

This document outlines recovery procedures for emergency scenarios, including bootloader restoration, desktop configuration reset, and chroot operations.

## 1. Entering Chroot from Arch Linux Live ISO

If the installed system fails to boot or system services need maintenance:

1. Boot into the Arch Linux Live ISO in UEFI mode.
2. If using Btrfs, mount the subvolumes:
   ```bash
   mount -o subvol=@ /dev/disk/by-label/HORIZON_ROOT /mnt
   mount -o subvol=@home /dev/disk/by-label/HORIZON_ROOT /mnt/home
   mount /dev/disk/by-label/HORIZON_EFI /mnt/boot/efi
   ```
3. Enter the target environment:
   ```bash
   arch-chroot /mnt
   ```

## 2. Restoring the Bootloader

### Limine (Default)
```bash
# Inside chroot:
limine bios-install /dev/sdX   # (or /dev/nvme0n1)
```

### systemd-boot
```bash
bootctl install --esp-path=/boot/efi
```

### GRUB
```bash
grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=HORIZON
grub-mkconfig -o /boot/grub/grub.cfg
```

## 3. Resetting Horizon Desktop Configurations

To restore the default Caelestia shell, SDDM theme, and KDE configuration to their clean factory defaults:

```bash
# Re-apply defaults from the repo checkout:
./scripts/deploy-horizon.sh /

# Or reset individual user shell configuration:
cp defaults/shell/shell.json ~/.config/caelestia/shell.json
cp defaults/shell/shell-tokens.json ~/.config/caelestia/shell-tokens.json
systemctl --user restart caelestia-shell.service
```

## 4. Resetting SDDM Configuration

If SDDM fails to start or reverts to an unintended theme:

```bash
# Ensure 99-ryoku.conf is active
echo -e "[Theme]\nCurrent=ryoku" > /etc/sddm.conf.d/99-ryoku.conf

# Ensure any conflicting dropins are removed
rm -f /etc/sddm.conf.d/zz-caelestia.conf

# Test greeter in test mode:
sddm-greeter-qt6 --test-mode --theme /usr/share/sddm/themes/ryoku
```
