export const TAOBAO_API_URL = 'https://eco.taobao.com/router/rest';

/**
 * Official Taobao TOP / 万相台无界 methods verified against current official docs.
 * These are names only; request schemas are implemented separately so we do not
 * invent parameters for restricted APIs.
 */
export const TAOBAO_READONLY_METHODS = {
  campaignList: 'taobao.universalbp.new.campaign.findlist',
  campaignPage: 'taobao.universalbp.new.campaign.findpage',
  campaignGet: 'taobao.universalbp.new.campaign.get',
  realtimeReport: 'taobao.universalbp.new.report.query.realtime',
  campaignReportSpecial: 'taobao.universalbp.new.report.query.campaign.special',
  itemPromotionReport: 'taobao.universalbp.new.report.query.item.promotion',
  spendSummary: 'taobao.universalbp.new.report.chargesum',
  crowdList: 'taobao.universalbp.new.crowd.findlist',
  creativeList: 'taobao.universalbp.new.creative.getbindcreativelist',
  creativeReport: 'taobao.universalbp.new.creative.report.material',
} as const;

export type TaobaoReadonlyMethod =
  (typeof TAOBAO_READONLY_METHODS)[keyof typeof TAOBAO_READONLY_METHODS];

export const TAOBAO_WRITE_METHODS = {
  updateBudget: 'taobao.universalbp.new.campaign.budget.batchupdate',
  updateBid: 'taobao.universalbp.new.campaign.bid.batchupdate',
  updateAdvanced: 'taobao.universalbp.new.campaign.advanced.batchupdate',
  updatePart: 'taobao.universalbp.new.campaign.updatepart',
  pauseOrDelete: 'taobao.universalbp.new.campaign.delete',
} as const;

export function assertTaobaoReadonly(method: string): void {
  if (Object.values(TAOBAO_WRITE_METHODS).includes(method as never)) {
    throw new Error(`Taobao write method blocked in read-only mode: ${method}`);
  }
}
