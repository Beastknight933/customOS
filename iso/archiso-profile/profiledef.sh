#!/usr/bin/env bash
# Horizon OS Live ISO Profile Definition
iso_name="horizon-os"
iso_label="HORIZON_$(date +%Y%m)"
iso_publisher="Horizon OS Project <https://github.com/Beastknight933/customOS>"
iso_application="Horizon OS Live Installation Medium"
iso_version="$(date +%Y.%m.%d)"
install_dir="horizon"
buildmodes=('iso')
bootmodes=('bios.syslinux'
           'uefi.systemd-boot')
arch="x86_64"
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'zstd')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/root"]="0:0:750"
  ["/root/.bash_profile"]="0:0:755"
  ["/root/.zlogin"]="0:0:755"
  ["/usr/local/bin/horizon-install"]="0:0:755"
  ["/opt/horizon-os/installer/horizon-tui.py"]="0:0:755"
  ["/opt/horizon-os/install.sh"]="0:0:755"
)
