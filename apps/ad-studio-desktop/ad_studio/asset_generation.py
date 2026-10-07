from pathlib import Path
import json
from dataclasses import dataclass
from .models import Asset, uid

@dataclass
class AssetGenerationResult:
    asset: Asset
    cost_rmb: float
    provider: str

class AssetGenerator:
    """通用云端素材生成适配层；供应商由本地配置决定，不绑定单一平台。"""
    def __init__(self, config_path: Path, library_root: Path):
        self.config_path=config_path
        self.library_root=library_root
        self.config=self._load()

    def _load(self):
        if not self.config_path.exists(): return {}
        try: return json.loads(self.config_path.read_text(encoding="utf-8"))
        except Exception: return {}

    def _cfg(self, kind):
        return self.config.get(kind) or self.config.get("asset_generation") or {}

    def configured(self, kind):
        cfg=self._cfg(kind)
        return bool(cfg.get("endpoint") and cfg.get("api_key"))

    def price(self, kind):
        try: return float(self._cfg(kind).get("price_rmb",0.0))
        except Exception: return 0.0

    def generate(self, kind, name, prompt, tags=None, request_id=""):
        cfg=self._cfg(kind)
        if not cfg.get("endpoint") or not cfg.get("api_key"):
            raise RuntimeError(f"未配置{kind}自动生成服务")
        # 供应商协议不同，具体 HTTP 调用由后续 provider adapter 实现。
        raise RuntimeError("已配置素材生成入口，但当前供应商协议尚未适配")
