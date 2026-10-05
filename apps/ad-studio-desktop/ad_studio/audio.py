from pathlib import Path
import subprocess, shutil

def _ffmpeg():
    p=shutil.which('ffmpeg')
    if not p: raise RuntimeError('未找到 FFmpeg')
    return p

def make_silence(output:Path,duration=3):
    output.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run([_ffmpeg(),'-y','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t',str(duration),'-c:a','aac','-b:a','128k',str(output)],check=True,capture_output=True)
    return output

def mix_voice_bgm(voice:Path,bgm:Path,output:Path):
    output.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run([_ffmpeg(),'-y','-i',str(voice),'-stream_loop','-1','-i',str(bgm),'-filter_complex','[1:a]volume=0.16[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2[a]','-map','[a]','-c:a','aac','-b:a','192k',str(output)],check=True,capture_output=True)
    return output
