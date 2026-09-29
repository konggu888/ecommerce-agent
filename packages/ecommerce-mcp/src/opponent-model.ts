import { Action, CompetitorSnapshot, GameState } from './game-state';

export type OpponentResponse =
  | 'MATCH_PRICE'
  | 'RAISE_BID'
  | 'HOLD'
  | 'DEFEND_TRAFFIC'
  | 'SHIFT_TO_CONTENT'
  | 'UNKNOWN';

export interface OpponentModel {
  competitorId: string;
  response: OpponentResponse;
  probability: number;
  rationale: string[];
}

export interface BreakthroughInput {
  state: GameState;
  action: Action;
  opponent: OpponentModel[];
}

export interface OpponentBreakthrough {
  type: 'PRICE_GAP' | 'TRAFFIC_GAP' | 'CONVERSION_GAP' | 'CONTENT_GAP' | 'RESILIENCE_GAP' | 'NO_CLEAR_GAP';
  score: number;
  reason: string;
  suggestedActions: Action[];
  opponentResponseRisk: number;
}

function modelOne(c: CompetitorSnapshot, state: GameState): OpponentModel {
  const rationale: string[] = [];
  let response: OpponentResponse = 'UNKNOWN';
  let probability = 0.35;

  const priceGap = c.price != null ? c.price - state.price : 0;
  if (priceGap > 0.05 * Math.max(1, state.price)) {
    response = 'MATCH_PRICE';
    probability = 0.62;
    rationale.push('竞品当前价格明显高于我方，存在跟价空间');
  } else if ((c.trafficShare ?? 0) > 0.45) {
    response = 'DEFEND_TRAFFIC';
    probability = 0.68;
    rationale.push('竞品流量份额较高，可能优先防守流量位');
  } else if ((c.estimatedCtr ?? 0) > (state.ctr ?? 0) * 1.15) {
    response = 'RAISE_BID';
    probability = 0.58;
    rationale.push('竞品点击效率更高，可能通过竞价维持曝光');
  } else if ((c.estimatedCvr ?? 0) > (state.cvr ?? 0) * 1.15) {
    response = 'SHIFT_TO_CONTENT';
    probability = 0.52;
    rationale.push('竞品转化效率更高，内容/商品表达可能形成防守');
  } else {
    response = 'HOLD';
    probability = 0.48;
    rationale.push('当前公开信号不足以支持强响应判断');
  }

  return { competitorId: c.competitorId, response, probability, rationale };
}

export function modelOpponentResponses(state: GameState): OpponentModel[] {
  return state.competitors.map(c => modelOne(c, state));
}

export function detectBreakthrough(input: BreakthroughInput): OpponentBreakthrough {
  const s = input.state;
  const priceGaps = s.competitors.filter(c => c.price != null).map(c => (c.price! - s.price) / Math.max(1, s.price));
  const ctrGaps = s.competitors.filter(c => c.estimatedCtr != null).map(c => c.estimatedCtr! - (s.ctr ?? 0));
  const cvrGaps = s.competitors.filter(c => c.estimatedCvr != null).map(c => c.estimatedCvr! - (s.cvr ?? 0));
  const maxPriceGap = priceGaps.length ? Math.max(...priceGaps) : 0;
  const maxCtrGap = ctrGaps.length ? Math.max(...ctrGaps) : 0;
  const maxCvrGap = cvrGaps.length ? Math.max(...cvrGaps) : 0;
  const responseRisk = input.opponent.length
    ? input.opponent.reduce((n, o) => n + (o.response === 'MATCH_PRICE' || o.response === 'RAISE_BID' ? o.probability : 0), 0) / input.opponent.length
    : 0.5;

  if (input.action === 'CHANGE_PRICE' && maxPriceGap > 0.08) {
    return { type: 'PRICE_GAP', score: Math.min(1, maxPriceGap * 4), reason: '存在可量化的相对价格空间，但需要扣除跟价响应风险', suggestedActions: ['CHANGE_PRICE'], opponentResponseRisk: responseRisk };
  }
  if ((input.action === 'INCREASE_BID' || input.action === 'INCREASE_BUDGET') && maxCtrGap < 0) {
    return { type: 'TRAFFIC_GAP', score: Math.min(1, Math.abs(maxCtrGap) * 8), reason: '当前点击效率弱于可见竞品，单纯加价可能放大低效率', suggestedActions: ['CHANGE_KEYWORD', 'CHANGE_TARGETING', 'DECREASE_BID'], opponentResponseRisk: responseRisk };
  }
  if (maxCvrGap > 0.02) {
    return { type: 'CONVERSION_GAP', score: Math.min(1, maxCvrGap * 10), reason: '竞品转化效率更高，突破点更可能在商品表达/内容/承接而非单纯买流量', suggestedActions: ['CHANGE_TARGETING', 'CHANGE_KEYWORD'], opponentResponseRisk: responseRisk };
  }
  if (responseRisk > 0.6) {
    return { type: 'RESILIENCE_GAP', score: responseRisk, reason: '对手响应概率较高，应该优先寻找对手难以即时复制的变量', suggestedActions: ['CHANGE_TARGETING', 'CHANGE_KEYWORD', 'HOLD'], opponentResponseRisk: responseRisk };
  }
  if (maxPriceGap > 0.03) {
    return { type: 'PRICE_GAP', score: Math.min(1, maxPriceGap * 3), reason: '存在中等价格空间，适合小规模实验验证', suggestedActions: ['CHANGE_PRICE'], opponentResponseRisk: responseRisk };
  }
  return { type: 'NO_CLEAR_GAP', score: 0.2, reason: '当前我方、对手和市场数据不足以确认稳定突破口', suggestedActions: ['HOLD'], opponentResponseRisk: responseRisk };
}
