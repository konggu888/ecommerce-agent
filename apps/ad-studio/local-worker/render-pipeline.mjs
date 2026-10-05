import {execFileSync} from "node:child_process";
import fs from "node:fs";
import path from "node:path";
export function renderShot(input,output){
 fs.mkdirSync(path.dirname(output),{recursive:true});
 execFileSync("ffmpeg",["-y","-i",input,"-vf","scale=1080:-2:flags=lanczos,fps=30","-c:v","libx264","-preset","medium","-crf","20","-c:a","aac","-b:a","128k",output],{stdio:"inherit"}); return output;
}
export function concatShots(shotFiles,output){
 const list=output+".txt"; fs.writeFileSync(list,shotFiles.map(f=>"file '"+path.resolve(f).replaceAll("'","'\\''")+"'").join("\n"),"utf8");
 execFileSync("ffmpeg",["-y","-f","concat","-safe","0","-i",list,"-c","copy",output],{stdio:"inherit"}); fs.rmSync(list,{force:true}); return output;
}