from pathlib import Path
import math
import shutil
import subprocess

from .ffmpeg import best_h264_encoder

ASPECTS = {
    "9:16": (1080, 1920),
    "1:1": (1080, 1080),
    "16:9": (1920, 1080),
}

def ffmpeg_path():
    path = shutil.which("ffmpeg")
    if not path:
        raise RuntimeError("未找到 FFmpeg")
    return path

def _run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)

def has_nvenc():
    try:
        out = subprocess.run([ffmpeg_path(), "-hide_banner", "-encoders"], capture_output=True, text=True, timeout=10)
        return "h264_nvenc" in out.stdout
    except Exception:
        return False

def adapt_aspect(input_path: Path, output_path: Path, aspect: str = "9:16"):
    if aspect not in ASPECTS:
        raise ValueError(f"不支持的画幅：{aspect}")
    width, height = ASPECTS[aspect]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # 独立画幅适配采用中心裁切；需要执行 AI 焦点构图时使用 process_shot。
    vf = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}:x=(iw-{width})*0.5:y=(ih-{height})*0.5"
    codec = best_h264_encoder()
    _run([ffmpeg_path(), "-y", "-i", str(input_path), "-vf", vf, "-c:v", codec, "-preset", "p4" if codec == "h264_nvenc" else "medium", "-pix_fmt", "yuv420p", "-an", str(output_path)])
    return output_path

def _normalized_focus(value: float) -> float:
    """Return a safe normalized focal coordinate; invalid values use center."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.5
    if not math.isfinite(number):
        return 0.5
    return min(1.0, max(0.0, number))


def _focus_crop_filter(width: int, height: int, focus_x: float, focus_y: float) -> str:
    """Keep the normalized focal point near the crop center, clamped to image bounds.

    Coordinates describe the subject/focal point in the scaled source frame, not the
    crop-window offset. When there is insufficient overflow in an axis, the crop
    necessarily stays at zero on that axis.
    """
    x = _normalized_focus(focus_x)
    y = _normalized_focus(focus_y)
    crop_x = f"max(0,min(iw-{width},iw*{x:.6f}-{width}/2))"
    crop_y = f"max(0,min(ih-{height},ih*{y:.6f}-{height}/2))"
    return (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height}:x='{crop_x}':y='{crop_y}'"
    )


def process_shot(input_path: Path, output_path: Path, aspect: str = "9:16", speed: float = 1.0, focus_x: float = 0.5, focus_y: float = 0.5, transition: str = "硬切"):
    if speed <= 0:
        raise ValueError("速度必须大于 0")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    width, height = ASPECTS.get(aspect, ASPECTS["9:16"])
    vf = _focus_crop_filter(width, height, focus_x, focus_y)
    if speed != 1.0:
        vf += f",setpts={1.0/speed}*PTS"
    if transition == "淡入":
        vf += ",fade=t=in:st=0:d=0.25"
    elif transition == "淡出":
        # Fade-out must occur at the END of the processed clip, not at its start.
        # setpts above changes the output duration, so scale the probed input duration
        # by the selected playback speed before calculating the fade window.
        output_duration = probe_duration(input_path) / speed
        if not math.isfinite(output_duration) or output_duration <= 0:
            raise RuntimeError("无法确定有效镜头时长，不能执行淡出")
        fade_duration = min(0.25, output_duration)
        fade_start = max(0.0, output_duration - fade_duration)
        vf += f",fade=t=out:st={fade_start:.3f}:d={fade_duration:.3f}"
    codec = best_h264_encoder()
    cmd = [ffmpeg_path(), "-y", "-i", str(input_path), "-vf", vf]
    if speed != 1.0:
        # Keep original audio aligned with setpts-adjusted video duration.
        cmd.extend(["-af", f"atempo={speed:.6f}"])
    cmd.extend(["-c:v", codec, "-preset", "p4" if codec == "h264_nvenc" else "medium",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", str(output_path)])
    _run(cmd)
    return output_path

def mix_audio(input_path: Path, output_path: Path, bgm_path: Path | None = None, bgm_volume: float = 0.16):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not bgm_path:
        _run([ffmpeg_path(), "-y", "-i", str(input_path), "-af", "highpass=f=70,lowpass=f=14000", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", str(output_path)])
        return output_path
    _run([
        ffmpeg_path(), "-y", "-i", str(input_path), "-stream_loop", "-1", "-i", str(bgm_path),
        "-filter_complex", f"[0:a]highpass=f=70,lowpass=f=14000[voice];[1:a]volume={bgm_volume}[bg];[voice][bg]amix=inputs=2:duration=first:dropout_transition=2[a]",
        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(output_path)
    ])
    return output_path

def burn_subtitles(input_path: Path, output_path: Path, srt_path: Path, position: str = "底部安全区", style: str = "白字黑边"):
    if not srt_path.exists():
        raise RuntimeError("字幕文件不存在")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subtitle = str(srt_path).replace("\\", "/").replace(":", "\\:")
    codec = "h264_nvenc" if has_nvenc() else "libx264"
    if position == "不显示":
        shutil.copy2(input_path, output_path); return output_path
    alignment = {"底部安全区": 2, "中部安全区": 5, "顶部安全区": 8}.get(position, 2)
    force_style = f"Alignment={alignment},MarginV=90,Outline=2,Shadow=0,FontSize=20"
    if style == "黄字黑边": force_style += ",PrimaryColour=&H00FFFF&"
    elif style == "简洁白字": force_style += ",Outline=0"
    vf = f"subtitles='{subtitle}':force_style='{force_style}'"
    _run([ffmpeg_path(), "-y", "-i", str(input_path), "-vf", vf, "-c:v", codec, "-pix_fmt", "yuv420p", "-c:a", "copy", str(output_path)])
    return output_path

def probe_duration(input_path: Path):
    result = _run([shutil.which("ffprobe") or "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(input_path)])
    return float(result.stdout.strip())
