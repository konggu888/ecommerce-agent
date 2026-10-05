import fs from "node:fs";
import path from "node:path";
export function writeManifest(project,dir="./data/ad-studio/projects"){
 fs.mkdirSync(dir,{recursive:true}); const file=path.join(dir,project.id+".json");
 fs.writeFileSync(file,JSON.stringify(project,null,2),"utf8"); return file;
}
export function updateShot(projectFile,shotId,patch){
 const p=JSON.parse(fs.readFileSync(projectFile,"utf8")); const i=p.shots.findIndex(s=>s.id===shotId);
 if(i<0)throw new Error("镜头不存在"); p.shots[i]={...p.shots[i],...patch}; p.updatedAt=new Date().toISOString();
 fs.writeFileSync(projectFile,JSON.stringify(p,null,2),"utf8"); return p;
}