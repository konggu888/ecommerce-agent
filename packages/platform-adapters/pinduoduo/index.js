import { PlatformAdapter } from '../src/index.js';

export class PinduoduoAdapter extends PlatformAdapter {
  constructor(executor = null) { super('pinduoduo'); this.executor = executor; }
  async getShop() { return this.executor ? this.executor.getShop() : { platform: 'pinduoduo', mocked: true }; }
  async getProducts() { return this.executor ? this.executor.getProducts() : []; }
  async getOrders() { return this.executor ? this.executor.getOrders() : []; }
  async getCampaigns() { return this.executor ? this.executor.getCampaigns() : []; }
  async getCampaignReport() { return this.executor ? this.executor.getCampaignReport() : []; }
}
