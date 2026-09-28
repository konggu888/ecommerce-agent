# Inventory + Cashflow Constraints v0.1

Scaling paid traffic must be constrained by inventory and cash availability, not only ROAS.

Inventory inputs:
- stock on hand
- reserved stock
- average daily units
- replenishment lead time
- safety-stock days
- inbound units

Cashflow inputs:
- available cash
- pending receivables
- payables due
- daily operating cash need
- already committed ad spend

Outputs:
- safe daily unit pace
- stock coverage days
- maximum additional ad-spend envelope
- constraint reasons

The engine should prefer HOLD/DECREASE or a lower-risk experiment when inventory coverage is below replenishment lead time plus safety buffer, or when additional ad commitments would violate cash constraints.
