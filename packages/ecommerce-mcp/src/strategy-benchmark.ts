import { runBacktest, SimShop, BacktestRound } from './backtest-engine';

export type Strategy = 'NO_CHANGE' | 'FIXED_RULE' | 'GAME_AGENT';
export type Scenario = 'NORMAL' | 'COMPETITION' | 'TRAFFIC_COST' | 'LOW_CVR' | 'PRICE_WAR' | 'LOW_STOCK' | 'CASH_TIGHT' | 'DEMAND_SURGE';

export interface BenchmarkResult { strategy: Strategy; scenario: Scenario; totalSpend: number; totalRevenue: number; totalConversions: number; finalStock: number; finalCash: number; avgRoi: number; actionCount: number; }

function applyStrategy(shop: SimShop, strategy: Strategy, scenario: Scenario): SimShop {
  const s = JSON.parse(JSON.stringify(shop)) as SimShop;
  const stress = scenario === 'COMPETITION' ? 0.85 : scenario === 'TRAFFIC_COST' ? 0.75 : scenario === 'LOW_CVR' ? 0.65 : scenario === 'PRICE_WAR' ? 0.8 : scenario === 'DEMAND_SURGE' ? 1.15 : 1;
  for (const c of s.campaigns) {
    if (strategy === 'NO_CHANGE') continue;
    if (strategy === 'FIXED_RULE') c.budget *= stress > 1 ? 1.1 : 0.9;
    if (strategy === 'GAME_AGENT') {
      if (scenario === 'LOW_STOCK' || scenario === 'CASH_TIGHT') c.budget *= 0.75;
      else if (scenario === 'DEMAND_SURGE') c.budget *= 1.1;
      else c.budget *= stress < 0.9 ? 0.9 : 1.05;
    }
  }
  return s;
}

export function benchmark(shop: SimShop, rounds = 30, scenarios: Scenario[] = ['NORMAL','COMPETITION','TRAFFIC_COST','LOW_CVR','PRICE_WAR','LOW_STOCK','CASH_TIGHT','DEMAND_SURGE']): BenchmarkResult[] {
  const results: BenchmarkResult[] = [];
  for (const scenario of scenarios) for (const strategy of ['NO_CHANGE','FIXED_RULE','GAME_AGENT'] as Strategy[]) {
    const roundsOut: BacktestRound[] = runBacktest(applyStrategy(shop, strategy, scenario), rounds, 42);
    const totalSpend = roundsOut.reduce((x,r)=>x+r.spend,0);
    const totalRevenue = roundsOut.reduce((x,r)=>x+r.revenue,0);
    const totalConversions = roundsOut.reduce((x,r)=>x+r.conversions,0);
    const final = roundsOut[roundsOut.length-1];
    results.push({ strategy, scenario, totalSpend, totalRevenue, totalConversions, finalStock: final?.stock ?? 0, finalCash: final?.cash ?? 0, avgRoi: totalSpend ? totalRevenue/totalSpend : 0, actionCount: roundsOut.filter(r=>r.action).length });
  }
  return results;
}
