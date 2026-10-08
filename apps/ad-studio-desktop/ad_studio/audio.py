from pathlib import Path
import subprocess
import shutil

def _ffmpeg():
    p = shutil.which("ffmpeg")
    if not p:
        raise RuntimeError("未找到 FFmpeg")
    return p

def make_silence(output: Path, duration=3):
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        _ffmpeg(), "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-t", str(duration), "-c:a", "aac", "-b:a", "128k", str(output)
    ], check=True, capture_output=True)
    return output

def mix_voice_bgm(voice: Path, bgm: Path, output: Path):
    """保留人声主体，先做轻度降噪，再以较低音量混入循环背景音乐。"""
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        _ffmpeg(), "-y", "-i", str(voice), "-stream_loop", "-1", "-i", str(bgm),
        "-filter_complex",
        "[0:a]highpass=f=80,lowpass=f=12000,afftdn=nr=10:nf=-25,volume=1.0[voice];"
        "[1:a]volume=0.12[bg];"
        "[voice][bg]amix=inputs=2:duration=first:dropout_transition=2,"
        "alimiter=limit=0.95:level=disabled[a]",
        "-map", "[a]", "-c:a", "aac", "-b:a", "192k", str(output)
    ], check=True, capture_output=True)
    return output

def normalize_voice(voice: Path, output: Path):
    """仅处理原始人声：轻度降噪并做响度归一，避免背景音乐掩盖口播。"""
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        _ffmpeg(), "-y", "-i", str(voice),
        "-af", "highpass=f=80,lowpass=f=12000,afftdn=nr=10:nf=-25,"
               "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:a", "aac", "-b:a", "192k", str(output)
    ], check=True, capture_output=True)
    return output
