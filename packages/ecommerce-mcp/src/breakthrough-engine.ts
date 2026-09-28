import { GameState } from './game-state';
import { planIntegratedGame } from './integrated-game-planner';

export interface Breakthrough {
 type:'PRICE'|'TRAFFIC'|'CONVERSION'|'CONTENT'|'REPUTATION'|'SUPPLY'|'CASHFLOW'|'RESILIENCE';
 score:number; evidence:string[]; reason:string; firstMove:string; opponentResponse:string; followUp:string; confidence:number;
}
export function findBreakthroughs(state:GameState):Breakthrough[] {
 const plan=planIntegratedGame(state,3), roi=state.roi??0, cvr=state.cvr??0, ctr=state.ctr??0;
 const out:Breakthrough[]=[];
 if(roi>2.5) out.push({type:'TRAFFIC',score:.78,evidence:['ROI '+roi.toFixed(2)],reason:'单位经济允许扩大有效流量测试',firstMove:plan.bestPath[0]??'HOLD',opponentResponse:plan.nodes[0]?.opponentAction??'等待观察',followUp:plan.bestPath[1]??'HOLD',confidence:.68});
 if(cvr<.03) out.push({type:'CONVERSION',score:.74,evidence:['CVR '+(cvr*100).toFixed(2)+'%'],reason:'转化率可能是比继续加流量更直接的突破口',firstMove:'CONTENT_ANGLE',opponentResponse:'改变内容打法',followUp:'DIFFERENTIATE_PRODUCT',confidence:.65});
 if(ctr<.03) out.push({type:'CONTENT',score:.72,evidence:['CTR '+(ctr*100).toFixed(2)+'%'],reason:'注意力获取可能限制流量效率',firstMove:'CREATIVE_REFRESH',opponentResponse:'创意反击',followUp:'CONTENT_ANGLE',confidence:.62});
 out.push({type:'RESILIENCE',score:plan.robustness,evidence:['多轮鲁棒性 '+plan.robustness.toFixed(2)],reason:'突破口不仅看短期收益，还看对手反击后的持续性',firstMove:plan.bestPath[0]??'HOLD',opponentResponse:plan.nodes[0]?.opponentAction??'等待观察',followUp:plan.bestPath[1]??'HOLD',confidence:.6});
 return out.sort((a,b)=>b.score-a.score);
}