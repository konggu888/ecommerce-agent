export type CampaignObservation = {
  campaignId: string;
  spend: number;
  revenue: number;
  clicks: number;
  impressions: number;
  conversions: number;
  budget: number;
  bid: number;
  grossMarginRate: number;
  previousRoi?: number;
  previousCvr?: number;
};

export type DecisionAction = 'increase_budget' | 'decrease_budget' | 'increase_bid' | 'decrease_bid' | 'hold';

export type DecisionProposal = {
  campaignId: string;
  action: DecisionAction;
  changePct: number;
  rationale: string;
  expectedEffect: string;
  confidence: number;
  requiresApproval: boolean;
};

const safeRatio = (n: number, d: number) => (d > 0 ? n / d : 0);

export function analyzeCampaign(c: CampaignObservation): DecisionProposal {
  const roi = safeRatio(c.revenue, c.spend);
  const cvr = safeRatio(c.conversions, c.clicks);
  const ctr = safeRatio(c.clicks, c.impressions);
  const breakEvenRoi = c.grossMarginRate > 0 ? 1 / c.grossMarginRate : Infinity;

  if (c.spend <= 0 || c.impressions <= 0) {
    return { campaignId: c.campaignId, action: 'hold', changePct: 0, rationale: 'Insufficient data for a controlled change.', expectedEffect: 'Collect more observations.', confidence: 0.2, requiresApproval: true };
  }

  if (roi < breakEvenRoi * 0.8) {
    return { campaignId: c.campaignId, action: 'decrease_budget', changePct: 10, rationale: `ROI ${roi.toFixed(2)} is materially below estimated break-even ROI ${breakEvenRoi.toFixed(2)}.`, expectedEffect: 'Reduce inefficient spend while preserving a controlled learning sample.', confidence: 0.72, requiresApproval: true };
  }

  if (roi > breakEvenRoi * 1.4 && cvr > 0 && ctr > 0) {
    return { campaignId: c.campaignId, action: 'increase_budget', changePct: 10, rationale: `ROI ${roi.toFixed(2)} is materially above estimated break-even and conversion signals are non-zero.`, expectedEffect: 'Test incremental spend and observe marginal ROI.', confidence: 0.68, requiresApproval: true };
  }

  if (c.previousCvr !== undefined && cvr < c.previousCvr * 0.75) {
    return { campaignId: c.campaignId, action: 'decrease_bid', changePct: 5, rationale: 'Current CVR is materially below the previous observation.', expectedEffect: 'Reduce acquisition pressure while monitoring conversion recovery.', confidence: 0.58, requiresApproval: true };
  }

  return { campaignId: c.campaignId, action: 'hold', changePct: 0, rationale: 'Current evidence does not justify a controlled intervention.', expectedEffect: 'Continue observation and compare against baseline.', confidence: 0.55, requiresApproval: true };
}

export function analyzePortfolio(campaigns: CampaignObservation[]) {
  return campaigns.map(analyzeCampaign);
}
