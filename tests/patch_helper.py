#!/usr/bin/env python3
import os

root = "/var/tmp/build-caelestia/caelestia-kde-2.6.3"
path = os.path.join(root, "scripts", "10-autostart.sh")
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "Self-heal Caelestia lock screen" in line:
        skip = True
        new_lines.append("# Horizon OS: Preserved KScreenLocker configuration without hijack\n")
        continue
    if skip:
        if line.strip() == "fi" and "kwriteconfig6" not in line and "ShellPackage" not in line:
            # Check if this closes the outer if
            # Wait, the inner if closes with fi at line 86, and outer closes with fi at line 88.
            # Let's see if next line after fi is '# No --daemonize'
            pass
        if "No --daemonize" in line:
            skip = False
            new_lines.append(line)
        continue
    new_lines.append(line)

with open(path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("10-autostart.sh patched successfully!")
