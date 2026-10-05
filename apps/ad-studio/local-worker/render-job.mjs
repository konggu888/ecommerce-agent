import fs from "node:fs";
import path from "node:path";
import {renderShot,concatShots} from "./render-pipeline.mjs";
const projectFile=process.argv[2],shotId=process.argv[3];
if(!projectFile){console.error("用法：node render-job.mjs <项目JSON> [镜头ID]");process.exit(1)}
const p=JSON.parse(fs.readFileSync(projectFile,"utf8"));
const shots=shotId?p.shots.filter(s=>s.id===shotId):p.shots.filter(s=>s.status!=="已生成");
if(!shots.length){console.log("没有需要处理的镜头");process.exit(0)}
for(const s of shots){
 if(!s.videoPath){console.log("镜头 "+s.id+" 等待视频生成器提供源文件；本地工作器只负责后期加工。");continue}
 const out=path.join(path.dirname(projectFile),"renders",p.id,s.id,"v"+s.version+".mp4");
 renderShot(s.videoPath,out);s.finalPath=out;s.status="已生成";
}
p.updatedAt=new Date().toISOString();fs.writeFileSync(projectFile,JSON.stringify(p,null,2),"utf8");
const ready=p.shots.filter(s=>s.finalPath).map(s=>s.finalPath);
if(ready.length===p.shots.length)concatShots(ready,path.join(path.dirname(projectFile),"renders",p.id,"final.mp4"));
console.log("本地后期处理完成");