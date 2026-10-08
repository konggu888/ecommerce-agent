from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import shutil
import subprocess
import urllib.request
import urllib.error


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass
class Transcript:
    text: str
    segments: list[TranscriptSegment]


def extract_audio(video: Path, output: Path) -> Path:
    """把实拍视频音轨抽成 16kHz 单声道 WAV，便于转写。"""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("未找到 FFmpeg，无法提取口播音频。")
    video = Path(video)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg, "-y", "-i", str(video), "-vn",
        "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(output),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=180)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"提取口播音频失败：{video.name}：{exc.stderr[-300:]}") from exc
    return output


def transcribe_openai_compatible(
    audio: Path,
    endpoint: str,
    api_key: str,
    model: str,
    timeout: int = 180,
) -> Transcript:
    """调用常见 OpenAI-compatible /audio/transcriptions 接口。

    使用 multipart/form-data，要求服务端至少支持 file/model/response_format。
    若服务端支持 verbose_json，则会尽量保留 segment 时间戳。
    """
    if not endpoint.strip():
        raise RuntimeError("未配置语音转写 endpoint。")
    if not api_key.strip():
        raise RuntimeError("未配置语音转写 API Key。")
    audio = Path(audio)
    if not audio.exists():
        raise RuntimeError(f"音频文件不存在：{audio}")

    boundary = "----AdStudioTranscriptBoundary7MA4YWxkTrZu0gW"
    body = bytearray()

    def field(name: str, value: str) -> None:
        body.extend(
            (
                f"--{boundary}\r\n"
                f"Content-Disposition: form-data; name=\"{name}\"\r\n\r\n"
                f"{value}\r\n"
            ).encode()
        )

    field("model", model)
    field("response_format", "verbose_json")
    field("timestamp_granularities[]", "segment")
    raw = audio.read_bytes()
    body.extend(
        (
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"file\"; filename=\"{audio.name}\"\r\n"
            "Content-Type: audio/wav\r\n\r\n"
        ).encode()
    )
    body.extend(raw)
    body.extend(f"\r\n--{boundary}--\r\n".encode())

    req = urllib.request.Request(
        endpoint,
        data=bytes(body),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:800]
        raise RuntimeError(f"语音转写接口 HTTP {exc.code}：{detail}") from exc
    except Exception as exc:
        raise RuntimeError(f"语音转写请求失败：{exc}") from exc

    text = str(data.get("text", "") or "").strip()
    segments = []
    for item in data.get("segments", []) or []:
        try:
            start = float(item.get("start", 0) or 0)
            end = float(item.get("end", start) or start)
            value = str(item.get("text", "") or "").strip()
            if value:
                segments.append(TranscriptSegment(start, end, value))
        except (TypeError, ValueError):
            continue
    return Transcript(text=text, segments=segments)
