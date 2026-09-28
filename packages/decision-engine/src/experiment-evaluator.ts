export type ExperimentResult = 'POSITIVE' | 'NEGATIVE' | 'INCONCLUSIVE';

export interface PeriodMetrics {
  spend: number;
  revenue: number;
  conversions: number;
  clicks: number;
  impressions: number;
}

export interface ExperimentInput {
  baseline: PeriodMetrics;
  treatment: PeriodMetrics;
  minSpend?: number;
  minConversions?: number;
  expectedLift?: number;
}

export interface ExperimentEvaluation {
  result: ExperimentResult;
  baselineRoi: number;
  treatmentRoi: number;
  roiLift: number;
  cvrLift: number;
  cpcChange: number;
  evidenceLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  reasons: string[];
}

function roi(m: PeriodMetrics): number {
  return m.spend > 0 ? m.revenue / m.spend : 0;
}

function cvr(m: PeriodMetrics): number {
  return m.clicks > 0 ? m.conversions / m.clicks : 0;
}

function cpc(m: PeriodMetrics): number {
  return m.clicks > 0 ? m.spend / m.clicks : 0;
}

/**
 * Evaluates a controlled before/after experiment conservatively.
 * This is evidence scoring, not a causal guarantee. External confounders
 * must be recorded by the caller (price, stock, promotion, seasonality, etc.).
 */
export function evaluateExperiment(input: ExperimentInput): ExperimentEvaluation {
  const baselineRoi = roi(input.baseline);
  const treatmentRoi = roi(input.treatment);
  const roiLift = baselineRoi > 0 ? treatmentRoi / baselineRoi - 1 : 0;
  const baseCvr = cvr(input.baseline);
  const treatmentCvr = cvr(input.treatment);
  const cvrLift = baseCvr > 0 ? treatmentCvr / baseCvr - 1 : 0;
  const baseCpc = cpc(input.baseline);
  const treatmentCpc = cpc(input.treatment);
  const cpcChange = baseCpc > 0 ? treatmentCpc / baseCpc - 1 : 0;

  const minSpend = input.minSpend ?? 100;
  const minConversions = input.minConversions ?? 10;
  const expectedLift = input.expectedLift ?? 0.05;

  const evidencePoints = [
    input.treatment.spend >= minSpend,
    input.treatment.conversions >= minConversions,
    input.treatment.impressions >= 1000,
  ].filter(Boolean).length;

  const evidenceLevel = evidencePoints >= 3 ? 'HIGH' : evidencePoints >= 2 ? 'MEDIUM' : 'LOW';
  const reasons: string[] = [];

  if (input.treatment.spend < minSpend) reasons.push('treatment spend is below the minimum evidence threshold');
  if (input.treatment.conversions < minConversions) reasons.push('treatment conversions are below the minimum evidence threshold');
  if (input.treatment.impressions < 1000) reasons.push('treatment impressions are below the minimum evidence threshold');
  if (Math.abs(roiLift) < expectedLift) reasons.push('ROI movement is smaller than the configured expected lift');

  let result: ExperimentResult = 'INCONCLUSIVE';
  if (evidenceLevel !== 'LOW' && roiLift >= expectedLift && cvrLift >= -0.02) result = 'POSITIVE';
  if (evidenceLevel !== 'LOW' && roiLift <= -expectedLift) result = 'NEGATIVE';

  return { result, baselineRoi, treatmentRoi, roiLift, cvrLift, cpcChange, evidenceLevel, reasons };
}
