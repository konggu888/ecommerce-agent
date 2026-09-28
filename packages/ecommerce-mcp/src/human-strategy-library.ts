export type HumanStrategyDomain =
  | 'PRICE'
  | 'AD_BID'
  | 'TRAFFIC'
  | 'TARGETING'
  | 'CONTENT'
  | 'CONVERSION'
  | 'REPUTATION'
  | 'CUSTOMER_SERVICE'
  | 'PRODUCT'
  | 'SUPPLY'
  | 'INVENTORY'
  | 'CASHFLOW'
  | 'TIMING'
  | 'CHANNEL'
  | 'INFORMATION'
  | 'PLATFORM_COMPLIANCE'
  | 'LEGITIMATE_REPORTING';

export type HumanStrategy =
  | 'PRICE_TEST'
  | 'BUNDLE_VALUE'
  | 'DIFFERENTIATE_PRODUCT'
  | 'CHANGE_TARGETING'
  | 'CHANGE_KEYWORD'
  | 'CONTENT_ANGLE'
  | 'CREATIVE_REFRESH'
  | 'REVIEW_RECOVERY'
  | 'SERVICE_SPEED'
  | 'AFTER_SALES_REDUCTION'
  | 'PRODUCT_QA'
  | 'STOCK_ADVANTAGE'
  | 'SUPPLY_LOCK'
  | 'LAUNCH_TIMING'
  | 'DAYPARTING'
  | 'CHANNEL_SHIFT'
  | 'COMPETITOR_MONITORING'
  | 'LEGITIMATE_PLATFORM_REPORT'
  | 'COMPLIANCE_REMEDIATION'
  | 'WAIT_AND_OBSERVE';

export interface HumanFactorSignal {
  factor:
    | 'PRICE_SENSITIVITY'
    | 'TRUST'
    | 'SOCIAL_PROOF'
    | 'LOSS_AVERSION'
    | 'HABIT'
    | 'CONVENIENCE'
    | 'STATUS'
    | 'URGENCY'
    | 'RECIPROCITY'
    | 'RISK_AVERSION'
    | 'CURIOSITY'
    | 'SWITCHING_COST'
    | 'ATTENTION';
  strength: number;
  evidence: string[];
}

export interface StrategyCandidate {
  strategy: HumanStrategy;
  domain: HumanStrategyDomain;
  target: 'CUSTOMER' | 'COMPETITOR' | 'PLATFORM' | 'SUPPLIER' | 'MARKET';
  mechanism: string;
  humanFactors: HumanFactorSignal[];
  expectedEffect: string;
  copyability: number;
  downside: string[];
  evidenceRequired: string[];
  allowed: boolean;
}

const STRATEGIES: StrategyCandidate[] = [
  {
    strategy: 'PRICE_TEST', domain: 'PRICE', target: 'CUSTOMER',
    mechanism: '通过小范围价格实验测试价格弹性，而不是直接进入价格战',
    humanFactors: [{ factor: 'PRICE_SENSITIVITY', strength: 0.8, evidence: ['转化率/客单价变化'] }],
    expectedEffect: '测试需求弹性', copyability: 0.9,
    downside: ['毛利下降', '可能触发跟价'], evidenceRequired: ['价格、订单、毛利'], allowed: true
  },
  {
    strategy: 'BUNDLE_VALUE', domain: 'PRODUCT', target: 'CUSTOMER',
    mechanism: '通过组合、赠品或服务提高感知价值，避免只比较单价',
    humanFactors: [{ factor: 'CONVENIENCE', strength: 0.7, evidence: ['连带购买率'] }, { factor: 'LOSS_AVERSION', strength: 0.5, evidence: ['优惠使用率'] }],
    expectedEffect: '降低纯价格比较', copyability: 0.65,
    downside: ['成本增加', '规则限制'], evidenceRequired: ['毛利、连带购买'], allowed: true
  },
  {
    strategy: 'DIFFERENTIATE_PRODUCT', domain: 'PRODUCT', target: 'CUSTOMER',
    mechanism: '制造可验证的产品差异，让竞品无法通过简单降价复制',
    humanFactors: [{ factor: 'TRUST', strength: 0.8, evidence: ['退货率、评价内容'] }],
    expectedEffect: '提高非价格竞争权重', copyability: 0.35,
    downside: ['开发成本', '供应链要求'], evidenceRequired: ['产品属性、评价'], allowed: true
  },
  {
    strategy: 'CONTENT_ANGLE', domain: 'CONTENT', target: 'CUSTOMER',
    mechanism: '改变卖点表达和内容入口，争夺注意力而非直接购买竞品流量',
    humanFactors: [{ factor: 'ATTENTION', strength: 0.8, evidence: ['完播率、点击率'] }, { factor: 'CURIOSITY', strength: 0.5, evidence: ['内容互动'] }],
    expectedEffect: '获得增量注意力', copyability: 0.55,
    downside: ['内容试错成本'], evidenceRequired: ['内容指标'], allowed: true
  },
  {
    strategy: 'REVIEW_RECOVERY', domain: 'REPUTATION', target: 'CUSTOMER',
    mechanism: '针对真实差评原因进行产品、物流、客服整改，并依法依规处理异常评价',
    humanFactors: [{ factor: 'TRUST', strength: 0.9, evidence: ['评价主题、售后原因'] }, { factor: 'SOCIAL_PROOF', strength: 0.8, evidence: ['评分、评价结构'] }],
    expectedEffect: '恢复真实信任信号', copyability: 0.5,
    downside: ['整改成本'], evidenceRequired: ['真实评价、售后数据'], allowed: true
  },
  {
    strategy: 'SERVICE_SPEED', domain: 'CUSTOMER_SERVICE', target: 'CUSTOMER',
    mechanism: '缩短响应、履约和售后处理时间，降低消费者的不确定性',
    humanFactors: [{ factor: 'CONVENIENCE', strength: 0.8, evidence: ['响应时长、退款率'] }, { factor: 'RISK_AVERSION', strength: 0.7, evidence: ['投诉率'] }],
    expectedEffect: '提高转化与复购', copyability: 0.65,
    downside: ['服务成本'], evidenceRequired: ['客服/履约数据'], allowed: true
  },
  {
    strategy: 'LEGITIMATE_PLATFORM_REPORT', domain: 'LEGITIMATE_REPORTING', target: 'PLATFORM',
    mechanism: '仅依据可核验的违规事实，通过平台正规渠道提交证据，由平台规则决定处理',
    humanFactors: [],
    expectedEffect: '降低真实违规造成的不公平竞争影响', copyability: 0.8,
    downside: ['误报风险', '证据不足不会成立'], evidenceRequired: ['原始证据、平台规则、时间线'], allowed: true
  },
  {
    strategy: 'COMPLIANCE_REMEDIATION', domain: 'PLATFORM_COMPLIANCE', target: 'PLATFORM',
    mechanism: '监测规则变化并修正自身经营行为，避免被规则变化形成突发性打击',
    humanFactors: [{ factor: 'RISK_AVERSION', strength: 0.7, evidence: ['规则变化'] }],
    expectedEffect: '降低平台规则风险', copyability: 0.8,
    downside: ['合规成本'], evidenceRequired: ['官方规则'], allowed: true
  },
  {
    strategy: 'WAIT_AND_OBSERVE', domain: 'TIMING', target: 'MARKET',
    mechanism: '信息不足或对手响应高度不确定时保留行动能力',
    humanFactors: [{ factor: 'LOSS_AVERSION', strength: 0.5, evidence: ['不确定性'] }],
    expectedEffect: '避免不可逆错误', copyability: 1,
    downside: ['可能错失窗口'], evidenceRequired: ['置信度'], allowed: true
  }
];

export function listHumanStrategyCandidates(): StrategyCandidate[] {
  return STRATEGIES;
}

export function filterHumanStrategies(input: {
  allowedDomains?: HumanStrategyDomain[];
  requireEvidence?: boolean;
}): StrategyCandidate[] {
  return STRATEGIES.filter(s =>
    s.allowed &&
    (!input.allowedDomains?.length || input.allowedDomains.includes(s.domain)) &&
    (!input.requireEvidence || s.evidenceRequired.length > 0)
  );
}
