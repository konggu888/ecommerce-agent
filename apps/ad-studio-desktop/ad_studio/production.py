from pathlib import Path
import json
import datetime
from .models import Project, Shot
from .ffmpeg import make_clip, concat
from .providers import GenerationRequest, load_video_provider
from .postprocess import process_shot
from .library import LocalLibrary

class ProductionStore:
    def __init__(self, root: Path):
        self.root=root; self.root.mkdir(parents=True,exist_ok=True)

    def save(self, project: Project):
        project.updated_at=datetime.datetime.now().isoformat(timespec='seconds')
        project.save(self.root)

    def load(self, project_id: str):
        p=self.root/f'{project_id}.json'
        if not p.exists(): return None
        data=json.loads(p.read_text(encoding='utf-8'))
        data['shots']=[Shot(**s) for s in data.get('shots',[])]
        return Project(**data)

    def render_path(self, project: Project, shot: Shot):
        folder=self.root/'renders'/project.id/shot.id
        folder.mkdir(parents=True,exist_ok=True)
        return folder/f'v{shot.version}.mp4'

    def current_shots(self, project: Project):
        return [s for s in sorted(project.shots,key=lambda x:x.index) if s.video_path and Path(s.video_path).exists()]

    def mark_ready(self, project: Project, shot: Shot, output: Path):
        shot.video_path=str(output); shot.status='已生成'; self.save(project)

    def resolve_assets(self, project: Project, shot: Shot):
        """本地优先；缺失时返回明确的生成需求。真正生成由对应生成器执行。"""
        library=LocalLibrary(self.root)
        resolution={}
        plan_shots=project.creative_plan.get("shots", []) if project.creative_plan else []
        ai=next((x for x in plan_shots if int(x.get("index", -1)) == shot.index), {})
        req=ai.get("asset_resolution", {}) or {}
        for kind, tags in (("演员", req.get("actor_tags", [])), ("场景", req.get("scene_tags", [])), ("商品素材", req.get("product_tags", []))):
            found=library.best_match(kind,tags)
            resolution[kind]={"asset":found.id if found else None,"source":"本地素材库" if found else "待自动生成","generate_if_missing":bool(req.get("generation_if_missing", True))}
        if resolution["演员"]["asset"]: shot.actor_id=resolution["演员"]["asset"]
        if resolution["场景"]["asset"]: shot.scene_id=resolution["场景"]["asset"]
        shot.asset_source="library" if all(x["asset"] for x in resolution.values()) else "generate_missing"
        project.creative_plan.setdefault("asset_resolution", {})[shot.id]=resolution
        self.save(project)
        return resolution

    def render_cloud_shot(self, project: Project, shot: Shot, provider_path: Path):
        out=self.render_path(project,shot)
        resolution=self.resolve_assets(project,shot)
        provider=load_video_provider(provider_path)
        prompt='\\n'.join([f'标题：{shot.title}',f'画面：{shot.visual}',f'文案：{shot.script}'])
        shot.status='生成中…'; shot.provider=getattr(provider,'provider_name','Generic REST'); self.save(project)
        result=provider.generate(GenerationRequest(prompt=prompt,output=out,duration=3,reference_assets=[x for x in [shot.actor_id,shot.scene_id,*shot.product_asset_ids] if x]))
        shot.actual_cost_rmb=round(float(getattr(provider,'cost_per_shot_rmb',0.0)),4)
        self.mark_ready(project,shot,result)
        return result

    def render_placeholder_shot(self, project: Project, shot: Shot):
        out=self.render_path(project,shot)
        make_clip(out,3)
        self.mark_ready(project,shot,out)
        return out

    def postprocess_shot(self, project: Project, shot: Shot, aspect: str = "9:16", speed: float = 1.0):
        if not shot.video_path or not Path(shot.video_path).exists():
            raise RuntimeError("当前镜头还没有真实成片，不能做本地后处理")
        src=Path(shot.video_path)
        out=self.root/'postprocessed'/project.id/shot.id/f'v{shot.version}-{aspect.replace(":", "x")}.mp4'
        shot.status='本地4050处理中…'
        self.save(project)
        plan_shots=project.creative_plan.get("shots", []) if project.creative_plan else []
        ai=next((x for x in plan_shots if int(x.get("index", -1)) == shot.index), {})
        focus_x=float(ai.get("focus_x", getattr(shot, "focus_x", 0.5)))
        focus_y=float(ai.get("focus_y", getattr(shot, "focus_y", 0.5)))
        ai_speed=float(ai.get("speed", getattr(shot, "speed", speed)))
        transition=str(ai.get("transition", getattr(shot, "transition", "硬切")))
        process_shot(src,out,aspect,ai_speed,focus_x,focus_y,transition)
        shot.video_path=str(out)
        shot.status='已后处理'
        self.save(project)
        return out

    def build_final(self, project: Project, aspect: str = "9:16"):
        shots=self.current_shots(project)
        if len(shots)!=len(project.shots):
            raise RuntimeError(f'还有 {len(project.shots)-len(shots)} 个镜头没有成片，暂不能输出最终广告')
        out=self.root/'final'/project.id/f'final-{aspect.replace(":", "x")}.mp4'
        concat([Path(s.video_path) for s in shots],out)
        return out
