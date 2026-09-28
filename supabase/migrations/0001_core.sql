create extension if not exists pgcrypto;

create table if not exists shops (
  id uuid primary key default gen_random_uuid(),
  platform text not null check (platform in ('taobao','tmall','pinduoduo')),
  external_shop_id text not null,
  name text,
  status text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(platform, external_shop_id)
);

create table if not exists products (
  id uuid primary key default gen_random_uuid(),
  shop_id uuid not null references shops(id) on delete cascade,
  external_product_id text not null,
  title text,
  status text,
  price numeric(14,2),
  cost numeric(14,2),
  inventory integer,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(shop_id, external_product_id)
);

create table if not exists orders (
  id uuid primary key default gen_random_uuid(),
  shop_id uuid not null references shops(id) on delete cascade,
  external_order_id text not null,
  product_id uuid references products(id) on delete set null,
  status text,
  gross_amount numeric(14,2),
  refund_amount numeric(14,2) not null default 0,
  paid_at timestamptz,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique(shop_id, external_order_id)
);

create table if not exists campaigns (
  id uuid primary key default gen_random_uuid(),
  shop_id uuid not null references shops(id) on delete cascade,
  product_id uuid references products(id) on delete set null,
  external_campaign_id text not null,
  platform_type text,
  name text,
  status text,
  daily_budget numeric(14,2),
  bid numeric(14,4),
  strategy text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(shop_id, external_campaign_id)
);

create table if not exists campaign_metrics (
  id bigserial primary key,
  campaign_id uuid not null references campaigns(id) on delete cascade,
  captured_at timestamptz not null,
  impressions bigint not null default 0,
  clicks bigint not null default 0,
  spend numeric(14,2) not null default 0,
  conversions numeric(14,4) not null default 0,
  revenue numeric(14,2) not null default 0,
  refunds numeric(14,2) not null default 0,
  metadata jsonb not null default '{}'::jsonb
);

create table if not exists keywords (
  id uuid primary key default gen_random_uuid(),
  campaign_id uuid not null references campaigns(id) on delete cascade,
  external_keyword_id text,
  keyword text not null,
  status text,
  bid numeric(14,4),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique(campaign_id, keyword)
);

create table if not exists targeting (
  id uuid primary key default gen_random_uuid(),
  campaign_id uuid not null references campaigns(id) on delete cascade,
  external_targeting_id text,
  targeting_type text not null,
  targeting_key text not null,
  status text,
  bid numeric(14,4),
  multiplier numeric(10,4),
  metadata jsonb not null default '{}'::jsonb,
  unique(campaign_id, targeting_type, targeting_key)
);

create table if not exists decisions (
  id uuid primary key default gen_random_uuid(),
  shop_id uuid references shops(id) on delete set null,
  platform text,
  decision_type text not null,
  hypothesis text,
  rationale text,
  confidence numeric(6,5),
  proposed_action jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists experiments (
  id uuid primary key default gen_random_uuid(),
  shop_id uuid references shops(id) on delete set null,
  name text not null,
  hypothesis text not null,
  status text not null default 'planned',
  control jsonb not null default '{}'::jsonb,
  treatment jsonb not null default '{}'::jsonb,
  started_at timestamptz,
  ended_at timestamptz,
  result jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists action_logs (
  id uuid primary key default gen_random_uuid(),
  shop_id uuid references shops(id) on delete set null,
  platform text,
  action_type text not null,
  permission_level text not null check (permission_level in ('LEVEL_1_READ_ONLY','LEVEL_2_APPROVAL_REQUIRED','LEVEL_3_AUTO_EXECUTION')),
  mode text not null check (mode in ('dry_run','approval','live')),
  target jsonb not null default '{}'::jsonb,
  before_state jsonb not null default '{}'::jsonb,
  requested_state jsonb not null default '{}'::jsonb,
  result jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_campaign_metrics_campaign_time on campaign_metrics(campaign_id, captured_at desc);
create index if not exists idx_orders_shop_created on orders(shop_id, created_at desc);
create index if not exists idx_action_logs_shop_time on action_logs(shop_id, created_at desc);
