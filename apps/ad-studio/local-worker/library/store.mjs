import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

export class LocalAssetLibrary {
  constructor(root=path.resolve(process.env.AD_STUDIO_DATA_DIR||"./data/ad-studio")) {
    this.root=root; this.assetsDir=path.join(root,"assets"); this.indexFile=path.join(root,"library.json");
    fs.mkdirSync(this.assetsDir,{recursive:true});
    if(!fs.existsSync(this.indexFile)) fs.writeFileSync(this.indexFile,JSON.stringify({version:1,assets:[]},null,2),"utf8");
  }
  read(){return JSON.parse(fs.readFileSync(this.indexFile,"utf8"))}
  write(data){const tmp=this.indexFile+".tmp";fs.writeFileSync(tmp,JSON.stringify(data,null,2),"utf8");fs.renameSync(tmp,this.indexFile)}
  list(kind){return this.read().assets.filter(a=>a.active&&(!kind||a.kind===kind))}
  get(id){return this.read().assets.find(a=>a.id===id)||null}
  add({kind,name,source="user_upload",metadata={},tags=[],filePath=null}){
    const id=crypto.randomUUID(); let storedPath=null;
    if(filePath){const ext=path.extname(filePath);storedPath=path.join(this.assetsDir,id+ext);fs.copyFileSync(filePath,storedPath)}
    const item={id,kind,name,source,metadata,tags,reusable:true,active:true,assetPath:storedPath,createdAt:new Date().toISOString(),updatedAt:new Date().toISOString()};
    const db=this.read();db.assets.push(item);this.write(db);return item;
  }
  remove(id){const db=this.read(),item=db.assets.find(a=>a.id===id);if(!item)return false;item.active=false;item.updatedAt=new Date().toISOString();this.write(db);return true}
  findReusable(kind,tags=[]){return this.list(kind).map(a=>({...a,score:tags.filter(t=>a.tags.includes(t)).length})).sort((a,b)=>b.score-a.score)}
}