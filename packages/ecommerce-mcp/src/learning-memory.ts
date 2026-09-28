export interface DecisionRecord {
  id: string;
  shopId: string;
  productId?: string;
  campaignId?: string;
  observedState: Record<string, number | string | boolean | null>;
  hypothesis: string;
  action: string;
  expected: Record<string, number | string | null>;
  constraints: string[];
  confidence: number;
  createdAt: string;
}

export interface OutcomeRecord {
  decisionId: string;
  observed: Record<string, number | string | null>;
  evaluation: 'POSITIVE' | 'NEGATIVE' | 'INCONCLUSIVE';
  errorMetrics: Record<string, number>;
  observedAt: string;
}

export interface LearningSignal {
  decisionId: string;
  calibrationError: number;
  useful: boolean;
  lesson: string;
}

export function evaluateLearning(decision: DecisionRecord, outcome: OutcomeRecord): LearningSignal {
  const expectedRoi = Number(decision.expected.roi);
  const observedRoi = Number(outcome.observed.roi);
  const calibrationError = Number.isFinite(expectedRoi) && Number.isFinite(observedRoi)
    ? Math.abs(expectedRoi - observedRoi)
    : 1;
  const useful = outcome.evaluation !== 'INCONCLUSIVE';
  const lesson = !useful
    ? 'Insufficient evidence; do not update strategy weights.'
    : calibrationError < 0.2
      ? 'Prediction was well calibrated; retain strategy weight.'
      : 'Prediction error was material; reduce confidence for similar states and investigate confounders.';
  return { decisionId: decision.id, calibrationError, useful, lesson };
}
