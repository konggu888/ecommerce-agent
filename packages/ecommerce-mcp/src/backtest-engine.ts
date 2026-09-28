export interface SimProduct { id: string; price: number; marginPerOrder: number; stock: number; replenishmentDays: number; safetyStockDays: number; }
export interface SimCampaign { id: string; productId: string; budget: number; bid: number; }
export interface SimShop { id: string; products: SimProduct[]; campaigns: SimCampaign[]; cash: number; }
export interface BacktestRound { round: number; shopId: string; spend: number; revenue: number; conversions: number; roi: number; stock: number; cash: number; action?: string; }

export function runBacktest(shop: SimShop, rounds: number, seed = 1): BacktestRound[] {
  let state = JSON.parse(JSON.stringify(shop)) as SimShop;
  const out: BacktestRound[] = [];
  let s = seed >>> 0;
  const rnd = () => { s = (1664525 * s + 1013904223) >>> 0; return s / 4294967296; };
  for (let round = 1; round <= rounds; round++) {
    let spend = 0, revenue = 0, conversions = 0;
    for (const c of state.campaigns) {
      const p = state.products.find(x => x.id === c.productId);
      if (!p) continue;
      const actualSpend = Math.min(c.budget, Math.max(0, state.cash));
      const efficiency = Math.max(0.15, Math.min(2, 0.7 + (c.bid - 1) * 0.25 + (rnd() - 0.5) * 0.2));
      const orders = Math.min(p.stock, Math.floor(actualSpend * efficiency / Math.max(1, p.price * 0.25)));
      spend += actualSpend;
      conversions += orders;
      revenue += orders * p.price;
      p.stock -= orders;
      state.cash = Math.max(0, state.cash - actualSpend + orders * p.marginPerOrder);
    }
    const roi = spend > 0 ? revenue / spend : 0;
    out.push({ round, shopId: state.id, spend, revenue, conversions, roi, stock: state.products.reduce((n,p) => n+p.stock,0) });
  }
  return out;
}
