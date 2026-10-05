import {execFileSync} from "node:child_process";
function run(cmd,args){try{return execFileSync(cmd,args,{encoding:"utf8",stdio:["ignore","pipe","pipe"]}).trim()}catch{return null}}
const name=run("nvidia-smi",["--query-gpu=name","--format=csv,noheader"]);
const mem=run("nvidia-smi",["--query-gpu=memory.total","--format=csv,noheader"]);
const driver=run("nvidia-smi",["--query-gpu=driver_version","--format=csv,noheader"]);
if(!name){console.log(JSON.stringify({ok:false,message:"未检测到 NVIDIA GPU；请安装 NVIDIA 驱动后重试。"},null,2));process.exit(1)}
const m=mem?Number.parseFloat(mem):null;
console.log(JSON.stringify({ok:true,gpu:name,vramGb:m?Math.round(m/1024*10)/10:null,driver,mode:m&&m<=7?"4050/6GB保守模式":"高显存模式"},null,2));