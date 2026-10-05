export type ActorSource="系统生成"|"用户上传"|"AI生成";
export type Actor={id:string;name:string;gender:"男"|"女";age:number;style:string;source:ActorSource;assetUrl?:string;tags:string[];active:boolean};
export const DEFAULT_ACTORS:Actor[]=[
{id:"actor-linchuan",name:"林川",gender:"男",age:28,style:"自然、可信、生活化",source:"系统生成",tags:["口播","生活","通勤"],active:true},
{id:"actor-zhounye",name:"周野",gender:"男",age:32,style:"成熟、专业、强转化",source:"系统生成",tags:["专业","测评","强转化"],active:true},
{id:"actor-suning",name:"苏宁",gender:"女",age:26,style:"亲和、轻松、种草感",source:"系统生成",tags:["种草","生活","UGC"],active:true},
{id:"actor-guyao",name:"顾瑶",gender:"女",age:31,style:"高级、理性、专业",source:"系统生成",tags:["高级","职场","专业"],active:true}
];
export function selectActors(actors:Actor[],gender?:Actor["gender"],tags:string[]=[]){
 const pool=actors.filter(a=>a.active&&(!gender||a.gender===gender));
 const scored=pool.map(a=>({...a,score:tags.filter(t=>a.tags.includes(t)).length})).sort((a,b)=>b.score-a.score);
 return scored.slice(0,2);
}