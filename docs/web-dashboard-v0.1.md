# Web Dashboard v0.1

目标：不是只增加一个“Web 搜索”功能，而是让整个 Ecommerce Agent 在 Web 控制台可见。

## 页面
- 总览：店铺、市场状态、ROI、预算、完整决策链。
- Web 市场情报：竞品价格、活动、类目趋势、流量成本、平台规则、内容热点。
- 商业博弈：我方数据 + 对手观察 + 市场状态 → 策略候选。
- 广告/流量：预算、出价、CPC、CTR、CVR、ROI、边际回报。
- 实验与回测：实验状态、样本、结果、场景回测。
- Risk Controller：分析、审批、受限自动、禁止。
- 任务监控：长任务进度与最终状态。
- 学习记忆：预期结果 vs 实际结果。

## 核心原则
Web 是情报输入层，不直接执行广告/订单等写操作：

Web 事实 → 市场信号 → 竞争假设 → 证据 → Game Agent → 约束 → Risk Controller → 执行

每条外部观察应保存 URL、title、fetchedAt、sourceType、reliability、observation、signal、expiration/staleness。

当前 apps/web 使用零依赖静态控制台和模拟数据，先把完整系统界面跑起来；后续接真实 API、Supabase Realtime、Web 搜索/网页采集和店铺适配器。