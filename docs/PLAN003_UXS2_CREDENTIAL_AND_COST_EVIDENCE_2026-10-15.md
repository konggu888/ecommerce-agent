# PLAN-003 / UXS-2｜凭据、费用账本与外部端点证据审查

日期：2026-10-15  
仓库：`konggu888/ecommerce-agent`  
分支：`feat/product-drama-visual-review`  
审查基线：`9c5faa74c05ca7f6dfacf97cad1f33b184d7113f`  
性质：静态代码与文档证据映射；不是产品修复，也不是正式验收结论。

## 1. 本轮核验基线

- PR #32 保持 Open / unmerged。
- 基线 SHA 的 PR-triggered CI（run 1845）与 `ad-studio-doc-sync`（run 1668）均 completed/success；Netlify deploy-preview status success。
- 当前连接器返回的是 PR 触发工作流。Push-triggered CI 与 Push-triggered docs-sync 未独立核实，不把它们写成已通过。
- 本轮未运行本地测试，未连接真实模型、代理站或 Provider，未产生真实外部调用或核对账单。

## 2. 已由当前代码证据支持的事实

### 2.1 文本模型凭据落盘

文件：`apps/ad-studio-desktop/ad_studio/model_router.py`

- `ModelProfile.public()` 仅在公开展示字典中将 `api_key` 替换为 `***`。
- `ModelRouter.save()` 对完整 `self.data` 进行 JSON 序列化并写入配置路径；模型 profile 中的 `api_key` 因此会被写入普通 JSON 配置文件。
- 结论：UI 掩码不等于静态加密或系统凭据库。当前证据不支持“API Key 已安全加密保存”的说法。

### 2.2 视频与资产 Provider 凭据及数据发送

文件：`apps/ad-studio-desktop/ad_studio/providers.py`

- `load_video_provider()` 从 `video-provider.json` 读取 `endpoint`、`api_key`、模型和参考素材选项。
- `load_asset_provider()` 从 `asset-generation.json` 读取 `endpoint`、`api_key` 与模型。
- 视频/资产请求把 API Key 放入 Bearer Authorization header，并向配置 endpoint 发送 JSON payload。
- 视频流程可以发送参考素材路径；启用 `embed_reference_assets` 时会把可读的本地参考图片编码成 data URI 后放入请求。
- 当前静态证据未证明所有这些请求前都有清楚的数据接收方、发送内容、云端/本地目标和费用提示；也未证明重定向目标受到明确的主机边界约束。

### 2.3 费用账本的“未知”与“零”仍未可靠区分

文件：`apps/ad-studio-desktop/ad_studio/usage_ledger.py`

- `record()` 的 token 数、`estimated_cost_rmb`、`unit_cost_rmb` 默认值均为 0；`record_many()` 对缺少字段同样以 0 补齐。
- `project_summary()` 返回字段名 `actual_cost_rmb`，但它累计的是成功记录中的 `estimated_cost_rmb`，即配置价格推算值，不是供应商账单核实值。
- 因此至少存在两个证据缺口：缺失 usage/单价时，零值不能区分“免费”“未配置价格”与“供应商未返回用量”；摘要字段的 “actual” 命名也可能让用户误以为是账单实值。
- 本轮只登记为既有 A51–A65 费用合同的候选映射，尚未逐项比对完整合同和所有调用方，不能据此宣布独立合同已覆盖或已验收。

### 2.4 账本记录不是供应商账单

账本记录模型、Provider、token 数、状态和估算金额，可用于本地追踪，但现有静态证据不能证明：
- 中转站与上游供应商账单一致；
- 供应商不返回 usage 时费用仍可准确计算；
- 图片、视频、缓存、最低消费或按请求计费均被统一建模；
- “估算金额”已与真实账单对账。

真实 Provider、代理站、实际扣费与账单验证继续按既定计划暂缓。

## 3. 对现有验收合同的候选映射（尚未完成语义裁决）

| 正式 ID 候选 | 本轮发现 | 当前证据结论 | 仍缺什么 |
|---|---|---|---|
| A13 | 模型路由和模型调用 | `resolve_route()` 存在自动回退路径；仅有设置/路由证据不等于逐次授权 | 逐项核对合同；明确拒绝回退后外部调用计数为 0 的专项测试 |
| A29 | 数据边界 | 自定义 Base URL/Provider endpoint 是请求目的地；视觉/参考素材可能随请求发送 | 端点披露、数据类别提示、拒绝外发的负例与端点/重定向边界证据 |
| A30 | 异常恢复 | 调用失败和费用不确定状态可能需要可恢复提示 | 核对失败、取消、重试是否产生重复外部副作用和重复记账 |
| A51–A65 | 费用估算、账本、恢复与成本状态 | 账本字段默认 0；`actual_cost_rmb` 汇总估算值 | 逐个保留不同合同；未知/未配置/估算/账单实值状态及调用方展示核验 |
| A31 / A32 | 帮助与 AI 接手 | 文档已有部分限制说明，但此报告仅补充证据，不代表所有帮助文本已同步核验 | 将本报告纳入权威台账和接手入口，并在后续文档同步任务中核对 |

候选映射不是正式去重裁决。不得因主题相似就合并 A ID，也不得新增 A113+。

## 4. 尚未完成的检查

本轮没有足够证据确认以下路径，因此明确标为“未核实”，不推断安全或不安全：

1. 凭据是否进入应用日志、异常追踪、诊断包或调试输出。
2. 导出、备份、迁移、复制配置与项目打包是否包含 API Key，以及是否有脱敏/排除规则。
3. 配置文件在 Windows 上的实际 ACL/权限、系统凭据库支持、加密密钥生命周期。
4. 用户修改 endpoint 后的 URL scheme/host 校验、重定向行为、内网地址访问边界与下载 URL 验证。
5. 取消、拒绝回退或拒绝外发时，各文本/视觉/资产/视频外部调用计数是否严格为零。
6. 费用 UI 是否把“价格未配置”“usage 缺失”“估算为零”和“实际账单已核对”分别呈现。

这些检查应继续映射到既有 A0–A112，不应立即转成产品开发任务或新增正式编号。

## 5. 下一步执行顺序

仍按 `docs/AD_STUDIO_PROGRESS_DASHBOARD.md` 的唯一权威状态执行 PLAN-003，不改变主线：

1. 继续查明凭据在日志、导出、备份、迁移中的流向，并记录代码路径/测试证据。
2. 逐项核对 A13、A29、A30、A51–A65 的正式合同全文，裁决哪些已有覆盖、部分覆盖、合同不同或证据不足。
3. 对“费用确认前不允许任何收费或外发调用”这一既有合同，继续追踪 `App.create()` 的完整编排顺序；目前已知创意规划调用早于预算确认，仍是 P0 候选阻断。
4. 只在静态证据映射与语义裁决完成后，再确定既有专项测试是否缺失；本轮不修改产品代码。
5. 保持 `fully_audited=0`、`semantic_dedup_completed=false` 与总体完成率关闭，直到权威台账中的退出条件有逐项证据支持。

## 6. 停止边界

- 不开发产品功能，不连接真实服务，不产生真实扣费。
- 不删除、合并或重新编号 A0–A112，不新增 A113+。
- 不把 CI 绿灯、UI 掩码、估算金额或静态代码存在误当成安全验收。
- PR #32 必须保持 Open / unmerged。
