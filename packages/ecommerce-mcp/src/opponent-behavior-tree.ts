export type OpponentNodeKind =
  | 'PRICE'
  | 'AD'
  | 'TRAFFIC'
  | 'CONTENT'
  | 'REPUTATION'
  | 'REPORTING'
  | 'PRODUCT'
  | 'SUPPLY'
  | 'PLATFORM'
  | 'INFORMATION'
  | 'WAIT';

export interface OpponentBranch {
  action: string;
  kind: OpponentNodeKind;
  likelihood: number;
  impact: number;
  detectability: number;
  responseOptions: string[];
  evidenceNeeded: string[];
  blockedFromAutomation?: boolean;
}

export interface OpponentBehaviorTree {
  root: string;
  branches: OpponentBranch[];
  maxDepth: number;
  principle: string;
}

const branches: OpponentBranch[] = [
  { action:'跟价/价格战',kind:'PRICE',likelihood:.75,impact:.7,detectability:.95,responseOptions:['保持利润底线','价值差异化','组合装/规格差异'],evidenceNeeded:['竞品价格时间序列'] },
  { action:'提高广告竞价',kind:'AD',likelihood:.65,impact:.6,detectability:.8,responseOptions:['调整出价','转移关键词','降低低效流量依赖'],evidenceNeeded:['CPC/CPM/流量变化'] },
  { action:'改变内容打法',kind:'CONTENT',likelihood:.55,impact:.55,detectability:.65,responseOptions:['刷新素材','改变内容角度','强化产品证据'],evidenceNeeded:['内容曝光/互动/转化变化'] },
  { action:'改善自身转化',kind:'PRODUCT',likelihood:.5,impact:.65,detectability:.55,responseOptions:['产品差异化','服务速度','商品页证据'],evidenceNeeded:['竞品商品/服务变化'] },
  { action:'评价/声誉攻击',kind:'REPUTATION',likelihood:.3,impact:.85,detectability:.45,responseOptions:['证据留存','评价恢复','平台复核'],evidenceNeeded:['评价时间序列','订单/售后记录'],blockedFromAutomation:true },
  { action:'举报/投诉竞争',kind:'REPORTING',likelihood:.25,impact:.8,detectability:.4,responseOptions:['核验自身合规','保存证据','平台复核'],evidenceNeeded:['平台规则','投诉记录'],blockedFromAutomation:true },
  { action:'供应链施压',kind:'SUPPLY',likelihood:.2,impact:.8,detectability:.35,responseOptions:['多供应商','安全库存','替代规格'],evidenceNeeded:['采购价格/交期/库存'] },
  { action:'利用平台规则',kind:'PLATFORM',likelihood:.2,impact:.9,detectability:.3,responseOptions:['合规修复','规则监控','人工审核'],evidenceNeeded:['官方规则原文'],blockedFromAutomation:true },
  { action:'信息误导/声誉传播',kind:'INFORMATION',likelihood:.2,impact:.75,detectability:.3,responseOptions:['事实核验','证据归档','平台/法律复核'],evidenceNeeded:['原始来源','时间线'],blockedFromAutomation:true },
  { action:'等待我方失误',kind:'WAIT',likelihood:.45,impact:.35,detectability:.2,responseOptions:['持续监控','降低暴露面','保持现金流'],evidenceNeeded:[] }
];

export function buildOpponentBehaviorTree(root='我方形成竞争优势'): OpponentBehaviorTree {
  return {
    root,
    branches,
    maxDepth: 4,
    principle: '预测对手可能反应，而不是假定对手只会按正常规则竞争；概率是模型估计，必须用实际实验校准。'
  };
}

export function rankOpponentBranches(tree: OpponentBehaviorTree) {
  return [...tree.branches]
    .map(b => ({...b, threatScore: b.likelihood*b.impact*(1-b.detectability*.5)}))
    .sort((a,b)=>b.threatScore-a.threatScore);
}
