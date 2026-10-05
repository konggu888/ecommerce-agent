import {execFileSync} from "node:child_process";
import fs from "node:fs";
const input=process.argv[2],output=process.argv[3]||"ad-studio-demo.mp4";
if(!input||!fs.existsSync(input)){console.error("用法：node render-demo.mjs <输入视频> [输出视频]");process.exit(1)}
try{execFileSync("ffmpeg",["-y","-i",input,"-vf","scale=1080:-2:flags=lanczos,fps=30","-c:v","libx264","-preset","medium","-crf","20","-c:a","aac","-b:a","128k",output],{stdio:"inherit"});console.log("本地广告后期任务完成："+output)}catch{console.error("未找到FFmpeg或渲染失败。");process.exit(1)}