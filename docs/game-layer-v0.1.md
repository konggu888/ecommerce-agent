# Commercial Game Layer v0.1

The agent models a shop/product/campaign as a state and evaluates alternative actions rather than immediately choosing a winner.

State dimensions:
- own price and unit economics
- budget and spend velocity
- impressions, clicks, conversions, revenue
- CTR, CVR, CPC, ROI
- observed competitor price/traffic signals

Candidate actions:
- increase/decrease budget
- increase/decrease bid
- hold
- change keyword/targeting
- change price

Each action returns expected impact, risks, evidence and confidence. The engine must preserve uncertainty and route execution through Risk Controller.

This is a decision-support model, not a claim that competitor data is complete or causal. Missing/estimated competitor observations must be labeled accordingly.
