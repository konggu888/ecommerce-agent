# 买家视角采集器 v0.1

## 目标
把“游客公开页面”和“用户登录后正常可见页面”统一进入数据标准化层，再进入商业博弈引擎。

## 数据入口
1. URL：公开商品/搜索/市场页面。
2. 买家会话：用户自行完成淘宝/拼多多登录，系统在授权浏览会话中读取该账号正常可见页面。
3. 卖家数据：未来通过平台允许的官方授权/API或用户导出的经营数据接入。

## 会话安全
- 不保存平台密码。
- 不绕过验证码、登录保护、访问控制或反爬限制。
- 不伪造设备/身份。
- 只读取当前会话正常可见的数据。
- 每条数据保存 source、observedAt、evidence、visibilityMode。

## 统一字段
platform, query, rank, productId, title, price, originalPrice, discount,
rating, reviewCount, salesCount, seller, category, tags, promotion,
shipping, stockText, contentSignals, fetchedAt, visibilityMode, sourceUrl

## 买家视角工作流
关键词/URL
→ 打开平台
→ 用户完成登录（如需要）
→ 搜索/打开页面
→ 提取当前可见信息
→ 标准化
→ 保存证据
→ 市场快照
→ 对手画像
→ 博弈引擎

## 博弈输入
我方数据 + 买家视角竞品数据 + 市场快照
→ opponent model
→ behavior tree
→ multi-round game
→ breakthrough engine
→ Risk Controller

## 当前限制
v0.1只定义架构和字段，不声称已经连接淘宝/拼多多真实买家会话。真实平台连接需要浏览器会话/授权适配器和合规的页面读取实现。
