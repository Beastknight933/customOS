#!/usr/bin/env python3
"""
Horizon OS Installer - Component Deployment Module
"""
import os
import shutil
from typing import Callable, Optional
from .executor import InstallExecutor

class ComponentDeployer:
    def __init__(self, executor: InstallExecutor, repo_root: str):
        self.executor = executor
        self.repo_root = repo_root
        self.target_root = executor.target_root

    def deploy_ryoku_sddm(self, on_output: Optional[Callable[[str], None]] = None) -> bool:
        """Deploy Ryoku Orbital SDDM theme and configure /etc/sddm.conf.d/99-ryoku.conf."""
        if on_output:
            on_output("Deploying Horizon Ryoku SDDM theme...")
        
        theme_src = os.path.join(self.repo_root, "custom-components", "ryoku-sddm")
        target_dir = os.path.join(self.target_root, "usr", "share", "sddm", "themes", "ryoku")
        
        if not self.executor.dry_run:
            os.makedirs(target_dir, exist_ok=True)
            for item in ["Main.qml", "metadata.desktop", "theme.conf", "preview.gif", "font", "i18n"]:
                src = os.path.join(theme_src, item)
                dst = os.path.join(target_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                elif os.path.isfile(src):
                    shutil.copy2(src, dst)

        # Write SDDM configuration
        self.executor.write_target_file("etc/sddm.conf.d/99-ryoku.conf", "[Theme]\nCurrent=ryoku\n")
        
        # Strictly delete any Caelestia SDDM override
        caelestia_override = os.path.join(self.target_root, "etc", "sddm.conf.d", "zz-caelestia.conf")
        if os.path.exists(caelestia_override):
            os.remove(caelestia_override)

        self.executor.logger.log(f"Ryoku SDDM theme deployed to {target_dir}")
        return True

    def deploy_overload_splash(self, on_output: Optional[Callable[[str], None]] = None) -> bool:
        """Deploy Overload Plasma 6 splash screen."""
        if on_output:
            on_output("Deploying Overload splash screen...")
            
        splash_src = os.path.join(self.repo_root, "custom-components", "splash")
        target_dir = os.path.join(self.target_root, "usr", "share", "plasma", "look-and-feel", "Overload")
        
        if not self.executor.dry_run:
            os.makedirs(target_dir, exist_ok=True)
            meta_src = os.path.join(splash_src, "metadata.json")
            if os.path.isfile(meta_src):
                shutil.copy2(meta_src, os.path.join(target_dir, "metadata.json"))
            contents_src = os.path.join(splash_src, "contents")
            if os.path.isdir(contents_src):
                shutil.copytree(contents_src, os.path.join(target_dir, "contents"), dirs_exist_ok=True)

        # Write ksplashrc
        self.executor.write_target_file("etc/xdg/ksplashrc", "[KSplash]\nEngine=KSplashQML\nTheme=Overload\n")
        self.executor.logger.log(f"Overload splash screen deployed to {target_dir}")
        return True

    def deploy_candy_icons(self, on_output: Optional[Callable[[str], None]] = None) -> bool:
        """Deploy Candy Bar (candy-icons) theme and set kdeglobals."""
        if on_output:
            on_output("Deploying Candy Bar icon theme...")
            
        icons_src = os.path.join(self.repo_root, "custom-components", "icons", "candy-icons")
        target_dir = os.path.join(self.target_root, "usr", "share", "icons", "candy-icons")
        
        if not self.executor.dry_run and os.path.isdir(icons_src):
            os.makedirs(target_dir, exist_ok=True)
            shutil.copytree(icons_src, target_dir, dirs_exist_ok=True)

        # Configure kdeglobals
        self.executor.write_target_file("etc/xdg/kdeglobals", "[Icons]\nTheme=candy-icons\n")
        self.executor.logger.log(f"Candy Bar icons deployed to {target_dir}")
        return True

    def deploy_horizon_kde_defaults(self, on_output: Optional[Callable[[str], None]] = None) -> bool:
        """Deploy Horizon KDE, KWin, and KScreenLocker default configurations."""
        if on_output:
            on_output("Applying Horizon OS KDE desktop and KWin defaults...")
            
        defaults_dir = os.path.join(self.repo_root, "defaults")
        
        # Copy KDE defaults
        for fname in ["kdeglobals", "ksplashrc", "kwinrc", "kscreenlockerrc"]:
            src_f = os.path.join(defaults_dir, "kde", fname)
            if os.path.exists(src_f):
                with open(src_f, "r", encoding="utf-8") as f:
                    self.executor.write_target_file(f"etc/xdg/{fname}", f.read())

        # Copy wallpapers
        wallpapers_src = os.path.join(defaults_dir, "visual-identity", "wallpapers")
        if os.path.exists(wallpapers_src):
            wall_target = os.path.join(self.target_root, "usr", "share", "wallpapers", "horizon")
            if not self.executor.dry_run:
                os.makedirs(wall_target, exist_ok=True)
                for w in os.listdir(wallpapers_src):
                    src_w = os.path.join(wallpapers_src, w)
                    if os.path.isfile(src_w):
                        shutil.copy2(src_w, os.path.join(wall_target, w))
            self.executor.logger.log(f"Wallpapers copied to {wall_target}")

        return True

    def deploy_caelestia_shell(self, username: str, on_output: Optional[Callable[[str], None]] = None) -> bool:
        """Deploy Caelestia shell package, configurations, user defaults, and autostart service."""
        if on_output:
            on_output("Deploying Caelestia KDE shell & Horizon configuration...")

        # Install pre-built Caelestia package if available
        pkg_dirs = [
            os.path.join(self.repo_root, "packages", "caelestia-kde"),
            os.path.join(self.repo_root, "custom-components", "caelestia-kde", "packaging"),
        ]
        pkg_file = None
        for pdir in pkg_dirs:
            if os.path.exists(pdir):
                for f in os.listdir(pdir):
                    if f.startswith("caelestia-kde") and f.endswith(".pkg.tar.zst"):
                        pkg_file = os.path.join(pdir, f)
                        break
            if pkg_file:
                break

        has_pacman = os.path.exists(os.path.join(self.target_root, "usr", "bin", "pacman"))
        if pkg_file and has_pacman and not self.executor.dry_run:
            target_pkg_dir = os.path.join(self.target_root, "tmp")
            os.makedirs(target_pkg_dir, exist_ok=True)
            pkg_name = os.path.basename(pkg_file)
            target_pkg_path = os.path.join(target_pkg_dir, pkg_name)
            shutil.copy2(pkg_file, target_pkg_path)
            self.executor.logger.log(f"Installing bundled Caelestia package: {pkg_name}")
            self.executor.chroot_exec(
                ["pacman", "-U", "--noconfirm", "--overwrite", "*", f"/tmp/{pkg_name}"],
                description=f"Installing {pkg_name}",
                on_output=on_output
            )
            # Clean up temporary package file
            try:
                os.remove(target_pkg_path)
            except OSError:
                pass

        shell_json_src = os.path.join(self.repo_root, "defaults", "shell", "shell.json")
        tokens_json_src = os.path.join(self.repo_root, "defaults", "shell", "shell-tokens.json")
        
        if os.path.exists(shell_json_src):
            with open(shell_json_src, "r", encoding="utf-8") as f:
                content = f.read()
                self.executor.write_target_file("etc/skel/.config/caelestia/shell.json", content)
                if username:
                    self.executor.write_target_file(f"home/{username}/.config/caelestia/shell.json", content)

        if os.path.exists(tokens_json_src):
            with open(tokens_json_src, "r", encoding="utf-8") as f:
                content = f.read()
                self.executor.write_target_file("etc/skel/.config/caelestia/shell-tokens.json", content)
                if username:
                    self.executor.write_target_file(f"home/{username}/.config/caelestia/shell-tokens.json", content)

        # Deploy autostart script and systemd unit (if not already installed by package)
        pkg_dir = os.path.join(self.repo_root, "custom-components", "caelestia-kde", "packaging")
        autostart_src = os.path.join(pkg_dir, "caelestia-autostart")
        service_src = os.path.join(pkg_dir, "caelestia-shell.service")

        if os.path.exists(autostart_src):
            with open(autostart_src, "r", encoding="utf-8") as f:
                self.executor.write_target_file("usr/bin/caelestia-autostart", f.read(), mode=0o755)

        if os.path.exists(service_src):
            with open(service_src, "r", encoding="utf-8") as f:
                self.executor.write_target_file("usr/lib/systemd/user/caelestia-shell.service", f.read())

        # Fix ownership of user config
        if username and not self.executor.dry_run:
            self.executor.chroot_exec(
                ["chown", "-R", f"{username}:{username}", f"/home/{username}/.config"],
                description="Fixing user config ownership",
                on_output=on_output
            )

        # Enable user systemd unit
        self.executor.chroot_exec(
            ["systemctl", "--global", "enable", "caelestia-shell.service"],
            description="Enabling Caelestia shell user service globally",
            on_output=on_output
        )

        return True
