# 淘宝 OAuth 实现计划

## 官方事实

- OAuth 授权先返回 `code`，再使用官方 `taobao.top.auth.token.create` 换取 access token。
- `code` 有效期约 30 分钟且只能使用一次。
- 开发/测试阶段 access token 有固定有效期；具体有效期以当前开放平台应用类型为准。
- Token、AppSecret 不能提交到 Git。

## 本项目实现

```text
浏览器
  -> /auth/taobao/start
  -> 淘宝授权页
  -> /auth/taobao/callback?code=...
  -> exchange code for access token
  -> encrypted/persistent token storage
  -> read-only API client
  -> Supabase normalized tables
```

## 环境变量

```text
TAOBAO_APP_KEY=
TAOBAO_APP_SECRET=
TAOBAO_REDIRECT_URI=
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
TOKEN_ENCRYPTION_KEY=
```

这些值只存在于本地 `.env` / 部署平台 Secret，不进入 GitHub。

## 安全要求

1. callback 必须校验 state，防止 CSRF。
2. OAuth code 只允许交换一次，并立即丢弃。
3. access token 不写日志、不返回前端、不进入 Git。
4. MCP 默认 READ_ONLY。
5. 写操作即使 API 存在，也必须经过 Risk Controller。
6. 在没有真实授权前，全部使用 Mock。

## 第一批只读 API

- `taobao.universalbp.new.material.shop.get`
- `taobao.universalbp.new.material.item.findpage`
- `taobao.universalbp.new.campaign.findpage`
- `taobao.universalbp.new.campaign.get`
- `taobao.universalbp.new.report.query.realtime`
- `taobao.universalbp.new.report.query.campaign`
- `taobao.universalbp.new.report.query.item.promotion`
- `taobao.universalbp.new.report.query.account`
- `taobao.universalbp.new.account.get.balance`
- `taobao.universalbp.new.crowd.findlist`

## 下一阶段

实现本地 OAuth callback 服务和 token vault；之后用真实授权进行一次只读连通性测试。任何预算、出价、暂停、删除等写 API 暂不调用。
