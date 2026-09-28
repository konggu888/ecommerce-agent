# ecommerce-agent

淘宝/天猫 + 拼多多统一电商博弈 Agent。

## 当前阶段

第一阶段只建立安全的本地/Mock 架构：不连接真实店铺，不执行真实广告修改。

## 架构

```text
Agent
  -> ecommerce-mcp (统一工具层)
  -> Platform Adapter
      -> Taobao Executor
      -> Pinduoduo Executor
  -> Risk Controller
  -> Audit Log
  -> Data Model / Supabase
```

平台执行层必须可替换：淘宝优先官方 API；拼多多优先官方开放能力，广告控制若无可用官方 API，再单独接后台自动化。不得虚构 API。

## 权限

- `LEVEL_1_READ_ONLY`：默认，仅允许读取
- `LEVEL_2_APPROVAL_REQUIRED`：写操作必须人工批准
- `LEVEL_3_AUTO_EXECUTION`：受风控限制的自动执行

第一阶段禁止真实执行。

## 数据模型

- shops
- products
- orders
- campaigns
- campaign_metrics
- keywords
- targeting
- decisions
- experiments
- action_logs

## 目录

```text
apps/agent/
packages/ecommerce-mcp/
packages/decision-engine/
packages/risk-controller/
packages/data-model/
packages/platform-adapters/taobao/
packages/platform-adapters/pinduoduo/
tests/
mock-data/
docs/
```

## 后续阶段

1. 接入 Supabase schema
2. 核验淘宝官方 API 并实现只读 Adapter
3. 核验拼多多官方开放能力并实现只读 Adapter
4. 建立统一广告数据模型
5. 加入决策/博弈分析
6. 加入人工审批执行
7. 最后才考虑自动执行
