# Security Policy — Horizon OS

## 1. Supported Versions

| Version | Status | Security Updates |
| :--- | :--- | :--- |
| **Horizon OS 2026.10 (Singularity)** | **Supported** | Active |

---

## 2. Security Architecture & Controls

### 2.1 Account Security & Privilege Management
- **Zero Insecure Defaults**: The Horizon OS installer does not ship with, generate, or accept default or hardcoded passwords.
- **Secure Password Prompting**: All password inputs utilize non-echoing terminal routines (`getpass`) and require explicit confirmation.
- **Root Account Policy**: By default, the root account is locked (`passwd -l root`), and administrative privileges are delegated via `sudo` for users in the `%wheel` group. If the user opts for a separate root password, it is prompted independently with verification.
- **Strict Input Validation**: Hostnames must conform to RFC 1123, and usernames are strictly restricted to POSIX compliant strings (`[a-z_][a-z0-9_-]*`).

### 2.2 Subprocess Safety & Secret Redaction
- **No Shell Interpolation**: All privileged commands and chroot operations pass arguments as discrete arrays, completely preventing shell metacharacter injection.
- **Isolated Stdin Password Injection**: Passwords are supplied to `chpasswd` exclusively via isolated pipes directly to stdin. Passwords never appear on process command lines (`ps`/`pgrep`) or in `/proc`.
- **Zero Credential Logging**: All installer logging facilities sanitize commands and redact secrets prior to writing to `/var/log/horizon-install.log`.

### 2.3 Storage Guards & Recovery Protection
- **Drive Filtering**: Live installation media and active host disks are identified via `sysfs`, `udev`, and mount inspection, blocking accidental selection.
- **Pre-execution Revalidation**: The installer revalidates disk identity immediately prior to GPT table generation.
- **Isolated Cleanup**: In the event of an installation failure, cleanup procedures unwind only target-specific mountpoints (`@`, `@home`, ESP) and swap devices without affecting host filesystems.

---

## 3. Reporting a Vulnerability

If you discover a security vulnerability within Horizon OS, please report it responsibly and confidentially:
1. Open a confidential draft security advisory via GitHub Repository Advisories.
2. Provide a clear description of the vulnerability, affected components, reproduction steps, and potential impact.
3. Do **not** disclose or publish details in public issues, discussions, or social media until maintainers have reviewed and addressed the issue.
