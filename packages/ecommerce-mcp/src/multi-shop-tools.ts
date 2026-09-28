export type ShopPlatform = 'taobao' | 'pinduoduo';
export type PermissionLevel = 'LEVEL_1_READ_ONLY' | 'LEVEL_2_APPROVAL_REQUIRED' | 'LEVEL_3_AUTO_EXECUTION';

export interface ShopContext {
  shopId: string;
  platform: ShopPlatform;
  externalShopId: string;
  name?: string;
  authorizationStatus: 'active' | 'expired' | 'missing' | 'error';
  permissionLevel: PermissionLevel;
}

export interface CampaignSummary {
  shopId: string;
  campaignId: string;
  name?: string;
  status?: string;
  budget?: number;
  spend?: number;
  revenue?: number;
  conversions?: number;
  roi?: number;
}

/**
 * Provider-neutral contracts. Implementations must resolve credentials server-side.
 * Tokens must never be returned to callers.
 */
export interface MultiShopTools {
  listShops(): Promise<ShopContext[]>;
  getShopContext(shopId: string): Promise<ShopContext>;
  getAllShopSummaries(range: { from: string; to: string }): Promise<CampaignSummary[]>;
  getShopCampaigns(shopId: string): Promise<CampaignSummary[]>;
  getShopCampaignReport(shopId: string, range: { from: string; to: string }): Promise<CampaignSummary[]>;
  compareShops(shopIds: string[], range: { from: string; to: string }): Promise<CampaignSummary[]>;
}

export function assertReadOnly(level: PermissionLevel): void {
  // All tools in this module are read-only. Write tools belong behind Risk Controller.
  if (!level) throw new Error('Missing permission level');
}
