from pathlib import Path
import shutil, subprocess

from .hardware import detect_hardware


def which(name): return shutil.which(name)
def available(): return bool(which('ffmpeg')) and bool(which('ffprobe'))


def available_encoders():
    if not which('ffmpeg'):
        return []
    try:
        p=subprocess.run(['ffmpeg','-hide_banner','-encoders'],capture_output=True,text=True,timeout=10)
        text=p.stdout
        known=['h264_nvenc','hevc_nvenc','h264_amf','hevc_amf','h264_qsv','hevc_qsv','h264_videotoolbox','hevc_videotoolbox']
        return [x for x in known if x in text]
    except Exception:
        return []


def best_h264_encoder():
    encoders=available_encoders()
    profile=detect_hardware()
    preferred={
        'CUDA':['h264_nvenc'],
        'ROCm':['h264_amf'],
        'Metal':['h264_videotoolbox'],
    }.get(profile.accelerator, [])
    for codec in preferred:
        if codec in encoders:
            return codec
    for codec in ['h264_qsv','h264_nvenc','h264_amf','h264_videotoolbox']:
        if codec in encoders:
            return codec
    return 'libx264'


def has_nvenc():
    return 'h264_nvenc' in available_encoders()


def make_clip(output:Path,duration=3,width=1080,height=1920):
    output.parent.mkdir(parents=True,exist_ok=True)
    if not which('ffmpeg'): raise RuntimeError('未找到 FFmpeg，请安装 FFmpeg 并加入 PATH')
    codec=best_h264_encoder()
    cmd=['ffmpeg','-y','-f','lavfi','-i',f'color=c=black:s={width}x{height}:r=30','-t',str(duration),'-c:v',codec,'-pix_fmt','yuv420p',str(output)]
    subprocess.run(cmd,check=True,capture_output=True,text=True)
    return output


def concat(clips:list[Path],output:Path):
    if not clips: raise ValueError('没有可拼接的镜头')
    if not which('ffmpeg'): raise RuntimeError('未找到 FFmpeg，请安装 FFmpeg 并加入 PATH')
    output.parent.mkdir(parents=True,exist_ok=True); manifest=output.with_suffix('.txt')
    manifest.write_text('\n'.join("file '"+str(p.resolve()).replace("'","'\\''")+"'") for p in clips),encoding='utf-8')
    subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(manifest),'-c','copy',str(output)],check=True,capture_output=True,text=True)
    return output
