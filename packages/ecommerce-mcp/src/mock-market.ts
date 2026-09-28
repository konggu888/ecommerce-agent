export type Platform = 'taobao' | 'pinduoduo';

export interface MockCampaign {
  shopId: string;
  platform: Platform;
  campaignId: string;
  productId: string;
  budget: number;
  bid: number;
  impressions: number;
  clicks: number;
  conversions: number;
  spend: number;
  revenue: number;
  roi: number;
}

export interface MarketAction {
  shopId: string;
  campaignId: string;
  budgetDelta?: number;
  bidDelta?: number;
}

export interface SimulationResult {
  before: MockCampaign[];
  after: MockCampaign[];
  actions: MarketAction[];
}

/**
 * Offline-only simulator. It deliberately models responses to budget/bid changes
 * without pretending to reproduce any platform's proprietary auction algorithm.
 */
export function simulateMarket(campaigns: MockCampaign[], actions: MarketAction[]): SimulationResult {
  const before = structuredClone(campaigns);
  const after = structuredClone(campaigns);

  for (const action of actions) {
    const campaign = after.find(c => c.shopId === action.shopId && c.campaignId === action.campaignId);
    if (!campaign) continue;

    const budgetFactor = action.budgetDelta ? Math.max(0.5, Math.min(1.5, 1 + action.budgetDelta / Math.max(campaign.budget, 1))) : 1;
    const bidFactor = action.bidDelta ? Math.max(0.7, Math.min(1.3, 1 + action.bidDelta / Math.max(campaign.bid, 0.01))) : 1;
    const demandFactor = 0.65 + 0.35 * Math.min(1.5, budgetFactor);
    const auctionFactor = 0.75 + 0.25 * Math.min(1.3, bidFactor);

    campaign.budget = Math.max(0, campaign.budget + (action.budgetDelta ?? 0));
    campaign.bid = Math.max(0, campaign.bid + (action.bidDelta ?? 0));
    campaign.impressions = Math.max(0, Math.round(campaign.impressions * demandFactor * auctionFactor));
    campaign.clicks = Math.max(0, Math.round(campaign.clicks * (0.9 + 0.1 * auctionFactor)));
    campaign.conversions = Math.max(0, Math.round(campaign.conversions * (0.95 + 0.05 * demandFactor)));
    campaign.spend = Math.max(0, campaign.spend * auctionFactor * demandFactor);
    campaign.revenue = Math.max(0, campaign.revenue * (0.95 + 0.05 * demandFactor));
    campaign.roi = campaign.spend > 0 ? campaign.revenue / campaign.spend : 0;
  }

  return { before, after, actions };
}
