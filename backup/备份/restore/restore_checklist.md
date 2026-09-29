# 灾难恢复核验清单

## A. 项目
- [ ] 新 Supabase 项目创建完成。
- [ ] 区域、PostgreSQL 主版本与原项目兼容。
- [ ] 新 Project URL 已记录。
- [ ] 新 publishable/anon key 已生成。
- [ ] service_role/secret keys 已重新生成并只放在安全的部署环境。

## B. Database
- [ ] public 表数量与 database-schema.json 一致。
- [ ] 每张表字段、类型、默认值、NOT NULL 一致。
- [ ] PRIMARY KEY / UNIQUE / CHECK / FOREIGN KEY 一致。
- [ ] indexes 一致。
- [ ] RLS 开关一致。
- [ ] policies 一致。
- [ ] 每个 database-data/*.json 的 row_count 与恢复后 SELECT COUNT(*) 一致。
- [ ] 关键外键抽查通过。
- [ ] sandbox_runs、sandbox_events、sandbox_market_signals、sandbox_agent_rounds 等核心沙盒表数据存在。

## C. Edge Functions
- [ ] sandbox-benchmark 已部署。
- [ ] sandbox-state 已部署。
- [ ] sandbox-agent-runner 已部署。
- [ ] verify_jwt 与 manifest 一致。
- [ ] 函数源码版本与 edge-functions/ 快照一致。
- [ ] 逐个调用测试接口。

## D. Website
- [ ] GitHub Pages 能打开。
- [ ] Strategy Center 能打开。
- [ ] Supabase URL/key 指向新项目。
- [ ] 读取历史棋谱/沙盒数据正常。
- [ ] 新建运行、读取运行状态、读取结果正常。
- [ ] 浏览器 Console 无关键错误。

## E. Security
- [ ] 不把 service_role、数据库密码、JWT secret、OAuth secret 写入 Git。
- [ ] 重新生成所有第三方凭证。
- [ ] 对 public 表重新执行 Supabase Security Advisor。
- [ ] 原项目关闭 RLS 的 12 张表必须重新审查访问策略。
- [ ] Edge Function 中的认证方式逐项确认。

## F. 最终验收
恢复完成后必须得到：网站代码正常、数据库结构一致、数据库数据行数一致、Edge Functions 可运行、Auth/Storage 与快照一致、Secrets 已重新生成、Security Advisor 已复核。
