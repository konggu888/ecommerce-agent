# 备份｜完整灾备恢复包

快照日期：2026-09-29
仓库：konggu888/ecommerce-agent
灾备分支：备份
Supabase：ecommerce-agent / skuoxmrzlxhebzhfgbyn
区域：ap-southeast-1
PostgreSQL：17.6.1.166

## 恢复目标

假设原 Supabase 项目完全不可用，从零建立新的 Supabase/PostgreSQL 项目后，使用本目录恢复：

1. 网站代码：本分支全部 Git 文件。
2. 数据库结构：database-schema.json + database-data/。
3. 数据库数据：database-data/ 下全部非空表快照。
4. Supabase Edge Functions：edge-functions/。
5. 数据库扩展清单：extensions.json。
6. 项目/运行环境元数据：project-metadata.json。
7. Auth/Storage 状态：auth-storage-manifest.json。
8. 恢复程序：restore/restore_database.py。
9. 恢复后的核验：restore/restore_checklist.md。

## 当前快照状态

- Auth 用户：0
- Auth identities：0
- Storage buckets：0
- Storage objects：0
- 因此本次快照不存在需要搬运的 Auth 用户或 Storage 文件。
- 当前有数据的业务/沙盒表已经保存到 database-data/。

## 重要边界

这个 GitHub 仓库是公开仓库，因此绝不把 service_role、数据库密码、JWT secret、OAuth client secret、第三方平台密钥、Auth 密码哈希或其他秘密写入仓库。

这些秘密必须在恢复时重新创建/轮换，并按 restore/restore_checklist.md 填回。

因此这里的“完整灾备”指：代码、数据库结构、当前非空数据、Edge Functions、扩展/策略/项目状态和恢复程序全部有可重建材料；秘密凭证不复制，而是通过重新生成/轮换恢复。

## 恢复顺序

1. 创建新的 Supabase 项目。
2. 使用 database-schema.json / restore_database.py 重建 public 数据库结构。
3. 按外键依赖导入 database-data/。
4. 恢复 RLS 与 policies。
5. 部署 edge-functions/ 中的函数源码，并核对 verify_jwt。
6. 重新生成 publishable/anon key 与 service credentials；不要复用旧 secret。
7. 将新的 Supabase URL / publishable key 写入网站部署环境。
8. 运行 restore/restore_checklist.md 中的完整核验。
9. 最后才重新开放网站流量。

## 当前已知安全事项

原项目有 12 个 public 表关闭 RLS：shops、products、orders、campaigns、campaign_metrics、keywords、targeting、decisions、experiments、action_logs、shop_authorizations、shop_permissions。

恢复时不要简单地“全部开启 RLS 就结束”；必须根据实际访问模型创建对应 policies，否则前端访问会被阻断。database-schema.json 保存了当前 policies/RLS 状态，恢复后应逐项核对。
