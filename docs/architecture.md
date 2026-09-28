# Architecture

## Layers

1. Agent/Decision Engine: analyzes market, product, advertising and competition.
2. `ecommerce-mcp`: exposes platform-neutral tools.
3. Platform adapters: translate neutral commands to Taobao or Pinduoduo implementations.
4. Risk Controller: permission, limits, dry-run and audit checks.
5. Data layer: Supabase/Postgres for durable state and experiment history.

## Execution contract

All write actions follow:

`decision -> action proposal -> risk controller -> approval/auto policy -> executor -> audit log`

Default mode is `LEVEL_1_READ_ONLY`. Real credentials are never stored in source control.

## Platform policy

- Taobao/Tmall: use Alibaba official APIs only after each API is verified against current documentation.
- Pinduoduo: use official open-platform capabilities where available. Do not invent advertising APIs. If advertising control is not exposed, a separate browser automation executor may be evaluated later.

## First milestone

The first milestone is read-only normalized data plus Mock execution. No live advertising changes are permitted.
