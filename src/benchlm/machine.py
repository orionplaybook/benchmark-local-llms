"""Detect the machine the benchmark runs on (no hostnames stored)."""
from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess


def _run(cmd, timeout=20) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def _mac() -> dict:
    info = {"os": "macOS", "os_version": platform.mac_ver()[0], "arch": platform.machine()}
    raw = _run(["system_profiler", "SPHardwareDataType", "SPDisplaysDataType", "-json"], 60)
    try:
        sp = json.loads(raw)
    except ValueError:
        sp = {}
    hw = (sp.get("SPHardwareDataType") or [{}])[0]
    gpu = (sp.get("SPDisplaysDataType") or [{}])[0]
    info["model_name"] = hw.get("machine_name")
    info["model_identifier"] = hw.get("machine_model")
    info["chip"] = hw.get("chip_type") or _run(["sysctl", "-n", "machdep.cpu.brand_string"]).strip()
    procs = hw.get("number_processors", "")  # e.g. "proc 18:6:12:0"
    m = re.match(r"proc\s+(\d+):?(\d+)?:?(\d+)?", str(procs))
    cores = _run(["sysctl", "-n", "hw.ncpu"]).strip()
    info["cpu_cores"] = int(m.group(1)) if m else (int(cores) if cores.isdigit() else None)
    if m and m.group(2):
        # Apple reports top tier first; M5-generation names the tiers "Super" and "Performance".
        tiers = [int(x) for x in m.groups()[1:] if x]
        labels = ["Super", "Performance", "Efficiency"] if "M5" in (info["chip"] or "") else ["Performance", "Efficiency", "Other"]
        info["cpu_cores_detail"] = " + ".join(f"{n} {labels[i]}" for i, n in enumerate(tiers) if n)
    gc = gpu.get("sppci_cores")
    info["gpu_cores"] = int(gc) if str(gc).isdigit() else None
    mem = _run(["sysctl", "-n", "hw.memsize"]).strip()
    info["memory_bytes"] = int(mem) if mem.isdigit() else None
    return info


def _windows() -> dict:
    info = {"os": "Windows", "os_version": platform.version(), "arch": platform.machine()}
    ps = ("$cs=Get-CimInstance Win32_ComputerSystem;$p=Get-CimInstance Win32_Processor|Select -First 1;"
          "$g=Get-CimInstance Win32_VideoController|Select -First 1;"
          "@{model=$cs.Model;maker=$cs.Manufacturer;mem=$cs.TotalPhysicalMemory;cpu=$p.Name;"
          "cores=$p.NumberOfCores;threads=$p.NumberOfLogicalProcessors;gpu=$g.Name;vram=$g.AdapterRAM}|ConvertTo-Json")
    raw = _run(["powershell", "-NoProfile", "-Command", ps], 60)
    try:
        d = json.loads(raw)
    except ValueError:
        d = {}
    info.update({
        "model_name": f"{d.get('maker') or ''} {d.get('model') or ''}".strip() or None,
        "model_identifier": d.get("model"),
        "chip": d.get("cpu"),
        "cpu_cores": d.get("cores"),
        "cpu_cores_detail": f"{d.get('threads')} threads" if d.get("threads") else None,
        "gpu": d.get("gpu"),
        "gpu_cores": None,
        "memory_bytes": d.get("mem"),
    })
    smi = shutil.which("nvidia-smi")
    if smi:
        out = _run([smi, "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"])
        if out.strip():
            name, total = [x.strip() for x in out.splitlines()[0].split(",")[:2]]
            info["gpu"] = name
            info["gpu_vram_bytes"] = int(float(total) * 1024 * 1024)
    return info


def _linux() -> dict:
    info = {"os": "Linux", "os_version": platform.release(), "arch": platform.machine(),
            "model_name": None, "model_identifier": None, "cpu_cores": os.cpu_count(), "gpu_cores": None}
    try:
        with open("/proc/cpuinfo") as f:
            m = re.search(r"model name\s*:\s*(.+)", f.read())
            info["chip"] = m.group(1).strip() if m else platform.processor()
        with open("/proc/meminfo") as f:
            m = re.search(r"MemTotal:\s*(\d+)", f.read())
            info["memory_bytes"] = int(m.group(1)) * 1024 if m else None
    except OSError:
        pass
    return info


def detect() -> dict:
    system = platform.system()
    if system == "Darwin":
        info = _mac()
    elif system == "Windows":
        info = _windows()
    else:
        info = _linux()
    try:
        info["disk_bytes"] = shutil.disk_usage(os.path.expanduser("~")).total
    except OSError:
        info["disk_bytes"] = None
    gb = round((info.get("memory_bytes") or 0) / 1024 ** 3)
    chip = (info.get("chip") or "cpu").replace("Apple ", "")
    ident = info.get("model_identifier") or info.get("model_name") or system
    info["machine_id"] = re.sub(r"[^A-Za-z0-9,._-]+", "", f"{ident}-{chip}-{gb}GB")
    short = info.get("model_name") or system
    info["label"] = f"{short} {chip} {gb}GB"
    info["specs_extra"] = {}
    return info
