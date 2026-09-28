import { benchmark, Scenario, Strategy, BenchmarkResult } from './strategy-benchmark';
import { SimShop } from './backtest-engine';

export interface ScenarioSummary {
  scenario: Scenario;
  results: BenchmarkResult[];
  safety: Record<Strategy, { inventoryRisk: boolean; cashRisk: boolean }>;
}

export function buildBenchmarkReport(shop: SimShop, rounds = 30, scenarios?: Scenario[]): ScenarioSummary[] {
  const rows = benchmark(shop, rounds, scenarios);
  const names: Strategy[] = ['NO_CHANGE', 'FIXED_RULE', 'GAME_AGENT'];
  const selected = (scenarios ?? ['NORMAL','COMPETITION','TRAFFIC_COST','LOW_CVR','PRICE_WAR','LOW_STOCK','CASH_TIGHT','DEMAND_SURGE']);
  return selected.map(scenario => {
    const results = rows.filter(r => r.scenario === scenario);
    const safety = Object.fromEntries(names.map(strategy => {
      const r = results.find(x => x.strategy === strategy);
      return [strategy, { inventoryRisk: (r?.finalStock ?? 0) <= 0, cashRisk: (r?.finalCash ?? 0) <= 0 }];
    })) as ScenarioSummary['safety'];
    return { scenario, results, safety };
  });
}
