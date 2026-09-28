import { benchmark, Scenario, Strategy, BenchmarkResult } from './strategy-benchmark';
import { SimShop } from './backtest-engine';

export interface ScenarioSummary {
  scenario: Scenario;
  results: BenchmarkResult[];
  safety: Record<Strategy, { inventoryRisk: boolean; cashRisk: boolean }>;
  diagnostics: {
    breakthroughSignals: number;
    blockedActions: number;
    learningSignals: number;
    averageCalibrationError: number;
    opponentActions: number;
  };
}

export interface BenchmarkReport {
  rounds: number;
  scenarios: ScenarioSummary[];
  totals: {
    runs: number;
    safetyFlags: number;
    gameAgentBlockedActions: number;
    gameAgentLearningSignals: number;
  };
}

const DEFAULT_SCENARIOS: Scenario[] = [
  'NORMAL','COMPETITION','TRAFFIC_COST','LOW_CVR',
  'PRICE_WAR','LOW_STOCK','CASH_TIGHT','DEMAND_SURGE'
];

export function buildBenchmarkReport(
  shop: SimShop,
  rounds = 30,
  scenarios: Scenario[] = DEFAULT_SCENARIOS
): ScenarioSummary[] {
  const rows = benchmark(shop, rounds, scenarios);
  const names: Strategy[] = ['NO_CHANGE', 'FIXED_RULE', 'GAME_AGENT'];

  return scenarios.map(scenario => {
    const results = rows.filter(r => r.scenario === scenario);
    const safety = Object.fromEntries(names.map(strategy => {
      const r = results.find(x => x.strategy === strategy);
      return [strategy, {
        inventoryRisk: (r?.finalStock ?? 0) <= 0,
        cashRisk: (r?.finalCash ?? 0) <= 0
      }];
    })) as ScenarioSummary['safety'];

    const agent = results.find(r => r.strategy === 'GAME_AGENT');
    return {
      scenario,
      results,
      safety,
      diagnostics: {
        breakthroughSignals: agent ? Object.values(agent.breakthroughCounts ?? {}).reduce((a,b)=>a+b,0) : 0,
        blockedActions: agent?.blockedActions ?? 0,
        learningSignals: agent?.learningSignals ?? 0,
        averageCalibrationError: agent?.averageCalibrationError ?? 0,
        opponentActions: agent ? Object.values(agent.opponentActions ?? {}).reduce((a,b)=>a+b,0) : 0
      }
    };
  });
}

/**
 * Full deterministic report for the simulator.
 * This is deliberately descriptive: it exposes outcomes and safety diagnostics
 * rather than assigning a single "winner" to the strategies.
 */
export function runBenchmarkReport(
  shop: SimShop,
  rounds = 30,
  scenarios: Scenario[] = DEFAULT_SCENARIOS
): BenchmarkReport {
  const scenarioReports = buildBenchmarkReport(shop, rounds, scenarios);
  let safetyFlags = 0;
  let blockedActions = 0;
  let learningSignals = 0;

  for (const report of scenarioReports) {
    for (const strategy of Object.keys(report.safety) as Strategy[]) {
      const s = report.safety[strategy];
      if (s.inventoryRisk || s.cashRisk) safetyFlags++;
    }
    blockedActions += report.diagnostics.blockedActions;
    learningSignals += report.diagnostics.learningSignals;
  }

  return {
    rounds,
    scenarios: scenarioReports,
    totals: {
      runs: scenarioReports.length * 3,
      safetyFlags,
      gameAgentBlockedActions: blockedActions,
      gameAgentLearningSignals: learningSignals
    }
  };
}
