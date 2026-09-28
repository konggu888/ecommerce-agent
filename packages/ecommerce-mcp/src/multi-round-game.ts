import { Action, GameState } from './game-state';
import { OpponentModel, modelOpponentResponses } from './opponent-model';

export interface GameNode {
  round: number;
  action: Action;
  opponentResponses: OpponentModel[];
  immediateScore: number;
  continuationScore: number;
  opponentRisk: number;
  path: string[];
}

export interface MultiRoundPlan {
  horizon: number;
  nodes: GameNode[];
  bestPath: Action[];
  bestScore: number;
  robustness: number;
  explanation: string[];
}

const actions: Action[] = [
  'HOLD',
  'INCREASE_BUDGET',
  'DECREASE_BUDGET',
  'INCREASE_BID',
  'DECREASE_BID',
  'CHANGE_KEYWORD',
  'CHANGE_TARGETING',
  'CHANGE_PRICE'
];

function actionBaseScore(state: GameState, action: Action): number {
  const roi = state.roi ?? 0;
  const cvr = state.cvr ?? 0;
  const ctr = state.ctr ?? 0;
  if (action === 'HOLD') return 0.35;
  if (action === 'CHANGE_TARGETING') return cvr > 0.03 ? 0.72 : 0.58;
  if (action === 'CHANGE_KEYWORD') return ctr < 0.03 ? 0.68 : 0.55;
  if (action === 'CHANGE_PRICE') return state.price > 0 ? 0.55 : 0.3;
  if (action === 'INCREASE_BID') return roi > 2 && ctr > 0.02 ? 0.58 : 0.35;
  if (action === 'INCREASE_BUDGET') return roi > 2.5 ? 0.62 : 0.34;
  if (action === 'DECREASE_BID') return roi < 2 ? 0.55 : 0.38;
  if (action === 'DECREASE_BUDGET') return roi < 1.5 ? 0.62 : 0.3;
  return 0.3;
}

function opponentPenalty(action: Action, opponent: OpponentModel[]): number {
  if (!opponent.length) return 0.1;
  return opponent.reduce((sum, o) => {
    const copyable =
      (action === 'CHANGE_PRICE' && o.response === 'MATCH_PRICE') ||
      ((action === 'INCREASE_BID' || action === 'INCREASE_BUDGET') && o.response === 'RAISE_BID');
    return sum + (copyable ? o.probability * 0.35 : 0);
  }, 0) / opponent.length;
}

function projectState(state: GameState, action: Action, response?: OpponentModel): GameState {
  const next = { ...state };
  if (action === 'INCREASE_BUDGET') next.budget *= 1.1;
  if (action === 'DECREASE_BUDGET') next.budget *= 0.9;
  if (action === 'CHANGE_PRICE') next.price *= 0.98;
  if (action === 'INCREASE_BID') next.cpc = (next.cpc ?? 1) * 1.05;
  if (action === 'DECREASE_BID') next.cpc = (next.cpc ?? 1) * 0.95;
  if (action === 'CHANGE_TARGETING') next.cvr = (next.cvr ?? 0) * 1.05 + 0.002;
  if (action === 'CHANGE_KEYWORD') next.ctr = (next.ctr ?? 0) * 1.06 + 0.001;

  // Project the likely next-round state after the opponent observes our move.
  // This keeps the plan sequential instead of scoring every action independently.
  if (response?.response === 'MATCH_PRICE' && action === 'CHANGE_PRICE') next.price *= 1.01;
  if (response?.response === 'RAISE_BID' && (action === 'INCREASE_BID' || action === 'INCREASE_BUDGET')) next.cpc = (next.cpc ?? 1) * 1.04;
  if (response?.response === 'DEFEND_TRAFFIC' && (action === 'CHANGE_TARGETING' || action === 'CHANGE_KEYWORD')) next.ctr = (next.ctr ?? 0) * 0.985;
  if (response?.response === 'SHIFT_TO_CONTENT' && (action === 'CHANGE_KEYWORD' || action === 'CHANGE_TARGETING')) next.cvr = (next.cvr ?? 0) * 0.99;
  next.observedAt = new Date(Date.now() + 60000).toISOString();
  return next;
}

export function planMultiRoundGame(state: GameState, horizon = 3): MultiRoundPlan {
  const depth = Math.max(1, Math.min(5, horizon));
  const nodes: GameNode[] = [];
  let bestPath: Action[] = [];
  let bestScore = -Infinity;

  function search(current: GameState, round: number, score: number, path: Action[]) {
    if (round > depth) {
      if (score > bestScore) {
        bestScore = score;
        bestPath = [...path];
      }
      return;
    }
    for (const action of actions) {
      const opponent = modelOpponentResponses(current);
      const risk = opponentPenalty(action, opponent);
      const immediate = actionBaseScore(current, action) - risk;
      const discounted = immediate * Math.pow(0.85, round - 1);
      const nodeScore = score + discounted;
      nodes.push({
        round,
        action,
        opponentResponses: opponent,
        immediateScore: immediate,
        continuationScore: nodeScore,
        opponentRisk: risk,
        path: [...path, action].map(String)
      });
      const primaryResponse = [...opponent].sort((a, b) => b.probability - a.probability)[0];
      search(projectState(current, action, primaryResponse), round + 1, nodeScore, [...path, action]);
    }
  }

  search(state, 1, 0, []);
  const bestNodes = nodes.filter(n => n.path.join('|') === bestPath.map(String).join('|'));
  const risks = bestNodes.map(n => n.opponentRisk);
  const avgRisk = risks.length ? risks.reduce((a,b)=>a+b,0)/risks.length : 1;
  const robustness = Math.max(0, Math.min(1, 1 - avgRisk));

  return {
    horizon: depth,
    nodes,
    bestPath,
    bestScore,
    robustness,
    explanation: [
      `多轮视野: ${depth} 轮`,
      `候选路径数: ${nodes.length}`,
      `最优路径的对手响应风险: ${avgRisk.toFixed(2)}`,
      robustness >= 0.65 ? '路径具有较好的抗响应性' : '路径对对手响应较敏感，建议先做小规模实验'
    ]
  };
}
