from pathlib import Path
import json
import datetime
from .models import Project, Shot, accept_hybrid_generated_shot
from .ffmpeg import make_clip, concat
from .providers import GenerationRequest, load_video_provider, load_asset_provider
from .postprocess import process_shot
from .library import LocalLibrary
from .asset_generation import AssetGenerator, LocalAssetBackend
from .hardware import detect_hardware
from .capability import CapabilityRouter
from .usage_ledger import UsageLedger

class ProductionStore:
    def __init__(self, root: Path, library_root: Path | None = None):
        self.root=root; self.root.mkdir(parents=True,exist_ok=True)
        self.library_root=library_root or root
        self.ledger=UsageLedger(self.root/'usage-ledger.json')

    def save(self, project: Project):
        project.updated_at=datetime.datetime.now().isoformat(timespec='seconds')
        project.save(self.root)

    def load(self, project_id: str):
        p=self.root/f'{project_id}.json'
        if not p.exists(): return None
        data=json.loads(p.read_text(encoding='utf-8'))
        data['shots']=[Shot(**s) for s in data.get('shots',[])]
        return Project(**data)

    def _variant_index(self, project: Project) -> int:
        """读取当前项目激活方案；所有物理媒体路径都必须带方案隔离。"""
        try:
            return max(1, int((project.creative_plan or {}).get('variant_index', 1) or 1))
        except (TypeError, ValueError):
            return 1

    def render_path(self, project: Project, shot: Shot):
        variant=self._variant_index(project)
        folder=self.root/'renders'/project.id/f'variant-{variant}'/shot.id
        folder.mkdir(parents=True,exist_ok=True)
        return folder/f'v{shot.version}.mp4'

    def current_shots(self, project: Project):
        """返回可进入最终成片的镜头，严格按分镜序号排序并执行审核闸门。"""
        shots = []
        for shot in sorted(project.shots, key=lambda x: x.index):
            if not shot.video_path or not Path(shot.video_path).exists():
                continue
            if getattr(shot, "clip_source", "ai_generated") == "ai_generated" and getattr(shot, "storyboard_review", "不需要") == "待复核":
                continue
            shots.append(shot)
        return shots

    def final_render_inputs(self, project: Project):
        """返回最终拼接实际消费的镜头路径，便于 UI/测试审计顺序。"""
        shots = self.current_shots(project)
        return [{"index": shot.index, "shot_id": shot.id, "path": str(shot.video_path)} for shot in shots]

    def _sync_actual_cost(self, project: Project):
        summary = self.ledger.project_summary(project.id)
        project.cost_estimate.setdefault("actual", {})
        project.cost_estimate["actual"] = summary
        project.cost_estimate["actual_cost_rmb"] = summary["actual_cost_rmb"]

    def _record_actual_cost(self, project: Project, *, shot: Shot | None, category: str, amount_rmb: float, provider: str, quantity: float = 1.0, unit_cost_rmb: float = 0.0, function: str = "生成任务"):
        amount = round(float(amount_rmb or 0), 6)
        self.ledger.record(