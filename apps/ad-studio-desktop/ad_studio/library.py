from pathlib import Path
import json, shutil
from .models import Asset, uid

class LocalLibrary:
    def __init__(self,root:Path):
        self.root=root; self.assets=root/'assets'; self.index=root/'library.json'
        self.assets.mkdir(parents=True,exist_ok=True)
        if not self.index.exists(): self.index.write_text('[]',encoding='utf-8')
    def all(self): return [Asset(**x) for x in json.loads(self.index.read_text(encoding='utf-8'))]
    def ensure_defaults(self):
        defaults = [
            Asset('actor-linchuan','林川','演员','system',None,['口播','生活','通勤']),
            Asset('actor-zhounye','周野','演员','system',None,['专业','测评','强转化']),
            Asset('actor-suning','苏宁','演员','system',None,['种草','生活','UGC']),
            Asset('actor-guyao','顾瑶','演员','system',None,['高级','职场','专业']),
            Asset('scene-commute','地铁通勤','场景','system',None,['通勤','年轻','生活']),
            Asset('scene-home','家庭客厅','场景','system',None,['家庭','生活','真实']),
            Asset('scene-office','现代办公室','场景','system',None,['职场','专业','高级']),
            Asset('scene-street','城市街头','场景','system',None,['街头','UGC','年轻'])
        ]
        existing={a.id for a in self.all()}
        missing=[a for a in defaults if a.id not in existing]
        if missing: self._write(self.all()+missing)
        return missing
    def _write(self,items): self.index.write_text(json.dumps([x.__dict__ for x in items],ensure_ascii=False,indent=2),encoding='utf-8')
    def add_file(self,file_path,name,kind,source='user_upload',tags=None):
        src=Path(file_path); aid=uid(kind); dst=self.assets/(aid+'_'+src.name); shutil.copy2(src,dst)
        item=Asset(aid,name,kind,source,str(dst),tags or []); self._write(self.all()+[item]); return item
    def add(self,name,kind,source='system',tags=None,path=None):
        item=Asset(uid(kind),name,kind,source,path,tags or []); self._write(self.all()+[item]); return item
    def reusable(self,kind,tags=None):
        wanted=set(tags or [])
        return [a for a in self.all() if a.active and a.reusable and a.kind==kind and (not wanted or wanted.intersection(a.tags))]

    def best_match(self, kind, tags=None):
        """本地优先：按标签重合度选择最佳可复用素材。"""
        wanted=set(tags or [])
        candidates=[a for a in self.all() if a.active and a.reusable and a.kind==kind]
        if not candidates: return None
        if not wanted: return candidates[0]
        ranked=sorted(candidates,key=lambda a: len(wanted.intersection(set(a.tags))),reverse=True)
        return ranked[0] if wanted.intersection(set(ranked[0].tags)) else None

    def register_generated(self, name, kind, path, tags=None, request=""):
        """云端/AI生成后立即入本地永久资产库。"""
        return self.add(name, kind, source="ai_generated", tags=tags or [], path=str(path))

