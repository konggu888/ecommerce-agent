# Testing strategy

## 1. Taobao sandbox

Use the official Taobao sandbox for supported core TOP scenarios. Sandbox has separate credentials and endpoints from production. Do not use production AppKey/AppSecret against sandbox.

The official sandbox documentation describes core page/API scenarios such as shops, products, orders, refunds and logistics. It does not guarantee that every advertising/UniversalBP API is available in sandbox.

## 2. Advertising simulator

Use `packages/ecommerce-mcp/src/mock-market.ts` for offline advertising experiments. The simulator is intentionally deterministic and is not a claim about Taobao or Pinduoduo auction behavior.

It lets the decision engine test:

- budget changes
- bid changes
- before/after metrics
- ROI changes
- multi-shop comparisons

## 3. Production integration

When a real shop becomes available, use a separate production authorization and `shop_id`. Production API write calls affect real shops, so the system remains read-only until an explicit permission is granted.

## 4. Promotion API coverage

Taobao's current official UniversalBP documentation exposes read endpoints such as campaign lists/reports and also write endpoints such as budget and bid batch updates. The project must keep these capabilities separated by permission and never infer sandbox support from production documentation.
