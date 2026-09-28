import { runBacktest, SimShop, BacktestRound } from './backtest-engine';
import { GameState } from './game-state';
import { UnitEconomics } from './unit-economics';
import { InventoryState, CashflowState } from './inventory-cashflow';
import { RiskPolicy } from './risk-controller';
import { runAgentSimulation } from './agent-simulation';

export type Strategy = 'NO_CHANGE' | 'FIXED_RULE' | 'GAME_AGENT';
export type Scenario = 'NORMAL' | 'COMPETITION' | 'TRAFFIC_COST' | 'LOW_CVR' | 'PRICE_WAR' | 'LOW_STOCK' | 'CASH_TIGHT' | 'DEMAND_SURGE';
export interface BenchmarkResult {
  strategy: Strategy; scenario: Scenario; totalSpend: number; totalRevenue: number; totalConversions: number;
  finalStock: number; finalCash: number; avgRoi: number; actionCount: number;
  blockedActions?: number; learningSignals?: number; averageCalibrationError?: number;
  breakthroughCounts?: Record<string, number>; opponentActions?: Record<string, number>;
}

const RISK_POLICY: RiskPolicy = { maxBudgetChangePct: 10, maxBidChangePct: 5, maxDailySpend: 2000, maxActionsPerHour: 4, allowBudgetChange: true, allowBidChange: true, allowPause: false };

function factors(s: Scenario) {
  return {
    traffic: s === 'DEMAND_SURGE' ? 1.15 : s === 'TRAFFIC_COST' ? 0.75 : s === 'COMPETITION' ? 0.85 : 1,
    cvr: s === 'LOW_CVR' ? 0.65 : s === 'DEMAND_SURGE' ? 1.1 : 1,
    price: s === 'PRICE_WAR' ? 0.92 : 1
  };
}

function applyStrategy(shop: SimShop, strategy: Strategy, scenario: Scenario): SimShop {
  const s = JSON.parse(JSON.stringify(shop)) as SimShop;
  const stress = scenario === 'COMPETITION' ? 0.85 : scenario === 'TRAFFIC_COST' ? 0.75 : scenario === 'LOW_CVR' ? 0.65 : scenario === 'PRICE_WAR' ? 0.8 : scenario === 'DEMAND_SURGE' ? 1.15 : 1;
  if (strategy === 'FIXED_RULE') for (const c of s.campaigns) c.budget *= stress > 1 ? 1.1 : 0.9;
  if (scenario === 'LOW_STOCK') for (const p of s.products) p.stock = Math.max(3, Math.floor(p.stock * 0.18));
  if (scenario === 'CASH_TIGHT') s.cash = Math.max(100, s.cash * 0.18);
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

function gameAgentBenchmark(shop: SimShop, scenario: Scenario, rounds: number): BenchmarkResult {
  const p = shop.products[0], c = shop.campaigns[0];
  if (!p || !c) return { strategy:'GAME_AGENT', scenario, totalSpend:0, totalRevenue:0, totalConversions:0, finalStock:0, finalCash:shop.cash, avgRoi:0, actionCount:0 };
  const f = factors(scenario);
  const competitors = [
    { competitorId:'COMP-A', price:p.price*(scenario==='PRICE_WAR'?0.94:1.03), estimatedCtr:0.035, estimatedCvr:0.045, trafficShare:scenario==='COMPETITION'?0.48:0.24, observedAt:new Date().toISOString() },
    { competitorId:'COMP-B', price:p.price*1.06, estimatedCtr:0.028, estimatedCvr:0.04, trafficShare:0.18, observedAt:new Date().toISOString() }
  ];
  const initial: GameState = {
    shopId:shop.id, productId:p.id, campaignId:c.id, price:p.price*f.price, marginPerOrder:p.marginPerOrder,
    budget:c.budget, spend:0, impressions:10000*f.traffic, clicks:300*f.traffic,
    conversions:Math.max(1,Math.floor(300*0.04*f.cvr)), revenue:p.price,
    ctr:0.03*f.traffic, cvr:0.04*f.cvr, cpc:2, roi:3*f.traffic*f.cvr,
    competitors, observedAt:new Date().toISOString()
  };
  const sim = runAgentSimulation({
    rounds, seed:42, initial,
    market:{
      demand: scenario==='DEMAND_SURGE'?1.25:1,
      trafficCost: scenario==='TRAFFIC_COST'?1.45:scenario==='COMPETITION'?1.15:1,
      categoryCvr:0.04*f.cvr,
      competitors
    },
    inventory:{
      stockOnHand:p.stock, reservedStock:0, avgDailyUnits:Math.max(1,initial.conversions),
      replenishmentDays:p.replenishmentDays, safetyStockDays:p.safetyStockDays
    },
    cashflow:{
      availableCash:shop.cash, pendingReceivables:0, payableDue:0, dailyOperatingCashNeed:100, adSpendAlreadyCommitted:0
    },
    riskPolicy:RISK_POLICY
  });
  return {
    strategy:'GAME_AGENT', scenario, totalSpend:sim.summary.totalSpend, totalRevenue:sim.summary.totalRevenue,
    totalConversions:sim.summary.totalConversions, finalStock:sim.finalState.conversions ? Math.max(0, p.stock-sim.summary.totalConversions) : p.stock,
    finalCash:Math.max(0, shop.cash-sim.summary.totalSpend+sim.summary.totalConversions*p.marginPerOrder),
    avgRoi:sim.summary.finalRoi, actionCount:sim.summary.approvedActions,
    blockedActions:sim.summary.blockedActions, learningSignals:sim.summary.learningSignals,
    averageCalibrationError:sim.summary.averageCalibrationError,
    breakthroughCounts: sim.summary.breakthroughCounts,
    opponentActions: sim.summary.opponentActions
  };
}

export function benchmark(shop: SimShop, rounds = 30, scenarios: Scenario[] = ['NORMAL','COMPETITION','TRAFFIC_COST','LOW_CVR','PRICE_WAR','LOW_STOCK','CASH_TIGHT','DEMAND_SURGE']): BenchmarkResult[] {
  const results: BenchmarkResult[] = [];
  for (const scenario of scenarios) for (const strategy of ['NO_CHANGE','FIXED_RULE','GAME_AGENT'] as Strategy[]) {
    if (strategy === 'GAME_AGENT') { results.push(gameAgentBenchmark(shop, scenario, rounds)); continue; }
    const base = applyStrategy(shop, strategy, scenario);
    const roundsOut: BacktestRound[] = runBacktest(base, rounds, 42);
    const totalSpend=roundsOut.reduce((x,r)=>x+r.spend,0), totalRevenue=roundsOut.reduce((x,r)=>x+r.revenue,0), totalConversions=roundsOut.reduce((x,r)=>x+r.conversions,0);
    const final=roundsOut[roundsOut.length-1];
    results.push({strategy,scenario,totalSpend,totalRevenue,totalConversions,finalStock:final?.stock??0,finalCash:final?.cash??0,avgRoi:totalSpend?totalRevenue/totalSpend:0,actionCount:roundsOut.filter(r=>r.action&&r.action!=='HOLD').length});
  }
  return results;
}
