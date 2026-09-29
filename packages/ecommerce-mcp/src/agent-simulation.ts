import { runClosedLoop } from './closed-loop-agent';
import { GameState } from './game-state';
import { InventoryState, CashflowState } from './inventory-cashflow';
import { RiskPolicy, reconcileMarketRisk } from './risk-controller';
import { SimMarketRound } from './simulated-market';
import { createSimulatedOpponents, simulateOpponentTurn, snapshotsFromOpponents, recordOpponentMemory, SimulatedOpponent } from './opponent-simulator';
import { DecisionRecord, OutcomeRecord, LearningSignal, evaluateLearning } from './learning-memory';
import { simulateNonlinearMarket } from './nonlinear-market';
import { BehaviorObservation, BehaviorMode, updateBehaviorState } from './human-behavior-engine';

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
  responseBranches: { response: string; probability: number; nextActionHint: string }[];
  actualOpponentResponse: string;
  nextActionHint: string;
  opponentTurns: ReturnType<typeof simulateOpponentTurn>;
  learning: LearningSignal;
  nonlinear: { marginalRoi: number; crowding: number; bidEscalation: number; priceWar: number; stockConstraint: number; cashConstraint: number; stopSignal: boolean; stopReason: string };
  riskDimensions?: { capital: number; unitEconomics: number; market: number; operations: number; opponent: number; overall: number; };
  riskStopConditions?: string[];
  postMarketRisk?: { level: string; mode: string; approved: boolean; reasons: string[]; dimensions?: { capital: number; unitEconomics: number; market: number; operations: number; opponent: number; overall: number }; recommendedChangePct?: number; stopConditions?: string[] };
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
  let continuationCooldown = 0;
  let previousStopSignal = false;
  let activeBreakthrough: string | null = null;
  let breakthroughFailures = 0;
  let pendingActionHint: string | null = null;
  let behaviorObservations: BehaviorObservation[] = [];

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

    let selected = decision.recommended;
    // Adaptive breakthrough switching: after a failed/blocked route, prefer a candidate
    // attacking a different bottleneck instead of repeating the same game lever.
    if (activeBreakthrough && breakthroughFailures >= 1) {
      const alternative = decision.candidates.find(c =>
        c.risk.approved && c.breakthrough?.type && c.breakthrough.type !== activeBreakthrough
      );
      if (alternative && (!selected || alternative.score >= selected.score * 0.9)) selected = alternative;
    }
    if (previousStopSignal || continuationCooldown > 0) {
      const safer = decision.candidates.find(c => c.risk.approved && !['INCREASE_BUDGET', 'INCREASE_BID'].includes(c.action));
      if (safer) selected = safer;
      continuationCooldown = Math.max(0, continuationCooldown - 1);
    }
    if (pendingActionHint) {
      const hinted = decision.candidates.find(c => c.risk.approved && c.action === pendingActionHint);
      if (hinted && (!selected || hinted.score >= selected.score * 0.85)) selected = hinted;
      pendingActionHint = null;
    }
    const action = selected?.action ?? 'HOLD';
    const decisionId = 'SIM-' + String(round).padStart(3, '0');
    const expectedRoi = selected ? Math.max(0, state.roi ?? 0) + selected.score * 0.5 : Math.max(0, state.roi ?? 0);
    const decisionRecord: DecisionRecord = {
      id: decisionId, shopId: state.shopId, productId: state.productId, campaignId: state.campaignId,
      observedState: { price: state.price, budget: state.budget, roi: state.roi ?? 0, ctr: state.ctr ?? 0, cvr: state.cvr ?? 0 },
      hypothesis: selected?.reasons.join('; ') ?? 'hold because no approved action', action,
      expected: { roi: expectedRoi }, constraints: selected?.risk.reasons ?? [], confidence: selected?.score ?? 0,
      createdAt: observedAt
    };
    const riskApproved = Boolean(selected?.risk.approved);
    if (riskApproved) { approvedActions++; recentActions++; } else if (action !== 'HOLD') blockedActions++;

    if (riskApproved && action === 'INCREASE_BUDGET') state.budget *= 1.1;
    if (riskApproved && action === 'DECREASE_BUDGET') state.budget *= 0.9;
    if (riskApproved && action === 'INCREASE_BID') state.cpc = Math.max(0.5, (state.cpc ?? 2) * 1.05);
    if (riskApproved && action === 'DECREASE_BID') state.cpc = Math.max(0.5, (state.cpc ?? 2) * 0.95);
    if (riskApproved && action === 'CHANGE_PRICE') state.price *= 0.98;

    const competitorShare = Math.max(0, Math.min(0.95, opponents.reduce((sum, o) => sum + o.trafficShare, 0)));
    const competitorPrice = opponents[0]?.price;
    const stagedPlan = selected?.positionPlan;
    const requestedSpend = action === 'HOLD'
      ? Math.min(state.budget, 100 / Math.max(0.5, market.trafficCost) + rnd() * 20)
      : riskApproved && stagedPlan
        ? Math.min(state.budget, stagedPlan.recommendedAmount)
        : 0;
    const nonlinear = simulateNonlinearMarket({
      action: action as any,
      budget: state.budget,
      spend: requestedSpend,
      cashAvailable: cashflow.availableCash,
      cpc: state.cpc ?? 2,
      trafficCost: market.trafficCost,
      demand: market.demand,
      categoryCvr: market.categoryCvr,
      ctr: state.ctr ?? 0.03,
      price: state.price,
      competitorTrafficShare: competitorShare,
      competitorPrice,
      inventory: inventory.stockOnHand
    });
    const spend = nonlinear.spend;
    const ctr = nonlinear.ctr;
    const clicks = nonlinear.clicks;
    const cvr = nonlinear.cvr;
    const conversions = nonlinear.conversions;
    const revenue = nonlinear.revenue;

    state = { ...state, spend, impressions: Math.floor(clicks / ctr), clicks, conversions, revenue, ctr, cvr, cpc: nonlinear.effectiveCpc, roi: spend ? revenue / spend : 0, observedAt };
    inventory.stockOnHand = Math.max(0, inventory.stockOnHand - conversions);
    cashflow.availableCash = Math.max(0, cashflow.availableCash - spend + conversions * (state.marginPerOrder ?? state.price * 0.3));
    totalSpend += spend; totalRevenue += revenue; totalConversions += conversions;

    const postMarketRisk = reconcileMarketRisk(
      {
        action: action as any,
        changePct: action === 'INCREASE_BUDGET' || action === 'DECREASE_BUDGET' ? 10 : 5,
        estimatedDailySpend: spend,
        confidence: selected?.score ?? 0
      },
      config.riskPolicy,
      recentActions,
      {
        marginalRoi: nonlinear.marginalRoi,
        totalRoi: nonlinear.totalRoi,
        crowding: nonlinear.crowding,
        bidEscalation: nonlinear.bidEscalation,
        priceWar: nonlinear.priceWar,
        stockConstraint: nonlinear.stockConstraint,
        cashConstraint: nonlinear.cashConstraint,
        stopSignal: nonlinear.stopSignal,
        stopReason: nonlinear.stopReason,
        inventory: inventory.stockOnHand,
        cashAvailable: cashflow.availableCash,
        opponentRisk: selected?.breakthrough?.opponentResponseRisk
      }
    );

    const turns = simulateOpponentTurn(opponents, state);
    const actualOpponentAction = turns[0]?.action ?? 'HOLD';
    const actualOpponentResponse =
      actualOpponentAction === 'MATCH_OR_UNDERCUT_PRICE' ? 'MATCH_PRICE' :
      actualOpponentAction === 'RAISE_BID_AND_DEFEND_TRAFFIC' ? 'RAISE_BID' :
      actualOpponentAction === 'SHIFT_CONTENT' ? 'SHIFT_TO_CONTENT' :
      actualOpponentAction === 'IMPROVE_CONVERSION' ? 'DEFEND_TRAFFIC' :
      'HOLD';
    const actualBehaviorMode: BehaviorMode =
      actualOpponentResponse === 'SHIFT_TO_CONTENT' ? 'POSITIVE' :
      actualOpponentResponse === 'MATCH_PRICE' || actualOpponentResponse === 'RAISE_BID' ? 'NEGATIVE' :
      actualOpponentResponse === 'DEFEND_TRAFFIC' ? 'DEFENSIVE' :
      'OBSERVE';
    behaviorObservations = [...behaviorObservations, {
      mode: actualBehaviorMode,
      observedAt,
      evidence: `模拟中实际观察到对手响应: ${actualOpponentResponse}`
    }].slice(-12);
    state.behaviorState = updateBehaviorState(behaviorObservations, state.behaviorState);
    const bestNode = decision.multiRound.nodes.find(n => n.round === 1 && n.action === action);
    const responseBranches = bestNode?.responseBranch ?? [];
    const matchedBranch = responseBranches.find(b => b.response === actualOpponentResponse);
    const nextActionHint = matchedBranch?.nextActionHint ?? responseBranches[0]?.nextActionHint ?? 'HOLD';
    pendingActionHint = nextActionHint;
    const evaluation: OutcomeRecord['evaluation'] = spend <= 0 || conversions < 1 ? 'INCONCLUSIVE' : (state.roi ?? 0) >= expectedRoi ? 'POSITIVE' : 'NEGATIVE';
    const currentBreakthrough = selected?.breakthrough?.type ?? 'NO_CLEAR_GAP';
    if (activeBreakthrough === null) activeBreakthrough = currentBreakthrough;
    if (currentBreakthrough !== activeBreakthrough) breakthroughFailures = 0;
    else if (evaluation === 'NEGATIVE' || nonlinear.stopSignal) breakthroughFailures += 1;
    else if (evaluation === 'POSITIVE') breakthroughFailures = 0;
    if (breakthroughFailures >= 2) activeBreakthrough = currentBreakthrough;
    const outcome: OutcomeRecord = { decisionId, observed: { roi: state.roi ?? 0, revenue, conversions, spend }, evaluation, errorMetrics: { roi: Math.abs(expectedRoi - (state.roi ?? 0)) }, observedAt };
    const learning = evaluateLearning(decisionRecord, outcome);
    totalCalibrationError += learning.calibrationError;
    learningSignals += learning.useful ? 1 : 0;
    strategyConfidence[action] = Math.max(0, Math.min(1, (strategyConfidence[action] ?? decisionRecord.confidence) + (learning.useful ? (learning.calibrationError < 0.2 ? 0.02 : -0.04) : 0)));
    previousStopSignal = !postMarketRisk.approved || nonlinear.stopSignal;
    if (nonlinear.stopSignal) continuationCooldown = 1;
    const opponentActions = turns.map(t => t.opponentId + ':' + t.action);

    recordOpponentMemory(opponents, action, round, evaluation, turns);

    const breakthrough = selected?.breakthrough?.type ?? 'NO_CLEAR_GAP';
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
      responseBranches: responseBranches.map(b => ({ response: b.response, probability: b.probability, nextActionHint: b.nextActionHint })),
      actualOpponentResponse,
      nextActionHint,
      opponentTurns: clone(turns),
      learning,
      nonlinear: { marginalRoi: nonlinear.marginalRoi, crowding: nonlinear.crowding, bidEscalation: nonlinear.bidEscalation, priceWar: nonlinear.priceWar, stockConstraint: nonlinear.stockConstraint, cashConstraint: nonlinear.cashConstraint, stopSignal: nonlinear.stopSignal, stopReason: nonlinear.stopReason },
      riskDimensions: selected?.risk.dimensions,
      riskStopConditions: selected?.risk.stopConditions,
      postMarketRisk
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
