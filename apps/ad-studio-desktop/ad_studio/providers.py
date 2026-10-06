from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, Any
import json
import urllib.request
import urllib.error
import time

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
    status_endpoint: str = ''
    poll_interval: float = 3.0
    task_id_field: str = 'id'
    status_field: str = 'status'

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

    def _find_task_id(self, body: dict[str, Any]) -> str:
        data = body.get('data')
        candidates = [body.get(self.task_id_field), body.get('task_id'), body.get('id'),
                      data.get(self.task_id_field) if isinstance(data, dict) else None,
                      data.get('task_id') if isinstance(data, dict) else None,
                      data.get('id') if isinstance(data, dict) else None]
        for value in candidates:
            if value is not None and str(value).strip():
                return str(value)
        raise RuntimeError('Provider 返回异步响应，但没有找到任务 ID。')

    def _status(self, task_id: str) -> dict[str, Any]:
        endpoint = self.status_endpoint.strip().replace('{task_id}', task_id)
        if not endpoint:
            raise RuntimeError('Provider 返回任务 ID，但未配置 status_endpoint。')
        headers = {'Content-Type': 'application/json', **self.headers}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        req = urllib.request.Request(endpoint, headers=headers, method='GET')
        try:
            with urllib.request.urlopen(req, timeout=min(self.timeout, 60)) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as exc:
            raise RuntimeError(f'查询视频任务失败：{exc}') from exc

    @staticmethod
    def _status_value(body: dict[str, Any], field: str) -> str:
        data = body.get('data')
        value = body.get(field)
        if value is None and isinstance(data, dict):
            value = data.get(field)
        return str(value or '').lower().strip()

    def _download(self, url: str, output: Path) -> Path:
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as response:
                output.write_bytes(response.read())
        except Exception as exc:
            raise RuntimeError(f'视频文件下载失败：{exc}') from exc
        if output.stat().st_size == 0:
            raise RuntimeError('下载后的视频文件为空。')
        return output

    def generate(self, request: GenerationRequest) -> Path:
        if not self.configured():
            raise RuntimeError('云端视频 Provider 尚未配置 endpoint/API Key。')
        payload = {'model': self.model, 'prompt': request.prompt, 'duration': request.duration}
        if request.reference_assets:
            payload['reference_assets'] = request.reference_assets
        body = self._request(payload)
        try:
            url = self._find_url(body)
            return self._download(url, request.output)
        except RuntimeError:
            task_id = self._find_task_id(body)
            if not self.status_endpoint:
                raise RuntimeError('Provider 返回异步任务，但未配置 status_endpoint；请在视频生成设置中填写任务查询地址。')
            deadline = time.time() + self.timeout
            while time.time() < deadline:
                status = self._status(task_id)
                value = self._status_value(status, self.status_field)
                if value in {'succeeded','success','completed','complete','done','finished'}:
                    url = self._find_url(status)
                    return self._download(url, request.output)
                if value in {'failed','failure','error','cancelled','canceled'}:
                    data = status.get('data')
                    detail = status.get('error') or (data.get('error') if isinstance(data, dict) else None) or value
                    raise RuntimeError(f'视频任务失败：{detail}')
                time.sleep(max(0.5, self.poll_interval))
            raise RuntimeError(f'视频任务 {task_id} 超时（>{self.timeout}秒）。')

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
    provider = GenericVideoProvider(endpoint=str(data.get('endpoint', '')), api_key=str(data.get('api_key', '')), model=str(data.get('model', '')), timeout=int(data.get('timeout', 300) or 300), headers=dict(data.get('headers', {}) or {}), status_endpoint=str(data.get('status_endpoint','')), poll_interval=float(data.get('poll_interval',3) or 3), task_id_field=str(data.get('task_id_field','id') or 'id'), status_field=str(data.get('status_field','status') or 'status'))
    return provider if provider.configured() else UnconfiguredProvider()
