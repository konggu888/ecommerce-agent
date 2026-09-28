export class PlatformAdapter {
  constructor(platform) { this.platform = platform; }
  async getShop() { throw new Error(`${this.platform}: getShop not implemented`); }
  async getProducts() { throw new Error(`${this.platform}: getProducts not implemented`); }
  async getOrders() { throw new Error(`${this.platform}: getOrders not implemented`); }
  async getCampaigns() { throw new Error(`${this.platform}: getCampaigns not implemented`); }
  async getCampaignReport() { throw new Error(`${this.platform}: getCampaignReport not implemented`); }
}
