export interface MarketSnapshot {
  shopId: string;
  platform: 'taobao' | 'pinduoduo';
  productId: string;
  observedAt: string;
  price?: number;
  sales?: number;
  adSpend?: number;
  impressions?: number;
  clicks?: number;
  conversions?: number;
  revenue?: number;
  cpc?: number;
  ctr?: number;
  cvr?: number;
  roi?: number;
  marketSignals?: Record<string, number | string | boolean>;
}

export interface CompetitiveState {
  state: 'OWN_PERFORMANCE' | 'PRICE_PRESSURE' | 'TRAFFIC_COST_PRESSURE' | 'CONVERSION_PRESSURE' | 'DEMAND_CHANGE' | 'MIXED' | 'INSUFFICIENT_DATA';
  confidence: number;
  evidence: string[];
  recommendedNextObservation: string[];
}

export interface MarketComparison {
  baseline: MarketSnapshot;
  current: MarketSnapshot;
  deltas: Record<string, number | null>;
  state: CompetitiveState;
}

function pctDelta(current?: number, baseline?: number): number | null {
  if (current == null || baseline == null || baseline === 0) return null;
  return (current - baseline) / Math.abs(baseline);
}

/**
 * Heuristic layer only. It does not claim causal attribution.
 * Causal claims require controlled experiments or stronger external evidence.
 */
export function compareMarketState(baseline: MarketSnapshot, current: MarketSnapshot): MarketComparison {
  const deltas = {
    price: pctDelta(current.price, baseline.price),
    sales: pctDelta(current.sales, baseline.sales),
    spend: pctDelta(current.adSpend, baseline.adSpend),
    impressions: pctDelta(current.impressions, baseline.impressions),
    clicks: pctDelta(current.clicks, baseline.clicks),
    conversions: pctDelta(current.conversions, baseline.conversions),
    revenue: pctDelta(current.revenue, baseline.revenue),
    cpc: pctDelta(current.cpc, baseline.cpc),
    ctr: pctDelta(current.ctr, baseline.ctr),
    cvr: pctDelta(current.cvr, baseline.cvr),
    roi: pctDelta(current.roi, baseline.roi),
  };

  const evidence: string[] = [];
  const recommendedNextObservation: string[] = [];

  const priceDown = (deltas.price ?? 0) < -0.03;
  const priceUp = (deltas.price ?? 0) > 0.03;
  const cpcUp = (deltas.cpc ?? 0) > 0.10;
  const impressionsDown = (deltas.impressions ?? 0) < -0.10;
  const ctrDown = (deltas.ctr ?? 0) < -0.10;
  const cvrDown = (deltas.cvr ?? 0) < -0.10;
  const demandDown = (deltas.sales ?? 0) < -0.10 && impressionsDown;

  if (priceDown) evidence.push('Observed price is lower than baseline.');
  if (priceUp) evidence.push('Observed price is higher than baseline.');
  if (cpcUp) evidence.push('CPC increased materially.');
  if (impressionsDown) evidence.push('Impressions decreased materially.');
  if (ctrDown) evidence.push('CTR decreased materially.');
  if (cvrDown) evidence.push('CVR decreased materially.');
  if (demandDown) evidence.push('Sales and impressions both decreased; demand weakening is a hypothesis.');

  let state: CompetitiveState['state'] = 'OWN_PERFORMANCE';
  let confidence = 0.45;

  if (cpcUp && !cvrDown) {
    state = 'TRAFFIC_COST_PRESSURE';
    confidence = 0.62;
    recommendedNextObservation.push('Compare CPC/CPM changes across comparable campaigns and time windows.');
  } else if (priceDown && (deltas.sales ?? 0) < -0.05) {
    state = 'PRICE_PRESSURE';
    confidence = 0.58;
    recommendedNextObservation.push('Collect comparable market price observations before changing bids.');
  } else if (cvrDown && (deltas.ctr ?? 0) > -0.05) {
    state = 'CONVERSION_PRESSURE';
    confidence = 0.60;
    recommendedNextObservation.push('Check product page, stock, shipping, price and promotion changes.');
  } else if (demandDown) {
    state = 'DEMAND_CHANGE';
    confidence = 0.55;
    recommendedNextObservation.push('Compare multiple products/categories to separate product-specific effects from market demand.');
  } else if (cpcUp && cvrDown) {
    state = 'MIXED';
    confidence = 0.52;
    recommendedNextObservation.push('Run a controlled budget/bid experiment before attributing the change to competition.');
  } else {
    recommendedNextObservation.push('Collect a longer baseline and peer/product comparison before making a structural attribution.');
  }

  return { baseline, current, deltas, state: { state, confidence, evidence, recommendedNextObservation } };
}
