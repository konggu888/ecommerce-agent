from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional
import json, uuid, datetime

def now(): return datetime.datetime.now().isoformat(timespec='seconds')
def uid(prefix): return f'{prefix}-{uuid.uuid4().hex[:10]}'

@dataclass
class Asset:
    id: str
    name: str
    kind: str
    source: str='user_upload'
    path: Optional[str]=None
    tags: list[str]=field(default_factory=list)
    active: bool=True
    reusable: bool=True

@dataclass
class Shot:
    id: str
    index: int
    title: str
    visual: str
    script: str
    actor_id: Optional[str]=None
    scene_id: Optional[str]=None
    product_asset_ids: list[str]=field(default_factory=list)
    status: str='待生成'
    version: int=1
    video_path: Optional[str]=None
    actual_cost_rmb: float=0.0
    provider: Optional[str]=None
    generated_from_request: Optional[str]=None
    asset_source: str='library'
    composition: str='主体清晰居中'
    focus_x: float=0.5
    focus_y: float=0.5
    subtitle_position: str='底部安全区'
    subtitle_style: str='白字黑边'
    pacing: str='标准'
    speed: float=1.0
    bgm_intensity: str='低'
    bgm_volume: float=0.16
    transition: str='硬切'
    clip_source: str='ai_generated'
    source_file: Optional[str]=None
    source_start: float=0.0
    source_duration: float=0.0
    source_ranges: list[list[float]] = field(default_factory=list)

@dataclass
class Project:
    id: str
    product_name: str
    platform: str
    form: str
    level: int
    actor_id: Optional[str]
    scene_id: Optional[str]
    shots: list[Shot]
    cost_estimate: dict = field(default_factory=dict)
    actual_cost_rmb: float = 0.0
    actual_cost_summary: dict = field(default_factory=dict)
    product_info: dict = field(default_factory=dict)
    creative_plan: dict = field(default_factory=dict)
    footage_folder: Optional[str]=None
    created_at: str=field(default_factory=now)
    updated_at: str=field(default_factory=now)
    def save(self, root: Path):
        root.mkdir(parents=True, exist_ok=True)
        (root/f'{self.id}.json').write_text(json.dumps(asdict(self),ensure_ascii=False,indent=2),encoding='utf-8')


def restore_variant_shot_cache(base_shots, saved_shots):
    """恢复广告方案完整镜头缓存，保留人工纳入的额外镜头。"""
    if not saved_shots:
        return list(base_shots)
    base_by_id = {str(getattr(shot, "id", "")): shot for shot in base_shots}
    restored = []
    for saved in saved_shots:
        if not isinstance(saved, dict):
            continue
        shot_id = str(saved.get("id", ""))
        if shot_id in base_by_id:
            shot = base_by_id[shot_id]
            for key, value in saved.items():
                if key != "id" and hasattr(shot, key):
                    setattr(shot, key, value)
            restored.append(shot)
        else:
            restored.append(Shot(**saved))
    return restored


def find_variant_insert_position(shots, target_shot_index):
    """按原始镜头稳定 ID 查找插入位置，避免多次插入导致 index 漂移。"""
    if target_shot_index is None:
        return len(shots)
    try:
        target = int(target_shot_index)
    except (TypeError, ValueError):
        return len(shots)
    stable_id = f"shot-{target:02d}"
    for pos, shot in enumerate(shots):
        if str(getattr(shot, "id", "")) == stable_id:
            return pos
    return next((pos for pos, shot in enumerate(shots) if int(getattr(shot, "index", 0) or 0) >= target), len(shots))


def accept_hybrid_generated_shot(task: dict, shots: list[Shot], *, accepted_shot_id: str | None = None):
    """人工明确通过后，才把已生成缺口作为额外镜头插入当前分镜。"""
    if not isinstance(task, dict):
        raise ValueError("缺口任务必须是字典")
    if task.get("review_status") not in {"已通过", "通过"}:
        raise ValueError("只有人工复核通过的素材才能纳入分镜")
    path = str(task.get("generated_path") or "").strip()
    if not path:
        raise ValueError("缺口任务没有生成文件")
    if task.get("accepted_into_storyboard"):
        return shots
    target_index = task.get("target_shot_index")
    position = find_variant_insert_position(shots, target_index)
    shot_id = accepted_shot_id or f"hybrid-{str(task.get('task_id') or 'gap')}-v1"
    # 避免同一任务重复插入。
    if any(str(getattr(s, "id", "")) == shot_id for s in shots):
        task["accepted_into_storyboard"] = True
        task["accepted_shot_id"] = shot_id
        return shots
    base_index = int(target_index) if target_index is not None else (position + 1)
    extra = Shot(
        id=shot_id,
        index=base_index,
        title=str(task.get("title") or "AI辅助画面"),
        visual=str(task.get("visual") or task.get("need") or "辅助画面"),
        script=str(task.get("script") or ""),
        status="已复核并纳入分镜",
        video_path=path,
        provider=task.get("provider"),
        actual_cost_rmb=float(task.get("estimated_cost_rmb") or 0),
        clip_source="ai_generated",
        asset_source="ai_generated",
        source_file=path,
    )
    shots.insert(position, extra)
    for idx, shot in enumerate(shots, start=1):
        shot.index = idx
    task["accepted_into_storyboard"] = True
    task["accepted_shot_id"] = shot_id
    return shots
