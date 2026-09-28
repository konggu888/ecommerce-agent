export type AdversarialBehavior =
  | 'MALICIOUS_NEGATIVE_REVIEW'
  | 'REVIEW_BRIGADING'
  | 'FAKE_POSITIVE_REVIEW'
  | 'REVIEW_SUPPRESSION'
  | 'MALICIOUS_REPORTING'
  | 'FALSE_COMPLAINT'
  | 'PRICE_UNDERCUTTING'
  | 'TRAFFIC_BID_WAR'
  | 'CLICK_FRAUD'
  | 'AD_INTERFERENCE'
  | 'COPYCAT_LISTING'
  | 'CONTENT_COPYING'
  | 'KEYWORD_INTERFERENCE'
  | 'CUSTOMER_POACHING'
  | 'STOCK_PRESSURE'
  | 'SUPPLY_DISRUPTION'
  | 'RUMOR_OR_REPUTATION_ATTACK'
  | 'PLATFORM_RULE_ABUSE'
  | 'PROMOTION_ARBITRAGE'
  | 'COORDINATED_COMPETITOR_ACTION'
  | 'INFORMATION_MANIPULATION'
  | 'OTHER';

export type AdversarialRisk = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface AdversarialSignal {
  behavior: AdversarialBehavior;
  risk: AdversarialRisk;
  detected: boolean;
  confidence: number;
  evidence: string[];
  impactChannels: Array<'RANKING'|'CONVERSION'|'TRAFFIC'|'REPUTATION'|'PRICE'|'SUPPLY'|'CASHFLOW'|'PLATFORM_ACCESS'>;
  response: 'MONITOR' | 'PROTECT' | 'DOCUMENT' | 'PLATFORM_REVIEW' | 'LEGAL_REVIEW' | 'BLOCK_AUTOMATION';
}

export interface AdversarialGameInput {
  baseline: {
    reviewRate?: number;
    negativeReviewRate?: number;
    complaintRate?: number;
    cpc?: number;
    cvr?: number;
    traffic?: number;
    price?: number;
  };
  current: {
    reviewRate?: number;
    negativeReviewRate?: number;
    complaintRate?: number;
    cpc?: number;
    cvr?: number;
    traffic?: number;
    price?: number;
  };
  evidence: string[];
}

export function detectAdversarialSignals(input: AdversarialGameInput): AdversarialSignal[] {
  const out: AdversarialSignal[] = [];
  const b = input.baseline;
  const c = input.current;

  if ((c.negativeReviewRate ?? 0) > Math.max((b.negativeReviewRate ?? 0) * 2.5, 0.08)) {
    out.push({
      behavior: 'MALICIOUS_NEGATIVE_REVIEW',
      risk: 'HIGH',
      detected: true,
      confidence: 0.55,
      evidence: [...input.evidence, '负面评价结构发生异常变化'],
      impactChannels: ['REPUTATION','CONVERSION'],
      response: 'DOCUMENT'
    });
  }

  if ((c.reviewRate ?? 0) > Math.max((b.reviewRate ?? 0) * 3, 0.2)) {
    out.push({
      behavior: 'REVIEW_BRIGADING',
      risk: 'HIGH',
      detected: true,
      confidence: 0.5,
      evidence: [...input.evidence, '评价发生异常集中'],
      impactChannels: ['REPUTATION','CONVERSION'],
      response: 'DOCUMENT'
    });
  }

  if ((c.complaintRate ?? 0) > Math.max((b.complaintRate ?? 0) * 2.5, 0.05)) {
    out.push({
      behavior: 'FALSE_COMPLAINT',
      risk: 'HIGH',
      detected: true,
      confidence: 0.45,
      evidence: [...input.evidence, '投诉率异常变化，需核验具体案件'],
      impactChannels: ['REPUTATION','PLATFORM_ACCESS'],
      response: 'PLATFORM_REVIEW'
    });
  }

  if ((c.cpc ?? 0) > (b.cpc ?? 0) * 1.5 && (c.traffic ?? 0) < (b.traffic ?? 0) * 0.8) {
    out.push({
      behavior: 'TRAFFIC_BID_WAR',
      risk: 'MEDIUM',
      detected: true,
      confidence: 0.5,
      evidence: [...input.evidence, '流量成本与有效流量同时异常'],
      impactChannels: ['TRAFFIC','CASHFLOW'],
      response: 'MONITOR'
    });
  }

  if ((c.price ?? 0) < (b.price ?? 0) * 0.85) {
    out.push({
      behavior: 'PRICE_UNDERCUTTING',
      risk: 'MEDIUM',
      detected: true,
      confidence: 0.9,
      evidence: [...input.evidence, '市场价格显著下降'],
      impactChannels: ['PRICE','CONVERSION','CASHFLOW'],
      response: 'PROTECT'
    });
  }

  return out;
}

export const adversarialStrategyPrinciple = {
  mode: 'DEFENSIVE_MODELING',
  description:
    '将恶意竞争作为对手可能采取的策略分支进行检测、压力测试和防御建模，而不是自动执行欺诈、操纵评价、虚假举报或其他违规行为。',
  keyQuestion:
    '如果对手不按正常商业规则竞争，我方哪些指标会先出现异常，我方怎样保留证据、降低损失并恢复竞争优势？'
};
