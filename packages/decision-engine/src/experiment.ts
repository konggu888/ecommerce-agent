import type { CampaignObservation, DecisionProposal } from './v0';

export type ExperimentProposal = {
  campaignId: string;
  baseline: Record<string, number>;
  treatment: Record<string, number>;
  hypothesis: string;
  guardrails: { maxChangePct: number; minimumObservations: number };
};

export function toExperiment(c: CampaignObservation, d: DecisionProposal): ExperimentProposal {
  return {
    campaignId: c.campaignId,
    baseline: { budget: c.budget, bid: c.bid },
    treatment: {
      budget: d.action.includes('budget') ? c.budget * (1 + (d.action === 'increase_budget' ? d.changePct : -d.changePct) / 100) : c.budget,
      bid: d.action.includes('bid') ? c.bid * (1 + (d.action === 'increase_bid' ? d.changePct : -d.changePct) / 100) : c.bid,
    },
    hypothesis: d.rationale,
    guardrails: { maxChangePct: Math.abs(d.changePct), minimumObservations: 100 },
  };
}
