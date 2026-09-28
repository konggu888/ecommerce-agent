export type WebSourceType =
  | 'NEWS'
  | 'PLATFORM_RULE'
  | 'COMPETITOR'
  | 'MARKETPLACE'
  | 'TREND'
  | 'CONTENT'
  | 'OTHER';

export type EvidenceLevel = 'FACT' | 'SIGNAL' | 'HYPOTHESIS' | 'UNVERIFIED';

export interface WebSource {
  sourceId: string;
  url: string;
  title: string;
  sourceType: WebSourceType;
  publisher?: string;
  observedAt: string;
  expiresAt?: string;
  reliability: number;
}

export interface WebObservation {
  observationId: string;
  source: WebSource;
  entity?: string;
  topic: string;
  observation: string;
  evidenceLevel: EvidenceLevel;
  numericValue?: number;
  unit?: string;
  direction?: 'UP' | 'DOWN' | 'FLAT' | 'UNKNOWN';
  relevance: number;
  tags: string[];
}

export interface WebMarketSignal {
  signalId: string;
  topic: string;
  direction: 'UP' | 'DOWN' | 'MIXED' | 'UNKNOWN';
  strength: number;
  confidence: number;
  evidence: WebObservation[];
  expiresAt?: string;
}

export interface WebIntelligenceSnapshot {
  observedAt: string;
  observations: WebObservation[];
  signals: WebMarketSignal[];
}

export function buildWebSignals(
  observations: WebObservation[],
  now = new Date()
): WebMarketSignal[] {
  const active = observations.filter((o) => {
    if (!o.source.expiresAt) return true;
    return new Date(o.source.expiresAt).getTime() >= now.getTime();
  });

  const groups = new Map<string, WebObservation[]>();
  for (const observation of active) {
    const list = groups.get(observation.topic) ?? [];
    list.push(observation);
    groups.set(observation.topic, list);
  }

  return [...groups.entries()].map(([topic, evidence], index) => {
    let up = 0;
    let down = 0;
    for (const item of evidence) {
      const weight = Math.max(0, Math.min(1, item.source.reliability * item.relevance));
      if (item.direction === 'UP') up += weight;
      if (item.direction === 'DOWN') down += weight;
    }

    const direction: WebMarketSignal['direction'] =
      up > down * 1.25 ? 'UP' :
      down > up * 1.25 ? 'DOWN' :
      up > 0 || down > 0 ? 'MIXED' : 'UNKNOWN';

    const total = up + down;
    return {
      signalId: `web-signal-${index + 1}`,
      topic,
      direction,
      strength: Math.min(1, total / Math.max(1, evidence.length)),
      confidence: Math.min(
        1,
        evidence.reduce((sum, item) => sum + item.source.reliability * item.relevance, 0) /
          Math.max(1, evidence.length)
      ),
      evidence,
      expiresAt: evidence
        .map((item) => item.source.expiresAt)
        .filter((v): v is string => Boolean(v))
        .sort()[0]
    };
  });
}

export function createMockWebIntelligence(now = new Date()): WebIntelligenceSnapshot {
  const iso = now.toISOString();
  const observations: WebObservation[] = [
    {
      observationId: 'mock-competitor-price',
      source: {
        sourceId: 'mock-market-01',
        url: 'https://mock.local/market/competitor-price',
        title: '模拟竞品价格变化',
        sourceType: 'COMPETITOR',
        publisher: 'Mock Market',
        observedAt: iso,
        reliability: 0.86
      },
      entity: 'SKU-DEMO-01',
      topic: 'competitor_price',
      observation: '同类竞品可见价格下降约6%。',
      evidenceLevel: 'SIGNAL',
      numericValue: -0.06,
      unit: 'ratio',
      direction: 'DOWN',
      relevance: 0.92,
      tags: ['price', 'competition']
    },
    {
      observationId: 'mock-traffic-cost',
      source: {
        sourceId: 'mock-traffic-01',
        url: 'https://mock.local/market/traffic-cost',
        title: '模拟类目流量成本',
        sourceType: 'MARKETPLACE',
        publisher: 'Mock Market',
        observedAt: iso,
        reliability: 0.82
      },
      topic: 'traffic_cost',
      observation: '同类流量 CPC 连续窗口上升约14%。',
      evidenceLevel: 'SIGNAL',
      numericValue: 0.14,
      unit: 'ratio',
      direction: 'UP',
      relevance: 0.88,
      tags: ['cpc', 'traffic']
    },
    {
      observationId: 'mock-demand',
      source: {
        sourceId: 'mock-trend-01',
        url: 'https://mock.local/trends/category',
        title: '模拟类目需求趋势',
        sourceType: 'TREND',
        publisher: 'Mock Trend',
        observedAt: iso,
        reliability: 0.72
      },
      topic: 'category_demand',
      observation: '类目搜索/内容热度上升，但归因仍不足。',
      evidenceLevel: 'HYPOTHESIS',
      numericValue: 0.11,
      unit: 'ratio',
      direction: 'UP',
      relevance: 0.76,
      tags: ['demand', 'content']
    },
    {
      observationId: 'mock-rule',
      source: {
        sourceId: 'mock-platform-01',
        url: 'https://mock.local/platform/rules',
        title: '模拟平台规则变化',
        sourceType: 'PLATFORM_RULE',
        publisher: 'Mock Platform',
        observedAt: iso,
        reliability: 0.55
      },
      topic: 'platform_rule',
      observation: '存在新的活动/流量规则信号，等待进一步证据。',
      evidenceLevel: 'UNVERIFIED',
      direction: 'UNKNOWN',
      relevance: 0.64,
      tags: ['platform', 'rule']
    }
  ];

  return { observedAt: iso, observations, signals: buildWebSignals(observations, now) };
}
