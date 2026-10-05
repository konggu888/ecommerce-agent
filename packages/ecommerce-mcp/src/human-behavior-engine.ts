export type BehaviorMode = 'POSITIVE' | 'NEGATIVE' | 'OBSERVE' | 'DEFENSIVE' | 'MIXED' | 'UNKNOWN';

export interface BehaviorObservation {
  mode: BehaviorMode;
  observedAt?: string;
  evidence?: string;
}

export interface BehaviorTransition {
  from: BehaviorMode;
  to: BehaviorMode;
  evidence: string[];
  confidence: number;
}

export interface BehaviorState {
  dominantMode: BehaviorMode;
  uncertainty: number;
  recentModes: BehaviorMode[];
  hypotheses: BehaviorHypothesis[];
  transitions: BehaviorTransition[];
  nextLikelyModes: BehaviorMode[];
  nextObservation: string;
}

export interface BehaviorHypothesis {
  id: string;
  name: string;
  confidence: number;
  sequenceFit: number;
  evidence: string[];
  nextLikelyModes: BehaviorMode[];
}

const PATTERNS: Array<{id:string;name:string;sequence:BehaviorMode[];next:BehaviorMode[]}> = [
  {id:'H01',name:'纯正向型',sequence:['POSITIVE','POSITIVE','POSITIVE'],next:['POSITIVE']},
  {id:'H02',name:'纯负向型',sequence:['NEGATIVE','NEGATIVE','NEGATIVE'],next:['NEGATIVE']},
  {id:'H03',name:'正负交替型',sequence:['POSITIVE','NEGATIVE','POSITIVE'],next:['NEGATIVE','POSITIVE']},
  {id:'H04',name:'先正后负型',sequence:['POSITIVE','POSITIVE','NEGATIVE'],next:['NEGATIVE','POSITIVE']},
  {id:'H05',name:'先负后正型',sequence:['NEGATIVE','NEGATIVE','POSITIVE'],next:['POSITIVE','NEGATIVE']},
  {id:'H06',name:'正负正型',sequence:['POSITIVE','NEGATIVE','POSITIVE'],next:['NEGATIVE','POSITIVE']},
  {id:'H07',name:'镜像型',sequence:['OBSERVE','POSITIVE','OBSERVE'],next:['POSITIVE','NEGATIVE','OBSERVE']},
  {id:'H09',name:'克制型',sequence:['OBSERVE','POSITIVE','OBSERVE'],next:['OBSERVE','POSITIVE']},
  {id:'H11',name:'防守转反击型',sequence:['DEFENSIVE','OBSERVE','POSITIVE'],next:['POSITIVE','OBSERVE']},
  {id:'H21',name:'多路径型',sequence:['POSITIVE','POSITIVE','NEGATIVE'],next:['POSITIVE','NEGATIVE','DEFENSIVE']},
  {id:'H34',name:'机会主义切换型',sequence:['MIXED','OBSERVE','POSITIVE'],next:['POSITIVE','NEGATIVE','OBSERVE']},
  {id:'H39',name:'学习进化型',sequence:['MIXED','OBSERVE','MIXED'],next:['POSITIVE','NEGATIVE','DEFENSIVE','OBSERVE']},
  {id:'H40',name:'自适应混合型',sequence:['POSITIVE','NEGATIVE','POSITIVE'],next:['POSITIVE','NEGATIVE','DEFENSIVE','OBSERVE']}
];

function normalize(seq: BehaviorObservation[]): BehaviorMode[] {
  return seq.map(x => x.mode).filter(x => x !== 'UNKNOWN');
}

function fit(observed: BehaviorMode[], pattern: BehaviorMode[]): number {
  if (!observed.length) return 0;
  const n = Math.min(observed.length, pattern.length);
  let matches = 0;
  for (let i=0;i<n;i++) if (observed[observed.length-n+i] === pattern[i]) matches++;
  const transitionCount = observed.length > 1 ? observed.length - 1 : 1;
  let switches = 0;
  for (let i=1;i<observed.length;i++) if (observed[i] !== observed[i-1]) switches++;
  const switchBonus = pattern.includes('MIXED') || pattern.includes('NEGATIVE') ? Math.min(0.2, switches / transitionCount * 0.2) : 0;
  return Math.min(1, matches / n * 0.8 + switchBonus);
}

export function inferHumanBehavior(observations: BehaviorObservation[], limit = 5): BehaviorHypothesis[] {
  const observed = normalize(observations);
  if (!observed.length) return [{id:'UNKNOWN',name:'信息不足',confidence:0,sequenceFit:0,evidence:['尚无足够连续观察'],nextLikelyModes:['OBSERVE']}];

  const scored = PATTERNS.map(p => {
    const confidence = fit(observed, p.sequence);
    return {
      id:p.id,
      name:p.name,
      confidence,
      sequenceFit: confidence,
      evidence:[
        `最近观察序列：${observed.slice(-6).join(' → ')}`,
        '这是行为模式假设，不是对手心理或身份判断'
      ],
      nextLikelyModes:p.next
    };
  }).sort((a,b)=>b.confidence-a.confidence);

  const total = scored.reduce((s,x)=>s+x.confidence,0);
  return scored.slice(0,Math.max(1,limit)).map(x => ({...x,confidence:total>0 ? x.confidence/total : 0}));
}

export function nextBehaviorObservation(observations: BehaviorObservation[]): string {
  if (observations.length < 2) return '继续收集至少一个连续观察窗口，不根据单次动作归因';
  const last = observations[observations.length-1].mode;
  const prev = observations[observations.length-2].mode;
  if (last !== prev) return '重点观察策略切换是否持续，以及切换后对市场指标造成的变化';
  return '重点观察当前行为是否连续三个窗口保持一致，避免把短期波动误判为稳定行为模式';
}


export function updateBehaviorState(
  observations: BehaviorObservation[],
  previous?: BehaviorState,
  limit = 5
): BehaviorState {
  const hypotheses = inferHumanBehavior(observations, limit);
  const recentModes = normalize(observations).slice(-6);
  const top = hypotheses[0];
  const transitions: BehaviorTransition[] = [];
  for (let i = 1; i < recentModes.length; i++) {
    const from = recentModes[i - 1], to = recentModes[i];
    if (from !== to) {
      transitions.push({
        from,
        to,
        evidence: [`观察到行为模式切换: ${from} → ${to}`],
        confidence: Math.min(0.9, 0.5 + (recentModes.length - i) * 0.05)
      });
    }
  }
  const previousMode = previous?.dominantMode;
  const dominantMode = top?.nextLikelyModes?.[0] && top.confidence >= 0.35
    ? top.nextLikelyModes[0]
    : (recentModes[recentModes.length - 1] ?? 'UNKNOWN');
  const uncertainty = Math.max(
    0,
    Math.min(
      1,
      1 - (top?.confidence ?? 0) + (previousMode && previousMode !== dominantMode ? 0.08 : 0)
    )
  );
  const nextLikelyModes = Array.from(new Set(
    hypotheses.flatMap(h => h.nextLikelyModes)
  )).slice(0, 5);
  return {
    dominantMode,
    uncertainty,
    recentModes,
    hypotheses,
    transitions,
    nextLikelyModes: nextLikelyModes.length ? nextLikelyModes : ['OBSERVE'],
    nextObservation: nextBehaviorObservation(observations)
  };
}
