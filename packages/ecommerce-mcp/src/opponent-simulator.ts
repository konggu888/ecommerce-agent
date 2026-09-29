import { CompetitorSnapshot, GameState } from './game-state';

export type OpponentStrategy = 'VALUE_DEFENSE' | 'TRAFFIC_DEFENSE' | 'PRICE_WAR' | 'HOLD' | 'CONTENT_SHIFT';

export interface OpponentMemory {
  ourActions: Array<{ action: string; round: number; outcome?: 'POSITIVE' | 'NEGATIVE' | 'INCONCLUSIVE' }>;
  responseHistory: Array<{ action: string; round: number }>;
  lastOurAction?: string;
  lastOutcome?: 'POSITIVE' | 'NEGATIVE' | 'INCONCLUSIVE';
  adaptationScore: number;
  /** How strongly this simulated opponent has learned our recurring action pattern. */
  learnedResponses: Record<string, string>;
  /** Number of repeated actions the opponent has seen us use. */
  repetitionCount: number;
}

export interface SimulatedOpponent {
  id: string;
  strategy: OpponentStrategy;
  price: number;
  budget: number;
  bid: number;
  trafficShare: number;
  ctr: number;
  cvr: number;
  inventory: number;
  cash: number;
  memory: OpponentMemory;
}

export interface OpponentTurn {
  opponentId: string;
  strategy: OpponentStrategy;
  action: string;
  price: number;
  bid: number;
  trafficShare: number;
  estimatedCtr: number;
  estimatedCvr: number;
  reason: string;
}

export function createSimulatedOpponents(state: GameState): SimulatedOpponent[] {
  return state.competitors.map((c, i) => ({
    id: c.competitorId,
    strategy: i % 5 === 0 ? 'PRICE_WAR' : i % 5 === 1 ? 'TRAFFIC_DEFENSE' : i % 5 === 2 ? 'VALUE_DEFENSE' : i % 5 === 3 ? 'CONTENT_SHIFT' : 'HOLD',
    price: c.price ?? state.price * (0.96 + i * 0.02),
    budget: 1000 + i * 300,
    bid: Math.max(0.5, (c.estimatedCtr ?? 0.03) * 60),
    trafficShare: c.trafficShare ?? 0.2,
    ctr: c.estimatedCtr ?? 0.03,
    cvr: c.estimatedCvr ?? state.cvr ?? 0.04,
    inventory: 100 + i * 50,
    cash: 5000 + i * 1500,
    memory: { ourActions: [], responseHistory: [], adaptationScore: 0.5, learnedResponses: {}, repetitionCount: 0 }
  }));
}

export function simulateOpponentTurn(opponents: SimulatedOpponent[], state: GameState): OpponentTurn[] {
  return opponents.map(o => {
    const lastAction = o.memory.lastOurAction;
    const lastOutcome = o.memory.lastOutcome;
    const learned = lastAction ? o.memory.learnedResponses[lastAction] : undefined;
    const repeated = o.memory.ourActions.filter(x => x.action === lastAction).length;
    const learningActive = o.memory.adaptationScore >= 0.6 && repeated >= 2;
    let action = 'HOLD';
    let reason = 'no strong threat detected';
    const learnedCounter = lastAction === 'CHANGE_PRICE' ? 'PRICE_WAR' : lastAction === 'INCREASE_BID' || lastAction === 'INCREASE_BUDGET' ? 'TRAFFIC_DEFENSE' : lastAction === 'CONTENT_VIDEO' || lastAction === 'CONTENT_MATRIX' ? 'CONTENT_SHIFT' : lastAction ? 'VALUE_DEFENSE' : o.strategy;
    const activeStrategy = learningActive && learned
      ? learned as OpponentStrategy
      : lastOutcome === 'NEGATIVE' ? learnedCounter as OpponentStrategy : o.strategy;
    if (activeStrategy === 'PRICE_WAR' && state.price < o.price * 1.03) {
      o.price = Math.max(1, Math.min(o.price, state.price * 0.995));
      action = 'MATCH_OR_UNDERCUT_PRICE';
      reason = learningActive ? '根据重复出现的我方动作启用历史反制' : 'protect price competitiveness';
    } else if (activeStrategy === 'TRAFFIC_DEFENSE' && (state.ctr ?? 0) > o.ctr * 1.05) {
      o.bid *= 1.06;
      o.trafficShare = Math.min(0.7, o.trafficShare + 0.03);
      action = 'RAISE_BID_AND_DEFEND_TRAFFIC';
      reason = learningActive ? '根据历史动作模式持续防守流量' : 'respond to traffic advantage';
    } else if (activeStrategy === 'VALUE_DEFENSE' && (state.cvr ?? 0) > o.cvr * 1.05) {
      o.cvr = Math.min(0.2, o.cvr * 1.05);
      action = 'IMPROVE_CONVERSION';
      reason = learningActive ? '根据历史动作模式持续强化价值防守' : 'respond to conversion disadvantage';
    } else if (activeStrategy === 'CONTENT_SHIFT') {
      o.ctr = Math.min(0.12, o.ctr * 1.015);
      action = 'SHIFT_CONTENT';
      reason = learningActive ? '根据历史动作模式持续切换内容防守' : 'seek attention without price escalation';
    }
    return {
      opponentId: o.id, strategy: activeStrategy, action, price: o.price, bid: o.bid,
      trafficShare: o.trafficShare, estimatedCtr: o.ctr, estimatedCvr: o.cvr, reason
    };
  });
}

export function recordOpponentMemory(opponents: SimulatedOpponent[], ourAction: string, round: number, outcome: 'POSITIVE' | 'NEGATIVE' | 'INCONCLUSIVE', turns: OpponentTurn[]): void {
  for (const o of opponents) {
    o.memory.ourActions.push({ action: ourAction, round, outcome });
    o.memory.responseHistory.push({ action: turns.find(t => t.opponentId === o.id)?.action ?? 'HOLD', round });
    o.memory.lastOurAction = ourAction;
    o.memory.lastOutcome = outcome;
    const repeatedCount = o.memory.ourActions.filter(x => x.action === ourAction).length;
    const learnedCounter = ourAction === 'CHANGE_PRICE' ? 'PRICE_WAR' :
      ourAction === 'INCREASE_BID' || ourAction === 'INCREASE_BUDGET' ? 'TRAFFIC_DEFENSE' :
      ourAction === 'CONTENT_VIDEO' || ourAction === 'CONTENT_MATRIX' ? 'CONTENT_SHIFT' : 'VALUE_DEFENSE';
    if (repeatedCount >= 2) o.memory.learnedResponses[ourAction] = learnedCounter;
    o.memory.repetitionCount = Math.max(0, repeatedCount);
    if (outcome === 'NEGATIVE') o.memory.adaptationScore = Math.min(1, o.memory.adaptationScore + 0.08);
    if (outcome === 'POSITIVE') o.memory.adaptationScore = Math.max(0, o.memory.adaptationScore - 0.03);
    o.memory.ourActions = o.memory.ourActions.slice(-12);
    o.memory.responseHistory = o.memory.responseHistory.slice(-12);
  }
}

export function snapshotsFromOpponents(opponents: SimulatedOpponent[], observedAt: string): CompetitorSnapshot[] {
  return opponents.map(o => ({
    competitorId: o.id,
    price: o.price,
    estimatedCtr: o.ctr,
    estimatedCvr: o.cvr,
    trafficShare: o.trafficShare,
    observedAt
  }));
}


export interface OpponentCounterMatrixEntry {
  counter: OpponentStrategy;
  pressure: number;
  observations: number;
}

export function buildOpponentCounterMatrix(opponents: SimulatedOpponent[]): Record<string, OpponentCounterMatrixEntry> {
  const matrix: Record<string, OpponentCounterMatrixEntry> = {};
  for (const o of opponents) {
    for (const [action, counter] of Object.entries(o.memory.learnedResponses)) {
      const observations = o.memory.ourActions.filter(x => x.action === action).length;
      const entry = matrix[action];
      const learning = Math.max(0, Math.min(1, (o.memory.adaptationScore - 0.4) / 0.6));
      const pressure = Math.min(1, 0.25 + learning * 0.5 + Math.min(0.25, observations * 0.05));
      if (!entry || pressure > entry.pressure) {
        matrix[action] = { counter: counter as OpponentStrategy, pressure, observations };
      }
    }
  }
  return matrix;
}
