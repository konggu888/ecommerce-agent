# 淘宝官方 OAuth 接入下一步

## 已核验

淘宝 TOP 官方文档当前提供 OAuth 授权入口：`https://oauth.taobao.com/authorize`；授权后通过 `taobao.top.auth.token.create` 用 code 换取 Access Token。官方文档说明 TOP API 使用 HTTPS 调用，且正式测试环境仍会访问线上真实淘宝数据；写操作会直接影响线上店铺，因此本项目第一阶段只做只读。

万相台无界官方 API 当前公开了实时报表、计划列表/详情、商品、店铺、账户余额等查询能力，同时也公开预算、出价、高级设置等写接口。本项目暂时不启用任何写接口。

## 当前安全策略

- 不在 Git 中保存 AppKey、AppSecret、Access Token、Session。
- 不要求用户把 Token 发到聊天里。
- 认证信息只允许通过本地环境变量/密钥管理注入。
- 默认权限 `LEVEL_1_READ_ONLY`。
- 任何写操作必须经过 Risk Controller。

## 环境变量预留

```text
TAOBAO_APP_KEY=
TAOBAO_APP_SECRET=
TAOBAO_REDIRECT_URI=
TAOBAO_ACCESS_TOKEN=
```

## 下一步实际操作

1. 在淘宝开放平台创建/配置自研应用。
2. 确认应用具备目标万相台无界 API 权限。
3. 配置 Redirect URI。
4. 完成 OAuth 授权，取得 code。
5. 服务端用官方 token API 换取 Access Token。
6. 先执行只读 API：店铺、商品、计划、实时/计划报表、余额、人群。
7. 将标准化结果写入 ecommerce-agent 的 Supabase 数据模型。
8. 用 MCP 暴露只读工具给 Agent。
9. 通过 Mock/真实只读数据测试后，才评估写权限。

## 官方文档依据

- TOP API 调用方法：https://developer.alibaba.com/docs/doc.htm?articleId=101617&docType=1
- TOP 应用环境说明：https://developer.alibaba.com/docs/doc.htm?articleId=108&docType=1&treeId=49
- 获取 Access Token：https://developer.alibaba.com/docs/api.htm?apiId=25388&scopeId=381
- 万相台无界 API 列表：https://developer.alibaba.com/docs/api.htm?apiId=68741
