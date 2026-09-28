import { Action } from './game-state';

export interface SpendStep {
  amount: number;
  incrementalSpend: number;
  expectedRoi: number;
  expectedRevenue: number;
  risk: number;
  continueIf: string;
  stopIf: string;
}

export interface PositionPlan {
  action: Action;
  steps: SpendStep[];
  recommendedAmount: number;
  stopReason: string;
}

export function buildPositionPlan(
  action: Action,
  budget: number,
  currentRoi: number,
  confidence: number,
  opponentRisk: number
): PositionPlan {
  const cap = Math.max(0, budget);
  const base = Math.max(20, Math.min(cap, cap * 0.25));
  const amounts = [base, Math.min(cap, base * 2), Math.min(cap, base * 4)].filter((v, i, a) => v > 0 && a.indexOf(v) === i);
  const steps = amounts.map((amount, i) => {
    const diminishing = Math.max(0.35, 1 - i * 0.18);
    const expectedRoi = Math.max(0, currentRoi * (0.82 + confidence * 0.3) * diminishing);
    const expectedRevenue = amount * expectedRoi;
    const risk = Math.min(1, opponentRisk * (1 + i * 0.25) + (1 - confidence) * 0.25);
    return {
      amount,
      incrementalSpend: i === 0 ? amount : amount - amounts[i - 1],
      expectedRoi,
      expectedRevenue,
      risk,
      continueIf: expectedRoi >= Math.max(1, currentRoi * 0.85) && risk < 0.65
        ? '关键指标达到预期且对手响应风险可控'
        : '不要自动扩大投入',
      stopIf: risk >= 0.65 || expectedRoi < Math.max(1, currentRoi * 0.85)
        ? 'ROI下降或对手响应风险过高'
        : '继续观察下一档'
    };
  });
  const safe = steps.filter(s => s.risk < 0.65 && s.expectedRoi >= Math.max(1, currentRoi * 0.85));
  return {
    action,
    steps,
    recommendedAmount: safe.length ? safe[safe.length - 1].amount : (steps[0]?.amount ?? 0),
    stopReason: safe.length ? '只有在前一档验证通过后才进入下一档' : '当前置信度/对手风险不足以支持扩大投入'
  };
}
