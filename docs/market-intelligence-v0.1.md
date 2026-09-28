# Market Intelligence v0.1

Goal: distinguish changes in the shop's own performance from plausible market/competitive pressure without pretending correlation proves causation.

## Observation layers

1. Own account: spend, impressions, clicks, CTR, CPC, conversions, CVR, revenue, ROI.
2. Product economics: selling price, cost, margin, stock, promotion, shipping.
3. Platform traffic: CPC/CPM movement, impression availability, campaign delivery.
4. Peer/market observations: comparable product prices, visible sales/engagement signals where legally and technically available.
5. Experiments: controlled budget/bid changes used to test hypotheses.

## State machine

OWN_PERFORMANCE
PRICE_PRESSURE
TRAFFIC_COST_PRESSURE
CONVERSION_PRESSURE
DEMAND_CHANGE
MIXED
INSUFFICIENT_DATA

The engine labels these as hypotheses/states, not facts about competitor intent.

## Decision rule

Do not automatically increase spend merely because ROI is high. First check marginal return, delivery capacity, inventory, margin and whether the observed change is product-specific or market-wide.

Do not automatically cut spend merely because ROI is low. Check attribution window, conversion lag, price/promotion changes, traffic cost, stock and controlled experiment history.

## Next stage

Add a market-observation adapter and experiment evaluator. For Taobao, use official campaign/item/report APIs where authorized. The current official Taobao docs expose campaign reports, item reports, campaign detail, real-time reports, and budget/bid update APIs; write APIs remain behind the risk controller. No unsupported competitor-data API is assumed.
