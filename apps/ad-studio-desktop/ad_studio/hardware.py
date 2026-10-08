from __future__ import annotations

from dataclasses import dataclass, asdict
import os
import platform
import re
import shutil
import subprocess
from typing import Any


@dataclass
class GPUDevice:
    name: str
    vendor: str
    vram_mb: int = 0
    driver: str = ""
    backend: str = "CPU"


@dataclass
class HardwareProfile:
    platform: str
    cpu: str
    cpu_cores: int
    ram_gb: float
    gpus: list[GPUDevice]
    accelerator: str
    encoders: list[str]
    local_ai_level: str
    execution_mode: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["gpus"] = [asdict(g) for g in self.gpus]
        return data


def _run(cmd: list[str], timeout: int = 5) -> str:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.stdout.strip() if p.returncode == 0 else ""
    except Exception:
        return ""


def _detect_nvidia() -> list[GPUDevice]:
    out = _run([
        "nvidia-smi",
        "--query-gpu=name,memory.total,driver_version",
        "--format=csv,noheader,nounits",
    ])
    devices = []
    for line in out.splitlines():
        parts = [x.strip() for x in line.split(",")]
        if len(parts) < 3:
            continue
        try:
            devices.append(GPUDevice(parts[0], "NVIDIA", int(float(parts[1])), parts[2], "CUDA"))
        except ValueError:
            pass
    return devices


def _detect_other_gpus() -> list[GPUDevice]:
    system = platform.system()
    text = ""
    if system == "Windows":
        text = _run([
            "powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_VideoController | "
            "Select-Object -ExpandProperty Name | Out-String",
        ])
    elif system == "Linux":
        text = _run(["bash", "-lc", "lspci 2>/dev/null | grep -Ei 'vga|3d|display'"])
    elif system == "Darwin":
        text = _run(["system_profiler", "SPDisplaysDataType"])
    devices = []
    for line in text.splitlines():
        name = line.strip()
        if not name:
            continue
        low = name.lower()
        if "nvidia" in low:
            continue
        vendor = "AMD" if "amd" in low or "radeon" in low else ("Intel" if "intel" in low or "arc" in low else "Apple" if "apple" in low else "Other")
        backend = "ROCm" if vendor == "AMD" else ("Metal" if vendor == "Apple" else "Unknown")
        devices.append(GPUDevice(name, vendor, 0, "", backend))
    return devices


def _detect_accelerator(gpus: list[GPUDevice]) -> str:
    if any(g.backend == "CUDA" for g in gpus):
        return "CUDA"
    if any(g.backend == "ROCm" for g in gpus) or shutil.which("rocminfo"):
        return "ROCm"
    if platform.system() == "Darwin":
        return "Metal"
    return "CPU"


def _detect_encoders() -> list[str]:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return []
    out = _run([ffmpeg, "-hide_banner", "-encoders"], timeout=10)
    known = ["h264_nvenc", "hevc_nvenc", "av1_nvenc", "h264_amf", "hevc_amf", "h264_qsv", "hevc_qsv", "av1_qsv", "h264_videotoolbox", "hevc_videotoolbox"]
    return [x for x in known if re.search(r"\b" + re.escape(x) + r"\b", out)]


def _local_ai_level(gpus: list[GPUDevice], accelerator: str) -> str:
    max_vram = max((g.vram_mb for g in gpus), default=0)
    if accelerator == "CUDA":
        if max_vram >= 16000:
            return "强"
        if max_vram >= 8000:
            return "标准"
        if max_vram >= 6000:
            return "基础"
        if max_vram > 0:
            return "轻量"
    if accelerator == "ROCm":
        if max_vram >= 16000:
            return "强"
        if max_vram >= 8000:
            return "标准"
        if max_vram > 0:
            return "基础"
    if accelerator == "Metal":
        return "标准（按统一内存动态判断）"
    return "CPU/云端"


def detect_hardware() -> HardwareProfile:
    gpus = _detect_nvidia() + _detect_other_gpus()
    accelerator = _detect_accelerator(gpus)
    ram_gb = 0.0
    try:
        import psutil
        ram_gb = round(psutil.virtual_memory().total / 1024**3, 1)
    except Exception:
        pass
    cores = os.cpu_count() or 1
    level = _local_ai_level(gpus, accelerator)
    mode = "local_first" if level in {"强", "标准"} else ("hybrid" if level in {"基础", "轻量", "标准（按统一内存动态判断）"} else "cloud_first")
    return HardwareProfile(platform=platform.platform(), cpu=platform.processor() or "未知CPU", cpu_cores=cores, ram_gb=ram_gb, gpus=gpus, accelerator=accelerator, encoders=_detect_encoders(), local_ai_level=level, execution_mode=mode)


def format_hardware(profile: HardwareProfile | None = None) -> str:
    p = profile or detect_hardware()
    if not p.gpus:
        gpu_text = "未检测到独立GPU"
    else:
        gpu_text = "；".join(f"{g.name} {g.vram_mb}MB" if g.vram_mb else g.name for g in p.gpus)
    return f"{gpu_text} · 加速={p.accelerator} · 本地AI={p.local_ai_level} · 执行策略={p.execution_mode}"
