from pathlib import Path
import json
import datetime
from .models import Project, Shot
from .ffmpeg import make_clip, concat
from .providers import GenerationRequest, load_video_provider
from .postprocess import process_shot

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

    def render_cloud_shot(self, project: Project, shot: Shot, provider_path: Path):
        out=self.render_path(project,shot)
        provider=load_video_provider(provider_path)
        prompt='\\n'.join([f'标题：{shot.title}',f'画面：{shot.visual}',f'文案：{shot.script}'])
        shot.status='生成中…'; shot.provider=getattr(provider,'provider_name','Generic REST'); self.save(project)
        result=provider.generate(GenerationRequest(prompt=prompt,output=out,duration=3,reference_assets=[x for x in [shot.actor_id,shot.scene_id] if x]))
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
        process_shot(src,out,aspect,speed)
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
