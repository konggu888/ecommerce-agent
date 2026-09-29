import { GameState, evaluateActions } from './game-state';
import { calculateAdConstraints, UnitEconomics } from './unit-economics';
import { calculateScaleConstraints, InventoryState, CashflowState } from './inventory-cashflow';
import { evaluateBusinessRisk, RiskPolicy, ProposedAction, RiskDecision } from './risk-controller';
import { modelOpponentResponses, detectBreakthrough, OpponentBreakthrough } from './opponent-model';
import { planMultiRoundGame, MultiRoundPlan } from './multi-round-game';
import { buildPositionPlan, PositionPlan } from './position-sizing';
import { inferOpponentUncertainty } from './threat-inference';
import { rankPositiveStrategies } from './positive-attack-engine';

export interface ClosedLoopInput { state: GameState; economics: UnitEconomics; inventory: InventoryState; cashflow: CashflowState; riskPolicy: RiskPolicy; recentActionCount: number; strategyConfidence?: Record<string, number>; }
export interface ClosedLoopCandidate { action: string; score: number; risk: RiskDecision; reasons: string[]; breakthrough?: OpponentBreakthrough; positionPlan?: PositionPlan; strategyId?: string; strategyName?: string; }
export interface ClosedLoopOutput { candidates: ClosedLoopCandidate[]; blocked: ClosedLoopCandidate[]; recommended: ClosedLoopCandidate | null; multiRound: MultiRoundPlan; }

export function runClosedLoop(input: ClosedLoopInput): ClosedLoopOutput {
  const economics = calculateAdConstraints(input.economics, input.state.cvr ?? 0);
  const contributionAfterAds = Math.max(0, economics.contributionBeforeAds - (input.state.spend / Math.max(1, input.state.conversions)));
  const scale = calculateScaleConstraints(input.inventory, input.cashflow, contributionAfterAds);
  const actions = evaluateActions(input.state);
  const opponent = modelOpponentResponses(input.state);
  const inferenceUncertainty = inferOpponentUncertainty(input.state);
  const multiRound = planMultiRoundGame(input.state, 3);
  const candidates: ClosedLoopCandidate[] = [];
  for (const a of actions) {
    let score = a.confidence;
    const learnedConfidence = input.strategyConfidence?.[a.action];
    if (learnedConfidence !== undefined) score += (learnedConfidence - 0.5) * 0.2;
    const reasons = [...a.evidence];
    if (inferenceUncertainty > 0) reasons.push(`对手行为存在信息不完全：不确定性 ${inferenceUncertainty.toFixed(2)}`);
    if (scale.reasons.length && a.action === 'INCREASE_BUDGET') { score -= 0.3; reasons.push(...scale.reasons); }
    if (!Number.isFinite(economics.breakEvenRoas) && a.action === 'INCREASE_BUDGET') { score -= 0.4; reasons.push('unit economics do not support scaling'); }
    const changePct = a.action === 'INCREASE_BUDGET' || a.action === 'DECREASE_BUDGET' ? 10 : 5;
    score -= inferenceUncertainty * 0.12;
    const proposed: ProposedAction = { action: a.action as ProposedAction['action'], changePct, estimatedDailySpend: input.state.budget, confidence: score };
    const breakthrough = detectBreakthrough({ state: input.state, action: a.action, opponent });
    score += breakthrough.score * 0.25;
    reasons.push(`突破口: ${breakthrough.type} — ${breakthrough.reason}`);
    const risk = evaluateBusinessRisk(proposed, input.riskPolicy, input.recentActionCount, {
      cashAvailable: input.cashflow.availableCash,
      inventory: input.inventory.stockOnHand,
      contributionAfterAds,
      currentRoi: input.state.roi ?? 0,
      marginalRoi: input.state.roi ?? 0,
      opponentRisk: Math.max(breakthrough.opponentResponseRisk, inferenceUncertainty)
    });
    const positionPlan = (a.action === 'INCREASE_BUDGET' || a.action === 'DECREASE_BUDGET' || a.action === 'INCREASE_BID' || a.action === 'DECREASE_BID')
      ? buildPositionPlan(a.action, input.state.budget, input.state.roi ?? 0, Math.max(0, Math.min(1, score)), breakthrough.opponentResponseRisk)
      : undefined;
    if (positionPlan) reasons.push(`分阶段投入: 首档 ${positionPlan.steps[0]?.amount?.toFixed(0) ?? 0}，建议上限 ${positionPlan.recommendedAmount.toFixed(0)}`);
    candidates.push({ action: a.action, score, risk, reasons, breakthrough, positionPlan });
  }
  // Add legitimate positive-growth strategies as distinct candidates.
  // They share the same risk gate and uncertainty model as budget/bid actions.
  const positive = rankPositiveStrategies(input.state, 8);
  for (const p of positive) {
    let score = p.score - inferenceUncertainty * 0.08;
    const reasons = [
      `正向攻势 ${p.strategyId}: ${p.strategyName}`,
      `触发条件: ${p.trigger}`,
      `下一观察: ${p.nextObservation}`,
      '竞品响应仅作为假设，不视为已观测事实'
    ];
    const proposed: ProposedAction = {
      action: p.mappedAction as ProposedAction['action'],
      changePct: 5,
      estimatedDailySpend: input.state.budget,
      confidence: score
    };
    const breakthrough = detectBreakthrough({ state: input.state, action: p.mappedAction, opponent });
    score += breakthrough.score * 0.15;
    const risk = evaluateBusinessRisk(proposed, input.riskPolicy, input.recentActionCount, {
      cashAvailable: input.cashflow.availableCash,
      inventory: input.inventory.stockOnHand,
      contributionAfterAds,
      currentRoi: input.state.roi ?? 0,
      marginalRoi: input.state.roi ?? 0,
      opponentRisk: Math.max(breakthrough.opponentResponseRisk, inferenceUncertainty)
    });
    candidates.push({
      action: p.mappedAction,
      score,
      risk,
      reasons,
      breakthrough,
      strategyId: p.strategyId,
      strategyName: p.strategyName
    });
  }

  candidates.sort((x,y)=>y.score-x.score);
  const blocked = candidates.filter(x => !x.risk.approved);
  const allowed = candidates.filter(x => x.risk.approved);
  return { candidates, blocked, recommended: allowed[0] ?? null, multiRound };
}
