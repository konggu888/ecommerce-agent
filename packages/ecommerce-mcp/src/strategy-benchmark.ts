import { runBacktest, SimShop, BacktestRound } from './backtest-engine';
import { runClosedLoop } from './closed-loop-agent';
import { GameState } from './game-state';
import { UnitEconomics } from './unit-economics';
import { InventoryState, CashflowState } from './inventory-cashflow';
import { RiskPolicy } from './risk-controller';

export type Strategy = 'NO_CHANGE' | 'FIXED_RULE' | 'GAME_AGENT';
export type Scenario = 'NORMAL' | 'COMPETITION' | 'TRAFFIC_COST' | 'LOW_CVR' | 'PRICE_WAR' | 'LOW_STOCK' | 'CASH_TIGHT' | 'DEMAND_SURGE';
export interface BenchmarkResult { strategy: Strategy; scenario: Scenario; totalSpend: number; totalRevenue: number; totalConversions: number; finalStock: number; finalCash: number; avgRoi: number; actionCount: number; }

const RISK_POLICY: RiskPolicy = { maxBudgetChangePct: 10, maxBidChangePct: 5, maxDailySpend: 2000, maxActionsPerHour: 4, allowBudgetChange: true, allowBidChange: true, allowPause: false };

function factors(s: Scenario) {
  return { traffic: s === 'DEMAND_SURGE' ? 1.15 : s === 'TRAFFIC_COST' ? 0.75 : s === 'COMPETITION' ? 0.85 : 1, cvr: s === 'LOW_CVR' ? 0.65 : s === 'DEMAND_SURGE' ? 1.1 : 1, price: s === 'PRICE_WAR' ? 0.92 : 1 };
}

function applyStrategy(shop: SimShop, strategy: Strategy, scenario: Scenario): SimShop {
  const s = JSON.parse(JSON.stringify(shop)) as SimShop;
  const stress = scenario === 'COMPETITION' ? 0.85 : scenario === 'TRAFFIC_COST' ? 0.75 : scenario === 'LOW_CVR' ? 0.65 : scenario === 'PRICE_WAR' ? 0.8 : scenario === 'DEMAND_SURGE' ? 1.15 : 1;
  if (strategy === 'FIXED_RULE') for (const c of s.campaigns) c.budget *= stress > 1 ? 1.1 : 0.9;
  return s;
}

function agentAction(shop: SimShop, scenario: Scenario, recentActions: number): string {
  const p = shop.products[0], c = shop.campaigns[0]; if (!p || !c) return 'HOLD';
  const f = factors(scenario);
  const conversions = Math.max(1, Math.floor(300 * 0.04 * f.cvr));
  const state: GameState = { shopId: shop.id, productId: p.id, campaignId: c.id, price: p.price * f.price, marginPerOrder: p.marginPerOrder, budget: c.budget, spend: Math.min(c.budget, 2000), impressions: 10000*f.traffic, clicks: 300*f.traffic, conversions, revenue: p.price*conversions, ctr: 0.03, cvr: 0.04*f.cvr, cpc: 2, roi: 3*f.traffic*f.cvr, competitors: [], observedAt: new Date().toISOString() };
  const economics: UnitEconomics = { sellingPrice: state.price, productCost: Math.max(0, p.price-p.marginPerOrder), fulfillmentCost: 0, platformFee: 0, paymentFee: 0, otherVariableCost: 0 };
  const inventory: InventoryState = { stockOnHand: p.stock, reservedStock: 0, avgDailyUnits: conversions, replenishmentDays: p.replenishmentDays, safetyStockDays: p.safetyStockDays };
  const cashflow: CashflowState = { availableCash: shop.cash, pendingReceivables: 0, payableDue: 0, dailyOperatingCashNeed: 100, adSpendAlreadyCommitted: 0 };
  return runClosedLoop({ state, economics, inventory, cashflow, riskPolicy: RISK_POLICY, recentActionCount: recentActions }).recommended?.action ?? 'HOLD';
}

export function benchmark(shop: SimShop, rounds = 30, scenarios: Scenario[] = ['NORMAL','COMPETITION','TRAFFIC_COST','LOW_CVR','PRICE_WAR','LOW_STOCK','CASH_TIGHT','DEMAND_SURGE']): BenchmarkResult[] {
  const results: BenchmarkResult[] = [];
  for (const scenario of scenarios) for (const strategy of ['NO_CHANGE','FIXED_RULE','GAME_AGENT'] as Strategy[]) {
    const base = applyStrategy(shop, strategy, scenario);
    const roundsOut: BacktestRound[] = [];
    if (strategy !== 'GAME_AGENT') roundsOut.push(...runBacktest(base, rounds, 42));
    else {
      const s = JSON.parse(JSON.stringify(base)) as SimShop; let actions = 0;
      for (let round=1; round<=rounds; round++) {
        const action = agentAction(s, scenario, actions); if (action !== 'HOLD') actions++;
        for (const c of s.campaigns) { if (action==='INCREASE_BUDGET') c.budget*=1.1; if (action==='DECREASE_BUDGET') c.budget*=0.9; if (action==='INCREASE_BID') c.bid*=1.05; if (action==='DECREASE_BID') c.bid*=0.95; }
        const one=runBacktest(s,1,42+round)[0]; if(one){one.action=action; roundsOut.push(one);}
      }
    }
    const totalSpend=roundsOut.reduce((x,r)=>x+r.spend,0), totalRevenue=roundsOut.reduce((x,r)=>x+r.revenue,0), totalConversions=roundsOut.reduce((x,r)=>x+r.conversions,0);
    const final=roundsOut[roundsOut.length-1];
    results.push({strategy,scenario,totalSpend,totalRevenue,totalConversions,finalStock:final?.stock??0,finalCash:final?.cash??0,avgRoi:totalSpend?totalRevenue/totalSpend:0,actionCount:roundsOut.filter(r=>r.action&&r.action!=='HOLD').length});
  }
  return results;
}
