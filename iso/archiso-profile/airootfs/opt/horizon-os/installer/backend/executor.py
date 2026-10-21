#!/usr/bin/env python3
"""
Horizon OS Installer - Command Executor & Stage Runner
Provides safe command execution, secret-redacted logging, process pipe isolation,
and rigorous mount-point verification.
"""
import os
import sys
import subprocess
import time
import shutil
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
        try:
            if self.file and not getattr(self.file, "closed", False):
                self.file.write(formatted + "\n")
                self.file.flush()
        except Exception:
            pass

    def close(self):
        try:
            self.file.close()
        except Exception:
            pass

class InstallExecutor:
    def __init__(self, dry_run: bool = False, target_root: str = "/mnt", logger: Optional[InstallLogger] = None):
        self.dry_run = dry_run
        self.target_root = os.path.abspath(target_root)
        self.logger = logger or InstallLogger()
        self.cancelled = False
        self.last_failed_command: Optional[str] = None
        self.last_error: Optional[str] = None
        self.current_stage: Optional[str] = None

    def set_stage(self, stage_name: str):
        """Set the current installation stage for diagnostic tracking."""
        self.current_stage = stage_name
        self.logger.log(f"STAGE: {stage_name}")

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
                err_msg = f"Command exited with code {proc.returncode}: {description or cmd_str}"
                self.logger.log(f"ERROR: {err_msg}")
                self.last_failed_command = description or cmd_str
                self.last_error = err_msg
                return False
            return True
        except Exception as e:
            err_msg = f"EXCEPTION executing {description or cmd[0]}: {str(e)}"
            self.logger.log(err_msg)
            self.last_failed_command = description or cmd_str
            self.last_error = err_msg
            if on_output:
                on_output(f"ERROR: {str(e)}")
            return False

    def chroot_exec(self, cmd: List[str], description: str = "", on_output: Optional[Callable[[str], None]] = None) -> bool:
        """Execute a command inside the target root via arch-chroot."""
        full_cmd = ["arch-chroot", self.target_root] + cmd
        return self.run_cmd(full_cmd, description=f"chroot: {description}", on_output=on_output)

    def set_user_password(self, username: str, password: str, description: str = "") -> bool:
        """
        Securely set user/root password without invoking shell interpretation,
        without echoing on command lines, and without writing secrets to logs.
        Uses chpasswd through an isolated stdin pipe.
        """
        if not username or not password:
            self.last_error = "Username or password cannot be empty"
            self.logger.log("ERROR: set_user_password called with empty username or password")
            return False

        desc = description or f"Setting password for user '{username}'"
        self.logger.log(f"CMD START: {desc} (secret redacted)")

        if self.dry_run:
            self.logger.log(f"DRYRUN: chpasswd for user '{username}' (secret redacted)")
            return True

        # Input data strictly passed via stdin: username:password\n
        pipe_input = f"{username}:{password}\n".encode("utf-8")

        # In chroot or direct execution
        cmd = ["arch-chroot", self.target_root, "chpasswd", "-c", "SHA512"]
        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = proc.communicate(input=pipe_input)
            
            if proc.returncode != 0:
                err_text = stderr.decode("utf-8", errors="replace").strip()
                err_msg = f"chpasswd failed with code {proc.returncode}: {err_text}"
                self.logger.log(f"ERROR: {err_msg}")
                self.last_failed_command = desc
                self.last_error = err_msg
                return False

            self.logger.log(f"CMD SUCCESS: Password securely updated for user '{username}'")
            return True
        except Exception as e:
            err_msg = f"EXCEPTION in set_user_password for '{username}': {str(e)}"
            self.logger.log(err_msg)
            self.last_failed_command = desc
            self.last_error = err_msg
            return False

    def verify_mount(self, mount_point: str, expected_fstype: Optional[str] = None) -> bool:
        """
        Verify that a directory is an actual active mountpoint on the system.
        Prevents installing files directly into host RAM or live media roots.
        """
        if self.dry_run:
            return True

        abs_mount = os.path.abspath(mount_point)
        # Check /proc/mounts
        if os.path.exists("/proc/mounts"):
            try:
                with open("/proc/mounts", "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.split()
                        if len(parts) >= 3:
                            target, fstype = parts[1], parts[2]
                            if target == abs_mount:
                                if expected_fstype and fstype != expected_fstype:
                                    self.logger.log(f"WARNING: Mount {abs_mount} has fstype {fstype}, expected {expected_fstype}")
                                    return False
                                return True
            except Exception as e:
                self.logger.log(f"EXCEPTION reading /proc/mounts: {str(e)}")

        # Fallback to os.path.ismount
        return os.path.ismount(abs_mount)

    def cleanup_target_mounts(self, target_disk: Optional[str] = None) -> bool:
        """
        Safely unmount all target filesystems in reverse order.
        Strictly enforces that ONLY mounts inside self.target_root or on target_disk are touched.
        NEVER unmounts host filesystems.
        """
        if self.dry_run:
            self.logger.log(f"DRYRUN: Unmounting target {self.target_root}")
            return True

        self.logger.log(f"Starting target mount cleanup for {self.target_root}")
        success = True
        target_abs = os.path.abspath(self.target_root)

        # 1. Deactivate swap if target_disk is specified
        if target_disk and os.path.exists("/proc/swaps"):
            try:
                with open("/proc/swaps", "r", encoding="utf-8") as f:
                    for line in f:
                        dev = line.split()[0]
                        if dev.startswith(target_disk):
                            self.logger.log(f"Deactivating target swap on {dev}")
                            subprocess.run(["swapoff", dev], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                self.logger.log(f"EXCEPTION during swapoff: {str(e)}")

        # 2. Gather mounts strictly rooted at self.target_root
        mounted_targets = []
        if os.path.exists("/proc/mounts"):
            try:
                with open("/proc/mounts", "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.split()
                        if len(parts) >= 2:
                            m_target = parts[1]
                            # Strict containment check
                            if m_target == target_abs or m_target.startswith(target_abs + "/"):
                                # Prohibit unmounting host root or essential host dirs
                                if m_target not in ["/", "/proc", "/sys", "/dev", "/run"]:
                                    mounted_targets.append(m_target)
            except Exception as e:
                self.logger.log(f"EXCEPTION reading /proc/mounts: {str(e)}")

        # Unmount in descending order of path length (deepest mounts first)
        for m in sorted(mounted_targets, key=len, reverse=True):
            self.logger.log(f"Unmounting {m}")
            res = subprocess.run(["umount", "-R", m], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode != 0:
                # Retry with lazy unmount if busy
                res_lazy = subprocess.run(["umount", "-l", m], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if res_lazy.returncode != 0:
                    self.logger.log(f"WARNING: Failed to unmount {m}")
                    success = False

        return success

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
