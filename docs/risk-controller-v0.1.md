# Risk Controller v0.1

Every write action must pass the risk controller before reaching a platform adapter.

Modes:
- ANALYZE_ONLY: never executes writes.
- APPROVAL_REQUIRED: produces a proposed action and waits for explicit approval.
- AUTO_LIMITED: may execute only within hard limits.
- AUTO_DISABLED: execution is blocked.

Hard limits are per shop:
- maximum budget change percentage
- maximum bid change percentage
- maximum daily ad spend
- maximum actions per hour
- allow/deny budget changes
- allow/deny bid changes
- allow/deny campaign pause/resume

Default state remains read-only. Low confidence, exceeded limits, disabled action types, or action-rate breaches must prevent automatic execution.

All decisions must be recorded in action_logs with before/after state, policy, and result.
