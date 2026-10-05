import {execFileSync} from "node:child_process";
const tools=["ffmpeg","ffprobe","ollama"],out={};
for(const t of tools){try{const v=execFileSync(t,["-version"],{encoding:"utf8",stdio:["ignore","pipe","ignore"]});out[t]=v.split("\n")[0]}catch{out[t]=null}}
console.log(JSON.stringify(out,null,2));