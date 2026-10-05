export type AssetKind="演员"|"场景"|"产品图"|"BGM"|"音效"|"字体"|"模板";
export type Asset={id:string;name:string;kind:AssetKind;source:"系统"|"用户上传"|"AI生成";url?:string;tags:string[];active:boolean};
export const DEFAULT_SCENES:Asset[]=[
{id:"scene-commute",name:"地铁通勤",kind:"场景",source:"系统",tags:["通勤","年轻","生活"],active:true},
{id:"scene-home",name:"家庭客厅",kind:"场景",source:"系统",tags:["家庭","生活","真实"],active:true},
{id:"scene-office",name:"现代办公室",kind:"场景",source:"系统",tags:["职场","专业","高级"],active:true},
{id:"scene-street",name:"城市街头",kind:"场景",source:"系统",tags:["街头","UGC","年轻"],active:true}
];