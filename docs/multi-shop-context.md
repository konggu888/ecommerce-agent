# Multi-shop MCP Context

The agent is always scoped to one or more `shop_id` values. Platform credentials and permissions are resolved server-side from the selected shop.

## Resolution flow

```text
Agent request
  -> shop selector
  -> load shop
  -> load authorization
  -> load shop permissions
  -> resolve platform adapter
  -> execute read/write tool
  -> risk controller
  -> audit log
```

## Rules

1. Never expose access tokens or refresh tokens to the Agent.
2. Every tool call must carry an explicit `shop_id` or an explicit, validated multi-shop scope.
3. Cross-shop aggregation is read-only by default.
4. A write operation must resolve permissions for every target shop independently.
5. One shop's authorization failure must not silently fall back to another shop.
6. Action logs must include `shop_id` and platform.
7. The default permission remains `LEVEL_1_READ_ONLY`.

## Planned MCP tools

- `list_shops()`
- `get_shop_context(shop_id)`
- `get_all_shop_summaries()`
- `get_shop_campaigns(shop_id)`
- `get_shop_campaign_report(shop_id, range)`
- `compare_shops(shop_ids, range)`

Future write tools must require a single explicit target shop unless a batch operation has an explicit allow-list and per-shop risk checks.
