import { TaobaoClient } from "./client";

export class TaobaoReadOnlyAdapter {
  constructor(private readonly client: TaobaoClient) {}

  /** Current shop information from the official 万相台 API. */
  getShop() {
    return this.client.call("taobao.universalbp.new.material.shop.get");
  }

  /** Product/material page from the official 万相台 API. */
  getProducts(params: Record<string, string | number | boolean> = {}) {
    return this.client.call("taobao.universalbp.new.material.item.findpage", params);
  }

  /** Campaign list. No mutation is performed by this adapter. */
  getCampaigns(params: Record<string, string | number | boolean> = {}) {
    return this.client.call("taobao.universalbp.new.campaign.findpage", params);
  }

  /** Realtime advertising report. */
  getRealtimeReport(params: Record<string, string | number | boolean> = {}) {
    return this.client.call("taobao.universalbp.new.report.query.realtime", params);
  }

  /** Campaign details. */
  getCampaign(params: Record<string, string | number | boolean>) {
    return this.client.call("taobao.universalbp.new.campaign.get", params);
  }

  /** Account cash balance. */
  getBalance() {
    return this.client.call("taobao.universalbp.new.account.get.balance");
  }

  /** Bound audience list for campaigns/ad groups. */
  getTargeting(params: Record<string, string | number | boolean> = {}) {
    return this.client.call("taobao.universalbp.new.crowd.findlist", params);
  }
}
