import { GameState, Action } from './game-state';
import { findBreakthroughs, Breakthrough } from './breakthrough-engine';
import { rankPositiveStrategies, PositiveStrategyCandidate } from './positive-attack-engine';

export type PositiveRoundStage =
  | 'TRIGGER'
  | 'OUR_ACTION'
  | 'OBSERVE'
  | 'RESPONSE_HYPOTHESIS'
  | 'DECISION';

export interface PositiveRound {
  round: number;
  stage: PositiveRoundStage;
  title: string;
  action?: Action;
  observation: string;
  responseHypothesis?: string[];
  stopCondition?: string;
  expansionCondition?: string;
}

export interface PositiveStrategyPlan {
  strategyId: string;
  strategyName: string;
  score: number;
  breakthrough?: Breakthrough;
  rounds: PositiveRound[];
  nextObservation: string;
  endStates: Array<'EXPAND' | 'HOLD' | 'DOWNGRADE' | 'WAIT' | 'STOP'>;
}

export interface PositiveStrategyPlannerOutput {
  discoveredBreakthroughs: Breakthrough[];
  candidates: PositiveStrategyPlan[];
  selectedStrategy: PositiveStrategyPlan | null;
  horizon: 3 | 5;
  nextObservation: string;
  principle: string;
}

function mapStageAction(candidate: PositiveStrategyCandidate): Action {
  return candidate.mappedAction;
}

function buildRounds(
  candidate: PositiveStrategyCandidate,
  breakthrough: Breakthrough | undefined,
  horizon: 3 | 5
): PositiveRound[] {
  const action = mapStageAction(candidate);
  const stop = breakthrough?.stopCondition ?? '关键指标未改善或单位经济恶化时停止扩大';
  const expand = breakthrough
    ? breakthrough.expectedSignal + '连续两个观察窗口保持改善后再扩大'
    : '关键指标连续两个观察窗口改善且风险可控后再扩大';

  const rounds: PositiveRound[] = [
    {
      round: 1,
      stage: 'TRIGGER',
      title: '确认突破口',
      observation: candidate.trigger,
      stopCondition: '触发条件无法从现有数据得到支持时，不进入动作实验'
    },
    {
      round: 2,
      stage: 'OUR_ACTION',
      title: '小规模实验',
      action,
      observation: candidate.nextObservation,
      responseHypothesis: candidate.opponentBranches
    },
    {
      round: 3,
      stage: 'OBSERVE',
      title: '观察结果',
      observation: candidate.nextObservation,
      stopCondition: stop,
      expansionCondition: expand
    }
  ];

  if (horizon === 5) {
    rounds.push(
      {
        round: 4,
        stage: 'RESPONSE_HYPOTHESIS',
        title: '重新评估市场/竞品响应',
        observation: '比较实验前后基线，并检查是否存在同步的竞品、平台或需求变化',
        responseHypothesis: [
          '竞品正常跟随',
          '无明显竞品响应',
          '平台/需求自然变化',
          '未知原因'
        ],
        stopCondition: '无法区分自身效果与外部变化时，回到小规模观察'
      },
      {
        round: 5,
        stage: 'DECISION',
        title: '进入下一轮',
        observation: '综合增量效果、单位经济、风险和可持续性',
        stopCondition: stop,
        expansionCondition: expand
      }
    );
  }

  return rounds;
}

export function buildPositiveStrategyPlan(
  state: GameState,
  horizon: 3 | 5 = 5,
  limit = 5
): PositiveStrategyPlannerOutput {
  const discoveredBreakthroughs = findBreakthroughs(state).slice(0, 5);
  const ranked = rankPositiveStrategies(state, Math.max(1, limit));

  const candidates = ranked.map((candidate) => {
    const breakthrough = discoveredBreakthroughs[0];
    return {
      strategyId: candidate.strategyId,
      strategyName: candidate.strategyName,
      score: candidate.score,
      breakthrough,
      rounds: buildRounds(candidate, breakthrough, horizon),
      nextObservation: candidate.nextObservation,
      endStates: ['EXPAND', 'HOLD', 'DOWNGRADE', 'WAIT', 'STOP'] as Array<'EXPAND' | 'HOLD' | 'DOWNGRADE' | 'WAIT' | 'STOP'>
    };
  });

  return {
    discoveredBreakthroughs,
    candidates,
    selectedStrategy: candidates[0] ?? null,
    horizon,
    nextObservation: candidates[0]?.nextObservation ?? '等待更多数据',
    principle: '只使用可观测数据选择策略；竞品响应只作为假设，不作为已知事实。'
  };
}
