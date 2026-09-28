export const READ_TOOLS = [
  'get_shop', 'get_products', 'get_product_detail', 'get_orders', 'get_finance',
  'get_campaigns', 'get_campaign_report', 'get_budget', 'get_bid',
  'get_keywords', 'get_targeting'
];

export const WRITE_TOOLS = [
  'set_budget', 'set_bid', 'pause_campaign', 'resume_campaign',
  'set_keyword_bid', 'set_targeting'
];

export const PERMISSIONS = Object.freeze({
  READ_ONLY: 'LEVEL_1_READ_ONLY',
  APPROVAL_REQUIRED: 'LEVEL_2_APPROVAL_REQUIRED',
  AUTO_EXECUTION: 'LEVEL_3_AUTO_EXECUTION'
});

export function toolContract() {
  return { read: [...READ_TOOLS], write: [...WRITE_TOOLS], defaultPermission: PERMISSIONS.READ_ONLY };
}
