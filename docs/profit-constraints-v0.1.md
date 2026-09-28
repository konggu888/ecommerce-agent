# Profit Constraints v0.1

ROI/ROAS alone is not the optimization target. The engine first derives contribution before advertising from selling price and variable costs, then calculates the maximum economically acceptable ad cost.

Inputs:
- selling price
- product cost
- fulfillment cost
- platform fee
- payment fee
- other variable costs
- target profit per order
- observed CVR

Outputs:
- contribution before ads
- break-even ROAS
- maximum CPA
- maximum CPC when CVR is known
- optional daily spend ceiling

If contribution after the target profit is non-positive, the engine must not recommend scaling paid traffic merely because observed ROAS is high. Missing cost data is treated as an uncertainty, not as zero cost.
