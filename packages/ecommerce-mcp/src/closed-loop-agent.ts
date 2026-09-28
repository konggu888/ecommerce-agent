import { GameState, evaluateActions } from './game-state';
import { calculateAdConstraints, UnitEconomics } from './unit-economics';
import { calculateScaleConstraints, InventoryState, CashflowState } from './inventory-cashflow';
import { evaluateRisk, RiskPolicy, ProposedAction, RiskDecision } from './risk-controller';

export interface ClosedLoopInput { state: GameState; economics: UnitEconomics; inventory: InventoryState; cashflow: CashflowState; riskPolicy: RiskPolicy; recentActionCount: number; }
export interface ClosedLoopCandidate { action: string; score: number; risk: RiskDecision; reasons: string[]; }
export interface ClosedLoopOutput { candidates: ClosedLoopCandidate[]; blocked: ClosedLoopCandidate[]; recommended: ClosedLoopCandidate | null; }

export function runClosedLoop(input: ClosedLoopInput): ClosedLoopOutput {
  const economics = calculateAdConstraints(input.economics, input.state.cvr ?? 0);
  const contributionAfterAds = Math.max(0, economics.contributionBeforeAds - (input.state.spend / Math.max(1, input.state.conversions)));
  const scale = calculateScaleConstraints(input.inventory, input.cashflow, contributionAfterAds);
  const actions = evaluateActions(input.state);
  const candidates: ClosedLoopCandidate[] = [];
  for (const a of actions) {
    let score = a.confidence;
    const reasons = [...a.evidence];
    if (scale.reasons.length && a.action === 'INCREASE_BUDGET') { score -= 0.3; reasons.push(...scale.reasons); }
    if (!Number.isFinite(economics.breakEvenRoas) && a.action === 'INCREASE_BUDGET') { score -= 0.4; reasons.push('unit economics do not support scaling'); }
    const changePct = a.action === 'INCREASE_BUDGET' || a.action === 'DECREASE_BUDGET' ? 10 : 5;
    const proposed: ProposedAction = { action: a.action as ProposedAction['action'], changePct, estimatedDailySpend: input.state.budget, confidence: score };
    const risk = evaluateRisk(proposed, input.riskPolicy, input.recentActionCount);
    candidates.push({ action: a.action, score, risk, reasons });
  }
  candidates.sort((x,y)=>y.score-x.score);
  const blocked = candidates.filter(x => !x.risk.approved);
  const allowed = candidates.filter(x => x.risk.approved);
  return { candidates, blocked, recommended: allowed[0] ?? null };
}
