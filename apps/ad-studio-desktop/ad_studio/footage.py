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
import time

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



def audit_footage_coverage(analysis: dict | None, creative_plan: dict | None = None) -> dict:
    """本地确定性检查卖点覆盖、开场候选和关键镜头缺口，不产生新的 AI 调用。"""
    analysis = rank_footage_analysis(analysis)
    creative_plan = creative_plan or {}
    clips = [x for x in analysis.get("clips", []) if isinstance(x, dict) and x.get("usable") is not False]
    clips.sort(key=lambda x: (int(x.get("material_rank", 999999) or 999999), str(x.get("source", ""))))
    def clean(v):
        return re.sub(r"[\\u3000\\s，。、“”‘’：；！？、（）()【】\\[\\]{}<>《》/\\\\|·_\\-]+", "", str(v or "").strip().lower())
    def match(point, item):
        p = clean(point)
        hay = clean(" ".join(str(x) for x in (item.get("selling_points") or []) + (item.get("visual_tags") or [])))
        if not p or not hay:
            return False
        if p in hay or hay in p:
            return True
        return any(p[i:j] in hay for i in range(len(p)) for j in (i + 2, min(len(p), i + 4)) if j > i and j - i >= 2)
    points = creative_plan.get("selling_points") or []
    if isinstance(points, dict): points = list(points.values())
    if not isinstance(points, list): points = [points]
    normalized = []
    for point in points:
        if isinstance(point, dict): point = point.get("name") or point.get("title") or point.get("point") or ""
        point = str(point).strip()
        if point and point not in normalized: normalized.append(point)
    if not normalized:
        for item in clips:
            for point in item.get("selling_points") or []:
                point = str(point).strip()
                if point and point not in normalized: normalized.append(point)
    coverage = []
    for point in normalized:
        matches = [x for x in clips if match(point, x)]
        matches.sort(key=lambda x: (not bool(x.get("best_take")), int(x.get("material_rank", 999999) or 999999), -float(x.get("selection_score", 0) or 0)))
        best = matches[0] if matches else None
        coverage.append({"name": point, "covered": bool(matches), "sources": [str(x.get("source", "")) for x in matches[:5]], "best_source": str(best.get("source", "")) if best else ""})
    candidates = []
    for item in clips:
        tags = {str(x).lower() for x in item.get("visual_tags") or []}
        score = float(item.get("selection_score", 0) or 0) + (8 if tags & {"product_visible", "demo", "detail", "person", "scene"} else 0) - (20 if tags & {"blur", "shake", "blocked"} else 0) + (4 if item.get("best_take") else 0)
        candidates.append((score, -int(item.get("material_rank", 999999) or 999999), item))
    candidates.sort(key=lambda x: (-x[0], x[1], str(x[2].get("source", ""))))
    opening = candidates[0][2] if candidates else None
    shots = creative_plan.get("shots") or []
    if not isinstance(shots, list): shots = []
    required = [("商品特写", ("特写", "细节", "detail", "近景")), ("商品演示", ("演示", "使用", "操作", "demo")), ("真人/场景", ("真人", "人物", "场景", "生活", "出镜", "person", "scene")), ("口播", ("口播", "说话", "讲解", "talking"))]
    missing = []
    for label, keys in required:
        requested = any(any(k.lower() in str(x.get("objective", x.get("visual", ""))).lower() for k in keys) for x in shots if isinstance(x, dict))
        found = any(any(k.lower() in " ".join(map(str, x.get("visual_tags") or [])).lower() for k in keys) for x in clips)
        if requested and not found: missing.append({"need": label, "reason": "创意分镜需要该类镜头，但当前可用实拍素材没有对应证据", "action": "待补拍"})
    covered = sum(1 for x in coverage if x["covered"])
    return {"coverage_score": round(100.0 * covered / len(coverage), 1) if coverage else 100.0, "opening_candidate": str(opening.get("source", "")) if opening else "", "selling_points": coverage, "missing_key_shots": missing, "missing_selling_points": [x["name"] for x in coverage if not x["covered"]], "candidate_sources": [str(x.get("source", "")) for x in clips[:10]], "method": "本地确定性覆盖审计"}



def classify_footage_gaps(coverage: dict | None, creative_plan: dict | None = None, *, generation_connected: bool = False) -> dict:
    """把实拍素材缺口分类为补拍/待生成/待补素材，不伪称生成已经接通。"""
    coverage = coverage or {}
    plan = creative_plan or {}
    points = {str(x.get("name", "")): x for x in coverage.get("selling_points", []) if isinstance(x, dict)}
    gaps = []
    for item in coverage.get("missing_key_shots", []) or []:
        if not isinstance(item, dict): continue
        need = str(item.get("need", "")).strip()
        reason = str(item.get("reason", "")).strip()
        text = f"{need} {reason}".lower()
        physical = any(k in text for k in ("实拍", "商品", "演示", "细节", "开箱", "操作", "使用", "材质", "接口", "功能"))
        if physical:
            action = "待补拍"; why = "缺少商品事实或实际操作证据，优先补拍，避免生成画面冒充真实商品表现。"
        elif generation_connected:
            action = "待生成"; why = "当前缺口属于可由已接通生成链补足的通用画面。"
        else:
            action = "待补素材"; why = "缺口不适合凭空编造；当前没有已接通的生成链，因此先标记为待补素材。"
        gaps.append({"need": need, "reason": reason, "action": action, "why": why})
    missing_points = []
    for raw_name in coverage.get("missing_selling_points", []) or []:
        name = str(raw_name).strip()
        if not name:
            continue
        # 覆盖审计可能只返回缺失卖点名称，不一定同时带 selling_points 详情；
        # 缺失本身就是待补拍任务，不应因为详情映射不存在而被静默丢弃。
        missing_points.append({
            "name": name,
            "action": "待补拍",
            "why": "该卖点没有可验证的实拍证据，不能在成片中虚构展示。",
        })
    return {"gap_count": len(gaps) + len(missing_points), "key_shot_gaps": gaps, "selling_point_gaps": missing_points, "generation_connected": bool(generation_connected), "method": "实拍素材缺口确定性分类"}

def build_footage_gap_tasks(
    coverage: dict | None,
    gaps: dict | None,
    creative_plan: dict | None = None,
) -> dict:
    """把素材缺口转成可执行的补拍/补素材任务，不执行拍摄或生成。"""
    coverage = coverage or {}
    gaps = gaps or {}
    plan = creative_plan or {}
    tasks = []
    counter = 1

    def add_task(action, need, reason, why, related_point="", priority="高",
                 framing="", acceptance=""):
        nonlocal counter
        need = str(need).strip()
        if not need:
            return
        tasks.append({
            "task_id": f"GAP-{counter:03d}",
            "type": action,
            "priority": priority,
            "need": need,
            "related_selling_point": related_point,
            "reason": str(reason).strip(),
            "why": str(why).strip(),
            "shoot_or_generate": framing or "补充能够直接证明该需求的素材。",
            "acceptance": acceptance or "素材清晰、主体可辨、能直接验证该需求，并可用于后续剪辑。",
            "status": "待处理",
        })
        counter += 1

    for item in gaps.get("key_shot_gaps", []) or []:
        if not isinstance(item, dict):
            continue
        need = str(item.get("need", "")).strip()
        action = str(item.get("action", "待补素材")).strip() or "待补素材"
        reason = str(item.get("reason", "")).strip()
        why = str(item.get("why", "")).strip()
        physical = action == "待补拍"
        if physical:
            framing = f"围绕“{need}”补拍真实商品证据：先完整展示主体，再完成对应动作/细节，避免遮挡并保留连续过程。"
            acceptance = f"至少有一段稳定、清晰的实拍能够直接证明“{need}”，商品主体完整可见，关键动作或细节不能被遮挡。"
        elif action == "待生成":
            framing = f"按“{need}”生成通用辅助画面；不得把虚构画面当作商品真实性能或事实证据。"
            acceptance = f"生成结果明确服务于“{need}”，且不会冒充真实商品实拍证据。"
        else:
            framing = f"补充能覆盖“{need}”的合法素材；优先使用真实商品/真实场景素材。"
            acceptance = f"新增素材能够直接覆盖“{need}”，并满足商品事实可验证要求。"
        add_task(action, need, reason, why, priority="高", framing=framing, acceptance=acceptance)

    for item in gaps.get("selling_point_gaps", []) or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        add_task(
            "待补拍",
            f"卖点：{name}",
            "当前素材池没有可验证的实拍素材覆盖该卖点。",
            str(item.get("why", "")).strip() or "重要卖点缺少真实证据。",
            related_point=name,
            priority="最高",
            framing=f"专门补拍“{name}”的证明镜头：商品完整露出，并把能证明该卖点的动作、结构或细节拍清楚。",
            acceptance=f"至少一段实拍可直接证明“{name}”，不能只靠字幕或口播声称；画面需清晰稳定。",
        )

    # 防止同一缺口同时以关键镜头和卖点任务重复出现。
    unique = []
    seen = set()
    for task in tasks:
        key = (task["type"], task["need"], task["related_selling_point"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(task)
    tasks = unique
    for i, task in enumerate(tasks, 1):
        task["task_id"] = f"GAP-{i:03d}"

    return {
        "task_count": len(tasks),
        "tasks": tasks,
        "source_coverage_score": coverage.get("coverage_score", 100.0),
        "generation_connected": bool(gaps.get("generation_connected", False)),
        "method": "实拍素材缺口转可执行任务清单",
        "next_step": "完成补拍/补素材后重新扫描素材文件夹并进入视觉分析、排名、覆盖审计和最终分镜复核。",
    }


def audit_footage_gap_completion(previous_tasks: dict | None, coverage: dict | None) -> dict:
    """根据新一轮确定性覆盖审计，验收上一轮补素材任务；不调用 AI。"""
    previous_tasks = previous_tasks or {}
    coverage = coverage or {}
    tasks = [dict(x) for x in previous_tasks.get("tasks", []) if isinstance(x, dict)]
    missing_shots = {str(x.get("need", "")).strip() for x in coverage.get("missing_key_shots", []) if isinstance(x, dict)}
    missing_points = {str(x).strip() for x in coverage.get("missing_selling_points", []) if str(x).strip()}
    point_names = {str(x.get("name", "")).strip() for x in coverage.get("selling_points", []) if isinstance(x, dict)}
    results = []
    completed = partial = pending = 0
    for task in tasks:
        need = str(task.get("need", "")).strip()
        point = str(task.get("related_selling_point", "")).strip()
        target_point = point or (need[3:].strip() if need.startswith("卖点：") else "")
        if target_point:
            is_missing = target_point in missing_points
            known = target_point in point_names or target_point in missing_points
        else:
            is_missing = need in missing_shots
            known = bool(need)
        item = dict(task)
        if known and not is_missing:
            item["status"] = "已完成"
            item["completion_reason"] = "新一轮覆盖审计已找到可用素材覆盖该任务。"
            item["completion_coverage_score"] = coverage.get("coverage_score", 0)
            completed += 1
        elif known and is_missing:
            item["status"] = "仍缺失"
            item["completion_reason"] = "新一轮分析后该缺口仍未被可用素材覆盖。"
            pending += 1
        else:
            item["status"] = "待复核"
            item["completion_reason"] = "新一轮分析无法稳定映射到上一轮任务，需人工确认。"
            partial += 1
        results.append(item)
    return {
        "task_count": len(results),
        "completed_count": completed,
        "still_missing_count": pending,
        "review_count": partial,
        "tasks": results,
        "coverage_score": coverage.get("coverage_score", 100.0),
        "method": "新旧覆盖审计差异验收（确定性）",
    }

def audit_final_footage_plan(
    plan: list[dict] | None,
    analysis: dict | None,
    coverage: dict | None = None,
) -> dict:
    """对最终素材分镜做确定性复核，并给每个镜头标记卖点/排名/重复组信息。"""
    items = [dict(x) for x in (plan or []) if isinstance(x, dict)]
    clips = {str(x.get("source", "")): x for x in (analysis or {}).get("clips", []) if isinstance(x, dict)}
    point_map = {str(x.get("name", "")): x for x in (coverage or {}).get("selling_points", []) if isinstance(x, dict)}
    used_points: set[str] = set()
    duplicate_groups: dict[str, list[str]] = {}
    for i, shot in enumerate(items, 1):
        source = str(shot.get("source", ""))
        info = clips.get(source, {})
        shot["material_rank"] = info.get("material_rank", 0)
        shot["selection_score"] = info.get("selection_score")
        shot["duplicate_group"] = info.get("duplicate_group", "")
        shot["best_take"] = bool(info.get("best_take", False))
        shot["sequence_index"] = i
        text = " ".join(str(shot.get(k, "")) for k in ("objective", "visual", "description", "voiceover", "subtitle", "selling_point"))
        matched = [p for p in point_map if p and p in text]
        if not matched:
            matched = [p for p, v in point_map.items() if v.get("best_source") == source]
        shot["covered_selling_points"] = matched
        used_points.update(matched)
        group = str(info.get("duplicate_group", ""))
        if group:
            duplicate_groups.setdefault(group, []).append(source)
    opening = str((coverage or {}).get("opening_candidate", ""))
    opening_used = bool(opening and any(str(x.get("source", "")) == opening for x in items))
    repeated_groups = {g: list(dict.fromkeys(v)) for g, v in duplicate_groups.items() if len(set(v)) > 1}
    missing = [p for p in point_map if p and point_map[p].get("covered") and p not in used_points]
    first_source = str(items[0].get("source", "")) if items else ""
    opening_warning = bool(opening and first_source != opening and not (items and items[0].get("hook")))
    return {
        "shot_count": len(items),
        "opening_candidate": opening,
        "opening_used": opening_used,
        "first_source": first_source,
        "opening_warning": opening_warning,
        "covered_selling_points": sorted(used_points),
        "missing_selling_points": missing,
        "duplicate_groups_reused": repeated_groups,
        "plan": items,
        "method": "最终分镜确定性复核：开场 + 卖点覆盖 + 素材排名 + 重复镜头",
    }

def append_footage_reanalysis_history(project_dir: Path, snapshot: dict) -> Path:
    """把每次重新分析的结果单独留档，避免覆盖后丢失上一轮判断。"""
    root = Path(project_dir) / 'footage-reanalysis-history'
    root.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime('%Y%m%d-%H%M%S')
    target = root / f'{stamp}.json'
    n = 2
    while target.exists():
        target = root / f'{stamp}-{n}.json'; n += 1
    target.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding='utf-8')
    return target


def archive_analyzed_waste(
    clips: list[FootageClip],
    analysis: dict,
    archive_root: Path,
    project_id: str,
    protected_paths: set[str] | None = None,
) -> tuple[list[FootageClip], list[dict]]:
    """根据视觉分析自动归档明确不可用的实拍素材；保留可用素材继续进入剪辑导演。

    只处理模型明确给出 usable=false 的素材，以及扫描阶段本身无法解析的视频。
    不删除源文件；采用移动方式进入 05_废片库，并写入归档清单，避免重复归档。
    """
    archive_dir = Path(archive_root) / project_id
    archive_dir.mkdir(parents=True, exist_ok=True)
    protected = {str(Path(p).expanduser().resolve()) for p in (protected_paths or set())}
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
        source = Path(clip.path)
        source_resolved = str(source.expanduser().resolve())
        if source_resolved in protected:
            kept.append(clip)
            records.append({
                'source': clip.name,
                'original_path': str(source),
                'reason': str(item.get('reason') or clip.note or 'AI判定素材不可用'),
                'score': item.get('score'),
                'visual_tags': item.get('visual_tags', []),
                'archived': False,
                'protected': True,
                'protected_reason': '当前项目已有成片/分镜正在引用该素材，重新分析不得自动移动源文件',
            })
            continue
        if not unusable:
            kept.append(clip)
            continue
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
