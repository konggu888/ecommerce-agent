export type Action = 'INCREASE_BUDGET' | 'DECREASE_BUDGET' | 'INCREASE_BID' | 'DECREASE_BID' | 'HOLD' | 'CHANGE_KEYWORD' | 'CHANGE_TARGETING' | 'CHANGE_PRICE' | 'CREATIVE_REFRESH' | 'DETAIL_PAGE_REFRESH' | 'CONTENT_VIDEO' | 'UGC_CONTENT' | 'REVIEW_QUALITY' | 'BRAND_COLLAB' | 'BRAND_AUTHORIZED_PRODUCT' | 'CERTIFICATION' | 'EXPERT_ENDORSEMENT' | 'SCENARIO_POSITIONING' | 'AUDIENCE_SEGMENTATION' | 'BUNDLE_VALUE' | 'SKU_LADDER' | 'PRODUCT_ITERATION' | 'PRODUCT_DIFFERENTIATION' | 'PACKAGING_UPGRADE' | 'FULFILLMENT_SPEED' | 'SERVICE_PROMISE' | 'CUSTOMER_SERVICE' | 'CONTENT_MATRIX' | 'LIVE_DEMO' | 'CREATOR_COLLAB' | 'SEARCH_CONTENT' | 'BRAND_SEARCH' | 'REPEAT_PURCHASE' | 'MEMBERSHIP' | 'CUSTOMER_NEW_PRODUCT_TEST' | 'CROSS_CATEGORY' | 'CHANNEL_EXPANSION' | 'REGIONAL_EXPANSION' | 'SEASONAL_WINDOW' | 'EVENT_CONTENT' | 'SUPPLY_CHAIN' | 'EXCLUSIVE_SUPPLY' | 'COST_STRUCTURE' | 'PRICE_ARCHITECTURE' | 'SOCIAL_PROOF' | 'COMPOUND_GROWTH' | 'PAUSE_CAMPAIGN' | 'RESUME_CAMPAIGN';

export interface CompetitorSnapshot {
  competitorId: string;
  productId?: string;
  price?: number;
  estimatedCtr?: number;
  estimatedCvr?: number;
  trafficShare?: number;
  observedAt: string;
}

import { ThreatInference } from './threat-inference';
import { BehaviorState } from './human-behavior-engine';

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
  /** Evidence-based threat hypotheses; never treated as direct attribution. */
  threatInferences?: ThreatInference[];
  /** Persistent, evidence-based opponent behavior state; not a psychological diagnosis. */
  behaviorState?: BehaviorState;
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
    { action: 'CHANGE_KEYWORD', expectedImpact: { ctr: 1 }, risks: ['may change traffic mix'], evidence: ['can test intent quality without direct price change'], confidence: 0.5 },
    { action: 'CHANGE_TARGETING', expectedImpact: { ctr: 1, traffic: 1 }, risks: ['audience volume may shrink'], evidence: ['can redirect traffic away from weak segments'], confidence: competitorPressure ? 0.58 : 0.48 },
    { action: 'CHANGE_PRICE', expectedImpact: { cvr: 1 }, risks: ['margin and price perception may change'], evidence: ['direct conversion lever when price gap exists'], confidence: state.competitors.some(c => (c.price ?? state.price) < state.price * 0.97) ? 0.42 : 0.52 },
  ];
  out.push(...evaluations);
  return out;
}
