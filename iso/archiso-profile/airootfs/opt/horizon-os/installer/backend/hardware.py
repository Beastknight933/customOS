#!/usr/bin/env python3
"""
Horizon OS Installer - Hardware Probing Module
"""
import os
import subprocess
import shutil
import platform
from typing import Dict, Any, List

def detect_uefi() -> bool:
    """Check if the system booted in UEFI mode."""
    return os.path.exists("/sys/firmware/efi")

def detect_cpu_info() -> Dict[str, Any]:
    """Detect CPU model and microarchitecture level (v2, v3, v4)."""
    info = {
        "model": platform.processor() or "Unknown CPU",
        "cores": os.cpu_count() or 1,
        "arch": platform.machine(),
        "v3_supported": False,
        "v4_supported": False,
    }
    
    # Check /proc/cpuinfo on Linux
    if os.path.exists("/proc/cpuinfo"):
        try:
            with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
                flags = []
                for line in f:
                    if line.startswith("model name") and info["model"] == "Unknown CPU":
                        info["model"] = line.split(":", 1)[1].strip()
                    elif line.startswith("flags"):
                        flags = line.split(":", 1)[1].strip().split()
                
                # Check x86-64-v3 flags: avx, avx2, bmi1, bmi2, fma, movbe
                v3_flags = {"avx", "avx2", "bmi1", "bmi2", "fma", "movbe"}
                info["v3_supported"] = v3_flags.issubset(set(flags))
                
                # Check x86-64-v4 flags: avx512f, avx512bw, avx512cd, avx512dq, avx512vl
                v4_flags = {"avx512f", "avx512bw", "avx512cd", "avx512dq", "avx512vl"}
                info["v4_supported"] = v4_flags.issubset(set(flags))
        except Exception:
            pass
    return info

def detect_memory() -> Dict[str, Any]:
    """Detect system RAM in MB and GB."""
    mem_total_mb = 0
    if os.path.exists("/proc/meminfo"):
        try:
            with open("/proc/meminfo", "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        kb = int(line.split()[1])
                        mem_total_mb = kb // 1024
                        break
        except Exception:
            pass
    return {
        "total_mb": mem_total_mb,
        "total_gb": round(mem_total_mb / 1024, 1) if mem_total_mb else 0,
    }

def detect_gpus() -> List[str]:
    """Detect graphics cards (NVIDIA, AMD, Intel, Virtual)."""
    gpus = []
    if shutil.which("lspci"):
        try:
            out = subprocess.check_output(["lspci", "-nn"], text=True)
            for line in out.splitlines():
                if "VGA" in line or "3D controller" in line or "Display controller" in line:
                    gpus.append(line.split(":", 2)[-1].strip())
        except Exception:
            pass
    if not gpus:
        gpus = ["Standard Display Adapter / Generic GPU"]
    return gpus

def probe_all_hardware() -> Dict[str, Any]:
    """Return complete hardware probing summary."""
    return {
        "uefi": detect_uefi(),
        "cpu": detect_cpu_info(),
        "memory": detect_memory(),
        "gpus": detect_gpus(),
    }
