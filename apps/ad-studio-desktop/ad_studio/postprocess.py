from pathlib import Path
import shutil
import subprocess

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
    # 保持主体完整性的中心裁切；后续可由 AI 提供 crop_x/crop_y。
    vf = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}"
    codec = "h264_nvenc" if has_nvenc() else "libx264"
    _run([ffmpeg_path(), "-y", "-i", str(input_path), "-vf", vf, "-c:v", codec, "-preset", "p4" if codec == "h264_nvenc" else "medium", "-pix_fmt", "yuv420p", "-an", str(output_path)])
    return output_path

def process_shot(input_path: Path, output_path: Path, aspect: str = "9:16", speed: float = 1.0):
    if speed <= 0:
        raise ValueError("速度必须大于 0")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    width, height = ASPECTS.get(aspect, ASPECTS["9:16"])
    vf = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}"
    if speed != 1.0:
        vf += f",setpts={1.0/speed}*PTS"
    codec = "h264_nvenc" if has_nvenc() else "libx264"
    _run([ffmpeg_path(), "-y", "-i", str(input_path), "-vf", vf, "-c:v", codec, "-preset", "p4" if codec == "h264_nvenc" else "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", str(output_path)])
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

def burn_subtitles(input_path: Path, output_path: Path, srt_path: Path):
    if not srt_path.exists():
        raise RuntimeError("字幕文件不存在")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subtitle = str(srt_path).replace("\\", "/").replace(":", "\\:")
    codec = "h264_nvenc" if has_nvenc() else "libx264"
    _run([ffmpeg_path(), "-y", "-i", str(input_path), "-vf", f"subtitles='{subtitle}'", "-c:v", codec, "-pix_fmt", "yuv420p", "-c:a", "copy", str(output_path)])
    return output_path

def probe_duration(input_path: Path):
    result = _run([shutil.which("ffprobe") or "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(input_path)])
    return float(result.stdout.strip())
