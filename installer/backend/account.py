#!/usr/bin/env python3
"""
Horizon OS Installer - Account & Identity Security Module
Provides RFC 1123 hostname validation, POSIX username validation,
and secure non-echoing password input routines.
"""
import sys
import re
import getpass
from typing import Tuple

def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate POSIX / shadow compliant username:
    - 1-32 chars
    - Starts with lowercase letter or underscore: [a-z_]
    - Contains only lowercase letters, digits, underscores, or hyphens: [a-z0-9_-]
    - Cannot end with a hyphen
    - Cannot be a reserved system account
    """
    if not username:
        return False, "Username cannot be empty."
    if len(username) > 32:
        return False, "Username cannot exceed 32 characters."
    if not re.match(r"^[a-z_][a-z0-9_-]*$", username):
        return False, "Username must start with a lowercase letter or underscore, containing only lowercase letters, digits, underscores, or hyphens."
    if username.endswith("-"):
        return False, "Username cannot end with a hyphen."
    reserved = {
        "root", "daemon", "bin", "sys", "sync", "games", "man", "lp", "mail",
        "news", "uucp", "proxy", "www-data", "backup", "list", "irc", "gnats",
        "nobody", "systemd-network", "systemd-resolve", "messagebus", "avahi",
    }
    if username in reserved:
        return False, f"'{username}' is a reserved system account."
    return True, "Valid"

def validate_hostname(hostname: str) -> Tuple[bool, str]:
    """
    Validate RFC 1123 compliant hostname:
    - 1-63 characters per label
    - Alphanumeric and hyphens only
    - Cannot start or end with a hyphen
    """
    if not hostname:
        return False, "Hostname cannot be empty."
    if len(hostname) > 63:
        return False, "Hostname cannot exceed 63 characters."
    if not re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$", hostname):
        return False, "Hostname must consist of letters, digits, and hyphens, and cannot start or end with a hyphen."
    return True, "Valid"

def prompt_secure_password(prompt_label: str, confirm_label: str = "Confirm Password") -> str:
    """Prompt for password with masking (non-echoing) and verification."""
    while True:
        try:
            pw1 = getpass.getpass(f"  {prompt_label}: ")
        except (EOFError, Exception):
            line = sys.stdin.readline()
            pw1 = line.rstrip("\r\n") if line else ""

        if not pw1:
            print("  Password cannot be empty. Please enter a valid password.")
            continue

        try:
            pw2 = getpass.getpass(f"  {confirm_label}: ")
        except (EOFError, Exception):
            line = sys.stdin.readline()
            pw2 = line.rstrip("\r\n") if line else ""

        if pw1 != pw2:
            print("  Passwords do not match. Please try again.")
            continue

        return pw1
