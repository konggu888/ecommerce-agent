export const DECISION_STEPS = Object.freeze([
  'market_analysis', 'competitor_analysis', 'product_analysis',
  'advertising_analysis', 'game_analysis', 'opportunity_detection',
  'decision', 'risk_check', 'execution'
]);

export function createDecisionContext(input = {}) {
  return { ...input, steps: [...DECISION_STEPS] };
}
