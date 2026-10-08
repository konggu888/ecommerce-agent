"""用户拍摄素材的扫描、分析与本地剪辑。

区别于“输入链接 -> AI生成视频”的流程，本模块提供第二条工作流：
输入链接 -> AI分析产品 -> 用户指定素材文件夹 -> 用户放入拍好的视频素材
-> AI思考剪辑方案 -> 本地FFmpeg按方案裁剪拼接 -> 成片。

剪辑只使用用户提供的素材文件，绝不伪造、不使用AI生成的视频素材。
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
import subprocess
import re
import shutil

from .ffmpeg import which, best_h264_encoder

VIDEO_EXTS = {'.mp4', '.mov', '.mkv', '.avi', '.webm', '.m4v', '.ts', '.flv'}


class FootageError(ValueError):
    pass


@dataclass
class FootageClip:
    name: str
    path: str
    duration: float
    width: int
    height: int
    fps: float
    note: str = ''

    def to_public(self) -> dict:
        """给 LLM 看的精简素材清单：只有文件名、时长、分辨率、帧率，不暴露本地绝对路径。"""
        return {
            'name': self.name,
            'duration': round(self.duration, 2),
            'width': self.width,
            'height': self.height,
            'fps': round(self.fps, 2),
        }


def probe_clip(path: Path) -> dict:
    """用 ffprobe 读取单个视频的时长/分辨率/帧率。"""
    if not which('ffprobe'):
        raise FootageError('未找到 ffprobe，请安装 FFmpeg 并加入 PATH')
    fmt = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
         '-show_entries', 'format=duration:stream=width,height,r_frame_rate',
         '-of', 'json', str(path)],
        capture_output=True, text=True, timeout=60,
    )
    if fmt.returncode != 0:
        raise FootageError(f'无法解析视频：{path.name}（{fmt.stderr.strip()[:120]}）')
    try:
        data = json.loads(fmt.stdout)
        duration = float(data.get('format', {}).get('duration', 0.0) or 0.0)
        stream = (data.get('streams') or [{}])[0]
        width = int(stream.get('width', 0) or 0)
        height = int(stream.get('height', 0) or 0)
        fps = 0.0
        fr = str(stream.get('r_frame_rate', '0/1') or '0/1')
        m = re.match(r'(\d+)/(\d+)', fr)
        if m:
            den = int(m.group(2))
            if den:
                fps = int(m.group(1)) / den
    except (ValueError, KeyError, IndexError) as exc:
        raise FootageError(f'视频信息格式异常：{path.name}') from exc
    return {'duration': duration, 'width': width, 'height': height, 'fps': fps}


def scan_footage(folder: Path) -> list[FootageClip]:
    """扫描文件夹内所有常见视频格式，逐个探测时长与分辨率。

    返回按文件名排序的素材列表；跳过无法解析的文件并记录 note。
    """
    folder = Path(folder)
    if not folder.exists() or not folder.is_dir():
        raise FootageError(f'素材文件夹不存在：{folder}')
    clips: list[FootageClip] = []
    for p in sorted(folder.iterdir()):
        if p.suffix.lower() not in VIDEO_EXTS or not p.is_file():
            continue
        try:
            info = probe_clip(p)
        except FootageError as exc:
            clips.append(FootageClip(name=p.name, path=str(p), duration=0.0,
                                     width=0, height=0, fps=0.0, note=str(exc)))
            continue
        clips.append(FootageClip(
            name=p.name, path=str(p),
            duration=info['duration'], width=info['width'],
            height=info['height'], fps=info['fps'],
        ))
    return clips



def extract_keyframes(path: Path, output_dir: Path, count: int = 4) -> list[dict]:
    """从实拍视频提取少量低分辨率关键帧，供支持视觉输入的模型分析。"""
    path = Path(path)
    output_dir = Path(output_dir)
    if not path.exists():
        raise FootageError(f'素材文件不存在：{path}')
    if not which('ffmpeg'):
        raise FootageError('未找到 ffmpeg，请安装 FFmpeg 并加入 PATH')
    count = max(1, min(8, int(count)))
    info = probe_clip(path)
    duration = max(0.1, float(info.get('duration', 0.0)))
    times = [0.0] if count == 1 else [duration * i / (count - 1) for i in range(count)]
    output_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    for i, ts in enumerate(times):
        out = output_dir / f'{path.stem}-{i+1:02d}.jpg'
        cmd = ['ffmpeg', '-y', '-ss', f'{ts:.3f}', '-i', str(path),
               '-frames:v', '1', '-vf', 'scale=640:-2', '-q:v', '5', str(out)]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=60)
        except subprocess.CalledProcessError as exc:
            raise FootageError(f'抽取关键帧失败：{path.name}：{exc.stderr[-300:]}') from exc
        frames.append({'path': str(out), 'time': round(ts, 3), 'label': f'{path.name}@{ts:.1f}s'})
    return frames


def build_visual_manifest(clips: list[FootageClip], output_dir: Path,
                          max_frames_per_clip: int = 4) -> list[dict]:
    """为每个可解析素材建立视觉分析清单。"""
    manifest = []
    for clip in clips:
        if clip.duration <= 0:
            continue
        frames = extract_keyframes(Path(clip.path), Path(output_dir) / clip.name, max_frames_per_clip)
        manifest.append({
            'name': clip.name, 'duration': round(clip.duration, 2),
            'width': clip.width, 'height': clip.height, 'fps': round(clip.fps, 2),
            'frames': frames,
        })
    return manifest


def footage_analysis_public(manifest: list[dict]) -> list[dict]:
    """仅返回可放入模型提示词的视觉清单，不暴露本地绝对路径。"""
    return [{
        'name': x['name'], 'duration': x['duration'],
        'width': x['width'], 'height': x['height'], 'fps': x['fps'],
        'keyframes': [{'label': f['label'], 'time': f['time']} for f in x.get('frames', [])],
    } for x in manifest]

def normalize_footage_analysis(analysis: dict | None) -> dict:
    """规范化视觉分析中的重复镜头分组与最佳版本信息。"""
    if not isinstance(analysis, dict):
        return {"clips": [], "global_summary": "", "recommended_duration_seconds": 0}
    result = dict(analysis)
    clips = result.get("clips")
    if not isinstance(clips, list):
        result["clips"] = []
        return result
    normalized = []
    for item in clips:
        if not isinstance(item, dict):
            continue
        x = dict(item)
        x["duplicate_group"] = str(x.get("duplicate_group") or "").strip()
        try:
            x["duplicate_confidence"] = max(0.0, min(1.0, float(x.get("duplicate_confidence", 0) or 0)))
        except (TypeError, ValueError):
            x["duplicate_confidence"] = 0.0
        try:
            x["take_rank"] = max(0, int(x.get("take_rank", 0) or 0))
        except (TypeError, ValueError):
            x["take_rank"] = 0
        x["best_take"] = bool(x.get("best_take", False))
        normalized.append(x)
    groups = {}
    for x in normalized:
        if x["duplicate_group"]:
            groups.setdefault(x["duplicate_group"], []).append(x)
    for group_items in groups.values():
        if not any(x["best_take"] for x in group_items):
            ranked = [x for x in group_items if x["take_rank"] > 0]
            best = min(ranked, key=lambda x: x["take_rank"]) if ranked else max(group_items, key=lambda x: float(x.get("score", 0) or 0))
            best["best_take"] = True
        for x in group_items:
            if x["best_take"] and x["take_rank"] <= 0:
                x["take_rank"] = 1
    result["clips"] = normalized
    return result


def rank_footage_analysis(analysis: dict | None) -> dict:
    """把 AI 视觉判断汇总成稳定的素材池优先级，不替代 AI 原始评分。"""
    result = normalize_footage_analysis(analysis)
    clips = result.get("clips", [])
    candidates = []
    for item in clips:
        if not isinstance(item, dict) or item.get("usable") is False:
            continue
        try:
            base = max(0.0, min(100.0, float(item.get("score", 0) or 0)))
        except (TypeError, ValueError):
            base = 0.0
        score = base
        tags = {str(x).lower() for x in item.get("visual_tags", []) if x is not None}
        speech = str(item.get("speech_quality", "")).lower()
        if item.get("best_take"):
            score += 6.0
        elif item.get("duplicate_group") and float(item.get("duplicate_confidence", 0) or 0) >= 0.7:
            score -= 8.0
        if speech == "clear":
            score += 4.0
        elif speech in {"filler", "unclear"}:
            score -= 4.0
        if tags & {"blur", "shake"}:
            score -= 8.0
        if tags & {"product_visible", "detail", "demo"}:
            score += 3.0
        item["selection_score"] = round(max(0.0, min(110.0, score)), 2)
        candidates.append(item)
    candidates.sort(key=lambda x: (-float(x.get("selection_score", 0)), str(x.get("source", ""))))
    for rank, item in enumerate(candidates, 1):
        item["material_rank"] = rank
    for item in clips:
        if item not in candidates:
            item["material_rank"] = 0
            item["selection_score"] = None
    result["clips"] = clips
    result["ranking"] = {
        "method": "AI评分 + 最佳版本 + 口播质量 + 画面标签 + 重复镜头惩罚",
        "candidate_count": len(candidates),
        "top_sources": [str(x.get("source", "")) for x in candidates[:10]],
    }
    return result


def archive_analyzed_waste(
    clips: list[FootageClip],
    analysis: dict,
    archive_root: Path,
    project_id: str,
) -> tuple[list[FootageClip], list[dict]]:
    """根据视觉分析自动归档明确不可用的实拍素材；保留可用素材继续进入剪辑导演。

    只处理模型明确给出 usable=false 的素材，以及扫描阶段本身无法解析的视频。
    不删除源文件；采用移动方式进入 05_废片库，并写入归档清单，避免重复归档。
    """
    archive_dir = Path(archive_root) / project_id
    archive_dir.mkdir(parents=True, exist_ok=True)
    analyzed = {str(x.get('source', '')).strip(): x for x in (analysis or {}).get('clips', []) if isinstance(x, dict)}
    records: list[dict] = []
    kept: list[FootageClip] = []

    def unique_target(source: Path) -> Path:
        target = archive_dir / source.name
        if not target.exists():
            return target
        for n in range(2, 10000):
            candidate = archive_dir / f'{source.stem}__{n}{source.suffix}'
            if not candidate.exists():
                return candidate
        raise FootageError(f'废片归档目标无法生成唯一文件名：{source.name}')

    for clip in clips:
        item = analyzed.get(clip.name, {})
        unusable = clip.duration <= 0 or item.get('usable') is False
        if clip.duration <= 0 and not item.get('reason'):
            item = {**item, 'reason': clip.note or 'FFmpeg 无法解析该视频'}
        if not unusable:
            kept.append(clip)
            continue
        source = Path(clip.path)
        reason = str(item.get('reason') or clip.note or 'AI判定素材不可用')
        record = {
            'source': clip.name,
            'original_path': str(source),
            'reason': reason,
            'score': item.get('score'),
            'visual_tags': item.get('visual_tags', []),
            'archived': False,
        }
        if source.exists() and source.is_file():
            target = unique_target(source)
            try:
                shutil.move(str(source), str(target))
                record['archive_path'] = str(target)
                record['archived'] = True
            except OSError as exc:
                record['error'] = str(exc)
                kept.append(clip)
        else:
            record['error'] = '源文件不存在，未移动'
        records.append(record)

    manifest = archive_dir / 'archive-manifest.json'
    manifest.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    return kept, records


def trim_clip(src: Path, out: Path, start: float = 0.0, duration: float | None = None) -> Path:
    """按起始秒与时长从素材中裁剪出一段镜头（重编码保证精确切割）。

    音频统一丢弃：广告镜头文案/字幕/BGM 由后续本地加工环节添加。
    """
    src = Path(src); out = Path(out)
    if not src.exists():
        raise FootageError(f'素材文件不存在：{src}')
    if not which('ffmpeg'):
        raise FootageError('未找到 FFmpeg，请安装 FFmpeg 并加入 PATH')
    out.parent.mkdir(parents=True, exist_ok=True)
    codec = best_h264_encoder()
    cmd = ['ffmpeg', '-y', '-ss', f'{max(0.0, start):.3f}', '-i', str(src)]
    if duration is not None and duration > 0:
        cmd += ['-t', f'{duration:.3f}']
    cmd += ['-c:v', codec, '-pix_fmt', 'yuv420p', '-an', str(out)]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return out


def trim_clip_copy(src: Path, out: Path, start: float = 0.0, duration: float | None = None) -> Path:
    """快速流复制裁剪（-c copy）。仅用于时长充分、不追求帧级精确的场景。"""
    src = Path(src); out = Path(out)
    if not src.exists():
        raise FootageError(f'素材文件不存在：{src}')
    if not which('ffmpeg'):
        raise FootageError('未找到 FFmpeg，请安装 FFmpeg 并加入 PATH')
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['ffmpeg', '-y', '-ss', f'{max(0.0, start):.3f}', '-i', str(src)]
    if duration is not None and duration > 0:
        cmd += ['-t', f'{duration:.3f}']
    cmd += ['-c', 'copy', str(out)]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return out


FOOTAGE_SCHEMA = {
    "footage_plan": [{
        "index": "integer",
        "source": "string 素材文件名，必须是给定素材清单里的文件名",
        "start": "number 素材内起始秒",
        "duration": "number 本镜头时长秒",
        "objective": "string 镜头目标",
        "visual": "string 画面说明",
        "script": "string 口播/文案",
        "composition": "string 主体清晰居中",
        "focus_x": "number 0..1",
        "focus_y": "number 0..1",
        "subtitle_position": "顶部安全区|中部安全区|底部安全区|不显示",
        "subtitle_style": "白字黑边|黄字黑边|简洁白字",
        "pacing": "慢|标准|快|极快",
        "speed": "number 0.75..1.5",
        "bgm_intensity": "无|低|中|高",
        "bgm_volume": "number 0..0.35",
        "transition": "硬切|淡入|淡出",
        "ranges": "可选，多段保留区间 [[start,end],...]；用于删除口播废话/重复段"
    }]
}


def validate_footage_plan(raw_plan: list[dict], clips: list[FootageClip]) -> tuple[list[dict], list[str]]:
    """校验 LLM 输出的剪辑方案：文件名必须来自素材清单，起止不能越界。

    返回 (items, warnings)：越界的时长自动截断到素材末尾并给出 warning；
    引用不存在素材直接报错（FootageError）。
    """
    if not isinstance(raw_plan, list) or not raw_plan:
        raise FootageError('AI 没有返回有效的剪辑方案（footage_plan 为空）')
    by_name = {c.name: c for c in clips}
    items: list[dict] = []
    warnings: list[str] = []
    for i, shot in enumerate(raw_plan, 1):
        if not isinstance(shot, dict):
            raise FootageError(f'第{i}个镜头不是有效对象')
        index = int(shot.get('index', i))
        source = str(shot.get('source', '')).strip()
        clip = by_name.get(source)
        if not clip:
            raise FootageError(
                f'镜头{index}引用了素材清单里不存在的文件「{source}」。'
                f'可用素材：{"、".join(sorted(by_name)[:10])}'
            )
        if clip.duration <= 0:
            raise FootageError(f'镜头{index}使用的素材「{source}」无法解析时长，不能用于剪辑')
        start = max(0.0, float(shot.get('start', 0.0) or 0.0))
        duration = float(shot.get('duration', 0.0) or 0.0)
        if duration <= 0:
            duration = max(0.5, clip.duration - start)
        remain = clip.duration - start
        if remain <= 0:
            raise FootageError(f'镜头{index}起始秒 {start:.1f}s 已超出素材「{source}」时长 {clip.duration:.1f}s')
        if duration > remain:
            warnings.append(f'镜头{index}时长 {duration:.1f}s 超出素材剩余 {remain:.1f}s，已截断到素材末尾')
            duration = remain
        raw_ranges = shot.get('ranges') or []
        ranges = []
        if raw_ranges:
            if not isinstance(raw_ranges, list):
                raise FootageError(f'镜头{index}的 ranges 必须是数组')
            for pair in raw_ranges:
                if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                    raise FootageError(f'镜头{index}的 ranges 必须使用 [start,end] 结构')
                a = max(0.0, float(pair[0]))
                b = min(clip.duration, float(pair[1]))
                if b <= a:
                    continue
                ranges.append([round(a, 3), round(b, 3)])
            ranges.sort(key=lambda x: x[0])
            merged = []
            for a, b in ranges:
                if merged and a <= merged[-1][1] + 0.02:
                    merged[-1][1] = max(merged[-1][1], b)
                else:
                    merged.append([a, b])
            ranges = merged
            if not ranges:
                raise FootageError(f'镜头{index}的 ranges 没有有效区间')
            start = ranges[0][0]
            duration = round(sum(b - a for a, b in ranges), 3)
        else:
            ranges = [[round(start, 3), round(start + duration, 3)]]
        item = {
            'index': index,
            'source': source,
            'start': round(start, 3),
            'duration': round(duration, 3),
            'ranges': ranges,
            'objective': str(shot.get('objective', '')),
            'visual': str(shot.get('visual', '')),
            'script': str(shot.get('script', '')),
            'composition': str(shot.get('composition', '主体清晰居中')),
            'focus_x': min(1.0, max(0.0, float(shot.get('focus_x', 0.5) or 0.5))),
            'focus_y': min(1.0, max(0.0, float(shot.get('focus_y', 0.5) or 0.5))),
            'subtitle_position': str(shot.get('subtitle_position', '底部安全区')),
            'subtitle_style': str(shot.get('subtitle_style', '白字黑边')),
            'pacing': str(shot.get('pacing', '标准')),
            'speed': min(1.5, max(0.75, float(shot.get('speed', 1.0) or 1.0))),
            'bgm_intensity': str(shot.get('bgm_intensity', '低')),
            'bgm_volume': min(0.35, max(0.0, float(shot.get('bgm_volume', 0.16) or 0.16))),
            'transition': str(shot.get('transition', '硬切')),
        }
        items.append(item)
    return items, warnings
