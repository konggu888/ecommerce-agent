export interface UnitEconomics {
  sellingPrice: number;
  productCost: number;
  fulfillmentCost: number;
  platformFee: number;
  paymentFee: number;
  otherVariableCost: number;
  targetProfitPerOrder?: number;
}

export interface AdConstraints {
  contributionBeforeAds: number;
  breakEvenRoas: number;
  targetRoas?: number;
  maxCpa: number;
  maxCpc?: number;
  maxDailyAdSpend?: number;
}

export function calculateAdConstraints(e: UnitEconomics, cvr = 0): AdConstraints {
  const contributionBeforeAds = e.sellingPrice - e.productCost - e.fulfillmentCost - e.platformFee - e.paymentFee - e.otherVariableCost;
  const targetContribution = e.targetProfitPerOrder ?? 0;
  const adAllowance = contributionBeforeAds - targetContribution;
  const breakEvenRoas = adAllowance > 0 ? e.sellingPrice / adAllowance : Infinity;
  const maxCpa = Math.max(0, adAllowance);
  const maxCpc = cvr > 0 ? maxCpa * cvr : undefined;
  return { contributionBeforeAds, breakEvenRoas, maxCpa, maxCpc };
}

export function isEconomicallyViable(roas: number, constraints: AdConstraints): boolean {
  if (!Number.isFinite(constraints.breakEvenRoas)) return false;
  return roas >= constraints.breakEvenRoas;
}
