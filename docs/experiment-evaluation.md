# Experiment Evaluation

The agent must not treat a before/after change as proof of causality.

For each budget, bid, keyword, targeting, or creative experiment, record:

- baseline period
- treatment period
- spend
- impressions
- clicks
- conversions
- revenue
- price and promotion changes
- stock/out-of-stock events
- major platform or campaign changes

The evaluator produces:

- baseline ROI
- treatment ROI
- ROI lift
- CVR lift
- CPC change
- evidence level
- positive / negative / inconclusive result

Default behavior is conservative: insufficient traffic, spend, or conversions produces `INCONCLUSIVE`, not an automatic optimization decision.

For real Taobao data, the reporting layer can use the official Universal BP campaign report APIs. The current official documentation exposes campaign report queries and realtime reports; write APIs for budget/bid changes remain behind the Risk Controller. See `docs/taobao-readonly-verified.md` and `docs/taobao-readonly-verified.md` for the project integration notes.
