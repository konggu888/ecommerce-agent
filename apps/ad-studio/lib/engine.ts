import type {CostEstimate,HardwareProfile,Platform} from "./types";
export function detectPlatform(raw:string):Platform{const u=raw.toLowerCase();if(/taobao|tmall/.test(u))return"淘宝";if(/jd\\.com/.test(u))return"京东";if(/pinduoduo|yangkeduo/.test(u))return"拼多多";if(/1688\\.com/.test(u))return"1688";if(/douyin/.test(u))return"抖音";return"自动识别";}
export function estimateCost(shots:number,cloudShots=Math.min(3,Math.ceil(shots/2))):CostEstimate{const cloud=Number((cloudShots*0.72).toFixed(2));const total=cloud;return{local:0,cloud,total,budget:3,overBudget:total>3};}
export function localPlan(hardware:HardwareProfile){return{local:["商品解析","策略分析","文案剧本","字幕","剪辑合成","视频编码"],cloud:["人物生成","场景生成","关键视频镜头","高质量配音"],note:hardware.vramGb<=6?"6GB显存模式：小模型与视频后处理本地执行，重生成任务不占用本地显存。":"高显存模式：允许扩展本地生成任务。"};}
