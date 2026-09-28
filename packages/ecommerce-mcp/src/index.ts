export * from './multi-shop-tools';

export const MCP_SERVER_NAME = 'ecommerce-mcp';
export const MCP_SERVER_VERSION = '0.1.0';

export const READ_ONLY_TOOLS = [
  'list_shops',
  'get_shop_context',
  'get_all_shop_summaries',
  'get_shop_campaigns',
  'get_shop_campaign_report',
  'compare_shops',
] as const;

export * from './game-state';
export * from './opponent-model';
export * from './closed-loop-agent';

export * from './multi-round-game';
