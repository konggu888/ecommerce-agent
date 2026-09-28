import { runClosedLoop } from './closed-loop-agent';
import { GameState } from './game-state';
import { InventoryState, CashflowState } from './inventory-cashflow';
import { RiskPolicy } from './risk-controller';
import { SimMarketRound } from './simulated-market';
import { createSimulatedOpponents, simulateOpponentTurn, snapshotsFromOpponents, SimulatedOpponent } from './opponent-simulator';
import { DecisionRecord, OutcomeRecord, LearningSignal, evaluateLearning } from './learning-memory';

export interface AgentSimulationConfig {
  rounds?: number;
  seed?: number;
  initial: GameState;
  market: { demand: number; trafficCost: number; categoryCvr: number; competitors: GameState['competitors'] };
  inventory: InventoryState;
  cashflow: CashflowState;
  riskPolicy: RiskPolicy;
}

export interface AgentSimulationRound extends SimMarketRound {
  recommendedAction: string;
  riskApproved: boolean;
  riskMode: string;
  decisionScore: number;
  opponentModel: string[];
  opponentTurns: ReturnType<typeof simulateOpponentTurn>;
  learning: LearningSignal;
}

export interface AgentSimulationResult {
  rounds: AgentSimulationRound[];
  finalState: GameState;
  summary: {
    totalSpend: number;
    totalRevenue: number;
    totalConversions: number;
    finalRoi: number;
    approvedActions: number;
    blockedActions: number;
    breakthroughCounts: Record<string, number>;
    opponentActions: Record<string, number>;
    learningSignals: number;
    averageCalibrationError: number;
    finalStock: number;
    finalCash: number;
  };
}

function clone<T>(v: T): T { return JSON.parse(JSON.stringify(v)); }

export function runAgentSimulation(config: AgentSimulationConfig): AgentSimulationResult {
  const rounds = Math.max(1, Math.min(200, config.rounds ?? 30));
  let state = clone(config.initial);
  let inventory = clone(config.inventory);
  const cashflow = clone(config.cashflow);
  const market = clone(config.market);
  const opponents: SimulatedOpponent[] = createSimulatedOpponents(state);
  let seed = (config.seed ?? 42) >>> 0;
  const rnd = () => { seed = (1664525 * seed + 1013904223) >>> 0; return seed / 4294967296; };
  const out: AgentSimulationRound[] = [];
  let approvedActions = 0;
  let blockedActions = 0;
  let recentActions = 0;
  const breakthroughCounts: Record<string, number> = {};
  const opponentActionCounts: Record<string, number> = {};
  let totalSpend = 0, totalRevenue = 0, totalConversions = 0;
  let totalCalibrationError = 0;
  let learningSignals = 0;
  const strategyConfidence: Record<string, number> = {};

  for (let round = 1; round <= rounds; round++) {
    const observedAt = new Date().toISOString();
    const competitorSnapshots = snapshotsFromOpponents(opponents, observedAt);
    const economics = {
      sellingPrice: state.price,
      productCost: Math.max(0, state.price - (state.marginPerOrder ?? state.price * 0.3)),
      fulfillmentCost: 0,
      platformFee: 0,
      paymentFee: 0,
      otherVariableCost: 0
    };

    const decision = runClosedLoop({
      state: { ...state, competitors: competitorSnapshots },
      economics,
      inventory,
      cashflow,
      riskPolicy: config.riskPolicy,
      recentActionCount: recentActions,
      strategyConfidence
    });

    const action = decision.recommended?.action ?? 'HOLD';
    const decisionId = 'SIM-' + String(round).padStart(3, '0');
    const expectedRoi = decision.recommended ? Math.max(0, state.roi ?? 0) + decision.recommended.score * 0.5 : Math.max(0, state.roi ?? 0);
    const decisionRecord: DecisionRecord = {
      id: decisionId, shopId: state.shopId, productId: state.productId, campaignId: state.campaignId,
      observedState: { price: state.price, budget: state.budget, roi: state.roi ?? 0, ctr: state.ctr ?? 0, cvr: state.cvr ?? 0 },
      hypothesis: decision.recommended?.reasons.join('; ') ?? 'hold because no approved action', action,
      expected: { roi: expectedRoi }, constraints: decision.recommended?.risk.reasons ?? [], confidence: decision.recommended?.score ?? 0,
      createdAt: observedAt
    };
    const riskApproved = Boolean(decision.recommended?.risk.approved);
    if (riskApproved) { approvedActions++; recentActions++; } else if (action !== 'HOLD') blockedActions++;

    if (riskApproved && action === 'INCREASE_BUDGET') state.budget *= 1.1;
    if (riskApproved && action === 'DECREASE_BUDGET') state.budget *= 0.9;
    if (riskApproved && action === 'INCREASE_BID') state.cpc = Math.max(0.5, (state.cpc ?? 2) * 1.05);
    if (riskApproved && action === 'DECREASE_BID') state.cpc = Math.max(0.5, (state.cpc ?? 2) * 0.95);
    if (riskApproved && action === 'CHANGE_PRICE') state.price *= 0.98;

    const pressure = market.trafficCost * (1 + Math.max(0, opponents[0]?.trafficShare ?? 0) * 0.3);
    const spend = Math.min(state.budget, Math.max(0, 100 / Math.max(0.5, pressure) + rnd() * 20));
    const ctr = Math.max(0.005, Math.min(0.12, (state.ctr ?? 0.03) * (action === 'CHANGE_KEYWORD' || action === 'CHANGE_TARGETING' ? 1.06 : 1)));
    const clicks = Math.floor(spend / Math.max(0.5, pressure));
    const cvr = Math.max(0.005, Math.min(0.2, market.categoryCvr * (action === 'CHANGE_PRICE' ? 1.02 : 1)));
    const conversions = Math.min(inventory.stockOnHand, Math.floor(clicks * cvr * market.demand));
    const revenue = conversions * state.price;

    state = { ...state, spend, impressions: Math.floor(clicks / ctr), clicks, conversions, revenue, ctr, cvr, cpc: clicks ? spend / clicks : 0, roi: spend ? revenue / spend : 0, observedAt };
    inventory.stockOnHand = Math.max(0, inventory.stockOnHand - conversions);
    cashflow.availableCash = Math.max(0, cashflow.availableCash - spend + conversions * (state.marginPerOrder ?? state.price * 0.3));
    totalSpend += spend; totalRevenue += revenue; totalConversions += conversions;

    const turns = simulateOpponentTurn(opponents, state);
    const evaluation: OutcomeRecord['evaluation'] = spend <= 0 || conversions < 1 ? 'INCONCLUSIVE' : state.roi >= expectedRoi ? 'POSITIVE' : 'NEGATIVE';
    const outcome: OutcomeRecord = { decisionId, observed: { roi: state.roi ?? 0, revenue, conversions, spend }, evaluation, errorMetrics: { roi: Math.abs(expectedRoi - (state.roi ?? 0)) }, observedAt };
    const learning = evaluateLearning(decisionRecord, outcome);
    totalCalibrationError += learning.calibrationError;
    learningSignals += learning.useful ? 1 : 0;
    strategyConfidence[action] = Math.max(0, Math.min(1, (strategyConfidence[action] ?? decisionRecord.confidence) + (learning.useful ? (learning.calibrationError < 0.2 ? 0.02 : -0.04) : 0)));
    const opponentActions = turns.map(t => t.opponentId + ':' + t.action);

    const breakthrough = decision.recommended?.breakthrough?.type ?? 'NO_CLEAR_GAP';
    breakthroughCounts[breakthrough] = (breakthroughCounts[breakthrough] ?? 0) + 1;
    for (const turn of turns) opponentActionCounts[turn.action] = (opponentActionCounts[turn.action] ?? 0) + 1;
    out.push({
      round,
      action: action as any,
      opponentActions,
      state: clone(state),
      breakthroughSignal: breakthrough,
      recommendedAction: action,
      riskApproved,
      riskMode: decision.recommended?.risk.mode ?? 'ANALYZE_ONLY',
      decisionScore: decision.recommended?.score ?? 0,
      opponentModel: decision.multiRound.bestPath,
      opponentTurns: clone(turns),
      learning
    });

    state.competitors = snapshotsFromOpponents(opponents, observedAt);
    market.demand = Math.max(0.65, Math.min(1.5, market.demand + (rnd() - 0.48) * 0.04));
    market.categoryCvr = Math.max(0.01, Math.min(0.12, market.categoryCvr + (rnd() - 0.5) * 0.002));
    recentActions = Math.max(0, recentActions - 1);
  }

  return {
    rounds: out,
    finalState: state,
    summary: {
      totalSpend,
      totalRevenue,
      totalConversions,
      finalRoi: totalSpend ? totalRevenue / totalSpend : 0,
      approvedActions,
      blockedActions,
      breakthroughCounts,
      opponentActions: opponentActionCounts,
      learningSignals,
      averageCalibrationError: rounds ? totalCalibrationError / rounds : 0,
      finalStock: inventory.stockOnHand,
      finalCash: cashflow.availableCash
    }
  };
}
