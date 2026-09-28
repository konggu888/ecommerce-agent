import { GameState } from './game-state';
import { modelOpponentResponses } from './opponent-model';
import { buildOpponentBehaviorTree, rankOpponentBranches } from './opponent-behavior-tree';

export interface StrategyPathNode { round:number; action:string; opponentAction:string; immediateScore:number; continuationScore:number; threatScore:number; humanFactors:string[]; blockedFromAutomation:boolean; }
export interface IntegratedGamePlan { horizon:number; nodes:StrategyPathNode[]; bestPath:string[]; bestScore:number; robustness:number; strategyMix:string[]; explanation:string[]; }

const actions=['HOLD','INCREASE_BUDGET','DECREASE_BUDGET','INCREASE_BID','DECREASE_BID','CHANGE_KEYWORD','CHANGE_TARGETING','CHANGE_PRICE','CONTENT_ANGLE','CREATIVE_REFRESH','BUNDLE_VALUE','DIFFERENTIATE_PRODUCT','SERVICE_SPEED','REVIEW_RECOVERY','PRODUCT_QA','STOCK_ADVANTAGE','LAUNCH_TIMING','DAYPARTING','CHANNEL_SHIFT','COMPETITOR_MONITORING','LEGITIMATE_PLATFORM_REPORT','COMPLIANCE_REMEDIATION'];

function baseScore(s:GameState,a:string):number {
 const roi=s.roi??0,cvr=s.cvr??0,ctr=s.ctr??0;
 if(a==='HOLD')return .35;if(a==='INCREASE_BUDGET')return roi>2.5?.62:.34;if(a==='DECREASE_BUDGET')return roi<1.5?.62:.3;
 if(a==='INCREASE_BID')return roi>2&&ctr>.02?.58:.35;if(a==='DECREASE_BID')return roi<2?.55:.38;
 if(a==='CHANGE_KEYWORD')return ctr<.03?.68:.55;if(a==='CHANGE_TARGETING')return cvr>.03?.72:.58;
 const m:Record<string,number>={CHANGE_PRICE:.55,CONTENT_ANGLE:.62,CREATIVE_REFRESH:.6,BUNDLE_VALUE:.63,DIFFERENTIATE_PRODUCT:.7,SERVICE_SPEED:.58,REVIEW_RECOVERY:.55,PRODUCT_QA:.62,STOCK_ADVANTAGE:.64,LAUNCH_TIMING:.5,DAYPARTING:.5,CHANNEL_SHIFT:.56,COMPETITOR_MONITORING:.48,LEGITIMATE_PLATFORM_REPORT:.4,COMPLIANCE_REMEDIATION:.5}; return m[a]??.3;
}
function project(s:GameState,a:string):GameState { const n={...s}; if(a==='INCREASE_BUDGET')n.budget*=1.1;if(a==='DECREASE_BUDGET')n.budget*=.9;if(a==='CHANGE_PRICE')n.price*=.98;if(a==='INCREASE_BID')n.cpc=(n.cpc??1)*1.05;if(a==='DECREASE_BID')n.cpc=(n.cpc??1)*.95;if(a==='CHANGE_TARGETING')n.cvr=(n.cvr??0)*1.05+.002;if(a==='CHANGE_KEYWORD')n.ctr=(n.ctr??0)*1.06+.001;return n; }
function factors(a:string):string[]{const m:Record<string,string[]>={CHANGE_PRICE:['价格敏感','损失厌恶'],BUNDLE_VALUE:['价值感知','便利性'],CONTENT_ANGLE:['注意力','好奇心'],CREATIVE_REFRESH:['注意力'],DIFFERENTIATE_PRODUCT:['信任','转换成本'],SERVICE_SPEED:['便利性','风险规避'],REVIEW_RECOVERY:['社会证明','信任'],PRODUCT_QA:['风险规避','信任'],STOCK_ADVANTAGE:['稀缺性','紧迫感'],LAUNCH_TIMING:['紧迫感','注意力'],CHANNEL_SHIFT:['便利性'],COMPETITOR_MONITORING:['信息优势'],LEGITIMATE_PLATFORM_REPORT:['风险规避'],COMPLIANCE_REMEDIATION:['风险规避']};return m[a]??[];}

export function planIntegratedGame(state:GameState,horizon=3):IntegratedGamePlan {
 const depth=Math.max(1,Math.min(5,horizon)),ranked=rankOpponentBranches(buildOpponentBehaviorTree()),nodes:StrategyPathNode[]=[];let bestPath:string[]=[],bestScore=-Infinity;
 function search(cur:GameState,round:number,score:number,path:string[]){if(round>depth){if(score>bestScore){bestScore=score;bestPath=[...path];}return;}const opponent=modelOpponentResponses(cur);for(const a of actions){const threat=ranked[(round-1)%Math.max(1,ranked.length)];const copyable=(a==='CHANGE_PRICE'&&threat?.kind==='PRICE')||(a.includes('BID')&&threat?.kind==='AD');const severe=['REPUTATION','REPORTING','PLATFORM','INFORMATION'].includes(threat?.kind??'');const penalty=(threat?.threatScore??0)*(copyable?.35:.12)+(severe?.06:0);const immediate=baseScore(cur,a)-penalty;const total=score+immediate*Math.pow(.85,round-1);nodes.push({round,action:a,opponentAction:threat?.action??(opponent[0]?.response??'等待观察'),immediateScore:immediate,continuationScore:total,threatScore:threat?.threatScore??0,humanFactors:factors(a),blockedFromAutomation:a==='LEGITIMATE_PLATFORM_REPORT'||a==='REVIEW_RECOVERY'});search(project(cur,a),round+1,total,[...path,a]);}}
 search(state,1,0,[]);const selected=nodes.filter(n=>bestPath.includes(n.action));const avg=selected.length?selected.reduce((x,n)=>x+n.threatScore,0)/selected.length:0;
 return {horizon:depth,nodes,bestPath,bestScore,robustness:Math.max(0,Math.min(1,1-avg)),strategyMix:[...new Set(bestPath)],explanation:['搜索视野 '+depth+' 轮','候选节点 '+nodes.length,'同时考虑人性策略、对手行为树与恶意竞争压力','恶意举报、恶意评价等只作为对手行为与防御压力测试，不进入自动执行']};
}