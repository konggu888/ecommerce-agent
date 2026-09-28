# Multi-round Commercial Game v0.1

## Purpose

Turn the ecommerce agent from single-step optimization into a finite-horizon commercial game:

`我方动作 → 对手响应 → 我方下一动作 → 对手再次响应`

The planner uses the current shop, competitor, and market state as its initial state.

## Core outputs

- opponent response model
- action-by-action opponent response risk
- 3-round default lookahead (configurable up to 5)
- candidate action paths
- path score
- robustness score
- explanation for whether the path is sensitive to opponent response

## Important limitation

This is a simulation/modeling layer, not a claim that competitor behavior is known. Probabilities are model estimates derived from observed inputs and should be calibrated with experiment outcomes.

## Decision chain

`我方数据 + 对手数据 + 市场状态`
→ `对手响应模型`
→ `多轮路径搜索`
→ `突破口/抗响应性`
→ `利润/库存/现金流`
→ `Risk Controller`
→ `实验/执行`
→ `结果回写 Memory`
