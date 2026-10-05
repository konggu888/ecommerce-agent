export const BUDGET_RMB=3;
export type CostDecision={estimatedRmb:number;requiresConfirmation:boolean;autoSwitchAllowed:false;qualityReductionAllowed:false};
export function enforceBudget(estimatedRmb:number):CostDecision{return{estimatedRmb,requiresConfirmation:estimatedRmb>BUDGET_RMB,autoSwitchAllowed:false,qualityReductionAllowed:false};}