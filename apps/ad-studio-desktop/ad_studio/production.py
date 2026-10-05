from pathlib import Path
import json
from .models import Project, Shot

class ProductionStore:
    def __init__(self, root: Path):
        self.root=root
        self.root.mkdir(parents=True,exist_ok=True)
    def save(self, project: Project):
        project.updated_at=__import__('datetime').datetime.now().isoformat(timespec='seconds')
        project.save(self.root)
    def render_path(self, project: Project, shot: Shot):
        folder=self.root/'renders'/project.id/shot.id
        folder.mkdir(parents=True,exist_ok=True)
        return folder/f'v{shot.version}.mp4'
    def current_shots(self, project: Project):
        return [s for s in project.shots if s.video_path]
    def mark_ready(self, project: Project, shot: Shot, output: Path):
        shot.video_path=str(output)
        shot.status='已生成'
        self.save(project)
