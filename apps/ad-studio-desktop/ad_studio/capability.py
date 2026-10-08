"""本地/云端能力调度：统一决定 LLM、素材生成、视频生成走本地还是云端。

原则：电脑有什么能力就用什么能力，做不了的再交给云端。
- LLM：本地 OpenAI 兼容服务（Ollama/vLLM/LM Studio 等）已在模型池启用 → 本地；
  否则云端模型有 API Key → 云端；硬件策略为云端优先时优先云端。
- 素材生成：本地图像服务（SD WebUI/ComfyUI 等）可达且硬件不要求云端优先 → 本地；
  否则云端 REST 适配器已配置 → 云端。
- 视频生成：本地视频服务可达且硬件不要求云端优先 → 本地；
  否则云端视频 Provider 已配置 → 云端。

本地端点识别：endpoint 指向 127.0.0.1 / localhost，或配置项 local=true；
也可通过 config.json 的 local_capability 提供默认探测端点（如 SD WebUI 7860、ComfyUI 8188）。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
import json
import urllib.request

from .hardware import HardwareProfile, detect_hardware


@dataclass
class ExecutionDecision:
    task: str              # 'llm' / 'asset' / 'video'
    target: str            # 'local' / 'cloud' / 'unavailable'
    reason: str            # 人类可读的决策依据
    endpoint: str = ""     # 实际要调用的端点
    mode: str = ""         # hardware execution_mode 快照

    def to_dict(self) -> dict[str, Any]:
        return {
            "task": self.task, "target": self.target, "reason": self.reason,
            "endpoint": self.endpoint, "mode": self.mode,
        }


def probe_http(url: str, timeout: float = 0.8) -> bool:
    """轻量探测 HTTP 服务是否可达；任何失败都返回 False，不抛异常。"""
    if not url:
        return False
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status < 500
    except Exception:
        return False


def is_local_endpoint(endpoint: str) -> bool:
    """端点指向本机（127.0.0.1 / localhost / 0.0.0.0）即视为本地服务。"""
    e = (endpoint or "").strip().lower()
    return e.startswith("local:") or "127.0.0.1" in e or "localhost" in e or "://0.0.0.0" in e


class CapabilityRouter:
    """以硬件画像 + 本机配置为输入，输出各生成层的执行目标。"""

    def __init__(
        self,
        config_root: Path,
        hardware: HardwareProfile | None = None,
        probe: Callable[[str], bool] | None = None,
    ):
        self.root = Path(config_root)
        self._hardware = hardware
        self._probe = probe or probe_http

    @property
    def hardware(self) -> HardwareProfile:
        # 惰性探测：只有真正需要决策时才跑硬件检测，避免每次构造都执行子进程。
        if self._hardware is None:
            self._hardware = detect_hardware()
        return self._hardware

    # ---- 配置读取（全部容错，缺文件按未配置处理） ----
    def _read_json(self, name: str) -> dict[str, Any]:
        p = self.root / name
        if not p.exists():
            return {}
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _config(self) -> dict[str, Any]:
        return self._read_json("config.json")

    def _hint(self, key: str) -> str:
        d = self._config()
        cap = d.get("local_capability", {}) if isinstance(d, dict) else {}
        return str(cap.get(key, "") or "").strip()

    def _model_config(self) -> dict[str, Any]:
        return self._read_json("model-config.json")

    def _video_config(self) -> dict[str, Any]:
        d = self._read_json("video-provider.json")
        if isinstance(d, dict):
            vp = d.get("video_provider", d)
            return vp if isinstance(vp, dict) else {}
        return {}

    def _asset_config(self, kind: str) -> dict[str, Any]:
        d = self._read_json("asset-generation.json")
        if not isinstance(d, dict):
            return {}
        return d.get(kind, {}) or {}

    # ---- 能力就绪判断 ----
    def local_llm_model(self) -> str:
        """第一个已启用且 provider=local_openai 的本地模型 id；没有返回空串。"""
        for m in self._model_config().get("models", []):
            if m.get("enabled", True) and m.get("provider") == "local_openai":
                return m.get("id", "")
        return ""

    def cloud_llm_ready(self) -> bool:
        for m in self._model_config().get("models", []):
            if m.get("enabled", True) and m.get("provider") != "local_openai" and m.get("api_key"):
                return True
        return False

    def _local_endpoint_candidate(self, cfg: dict[str, Any], hint_key: str) -> str:
        return (cfg.get("endpoint") or "").strip() or self._hint(hint_key)

    def _local_service_ready(self, cfg: dict[str, Any], hint_key: str) -> tuple[bool, str]:
        """返回 (是否可达, 端点)。端点未指向本机时不视为本地服务。"""
        ep = self._local_endpoint_candidate(cfg, hint_key)
        if not ep or not is_local_endpoint(ep):
            return False, ep
        return bool(self._probe(ep)), ep

    def _cloud_service_ready(self, cfg: dict[str, Any]) -> bool:
        ep = (cfg.get("endpoint") or "").strip()
        if not ep or is_local_endpoint(ep):
            return False
        return bool(cfg.get("api_key"))

    # ---- 决策 ----
    def decide_llm(self) -> ExecutionDecision:
        local_id = self.local_llm_model()
        cloud = self.cloud_llm_ready()
        mode = self.hardware.execution_mode
        if mode == "cloud_first" and cloud:
            return ExecutionDecision("llm", "cloud", "硬件策略为云端优先，且云端模型已配置可用", mode=mode)
        if local_id:
            return ExecutionDecision("llm", "local", f"检测到本地模型 {local_id}，本地执行", mode=mode)
        if cloud:
            return ExecutionDecision("llm", "cloud", "没有可用本地模型，改用云端模型", mode=mode)
        return ExecutionDecision("llm", "unavailable", "本地模型与云端模型均未配置", mode=mode)

    def decide_asset(self, kind: str) -> ExecutionDecision:
        cfg = self._asset_config(kind)
        mode = self.hardware.execution_mode
        ok, ep = self._local_service_ready(cfg, "asset_endpoint")
        if ok and mode != "cloud_first":
            return ExecutionDecision("asset", "local", f"本地{kind}生成服务可达（{ep}）", ep, mode)
        if self._cloud_service_ready(cfg):
            return ExecutionDecision("asset", "cloud", f"本地{kind}服务不可用或未配置，转云端", cfg.get("endpoint", ""), mode)
        return ExecutionDecision("asset", "unavailable", f"{kind}生成服务未配置（本地与云端均不可用）", mode=mode)

    def decide_video(self) -> ExecutionDecision:
        cfg = self._video_config()
        mode = self.hardware.execution_mode
        ok, ep = self._local_service_ready(cfg, "video_endpoint")
        if ok and mode != "cloud_first":
            return ExecutionDecision("video", "local", f"本地视频生成服务可达（{ep}）", ep, mode)
        if self._cloud_service_ready(cfg):
            return ExecutionDecision("video", "cloud", "本地视频服务不可用或未配置，转云端", cfg.get("endpoint", ""), mode)
        return ExecutionDecision("video", "unavailable", "视频生成服务未配置（本地与云端均不可用）", mode=mode)

    def snapshot(self) -> list[dict[str, Any]]:
        """供 UI 展示的三行能力调度摘要。"""
        return [
            self.decide_llm().to_dict(),
            self.decide_asset("演员").to_dict(),
            self.decide_video().to_dict(),
        ]
