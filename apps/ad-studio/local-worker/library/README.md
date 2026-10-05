# 本地资产库

不依赖 Supabase、Firebase、AWS 等第三方数据库。

默认目录：
./data/ad-studio/
- library.json：资产索引
- assets/：演员、场景、产品素材等实际文件

可通过 AD_STUDIO_DATA_DIR 指定移动硬盘/其他本地目录。

启动：
node local-worker/library/server.mjs

接口只监听 127.0.0.1，不对公网开放。

原则：
- AI生成演员第一次保存到本地
- 后续广告只引用 asset id 和本地文件，不重复生成
- 用户上传演员同样永久保存在本地资产库
- 删除采用软删除，避免历史广告失去素材引用
- 以后可以在不改变上层接口的情况下，把 JSON 索引升级为本地 SQLite；当前无需引入数据库服务。