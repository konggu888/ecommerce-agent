export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'BLOCKED';
export type ExecutionMode = 'ANALYZE_ONLY' | 'APPROVAL_REQUIRED' | 'AUTO_LIMITED' | 'AUTO_DISABLED';

export interface RiskPolicy {
  maxBudgetChangePct: number;
  maxBidChangePct: number;
  maxDailySpend: number;
  maxActionsPerHour: number;
  allowBudgetChange: boolean;
  allowBidChange: boolean;
  allowPause: boolean;
}

export interface ProposedAction {
  action: 'INCREASE_BUDGET' | 'DECREASE_BUDGET' | 'INCREASE_BID' | 'DECREASE_BID' | 'PAUSE_CAMPAIGN' | 'RESUME_CAMPAIGN';
  currentValue?: number;
  requestedValue?: number;
  changePct?: number;
  estimatedDailySpend?: number;
  confidence: number;
}

export interface RiskDecision {
  level: RiskLevel;
  mode: ExecutionMode;
  approved: boolean;
  reasons: string[];
  dimensions?: {
    capital: number;
    unitEconomics: number;
    market: number;
    operations: number;
    opponent: number;
    overall: number;
  };
  recommendedChangePct?: number;
  stopConditions?: string[];
}

export interface BusinessRiskContext {
  cashAvailable?: number;
  inventory?: number;
  contributionAfterAds?: number;
  currentRoi?: number;
  marginalRoi?: number;
  crowding?: number;
  priceWar?: number;
  opponentRisk?: number;
  stopSignal?: boolean;
}

export function evaluateBusinessRisk(
  action: ProposedAction,
  policy: RiskPolicy,
  recentActionCount: number,
  context: BusinessRiskContext = {}
): RiskDecision {
  const base = evaluateRisk(action, policy, recentActionCount);
  const capital = action.estimatedDailySpend && context.cashAvailable !== undefined
    ? Math.min(1, action.estimatedDailySpend / Math.max(1, context.cashAvailable)) : 0;
  const unitEconomics = context.marginalRoi !== undefined && context.currentRoi !== undefined
    ? Math.min(1, Math.max(0, (context.currentRoi - context.marginalRoi) / Math.max(1, context.currentRoi))) : 0;
  const market = Math.min(1, Math.max(context.crowding ?? 0, context.priceWar ?? 0));
  const operations = context.inventory !== undefined && context.inventory < 10 ? 0.8 : 0;
  const opponent = Math.min(1, context.opponentRisk ?? 0);
  const overall = Math.min(1, capital * 0.2 + unitEconomics * 0.3 + market * 0.2 + operations * 0.1 + opponent * 0.2);
  const reasons = [...base.reasons];
  if (context.stopSignal) reasons.push('nonlinear market stop signal triggered');
  if (capital >= 0.8) reasons.push('capital utilization is too high');
  if (unitEconomics >= 0.5) reasons.push('marginal economics are deteriorating');
  if (market >= 0.7) reasons.push('market pressure is high');
  if (operations >= 0.7) reasons.push('inventory constraint is high');
  if (opponent >= 0.7) reasons.push('opponent response risk is high');

  const hardBlock = !base.approved || context.stopSignal || overall >= 0.8;
  const level: RiskLevel = hardBlock ? 'BLOCKED' : overall >= 0.55 ? 'HIGH' : overall >= 0.3 ? 'MEDIUM' : 'LOW';
  const mode: ExecutionMode = hardBlock ? 'AUTO_DISABLED' : level === 'HIGH' ? 'APPROVAL_REQUIRED' : 'AUTO_LIMITED';
  return {
    level, mode, approved: !hardBlock, reasons,
    dimensions: { capital, unitEconomics, market, operations, opponent, overall },
    recommendedChangePct: hardBlock ? 0 : level === 'HIGH' ? Math.min(policy.maxBudgetChangePct, 5) : Math.min(policy.maxBudgetChangePct, 10),
    stopConditions: ['边际ROI持续下降', '对手反击风险显著上升', '库存或现金约束触发', '非线性市场发出停止信号']
  };
}

export function evaluateRisk(action: ProposedAction, policy: RiskPolicy, recentActionCount: number): RiskDecision {
  const reasons: string[] = [];
  if (recentActionCount >= policy.maxActionsPerHour) reasons.push('hourly action limit reached');
  if (action.estimatedDailySpend !== undefined && action.estimatedDailySpend > policy.maxDailySpend) reasons.push('daily spend limit exceeded');
  const pct = Math.abs(action.changePct ?? 0);
  if ((action.action === 'INCREASE_BUDGET' || action.action === 'DECREASE_BUDGET') && (!policy.allowBudgetChange || pct > policy.maxBudgetChangePct)) reasons.push('budget change exceeds policy');
  if ((action.action === 'INCREASE_BID' || action.action === 'DECREASE_BID') && (!policy.allowBidChange || pct > policy.maxBidChangePct)) reasons.push('bid change exceeds policy');
  if ((action.action === 'PAUSE_CAMPAIGN' || action.action === 'RESUME_CAMPAIGN') && !policy.allowPause) reasons.push('campaign state change is disabled');
  if (action.confidence < 0.7) reasons.push('confidence below auto-execution threshold');

  if (reasons.some(r => r.includes('exceeded') || r.includes('disabled') || r.includes('limit reached'))) return { level: 'BLOCKED', mode: 'AUTO_DISABLED', approved: false, reasons };
  if (reasons.length) return { level: 'HIGH', mode: 'APPROVAL_REQUIRED', approved: false, reasons };
  return { level: 'LOW', mode: 'AUTO_LIMITED', approved: true, reasons: [] };
}
