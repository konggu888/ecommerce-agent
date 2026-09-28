export interface InventoryState {
  stockOnHand: number;
  reservedStock: number;
  avgDailyUnits: number;
  replenishmentDays: number;
  safetyStockDays: number;
  inboundUnits?: number;
}

export interface CashflowState {
  availableCash: number;
  pendingReceivables: number;
  payableDue: number;
  dailyOperatingCashNeed: number;
  adSpendAlreadyCommitted: number;
}

export interface ScaleConstraints {
  safeDailyUnits: number;
  stockCoverageDays: number;
  maxAdditionalAdSpend: number;
  reasons: string[];
}

export function calculateScaleConstraints(i: InventoryState, c: CashflowState, contributionPerOrderAfterAds: number): ScaleConstraints {
  const sellable = Math.max(0, i.stockOnHand - i.reservedStock + (i.inboundUnits ?? 0));
  const stockCoverageDays = i.avgDailyUnits > 0 ? sellable / i.avgDailyUnits : Infinity;
  const safeDays = Math.max(1, i.replenishmentDays + i.safetyStockDays);
  const safeDailyUnits = sellable / safeDays;
  const cashAvailableForAds = Math.max(0, c.availableCash + c.pendingReceivables - c.payableDue - c.dailyOperatingCashNeed - c.adSpendAlreadyCommitted);
  const maxAdditionalAdSpend = contributionPerOrderAfterAds > 0 ? cashAvailableForAds : 0;
  const reasons: string[] = [];
  if (stockCoverageDays < safeDays) reasons.push('inventory coverage is below replenishment plus safety buffer');
  if (cashAvailableForAds <= 0) reasons.push('cashflow does not support additional committed ad spend');
  return { safeDailyUnits, stockCoverageDays, maxAdditionalAdSpend, reasons };
}
