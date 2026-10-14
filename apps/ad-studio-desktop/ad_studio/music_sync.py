"""Conservative beat-aware final editing helpers; local/offline only."""
from __future__ import annotations
import math, shutil, struct, subprocess
from pathlib import Path
from statistics import median


def detect_beats(samples: list[int], sample_rate: int, frame_ms: int = 50) -> dict:
    if sample_rate <= 0 or frame_ms <= 0 or not samples:
        return {"beats": [], "bpm": None, "confidence": 0.0, "reason": "音频样本无效"}
    frame_size=max(1, round(sample_rate*frame_ms/1000))
    energy=[]
    for start in range(0,len(samples),frame_size):
        frame=samples[start:start+frame_size]
        if frame: energy.append(math.sqrt(sum(float(x)*float(x) for x in frame)/len(frame)))
    if len(energy)<8 or max(energy,default=0.0)<=1.0:
        return {"beats":[],"bpm":None,"confidence":0.0,"reason":"音频过短或接近静音"}
    floor=median(energy); peak=max(energy); threshold=floor+max(peak-floor,1.0)*0.35
    candidates=[]
    for i in range(1,len(energy)-1):
        if energy[i]>=threshold and energy[i]>=energy[i-1] and energy[i]>energy[i+1]:
            t=(i*frame_size+frame_size/2)/sample_rate
            if not candidates or t-candidates[-1]>=0.25: candidates.append(t)
            elif energy[i]>energy[min(len(energy)-1,round(candidates[-1]*sample_rate/frame_size))]: candidates[-1]=t
    if len(candidates)<3:
        return {"beats":candidates,"bpm":None,"confidence":0.0,"reason":"节拍候选不足"}
    intervals=[b-a for a,b in zip(candidates,candidates[1:]) if b>a]
    if not intervals: return {"beats":candidates,"bpm":None,"confidence":0.0,"reason":"无法估计节拍间隔"}
    avg=sum(intervals)/len(intervals); variance=sum((x-avg)**2 for x in intervals)/len(intervals)
    cv=math.sqrt(variance)/avg if avg else 1.0
    regularity=max(0.0,min(1.0,1.0-cv)); contrast=max(0.0,min(1.0,(peak-floor)/max(peak,1.0)))
    confidence=round(min(1.0,len(candidates)/8.0)*(0.7*regularity+0.3*contrast),3)
    bpm=round(60.0/median(intervals),1) if median(intervals)>0 else None
    return {"beats":candidates,"bpm":bpm,"confidence":confidence,
            "reason":"检测到稳定候选" if confidence>=0.45 else "节拍置信度偏低，保留原切点"}


def analyze_music_file(path: Path) -> dict:
    path=Path(path)
    if not path.is_file() or path.stat().st_size<=0: raise RuntimeError(f"背景音乐文件不存在或为空：{path}")
    proc=subprocess.run([shutil.which("ffmpeg") or "ffmpeg","-v","error","-i",str(path),"-vn","-ac","1","-ar","11025","-f","s16le","pipe:1"],capture_output=True,check=True)
    usable=len(proc.stdout)-(len(proc.stdout)%2)
    if usable<=0: return {"beats":[],"bpm":None,"confidence":0.0,"reason":"无法解码有效音频"}
    samples=list(struct.unpack("<"+"h"*(usable//2),proc.stdout[:usable]))
    return detect_beats(samples,11025)




def derive_content_minimum_durations(shot_metadata: list[dict], durations: list[float]) -> dict:
    """Estimate conservative holds from dialogue, on-screen text, product role and CTA.

    This uses storyboard metadata only; it is not visual speech recognition or scene understanding.
    """
    protected = []
    for index, raw_duration in enumerate(durations):
        row = shot_metadata[index] if index < len(shot_metadata) and isinstance(shot_metadata[index], dict) else {}
        dialogue = str(row.get("dialogue") or row.get("script") or "")
        raw_text = row.get("on_screen_text") or []
        if isinstance(raw_text, str):
            text_items = [raw_text]
        elif isinstance(raw_text, (list, tuple)):
            text_items = [str(item) for item in raw_text if str(item).strip()]
        else:
            text_items = []
        dialogue_chars = sum(1 for char in dialogue if not char.isspace())
        on_screen_chars = sum(1 for value in text_items for char in value if not char.isspace())
        intent = row.get("editing_intent") if isinstance(row.get("editing_intent"), dict) else {}
        role = str(intent.get("role") or row.get("role") or "").strip().lower()
        content_text = " ".join(str(row.get(key) or "") for key in ("title", "objective", "visual", "generation_prompt"))
        product_requirements = row.get("product_asset_requirements") or row.get("product_asset_ids") or []
        if isinstance(product_requirements, str):
            product_requirements = [product_requirements] if product_requirements.strip() else []
        product_terms = ("商品", "产品", "特写", "材质", "接口", "规格", "细节", "功能展示", "使用演示", "操作步骤", "实测", "对比", "证据")
        product_hold = 2.0 if role in {"product_detail", "demonstration", "proof"} or product_requirements or any(term in content_text for term in product_terms) else 0.0
        cta_hold = 2.0 if str(row.get("cta_role") or "").strip() or role == "cta" else 0.0
        dialogue_hold = dialogue_chars / 4.5 + 0.35 if dialogue_chars else 0.0
        text_hold = on_screen_chars / 4.0 + 0.4 if on_screen_chars else 0.0
        minimum = max(0.8, dialogue_hold, text_hold, product_hold, cta_hold)
        protected.append({
            "shot_index": index + 1, "dialogue_chars": dialogue_chars,
            "on_screen_text_chars": on_screen_chars, "role": role or "未声明",
            "minimum_duration": round(minimum, 3),
            "basis": "分镜台词/屏幕文字/商品角色的保守时长估算；非视觉识别",
        })
    return {"minimum_durations": [item["minimum_duration"] for item in protected], "shots": protected}


def plan_beat_aligned_durations(durations:list[float], beat_times:list[float], confidence:float,
                                max_boundary_shift:float=0.25,max_shot_delta:float=0.25,
                                min_duration:float=0.8,min_confidence:float=0.45,allow_retime:bool=True,
                                minimum_durations:list[float]|None=None)->dict:
    try:
        original=[float(x) for x in durations]
        beats=sorted(float(x) for x in beat_times if math.isfinite(float(x)) and float(x)>=0)
        confidence=float(confidence)
    except (TypeError,ValueError):
        return {"durations":list(durations),"changed":False,"reason":"输入无效"}
    if not original or any(not math.isfinite(x) or x<=0 for x in original):
        return {"durations":list(durations),"changed":False,"reason":"镜头时长无效"}
    if not allow_retime:
        return {"durations":original,"changed":False,"reason":"含交叉溶解转场，当前保守保留原切点"}
    if minimum_durations is not None:
        try:
            protected = [float(value) for value in minimum_durations]
        except (TypeError, ValueError):
            return {"durations":original,"changed":False,"reason":"内容保护时长无效，保留原切点"}
        if len(protected) != len(original) or any(not math.isfinite(value) or value < min_duration for value in protected):
            return {"durations":original,"changed":False,"reason":"内容保护时长无效，保留原切点"}
        if any(old + 1e-9 < required for old, required in zip(original, protected)):
            return {"durations":original,"changed":False,"reason":"现有镜头时长已低于口播/字幕/商品展示保护需求，保留原切点"}
    else:
        protected = [min_duration] * len(original)
    if not math.isfinite(confidence) or confidence<min_confidence or not beats:
        return {"durations":original,"changed":False,"reason":"节拍置信度不足，保留原切点"}
    boundaries=[]; elapsed=0.0
    for duration in original[:-1]:
        elapsed+=duration; nearest=min(beats,key=lambda beat:abs(beat-elapsed),default=elapsed)
        boundaries.append(nearest if abs(nearest-elapsed)<=max_boundary_shift else elapsed)
    points=[0.0]+boundaries+[sum(original)]
    proposed=[points[i+1]-points[i] for i in range(len(original))]
    if any(not math.isfinite(x) or x<min_duration for x in proposed):
        return {"durations":original,"changed":False,"reason":"卡点会产生过短镜头，保留原切点"}
    if any(new + 1e-9 < required for new, required in zip(proposed, protected)):
        return {"durations":original,"changed":False,"reason":"节拍卡点会压缩口播/字幕/商品展示保护时长，保留原切点"}
    if any(abs(new-old)>max_shot_delta+1e-9 for new,old in zip(proposed,original)):
        return {"durations":original,"changed":False,"reason":"卡点调整超出安全范围，保留原切点"}
    if any(not 0.85<=old/new<=1.15 for old,new in zip(original,proposed)):
        return {"durations":original,"changed":False,"reason":"需要过度变速，保留原切点"}
    changed=any(abs(new-old)>0.015 for new,old in zip(proposed,original))
    return {"durations":proposed if changed else original,"changed":changed,
            "boundaries":points[1:-1] if changed else [sum(original[:i]) for i in range(1,len(original))],
            "reason":"切点已在安全范围内贴近音乐节拍" if changed else "现有切点已足够接近节拍"}


def _has_audio(path:Path)->bool:
    result=subprocess.run([shutil.which("ffprobe") or "ffprobe","-v","error","-select_streams","a:0","-show_entries","stream=codec_type","-of","csv=p=0",str(path)],capture_output=True,text=True,check=True)
    return bool(result.stdout.strip())


def retime_clip(input_path:Path,output_path:Path,speed:float)->Path:
    speed=float(speed)
    if not math.isfinite(speed) or not 0.85<=speed<=1.15: raise ValueError("音乐卡点变速必须在 0.85–1.15 倍之间")
    output_path.parent.mkdir(parents=True,exist_ok=True)
    cmd=[shutil.which("ffmpeg") or "ffmpeg","-y","-i",str(input_path),"-vf",f"setpts={1.0/speed:.8f}*PTS","-c:v","libx264","-preset","medium","-pix_fmt","yuv420p"]
    if _has_audio(Path(input_path)): cmd += ["-af",f"atempo={speed:.6f}","-c:a","aac","-b:a","192k"]
    else: cmd += ["-an"]
    cmd += ["-movflags","+faststart",str(output_path)]
    subprocess.run(cmd,capture_output=True,check=True)
    return output_path


def mix_global_bgm(video_path:Path,bgm_path:Path,output_path:Path,volume:float=0.16)->Path:
    volume=float(volume)
    if not math.isfinite(volume) or not 0.0<=volume<=1.0: raise ValueError("BGM 音量必须在 0–1 之间")
    if not Path(bgm_path).is_file(): raise RuntimeError(f"背景音乐文件不存在：{bgm_path}")
    output_path.parent.mkdir(parents=True,exist_ok=True)
    cmd=[shutil.which("ffmpeg") or "ffmpeg","-y","-i",str(video_path),"-stream_loop","-1","-i",str(bgm_path)]
    if _has_audio(Path(video_path)):
        filters=f"[0:a]volume=1[orig];[1:a]volume={volume:.4f}[bgm];[orig][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]"
    else: filters=f"[1:a]volume={volume:.4f}[a]"
    cmd += ["-filter_complex",filters,"-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",str(output_path)]
    subprocess.run(cmd,capture_output=True,check=True)
    return output_path
