# Backtest Engine v0.1

Runs repeated simulated rounds without touching platform accounts or spending real money.

Each round tracks spend, revenue, conversions, ROAS/ROI proxy, inventory and cash. A deterministic seed makes runs reproducible.

Validation should compare:
- baseline/no-agent policy
- fixed-rule policy
- game-agent policy

Do not optimize only for ROAS. Report profit contribution, inventory violations, cash constraints, drawdown and action count. A strategy is not promoted from backtest to real execution solely because it has a higher simulated return; it must also satisfy safety constraints and pass out-of-sample scenarios.
