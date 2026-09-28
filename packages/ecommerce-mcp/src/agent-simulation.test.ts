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

test('benchmark covers all eight sandbox scenarios and game-agent diagnostics', () => {
  const rows = benchmark(createDefaultSandboxShop(), 5);
  const scenarios = new Set(rows.map(r => r.scenario));
  assert.equal(scenarios.size, 8);
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
