import { Action } from './game-state';

export interface NonlinearMarketInput {
  action: Action;
  budget: number;
  spend: number;
  cpc: number;
  trafficCost: number;
  demand: number;
  categoryCvr: number;
  ctr: number;
  price: number;
  competitorTrafficShare: number;
  competitorPrice?: number;
  inventory: number;
}

export interface NonlinearMarketResult {
  spend: number;
  effectiveCpc: number;
  trafficEfficiency: number;
  ctr: number;
  cvr: number;
  clicks: number;
  conversions: number;
  revenue: number;
  marginalRoi: number;
  totalRoi: number;
  crowding: number;
  bidEscalation: number;
  priceWar: number;
  stockConstraint: number;
  cashConstraint: number;
  stopSignal: boolean;
  stopReason: string;
}

/**
 * Sandbox-only nonlinear response model.
 * It deliberately makes the marginal unit of spend less efficient as:
 * - our spend approaches the available budget,
 * - competitor traffic share rises,
 * - bids are increased repeatedly,
 * - price competition intensifies,
 * - inventory becomes scarce.
 */
export function simulateNonlinearMarket(input: NonlinearMarketInput): NonlinearMarketResult {
  const safeBudget = Math.max(0, input.budget);
  const safeSpend = Math.max(0, Math.min(safeBudget, input.spend));
  const baseCpc = Math.max(0.5, input.trafficCost);
  const competitorShare = Math.max(0, Math.min(0.95, input.competitorTrafficShare));
  const bidEscalation = input.action === 'INCREASE_BID'
    ? 1.12
    : input.action === 'DECREASE_BID'
      ? 0.92
      : 1;

  const budgetUtilization = safeBudget > 0 ? safeSpend / safeBudget : 1;
  const crowding = Math.min(0.55, competitorShare * 0.65 + Math.max(0, budgetUtilization - 0.35) * 0.45);
  const priceGap = input.competitorPrice && input.competitorPrice > 0
    ? (input.price - input.competitorPrice) / input.competitorPrice
    : 0;
  const priceWar = Math.min(0.5, Math.max(0, priceGap) * 1.8 + (input.action === 'CHANGE_PRICE' ? 0.06 : 0));

  const marginalPenalty = Math.min(0.7, budgetUtilization * 0.42 + crowding + (bidEscalation - 1) * 0.7 + priceWar);
  const effectiveCpc = Math.max(0.5, baseCpc * bidEscalation * (1 + crowding * 0.9 + priceWar * 0.35));
  const trafficEfficiency = Math.max(0.2, 1 - marginalPenalty);

  const ctrAction = input.action === 'CHANGE_KEYWORD' ? 1.10
    : input.action === 'CHANGE_TARGETING' ? 1.06
    : 1;
  const cvrAction = input.action === 'CHANGE_PRICE' ? 1.02
    : input.action === 'CHANGE_TARGETING' ? 1.01
    : 1;

  const ctr = Math.max(0.005, Math.min(0.12, input.ctr * ctrAction * (1 - crowding * 0.18)));
  const demandResponse = Math.max(0.55, Math.min(1.35, input.demand * (1 - priceWar * 0.8)));
  const cvr = Math.max(0.005, Math.min(0.2, input.categoryCvr * cvrAction * demandResponse));

  const rawClicks = safeSpend / effectiveCpc * trafficEfficiency;
  const clicks = Math.max(0, Math.floor(rawClicks));
  const stockConstraint = input.inventory <= 0 ? 1 : Math.max(0, Math.min(1, input.inventory / Math.max(1, clicks * cvr)));
  const conversions = Math.min(Math.max(0, input.inventory), Math.floor(clicks * cvr * stockConstraint));
  const revenue = conversions * input.price;
  const totalRoi = safeSpend > 0 ? revenue / safeSpend : 0;

  const previousSpend = Math.max(0, safeSpend * 0.75);
  const previousClicks = previousSpend / Math.max(0.5, baseCpc) * Math.max(0.2, 1 - crowding * 0.7);
  const previousConversions = previousClicks * input.categoryCvr * demandResponse;
  const incrementalSpend = Math.max(1, safeSpend - previousSpend);
  const incrementalRevenue = Math.max(0, revenue - previousConversions * input.price);
  const marginalRoi = incrementalRevenue / incrementalSpend;

  const cashConstraint = safeBudget <= 0 ? 1 : Math.max(0, Math.min(1, safeSpend / safeBudget));
  const stopSignal = marginalRoi < Math.max(0.8, totalRoi * 0.72)
    || stockConstraint < 0.25
    || crowding > 0.48
    || (input.action === 'INCREASE_BID' && effectiveCpc > baseCpc * 1.3);

  let stopReason = '边际收益仍可接受';
  if (marginalRoi < Math.max(0.8, totalRoi * 0.72)) stopReason = '边际ROI明显低于当前整体ROI';
  else if (stockConstraint < 0.25) stopReason = '库存约束已成为主要瓶颈';
  else if (crowding > 0.48) stopReason = '流量拥挤导致新增投入效率过低';
  else if (input.action === 'INCREASE_BID' && effectiveCpc > baseCpc * 1.3) stopReason = '竞价升级使有效CPC过高';

  return {
    spend: safeSpend,
    effectiveCpc,
    trafficEfficiency,
    ctr,
    cvr,
    clicks,
    conversions,
    revenue,
    marginalRoi,
    totalRoi,
    crowding,
    bidEscalation,
    priceWar,
    stockConstraint,
    cashConstraint,
    stopSignal,
    stopReason
  };
}
