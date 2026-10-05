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
    created_at: str=field(default_factory=now)
    updated_at: str=field(default_factory=now)
    def save(self, root: Path):
        root.mkdir(parents=True, exist_ok=True)
        (root/f'{self.id}.json').write_text(json.dumps(asdict(self),ensure_ascii=False,indent=2),encoding='utf-8')
