import { GameState } from './game-state';

export type ThreatHypothesisId = 'NORMAL_MARKET' | 'PLATFORM_CHANGE' | 'COMPETITOR_NORMAL' | 'ABNORMAL_COMPETITION' | 'UNKNOWN';

export interface ThreatEvidence {
  threatId: string;
  signal: string;
  strength: number; // 0..1, evidence strength only; not a probability of attacker identity
  observedAt?: string;
}

export interface ThreatHypothesis {
  id: ThreatHypothesisId;
  confidence: number; // calibrated belief, not attribution
  supportingEvidence: string[];
}

export interface ThreatInference {
  threatId: string;
  hypotheses: ThreatHypothesis[];
  attributionStatus: 'UNATTRIBUTED' | 'POSSIBLE_COMPETITIVE_BEHAVIOR' | 'STRONG_ASSOCIATION' | 'DIRECT_EVIDENCE';
  evidence: ThreatEvidence[];
  nextObservation: string;
}

export function normalizeHypotheses(h: ThreatHypothesis[]): ThreatHypothesis[] {
  const valid = h.filter(x => Number.isFinite(x.confidence) && x.confidence >= 0);
  const total = valid.reduce((s, x) => s + x.confidence, 0);
  if (!total) return valid.map(x => ({ ...x, confidence: 1 / Math.max(1, valid.length) }));
  return valid.map(x => ({ ...x, confidence: x.confidence / total }));
}

export function competitorInferenceRisk(inferences: ThreatInference[] = []): number {
  if (!inferences.length) return 0;
  return Math.min(1, inferences.reduce((sum, x) => {
    const abnormal = normalizeHypotheses(x.hypotheses).find(h => h.id === 'ABNORMAL_COMPETITION')?.confidence ?? 0;
    const attribution = x.attributionStatus === 'DIRECT_EVIDENCE' ? 1 : x.attributionStatus === 'STRONG_ASSOCIATION' ? 0.8 : x.attributionStatus === 'POSSIBLE_COMPETITIVE_BEHAVIOR' ? 0.45 : 0;
    return sum + Math.max(abnormal, abnormal * 0.7 + attribution * 0.3);
  }, 0) / inferences.length);
}

export function buildThreatInference(
  threatId: string,
  evidence: ThreatEvidence[],
  alternatives: ThreatHypothesis[] = []
): ThreatInference {
  const strength = evidence.length
    ? evidence.reduce((s, e) => s + Math.max(0, Math.min(1, e.strength)), 0) / evidence.length
    : 0;
  const hypotheses = normalizeHypotheses(
    alternatives.length ? alternatives : [
      { id: 'NORMAL_MARKET', confidence: 1 - strength * 0.45, supportingEvidence: [] },
      { id: 'COMPETITOR_NORMAL', confidence: strength * 0.25, supportingEvidence: [] },
      { id: 'ABNORMAL_COMPETITION', confidence: strength * 0.30, supportingEvidence: evidence.map(e => e.signal) },
      { id: 'UNKNOWN', confidence: 0.25, supportingEvidence: [] }
    ]
  );
  return {
    threatId,
    hypotheses,
    attributionStatus: 'UNATTRIBUTED',
    evidence,
    nextObservation: '继续观察同类信号是否持续，并检查至少一个独立指标或渠道是否同步异常。'
  };
}

export function inferOpponentUncertainty(state: GameState): number {
  return competitorInferenceRisk(state.threatInferences ?? []);
}
