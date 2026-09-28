# Decision Memory + Learning v0.1

Every decision is stored as a hypothesis with observed state, action, expected outcome, constraints, and confidence. After the evaluation window, an outcome is attached and prediction error is measured.

Rules:
- INCONCLUSIVE outcomes do not update strategy weights.
- Material prediction errors reduce confidence for similar future states and trigger investigation.
- Lessons must distinguish prediction error from external confounders such as seasonality, price changes, stockouts, platform traffic shifts, and concurrent campaigns.
- Memory is scoped by platform, shop, product/campaign and comparable state features; cross-shop transfer is evidence-weighted rather than assumed.
- Never learn credentials, tokens, or other secrets into decision memory.

Goal: improve calibration and strategy selection over time without turning one noisy outcome into a permanent rule.
