import { GameState, Action, CompetitorSnapshot } from './game-state';

export interface SimMarket {
  demand: number;
  trafficCost: number;
  categoryCvr: number;
  competitors: CompetitorSnapshot[];
}

export interface SimMarketRound {
  round: number;
  action: Action;
  opponentActions: string[];
  state: GameState;
  breakthroughSignal: string;
}

export interface SimMarketConfig {
  rounds?: number;
  seed?: number;
  initial: GameState;
  market: SimMarket;
}

function clone<T>(v: T): T { return JSON.parse(JSON.stringify(v)); }

export function runSimulatedMarket(config: SimMarketConfig): SimMarketRound[] {
  const rounds = Math.max(1, Math.min(200, config.rounds ?? 30));
  let s = clone(config.initial);
  const market = clone(config.market);
  let seed = (config.seed ?? 42) >>> 0;
  const rnd = () => { seed = (1664525 * seed + 1013904223) >>> 0; return seed / 4294967296; };
  const out: SimMarketRound[] = [];

  for (let round = 1; round <= rounds; round++) {
    const actions: Action[] = ['HOLD','INCREASE_BUDGET','DECREASE_BUDGET','INCREASE_BID','DECREASE_BID','CHANGE_KEYWORD','CHANGE_TARGETING','CHANGE_PRICE'];
    const action = actions[(round + Math.floor(rnd() * actions.length)) % actions.length];
    if (action === 'INCREASE_BUDGET') s.budget *= 1.08;
    if (action === 'DECREASE_BUDGET') s.budget *= 0.92;
    if (action === 'INCREASE_BID') market.trafficCost *= 1.04;
    if (action === 'DECREASE_BID') market.trafficCost *= 0.97;
    if (action === 'CHANGE_PRICE') s.price *= market.demand > 1 ? 1.01 : 0.98;

    const pressure = market.trafficCost * (1 + Math.max(0, market.competitors[0]?.trafficShare ?? 0) * 0.3);
    const spend = Math.min(s.budget, Math.max(0, s.spend * 0.15 + 120 / Math.max(0.5, pressure)));
    const ctr = Math.max(0.005, Math.min(0.12, (s.ctr ?? 0.03) * (action === 'CHANGE_KEYWORD' || action === 'CHANGE_TARGETING' ? 1.06 : 1)));
    const cvr = Math.max(0.005, Math.min(0.2, market.categoryCvr * (action === 'CHANGE_PRICE' ? 1.02 : 1)));
    const clicks = Math.floor(spend / Math.max(0.5, pressure));
    const conversions = Math.floor(Math.min(999, clicks * cvr * market.demand));
    const revenue = conversions * s.price;

    s = { ...s, spend, impressions: Math.floor(clicks / ctr), clicks, conversions, revenue, ctr, cvr, cpc: clicks ? spend / clicks : 0, roi: spend ? revenue / spend : 0, competitors: market.competitors, observedAt: new Date().toISOString() };

    const opponentActions: string[] = [];
    for (const c of market.competitors) {
      if (action === 'CHANGE_PRICE' && s.price < (c.price ?? s.price) * 0.97) {
        c.price = Math.max(1, (c.price ?? s.price) * 0.98);
        opponentActions.push(c.competitorId + ':MATCH_PRICE');
      } else if (action === 'INCREASE_BID' && (c.trafficShare ?? 0) > 0.3) {
        c.estimatedCtr = (c.estimatedCtr ?? 0.03) * 1.04;
        opponentActions.push(c.competitorId + ':RAISE_BID');
      } else if (action === 'CHANGE_TARGETING' || action === 'CHANGE_KEYWORD') {
        c.trafficShare = Math.max(0.05, (c.trafficShare ?? 0.2) * 0.98);
        opponentActions.push(c.competitorId + ':DEFEND_TRAFFIC');
      } else opponentActions.push(c.competitorId + ':HOLD');
    }

    const breakthroughSignal = s.cvr > market.categoryCvr * 1.08 ? 'CONVERSION_GAP' : s.ctr > 0.04 && pressure < 2 ? 'TRAFFIC_GAP' : s.roi > 3 ? 'ECONOMIC_GAP' : 'NO_CLEAR_GAP';
    out.push({ round, action, opponentActions, state: clone(s), breakthroughSignal });
    market.demand = Math.max(0.65, Math.min(1.5, market.demand + (rnd() - 0.48) * 0.04));
    market.categoryCvr = Math.max(0.01, Math.min(0.12, market.categoryCvr + (rnd() - 0.5) * 0.002));
  }
  return out;
}
