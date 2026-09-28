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
