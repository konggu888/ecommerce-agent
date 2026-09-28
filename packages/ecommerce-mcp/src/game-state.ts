export type Action = 'INCREASE_BUDGET' | 'DECREASE_BUDGET' | 'INCREASE_BID' | 'DECREASE_BID' | 'HOLD' | 'CHANGE_KEYWORD' | 'CHANGE_TARGETING' | 'CHANGE_PRICE';

export interface CompetitorSnapshot {
  competitorId: string;
  productId?: string;
  price?: number;
  estimatedCtr?: number;
  estimatedCvr?: number;
  trafficShare?: number;
  observedAt: string;
}

export interface GameState {
  shopId: string;
  productId: string;
  campaignId?: string;
  price: number;
  marginPerOrder?: number;
  budget: number;
  spend: number;
  impressions: number;
  clicks: number;
  conversions: number;
  revenue: number;
  ctr?: number;
  cvr?: number;
  cpc?: number;
  roi?: number;
  competitors: CompetitorSnapshot[];
  observedAt: string;
}

export interface ActionEvaluation {
  action: Action;
  expectedImpact: Record<string, number>;
  risks: string[];
  evidence: string[];
  confidence: number;
}

export function evaluateActions(state: GameState): ActionEvaluation[] {
  const out: ActionEvaluation[] = [];
  const roi = state.roi ?? 0;
  const competitorPressure = state.competitors.some(c => (c.trafficShare ?? 0) > 0.5);
  const evaluations: ActionEvaluation[] = [
    { action: 'HOLD', expectedImpact: {}, risks: [], evidence: ['baseline/control'], confidence: 0.5 },
    { action: 'INCREASE_BUDGET', expectedImpact: { spend: 1, revenue: 1 }, risks: ['marginal ROI may decline'], evidence: roi > 2 ? ['positive ROI signal'] : [], confidence: roi > 2 ? 0.65 : 0.35 },
    { action: 'DECREASE_BUDGET', expectedImpact: { spend: -1 }, risks: ['may lose learning/traffic'], evidence: roi > 0 && roi < 1 ? ['weak ROI signal'] : [], confidence: roi > 0 && roi < 1 ? 0.65 : 0.35 },
    { action: 'INCREASE_BID', expectedImpact: { traffic: 1 }, risks: ['higher CPC'], evidence: competitorPressure ? ['high observed competitor pressure'] : [], confidence: competitorPressure ? 0.55 : 0.35 },
    { action: 'DECREASE_BID', expectedImpact: { traffic: -1, cpc: -1 }, risks: ['traffic loss'], evidence: competitorPressure ? [] : ['no strong competitive pressure observed'], confidence: competitorPressure ? 0.35 : 0.55 },
  ];
  out.push(...evaluations);
  return out;
}
