"""兼容入口：GPU 信息现在由通用硬件能力引擎提供。"""

from .hardware import detect_hardware


def detect_gpu():
    """保留旧调用接口，避免旧代码失效；不再把任何显卡型号当作系统门槛。"""
    profile = detect_hardware()
    primary = profile.gpus[0] if profile.gpus else None
    return {
        "available": bool(profile.gpus),
        "name": primary.name if primary else "未检测到GPU",
        "vram_mb": primary.vram_mb if primary else 0,
        "driver": primary.driver if primary else "",
        "vendor": primary.vendor if primary else "",
        "backend": profile.accelerator,
        "mode": profile.execution_mode,
        "local_ai_level": profile.local_ai_level,
        "encoders": profile.encoders,
        "hardware": profile.to_dict(),
    }
