import test from 'node:test';
import assert from 'node:assert/strict';
import { runAgentSimulation } from './agent-simulation.ts';
import { benchmark } from './strategy-benchmark.ts';
import { createDefaultSandboxShop } from './run-sandbox-benchmark.ts';

const riskPolicy = {
  maxBudgetChangePct: 10,
  maxBidChangePct: 5,
  maxDailySpend: 2000,
  maxActionsPerHour: 4,
  allowBudgetChange: true,
  allowBidChange: true,
  allowPause: false
};

function config() {
  const shop = createDefaultSandboxShop();
  const p = shop.products[0], c = shop.campaigns[0];
  const competitors = [
    { competitorId:'COMP-A', price:91, estimatedCtr:0.035, estimatedCvr:0.045, trafficShare:0.24, observedAt:new Date().toISOString() },
    { competitorId:'COMP-B', price:94, estimatedCtr:0.028, estimatedCvr:0.04, trafficShare:0.18, observedAt:new Date().toISOString() }
  ];
  return {
    rounds:30, seed:42,
    initial:{shopId:shop.id,productId:p.id,campaignId:c.id,price:p.price,marginPerOrder:p.marginPerOrder,budget:c.budget,spend:0,impressions:10000,clicks:300,conversions:12,revenue:p.price*12,ctr:.03,cvr:.04,cpc:2,roi:3,competitors,observedAt:new Date().toISOString()},
    market:{demand:1,trafficCost:1,categoryCvr:.04,competitors},
    inventory:{stockOnHand:p.stock,reservedStock:0,avgDailyUnits:12,replenishmentDays:p.replenishmentDays,safetyStockDays:p.safetyStockDays},
    cashflow:{availableCash:shop.cash,pendingReceivables:0,payableDue:0,dailyOperatingCashNeed:100,adSpendAlreadyCommitted:0},
    riskPolicy
  };
}

test('agent simulation preserves non-negative stock and cash', () => {
  const result = runAgentSimulation(config());
  assert.equal(result.rounds.length, 30);
  assert.ok(result.summary.finalStock >= 0);
  assert.ok(result.summary.finalCash >= 0);
  assert.ok(Number.isFinite(result.summary.finalRoi));
  assert.ok(Number.isFinite(result.summary.averageCalibrationError));
  assert.ok(Object.values(result.summary.opponentActions).reduce((a,b) => a + b, 0) > 0);
});

test('risk controller blocks are recorded and do not count as approved actions', () => {
  const result = runAgentSimulation({...config(), riskPolicy:{...riskPolicy,maxDailySpend:10}});
  assert.ok(result.summary.blockedActions >= 0);
  assert.ok(result.summary.approvedActions >= 0);
  assert.ok(result.rounds.some(r => r.learning !== undefined));
});

test('closed-loop candidate set includes all executable game levers', async () => {
  const { runClosedLoop } = await import('./closed-loop-agent.ts');
  const cfg = config();
  const p = cfg.initial;
  const economics = {
    sellingPrice: p.price, productCost: p.price - p.marginPerOrder,
    fulfillmentCost: 0, platformFee: 0, paymentFee: 0, otherVariableCost: 0
  };
  const result = runClosedLoop({
    state: p, economics, inventory: cfg.inventory, cashflow: cfg.cashflow,
    riskPolicy, recentActionCount: 0
  });
  const actions = new Set(result.candidates.map(x => x.action));
  for (const action of ['HOLD','INCREASE_BUDGET','DECREASE_BUDGET','INCREASE_BID','DECREASE_BID','CHANGE_KEYWORD','CHANGE_TARGETING','CHANGE_PRICE']) {
    assert.ok(actions.has(action), action + ' missing from candidate set');
  }
});

test('action effects are reflected in observable market metrics', async () => {
  const { runAgentSimulation } = await import('./agent-simulation.ts');
  const base = config();
  const result = runAgentSimulation({...base, rounds: 1});
  const round = result.rounds[0];
  assert.ok(round.state.clicks >= 0);
  assert.ok(round.state.conversions >= 0);
  assert.ok(Number.isFinite(round.state.ctr));
  assert.ok(Number.isFinite(round.state.cvr));
  assert.ok(Number.isFinite(round.state.roi));
  assert.ok(round.state.observedAt);
});

test('position sizing uses staged spend and stops on weak economics or high response risk', async () => {
  const { buildPositionPlan } = await import('./position-sizing.ts');
  const plan = buildPositionPlan('INCREASE_BUDGET', 800, 3, 0.8, 0.2);
  assert.ok(plan.steps.length >= 2);
  assert.ok(plan.recommendedAmount > 0);
  assert.ok(plan.steps.every(s => s.amount <= 800));
  const risky = buildPositionPlan('INCREASE_BUDGET', 800, 3, 0.4, 0.9);
  assert.ok(risky.recommendedAmount <= plan.recommendedAmount);
  assert.match(risky.stopReason, /风险|置信度|投入/);
});

test('breakthrough output includes a bounded path, signal and stop condition', async () => {
  const { findBreakthroughs } = await import('./breakthrough-engine.ts');
  const cfg = config();
  const breakthroughs = findBreakthroughs(cfg.initial);
  assert.ok(breakthroughs.length > 0);
  for (const b of breakthroughs) {
    assert.ok(Array.isArray(b.path));
    assert.ok(b.path.length > 0);
    assert.ok(b.stopCondition.length > 0);
    assert.ok(b.expectedSignal.length > 0);
  }
});

test('multi-round planner carries likely opponent response into continuation state', async () => {
  const { planMultiRoundGame } = await import('./multi-round-game.ts');
  const cfg = config();
  const priceWar = planMultiRoundGame({
    ...cfg.initial,
    competitors: cfg.initial.competitors.map(x => ({...x, price: cfg.initial.price + 12}))
  }, 2);
  const calm = planMultiRoundGame({
    ...cfg.initial,
    competitors: cfg.initial.competitors.map(x => ({...x, price: cfg.initial.price - 2, trafficShare: 0.12}))
  }, 2);
  assert.notEqual(priceWar.bestScore, calm.bestScore);
  assert.ok(priceWar.nodes.some(n => n.opponentRisk > 0));
});

test('benchmark covers all eight sandbox scenarios and game-agent diagnostics', () => {
  const rows = benchmark(createDefaultSandboxShop(), 5);
  const scenarios = new Set(rows.map(r => r.scenario));
  assert.equal(scenarios.size, 8);
  const normalNoChange = rows.find(r => r.scenario === 'NORMAL' && r.strategy === 'NO_CHANGE');
  const trafficNoChange = rows.find(r => r.scenario === 'TRAFFIC_COST' && r.strategy === 'NO_CHANGE');
  const demandNoChange = rows.find(r => r.scenario === 'DEMAND_SURGE' && r.strategy === 'NO_CHANGE');
  assert.ok(normalNoChange && trafficNoChange && demandNoChange);
  assert.notEqual(normalNoChange.totalRevenue, trafficNoChange.totalRevenue);
  assert.notEqual(normalNoChange.totalRevenue, demandNoChange.totalRevenue);
  assert.equal(rows.filter(r => r.strategy === 'GAME_AGENT').length, 8);
  for (const row of rows.filter(r => r.strategy === 'GAME_AGENT')) {
    assert.ok(row.opponentActions);
    assert.ok(row.learningSignals !== undefined);
    assert.ok(row.averageCalibrationError !== undefined);
    assert.ok(row.finalStock >= 0);
    assert.ok(row.finalCash >= 0);
    assert.ok(Object.values(row.opponentActions ?? {}).reduce((a,b) => a + b, 0) > 0);
  }
});

test('nonlinear market shows diminishing marginal return under heavier spend', async () => {
  const { simulateNonlinearMarket } = await import('./nonlinear-market.ts');
  const base = {
    action: 'INCREASE_BUDGET' as const, budget: 800, spend: 160, cpc: 2,
    trafficCost: 1, demand: 1, categoryCvr: 0.04, ctr: 0.03, price: 100,
    competitorTrafficShare: 0.2, competitorPrice: 98, inventory: 100
  };
  const low = simulateNonlinearMarket(base);
  const high = simulateNonlinearMarket({...base, spend: 640});
  assert.ok(high.crowding > low.crowding);
  assert.ok(high.effectiveCpc >= low.effectiveCpc);
  assert.ok(high.marginalRoi <= low.marginalRoi);
});

test('nonlinear market exposes bid escalation and price-war pressure', async () => {
  const { simulateNonlinearMarket } = await import('./nonlinear-market.ts');
  const bid = simulateNonlinearMarket({
    action: 'INCREASE_BID', budget: 800, spend: 400, cpc: 2,
    trafficCost: 1, demand: 1, categoryCvr: 0.04, ctr: 0.03, price: 100,
    competitorTrafficShare: 0.55, competitorPrice: 99, inventory: 100
  });
  assert.ok(bid.bidEscalation > 1);
  assert.ok(bid.crowding > 0);
  assert.ok(Number.isFinite(bid.marginalRoi));
  assert.ok(typeof bid.stopSignal === 'boolean');
});

test('agent rounds expose nonlinear stop signals and marginal ROI', () => {
  const result = runAgentSimulation({...config(), rounds: 5});
  assert.equal(result.rounds.length, 5);
  assert.ok(result.rounds.every(r => Number.isFinite(r.nonlinear.marginalRoi)));
  assert.ok(result.rounds.some(r => r.nonlinear.crowding >= 0));
});


test('continuation policy reduces aggressive actions after a nonlinear stop signal', () => {
  const result = runAgentSimulation({...config(), rounds: 20});
  const rounds = result.rounds;
  for (let i = 0; i < rounds.length - 1; i++) {
    if (rounds[i].nonlinear.stopSignal) {
      assert.notEqual(rounds[i + 1].action, 'INCREASE_BUDGET');
      assert.notEqual(rounds[i + 1].action, 'INCREASE_BID');
    }
  }
});


test('post-market risk is reconciled from nonlinear feedback', async () => {
  const { reconcileMarketRisk } = await import('./risk-controller.ts');
  const policy = riskPolicy;
  const blocked = reconcileMarketRisk(
    { action: 'INCREASE_BUDGET', changePct: 10, estimatedDailySpend: 100, confidence: 0.9 },
    policy,
    0,
    {
      marginalRoi: 0.6, totalRoi: 3, crowding: 0.2, bidEscalation: 1,
      priceWar: 0, stockConstraint: 0.8, cashConstraint: 0.8,
      stopSignal: true, stopReason: '边际ROI明显下降'
    }
  );
  assert.equal(blocked.approved, false);
  assert.equal(blocked.mode, 'AUTO_DISABLED');

  const result = runAgentSimulation({...config(), rounds: 3});
  assert.ok(result.rounds.every(r => r.postMarketRisk !== undefined));
  assert.ok(result.rounds.every(r => Number.isFinite(r.postMarketRisk?.dimensions?.overall ?? 0)));
});

test('agent exposes adaptive breakthrough switching after repeated failed signals', () => {
  const result = runAgentSimulation({...config(), rounds: 30, seed: 7});
  const types = result.rounds.map(r => r.breakthroughSignal).filter(x => x && x !== 'NO_CLEAR_GAP');
  assert.ok(types.length > 0);
  const unique = new Set(types);
  assert.ok(unique.size >= 1);
  for (const round of result.rounds) {
    assert.ok(typeof round.breakthroughSignal === 'string');
  }
});
