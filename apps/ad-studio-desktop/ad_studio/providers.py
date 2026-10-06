from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, Any
import json
import urllib.request
import urllib.error

@dataclass
class GenerationRequest:
    prompt: str
    output: Path
    duration: float = 3
    reference_assets: list[str] = field(default_factory=list)

class ImageGenerator(Protocol):
    def generate(self, request: GenerationRequest) -> Path: ...
class VideoGenerator(Protocol):
    def generate(self, request: GenerationRequest) -> Path: ...
class VoiceGenerator(Protocol):
    def generate(self, text: str, output: Path) -> Path: ...
class SmallLLM(Protocol):
    def complete(self, prompt: str) -> str: ...

class UnconfiguredProvider:
    def generate(self, *args, **kwargs):
        raise RuntimeError('尚未配置云端生成器。请在设置中接入图像/视频/配音供应商。')
    def complete(self, *args, **kwargs):
        raise RuntimeError('尚未配置本地或云端小模型。')

@dataclass
class GenericVideoProvider:
    """可配置的 REST 视频生成适配器；不假定不同供应商 API 相同。"""
    endpoint: str
    api_key: str = ''
    model: str = ''
    timeout: int = 300
    headers: dict[str, str] = field(default_factory=dict)

    def configured(self) -> bool:
        return bool(self.endpoint.strip() and self.api_key.strip())

    def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {'Content-Type': 'application/json', **self.headers}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        req = urllib.request.Request(self.endpoint, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode('utf-8', errors='replace')[:1000]
            raise RuntimeError(f'视频 Provider HTTP {exc.code}：{detail}') from exc
        except Exception as exc:
            raise RuntimeError(f'视频 Provider 请求失败：{exc}') from exc

    @staticmethod
    def _find_url(body: dict[str, Any]) -> str:
        data = body.get('data')
        candidates = [body.get('video_url'), body.get('url'), data.get('video_url') if isinstance(data, dict) else None, data.get('url') if isinstance(data, dict) else None]
        for value in candidates:
            if isinstance(value, str) and value.startswith(('http://', 'https://')):
                return value
        raise RuntimeError('Provider 已返回，但没有找到 video_url/url；请按供应商 API 响应格式配置适配器。')

    def generate(self, request: GenerationRequest) -> Path:
        if not self.configured():
            raise RuntimeError('云端视频 Provider 尚未配置 endpoint/API Key。')
        payload = {'model': self.model, 'prompt': request.prompt, 'duration': request.duration}
        if request.reference_assets:
            payload['reference_assets'] = request.reference_assets
        url = self._find_url(self._request(payload))
        request.output.parent.mkdir(parents=True, exist_ok=True)
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as response:
                request.output.write_bytes(response.read())
        except Exception as exc:
            raise RuntimeError(f'视频文件下载失败：{exc}') from exc
        if request.output.stat().st_size == 0:
            raise RuntimeError('下载后的视频文件为空。')
        return request.output

def load_video_provider(path: Path) -> GenericVideoProvider | UnconfiguredProvider:
    if not path.exists():
        return UnconfiguredProvider()
    try:
        cfg = json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return UnconfiguredProvider()
    data = cfg.get('video_provider', cfg)
    if not isinstance(data, dict):
        return UnconfiguredProvider()
    provider = GenericVideoProvider(endpoint=str(data.get('endpoint', '')), api_key=str(data.get('api_key', '')), model=str(data.get('model', '')), timeout=int(data.get('timeout', 300) or 300), headers=dict(data.get('headers', {}) or {}))
    return provider if provider.configured() else UnconfiguredProvider()
