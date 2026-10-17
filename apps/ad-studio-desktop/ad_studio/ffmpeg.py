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
    manifest.write_text('\n'.join("file '"+str(p.resolve()).replace("'","'\\''")+"'" for p in clips),encoding='utf-8')
    subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(manifest),'-c','copy',str(output)],check=True,capture_output=True,text=True)
    return output


def _probe_clip(path: Path):
    """Return duration and audio-stream presence for transition-safe assembly."""
    if not which('ffprobe'):
        raise RuntimeError('未找到 FFprobe，无法计算镜头转场时间')
    meta = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type', '-of', 'json', str(path)], check=True, capture_output=True, text=True)
    import json
    data = json.loads(meta.stdout or '{}')
    duration = float((data.get('format') or {}).get('duration') or 0)
    if duration <= 0:
        raise RuntimeError(f'无法读取有效镜头时长：{path}')
    return duration, any(stream.get('codec_type') == 'audio' for stream in data.get('streams', []))


def concat_with_transitions(clips: list[Path], output: Path, transitions: list[str], aspect: str = '9:16', transition_seconds: float = 0.35):
    """Build actual adjacent xfade/acrossfade transitions; transitions[i] enters clip i."""
    profiles = {'9:16': (1080, 1920), '16:9': (1920, 1080), '1:1': (1080, 1080)}
    if aspect not in profiles:
        raise ValueError(f'不支持的画幅：{aspect}')
    if not clips:
        raise ValueError('没有可拼接的镜头')
    if len(clips) != len(transitions):
        raise ValueError('镜头与转场配置数量不一致')
    if not which('ffmpeg'):
        raise RuntimeError('未找到 FFmpeg，请安装 FFmpeg 并加入 PATH')
    output.parent.mkdir(parents=True, exist_ok=True)
    if len(clips) == 1:
        return concat(clips, output)
    probed = [_probe_clip(Path(clip)) for clip in clips]
    durations = [row[0] for row in probed]
    overlaps = [0.0]
    for i in range(1, len(clips)):
        if transitions[i] == '交叉溶解':
            overlaps.append(min(transition_seconds, durations[i - 1] * 0.4, durations[i] * 0.4))
        else:
            overlaps.append(0.001)
    width, height = profiles[aspect]
    filters = []
    for i, (duration, has_audio) in enumerate(probed):
        filters.append(f'[{i}:v]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},fps=30,settb=AVTB,setpts=PTS-STARTPTS,format=yuv420p[v{i}]')
        if has_audio:
            filters.append(f'[{i}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,asetpts=PTS-STARTPTS[a{i}]')
        else:
            filters.append(f'anullsrc=channel_layout=stereo:sample_rate=48000,atrim=duration={duration:.6f},asetpts=PTS-STARTPTS[a{i}]')
    v, a = 'v0', 'a0'
    for i in range(1, len(clips)):
        overlap = overlaps[i]
        offset = sum(durations[:i]) - sum(overlaps[1:i + 1])
        nv, na = f'vx{i}', f'ax{i}'
        filters.append(f'[{v}][v{i}]xfade=transition=fade:duration={overlap:.6f}:offset={offset:.6f}[{nv}]')
        filters.append(f'[{a}][a{i}]acrossfade=d={overlap:.6f}:c1=tri:c2=tri[{na}]')
        v, a = nv, na
    cmd = [which('ffmpeg'), '-y']
    for clip in clips:
        cmd.extend(['-i', str(clip)])
    cmd.extend(['-filter_complex', ';'.join(filters), '-map', f'[{v}]', '-map', f'[{a}]', '-c:v', best_h264_encoder(), '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(output)])
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return output
