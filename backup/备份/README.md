# 备份

- 快照时间：2026-09-29
- GitHub仓库：`konggu888/ecommerce-agent`
- 备份分支：`备份`
- 网站：`https://konggu888.github.io/ecommerce-agent/#strategy-center`
- Supabase项目：`ecommerce-agent` (`skuoxmrzlxhebzhfgbyn`)
- 数据库结构：`database-schema.json`
- 数据库非空表数据：`database-data/`
- Supabase迁移历史与Edge Functions清单：见 `manifest.json`

**恢复基线：优先从本分支恢复网站代码，再按数据库结构、迁移历史和数据快照恢复Supabase。**

**注意：** `shop_authorizations` 等表可能涉及访问令牌等敏感凭据；本备份未额外导出零行核心业务表之外的秘密配置。不要把服务密钥、数据库密码或JWT秘密提交到Git。
