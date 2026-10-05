from pathlib import Path
import shutil, subprocess

def which(name): return shutil.which(name)
def available(): return bool(which('ffmpeg')) and bool(which('ffprobe'))
def has_nvenc():
    if not which('ffmpeg'): return False
    p=subprocess.run(['ffmpeg','-hide_banner','-encoders'],capture_output=True,text=True,timeout=10)
    return 'h264_nvenc' in p.stdout

def make_clip(output:Path,duration=3,width=1080,height=1920):
    output.parent.mkdir(parents=True,exist_ok=True)
    if not which('ffmpeg'): raise RuntimeError('未找到 FFmpeg，请安装 FFmpeg 并加入 PATH')
    codec='h264_nvenc' if has_nvenc() else 'libx264'
    cmd=['ffmpeg','-y','-f','lavfi','-i',f'color=c=black:s={width}x{height}:r=30','-t',str(duration),'-c:v',codec,'-pix_fmt','yuv420p',str(output)]
    subprocess.run(cmd,check=True,capture_output=True,text=True)
    return output

def concat(clips:list[Path],output:Path):
    if not clips: raise ValueError('没有可拼接的镜头')
    if not which('ffmpeg'): raise RuntimeError('未找到 FFmpeg，请安装 FFmpeg 并加入 PATH')
    output.parent.mkdir(parents=True,exist_ok=True); manifest=output.with_suffix('.txt')
    manifest.write_text('\n'.join("file '"+str(p.resolve()).replace("'","'\\''")+"'" for p in clips),encoding='utf-8')
    subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(manifest),'-c','copy',str(output)],check=True,capture_output=True,text=True)
    return output
