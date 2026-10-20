#!/usr/bin/env python3
"""
Horizon OS Installer - Command Executor & Stage Runner
"""
import os
import sys
import subprocess
import time
from typing import Callable, Optional, List, Dict, Any

class InstallLogger:
    def __init__(self, log_path: str = "/var/log/horizon-install.log"):
        self.log_path = log_path
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            self.file = open(log_path, "a", encoding="utf-8")
        except Exception:
            self.log_path = "horizon-install.log"
            self.file = open(self.log_path, "a", encoding="utf-8")

    def log(self, message: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        self.file.write(formatted + "\n")
        self.file.flush()

    def close(self):
        try:
            self.file.close()
        except Exception:
            pass

class InstallExecutor:
    def __init__(self, dry_run: bool = False, target_root: str = "/mnt", logger: Optional[InstallLogger] = None):
        self.dry_run = dry_run
        self.target_root = target_root
        self.logger = logger or InstallLogger()
        self.cancelled = False

    def run_cmd(self, cmd: List[str], description: str = "", on_output: Optional[Callable[[str], None]] = None) -> bool:
        """Run a shell command with logging and optional real-time callback."""
        cmd_str = " ".join(cmd)
        self.logger.log(f"CMD START: {description or cmd_str}")
        if description and on_output:
            on_output(f">> {description}")

        if self.dry_run:
            self.logger.log(f"DRYRUN: {cmd_str}")
            if on_output:
                on_output(f"[DRYRUN] {cmd_str}")
            time.sleep(0.05)
            return True

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            for line in proc.stdout:
                line_clean = line.rstrip()
                self.logger.log(f"OUTPUT: {line_clean}")
                if on_output:
                    on_output(line_clean)
            if proc.stdout:
                proc.stdout.close()
            proc.wait()
            if proc.returncode != 0:
                self.logger.log(f"ERROR: Command exited with code {proc.returncode}")
                return False
            return True
        except Exception as e:
            self.logger.log(f"EXCEPTION: {str(e)}")
            if on_output:
                on_output(f"ERROR: {str(e)}")
            return False

    def chroot_exec(self, cmd: List[str], description: str = "", on_output: Optional[Callable[[str], None]] = None) -> bool:
        """Execute a command inside the target root via arch-chroot."""
        full_cmd = ["arch-chroot", self.target_root] + cmd
        return self.run_cmd(full_cmd, description=f"chroot: {description}", on_output=on_output)

    def write_target_file(self, rel_path: str, content: str, mode: int = 0o644):
        """Write a file into the target root directory."""
        full_path = os.path.join(self.target_root, rel_path.lstrip("/"))
        self.logger.log(f"WRITE FILE: {full_path}")
        if self.dry_run:
            self.logger.log(f"DRYRUN CONTENT ({len(content)} bytes):\n{content}")
            return
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        os.chmod(full_path, mode)
