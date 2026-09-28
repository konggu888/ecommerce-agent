# 淘宝/天猫官方 API 接入记录

更新时间：2026-09-28

## 已核实

官方 TOP API 使用 `https://eco.taobao.com/router/rest` 作为国内 HTTPS 请求地址。公共参数包括 `method`、`app_key`、`timestamp`、`v`、`sign_method`、`sign`、`format` 等；授权 API 需要商家授权后的 session/access token。

官方当前支持 `md5`、`hmac`（HMAC-MD5）以及 `hmac-sha256` 签名方式。本项目客户端当前使用 `hmac-sha256`。

## OAuth

授权入口：`https://oauth.taobao.com/authorize`

官方文档说明可先获得 code，再通过 `taobao.top.auth.token.create` 换取 access_token。token 生命周期取决于应用类型/上线状态，不能硬编码有效期。

## 万相台无界只读能力

当前适配器已经封装：

- `taobao.universalbp.new.material.shop.get`
- `taobao.universalbp.new.material.item.findpage`
- `taobao.universalbp.new.campaign.findpage`
- `taobao.universalbp.new.report.query.realtime`
- `taobao.universalbp.new.campaign.get`
- `taobao.universalbp.new.account.get.balance`
- `taobao.universalbp.new.crowd.findlist`

官方文档还明确列出了计划预算更新、计划出价更新、关键词修改、人群状态修改、高级设置修改等写 API；这些暂时不接入执行层，直到 Risk Controller 和人工批准流程完成。

## 安全规则

- AppSecret、session/access_token 不提交到 Git。
- 不在日志中打印凭证。
- 默认 `LEVEL_1_READ_ONLY`。
- 任何预算、出价、计划状态、关键词、人群等写操作必须经过统一 Risk Controller。
- 正式 API 的写请求会影响真实店铺，必须单独验证并人工批准。
