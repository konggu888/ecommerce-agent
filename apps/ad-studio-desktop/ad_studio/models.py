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
