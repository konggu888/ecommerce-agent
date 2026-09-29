import { Action, GameState } from './game-state';
import { OpponentModel, modelOpponentResponses } from './opponent-model';
import { BehaviorMode, BehaviorObservation, inferHumanBehavior, nextBehaviorObservation } from './human-behavior-engine';

export interface GameNode {
  round: number;
  action: Action;
  opponentResponses: OpponentModel[];
  immediateScore: number;
  continuationScore: number;
  opponentRisk: number;
  expectedGain: number;
  marginalPenalty: number;
  path: string[];
  responseBranch?: { response: string; probability: number; nextActionHint: Action; stopCondition: string; expansionCondition: string; behaviorMode: BehaviorMode; }[];
  behaviorHypotheses?: { id: string; name: string; confidence: number; nextLikelyModes: BehaviorMode[] }[];
  nextBehaviorObservation?: string;
}

export interface MultiRoundPlan {
  horizon: number;
  nodes: GameNode[];
  bestPath: Action[];
  bestScore: number;
  robustness: number;
  explanation: string[];
  behaviorTrajectory: BehaviorObservation[];
  behaviorHypotheses: { id: string; name: string; confidence: number; nextLikelyModes: BehaviorMode[] }[];
  nextBehaviorObservation: string;
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
  let bestBehaviorTrajectory: BehaviorObservation[] = [];
  let bestBehaviorHypotheses: { id: string; name: string; confidence: number; nextLikelyModes: BehaviorMode[] }[] = [];
  let bestNextBehaviorObservation = '继续观察对手行为';

  function search(current: GameState, round: number, score: number, path: Action[], behaviorTrajectory: BehaviorObservation[] = []) {
    if (round > depth) {
      if (score > bestScore) {
        bestScore = score;
        bestPath = [...path];
        bestBehaviorTrajectory = [...behaviorTrajectory];
        bestBehaviorHypotheses = inferHumanBehavior(bestBehaviorTrajectory, 4).map(h => ({ id: h.id, name: h.name, confidence: h.confidence, nextLikelyModes: h.nextLikelyModes }));
        bestNextBehaviorObservation = nextBehaviorObservation(bestBehaviorTrajectory);
      }
      return;
    }
    for (const action of actions) {
      const opponent = modelOpponentResponses(current);
      const risk = opponentPenalty(action, opponent);
      const scale = current.budget > 0 ? Math.min(1, Math.max(0, current.spend / current.budget)) : 1;
      const marginalPenalty = Math.min(0.5, scale * 0.35 + risk * 0.35);
      const expectedGain = Math.max(0, actionBaseScore(current, action) - marginalPenalty);
      const immediate = expectedGain - risk;
      const discounted = immediate * Math.pow(0.85, round - 1);
      const nodeScore = score + discounted;
      nodes.push({
        round,
        action,
        opponentResponses: opponent,
        immediateScore: immediate,
        continuationScore: nodeScore,
        opponentRisk: risk,
        expectedGain,
        marginalPenalty,
        path: [...path, action].map(String)
      });
      const branches = [...opponent].sort((a, b) => b.probability - a.probability).slice(0, 2);
      const branchProbabilityTotal = branches.reduce((sum, branch) => sum + branch.probability, 0);
      const responseBranch: { response: string; probability: number; nextActionHint: Action; stopCondition: string; expansionCondition: string; behaviorMode: BehaviorMode }[] = branches.map((branch) => {
        const nextActionHint =
          branch.response === 'MATCH_PRICE' ? 'CHANGE_TARGETING' :
          branch.response === 'RAISE_BID' ? 'CHANGE_KEYWORD' :
          branch.response === 'DEFEND_TRAFFIC' ? 'CHANGE_TARGETING' :
          branch.response === 'SHIFT_TO_CONTENT' ? 'CHANGE_KEYWORD' :
          'HOLD';
        const stopCondition =
          branch.response === 'RAISE_BID' ? '若边际ROI继续下降或竞品连续抬价则停止扩量' :
          branch.response === 'MATCH_PRICE' ? '若价格战导致毛利跌破安全线则停止降价' :
          branch.response === 'DEFEND_TRAFFIC' ? '若拥挤度继续上升且转化不改善则停止追加流量' :
          branch.response === 'SHIFT_TO_CONTENT' ? '若内容流量抢占且搜索效率下降则停止原路径扩张' :
          '若边际ROI下降则保持观察';
        const expansionCondition =
          branch.response === 'RAISE_BID' ? '只有边际ROI保持高于阈值且现金充足才切换关键词后扩量' :
          branch.response === 'MATCH_PRICE' ? '只有降价后的转化/毛利同时达标才继续扩张' :
          branch.response === 'DEFEND_TRAFFIC' ? '只有目标人群转化改善且拥挤度可控才扩大投入' :
          branch.response === 'SHIFT_TO_CONTENT' ? '只有内容侧新增转化超过搜索侧损失才迁移预算' :
          '连续两个观察窗口指标稳定后再扩大投入';
        const behaviorMode: BehaviorMode = branch.response === 'SHIFT_TO_CONTENT' ? 'POSITIVE' : branch.response === 'HOLD' ? 'OBSERVE' : 'DEFENSIVE';
        return { response: branch.response, probability: branchProbabilityTotal > 0 ? branch.probability / branchProbabilityTotal : 0, nextActionHint: nextActionHint as Action, stopCondition, expansionCondition, behaviorMode };
      });
      const nodeIndex = nodes.length - 1;
      nodes[nodeIndex].responseBranch = responseBranch;
      const behaviorTrajectory: BehaviorObservation[] = responseBranch.map(branch => ({ mode: branch.behaviorMode, evidence: `模型响应假设: ${branch.response}` }));
      const behaviorHypotheses = inferHumanBehavior(behaviorTrajectory, 4).map(h => ({ id: h.id, name: h.name, confidence: h.confidence, nextLikelyModes: h.nextLikelyModes }));
      nodes[nodeIndex].behaviorHypotheses = behaviorHypotheses;
      nodes[nodeIndex].nextBehaviorObservation = nextBehaviorObservation(behaviorTrajectory);
      // Branch-aware continuation: evaluate both likely responses instead of following
      // only the highest-probability branch. The probability-weighted continuation
      // becomes the node's continuation value; the highest-probability branch still
      // determines the concrete default path shown to the operator.
      if (branches.length) {
        let weightedContinuation = 0;
        branches.forEach((branch, index) => {
          const childPath = [...path, action, responseBranch[index].nextActionHint];
          const branchState = projectState(current, action, branch);
          const branchAction = responseBranch[index].nextActionHint;
          const branchImmediate = actionBaseScore(branchState, branchAction);
          const branchRisk = opponentPenalty(branchAction, modelOpponentResponses(branchState));
          const branchValue = Math.max(0, branchImmediate - branchRisk);
          weightedContinuation += branch.probability * branchValue;
          if (index === 0) {
            search(branchState, round + 1, nodeScore + branch.probability * branchValue, [...path, action], [...behaviorTrajectory, { mode: responseBranch[index].behaviorMode, evidence: `模型响应假设: ${branch.response}` }]);
          }
        });
        nodes[nodes.length - 1].continuationScore = score + discounted + Math.pow(0.85, round) * weightedContinuation;
      }
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
      `候选路径节点数: ${nodes.length}`,
      `最优路径的对手响应风险: ${avgRisk.toFixed(2)}`,
      robustness >= 0.65 ? '路径具有较好的抗响应性' : '路径对对手响应较敏感，建议先做小规模实验',
      '每个节点保留最高概率的两种对手响应，并给出下一步动作提示',
      `行为演变轨迹: ${bestBehaviorTrajectory.map(x => x.mode).join(' → ') || '暂无'}`,
      `下一行为观察: ${bestNextBehaviorObservation}`
    ],
    behaviorTrajectory: bestBehaviorTrajectory,
    behaviorHypotheses: bestBehaviorHypotheses,
    nextBehaviorObservation: bestNextBehaviorObservation
  }
  };
}
