export type ShotStatus="待生成"|"已生成"|"需重生成";
export type Shot={id:string;index:number;title:string;visual:string;script:string;actorId?:string;sceneId?:string;productAssetIds:string[];status:ShotStatus;version:number;videoPath?:string;audioPath?:string;subtitlePath?:string};
export type ProductionProject={id:string;productName:string;form:string;level:number;actorId?:string;sceneId?:string;shots:Shot[];bgmAssetId?:string;createdAt:string;updatedAt:string};
export function createShots(level:number,form:string,actorId?:string,sceneId?:string):Shot[]{
 const titles=["3秒钩子：直接抛出用户痛点","产品特写：展示核心功能","真人使用：自然场景体验","卖点证明：前后对比/细节","用户反应：强化可信度","结尾CTA：明确行动"];
 return titles.slice(0,level>=3?6:5).map((title,i)=>({id:"shot-"+(i+1),index:i+1,title,visual:sceneId?"调用已选场景完成画面":"等待场景匹配",script:"等待策略引擎生成文案",actorId,sceneId,productAssetIds:[],status:"待生成",version:1}));
}
export function markShotForRegeneration(project:ProductionProject,shotId:string):ProductionProject{
 return {...project,shots:project.shots.map(s=>s.id===shotId?{...s,status:"需重生成",version:s.version+1}:s),updatedAt:new Date().toISOString()};
}