#!/usr/bin/env bash
# Horizon OS Live ISO Profile Definition
iso_name="horizon-os"
iso_label="HORIZON_$(date +%Y%m)"
iso_publisher="Horizon OS Project <https://github.com/Beastknight933/customOS>"
iso_application="Horizon OS Live Installation Medium"
iso_version="$(date +%Y.%m.%d)"
install_dir="horizon"
buildmodes=('iso')
bootmodes=('bios.syslinux.mbr' 'bios.syslinux.eltorito'
           'uefi-ia32.systemd-boot.esp' 'uefi-x64.systemd-boot.esp'
           'uefi-ia32.systemd-boot.eltorito' 'uefi-x64.systemd-boot.eltorito')
arch="x86_64"
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'zstd')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/root"]="0:0:750"
  ["/root/.automated_script.sh"]="0:0:755"
  ["/usr/local/bin/horizon-install"]="0:0:755"
)
