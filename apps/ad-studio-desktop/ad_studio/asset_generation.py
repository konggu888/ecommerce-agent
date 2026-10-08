from pathlib import Path
import json
import base64
import urllib.request
from dataclasses import dataclass
from .models import Asset, uid
from .capability import CapabilityRouter
from .providers import GenericAssetProvider, GenerationRequest

@dataclass
class AssetGenerationResult:
    asset: Asset
    cost_rmb: float
    provider: str
    source: str = "cloud"   # 'local' / 'cloud'


class LocalAssetBackend:
    """本地图像生成后端（默认适配 Stable Diffusion WebUI /sdapi/v1/txt2img）。

    只要本机跑着 SD WebUI（或兼容 /sdapi/v1/txt2img 的服务）且硬件能承担推理，
    系统会优先用本地能力生成素材，不产生云端费用。其它本地服务协议需要
    对应适配器，未适配时返回真实错误，不会伪装成已生成。
    """

    def __init__(self, endpoint: str):
        self.endpoint = endpoint.rstrip("/")
        self.cost_per_asset_rmb = 0.0

    def generate_asset(self, prompt: str, output: Path, width: int = 1024, height: int = 1024, steps: int = 24) -> Path:
        url = self.endpoint + "/sdapi/v1/txt2img"
        payload = {"prompt": prompt, "steps": steps, "width": width, "height": height}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            raise RuntimeError(f"本地素材生成失败（{url}）：{exc}") from exc
        images = body.get("images") or []
        if not images:
            raise RuntimeError(f"本地素材生成返回为空（{url}）")
        raw = images[0]
        if isinstance(raw, str):
            if raw.startswith("data:image"):
                raw = raw.split(",", 1)[-1]
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(base64.b64decode(raw))
        else:
            raise RuntimeError("本地素材生成返回了不支持的图片格式")
        return output


class AssetGenerator:
    """本地/云端素材生成：电脑有能力（本地服务可达）就用本地，否则交云端 REST。"""

    def __init__(self, config_path: Path, library_root: Path, capability: CapabilityRouter | None = None):
        self.config_path = config_path
        self.library_root = library_root
        self.config = self._load()
        self.capability = capability or CapabilityRouter(config_path.parent)

    def _load(self):
        if not self.config_path.exists():
            return {}
        try:
            return json.loads(self.config_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _cfg(self, kind):
        return self.config.get(kind) or self.config.get("asset_generation") or {}

    def _is_local(self, cfg):
        e = (cfg.get("endpoint") or "").strip().lower()
        return cfg.get("local") is True or "127.0.0.1" in e or "localhost" in e

    def configured(self, kind):
        """本地端点不要求 API Key；远程端点必须带 Key 才算已配置。"""
        cfg = self._cfg(kind)
        if not cfg.get("endpoint"):
            return False
        return bool(cfg.get("api_key")) or self._is_local(cfg)

    def price(self, kind):
        try:
            return float(self._cfg(kind).get("price_rmb", 0.0))
        except Exception:
            return 0.0

    def generate(self, kind, name, prompt, tags=None, request_id=""):
        cfg = self._cfg(kind)
        if not cfg.get("endpoint"):
            raise RuntimeError(f"未配置{kind}自动生成服务（本地或云端）")
        decision = self.capability.decide_asset(kind)
        if decision.target == "local":
            return self._local_generate(kind, name, prompt, tags or [], cfg)
        if decision.target == "cloud":
            return self._cloud_generate(kind, name, prompt, tags or [], cfg)
        raise RuntimeError(f"{kind}自动生成服务不可用：{decision.reason}")

    def _asset_path(self, kind, filename):
        folder = self.library_root / "assets" / kind
        folder.mkdir(parents=True, exist_ok=True)
        return folder / filename

    def _local_generate(self, kind, name, prompt, tags, cfg):
        endpoint = (cfg.get("endpoint") or "").strip()
        aid = uid("asset")
        out = self._asset_path(kind, aid + ".png")
        LocalAssetBackend(endpoint).generate_asset(prompt, out)
        asset = Asset(aid, name, kind, "ai_generated", str(out), tags)
        return AssetGenerationResult(asset=asset, cost_rmb=0.0, provider="本地图像服务", source="local")

    def _cloud_generate(self, kind, name, prompt, tags, cfg):
        endpoint = (cfg.get("endpoint") or "").strip()
        api_key = cfg.get("api_key") or ""
        model = cfg.get("model") or ""
        aid = uid("asset")
        out = self._asset_path(kind, aid + ".png")
        provider = GenericAssetProvider(
            endpoint=endpoint,
            api_key=api_key,
            model=model,
            cost_per_asset_rmb=self.price(kind),
            provider_name=cfg.get("provider") or "Generic Asset REST",
        )
        provider.generate_asset(GenerationRequest(prompt=prompt, output=out, reference_assets=[]))
        asset = Asset(aid, name, kind, "ai_generated", str(out), tags)
        return AssetGenerationResult(asset=asset, cost_rmb=self.price(kind), provider=provider.provider_name, source="cloud")
