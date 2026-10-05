from pathlib import Path
import json, shutil
from .models import Asset, uid

class LocalLibrary:
    def __init__(self,root:Path):
        self.root=root; self.assets=root/'assets'; self.index=root/'library.json'
        self.assets.mkdir(parents=True,exist_ok=True)
        if not self.index.exists(): self.index.write_text('[]',encoding='utf-8')
    def all(self): return [Asset(**x) for x in json.loads(self.index.read_text(encoding='utf-8'))]
    def _write(self,items): self.index.write_text(json.dumps([x.__dict__ for x in items],ensure_ascii=False,indent=2),encoding='utf-8')
    def add_file(self,file_path,name,kind,source='user_upload',tags=None):
        src=Path(file_path); aid=uid(kind); dst=self.assets/(aid+'_'+src.name); shutil.copy2(src,dst)
        item=Asset(aid,name,kind,source,str(dst),tags or []); self._write(self.all()+[item]); return item
    def add(self,name,kind,source='system',tags=None,path=None):
        item=Asset(uid(kind),name,kind,source,path,tags or []); self._write(self.all()+[item]); return item
    def reusable(self,kind,tags=None):
        wanted=set(tags or []); return [a for a in self.all() if a.active and a.reusable and a.kind==kind and (not wanted or wanted.intersection(a.tags))]
