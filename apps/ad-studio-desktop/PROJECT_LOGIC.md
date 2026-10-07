# AI 商品广告工厂：代码逻辑与系统地图

本文不是用户手册，而是给接手项目的 AI/开发者看的系统级逻辑说明。修改代码后必须同步维护。

## 1. 总体职责分层

用户
→ AdStudio.exe / Tkinter桌面UI
→ 项目编排层 app.py
→ 商品资料采集 product_parser.py
→ 多模型创意决策 model_router.py
→ 创意结构 creative_engine.py
→ 成本预估 engine.py
→ 本地资产库 library.py
→ 素材生成 asset_generation.py
→ 生产执行 production.py
→ 本地后处理 postprocess.py
→ FFmpeg ffmpeg.py
→ 硬件能力 hardware.py / GPU兼容入口 gpu.py
→ 成本账本 usage_ledger.py

## 2. 创建项目主链

商品链接/资料
→ ProductParser
→ ProductInfo
→ ModelRouter
→ 创意方案
→ CreativeShot[]
→ validate_plan
→ 当前方案成本预估
→ 预算确认
→ ProductionStore
→ 资产解析
→ 镜头生成
→ 本地硬件能力调度 / FFmpeg
→ 最终拼接

预算确认是云端生成的闸门。确认前只能做采集、AI分析和估算，不应开始实际云端素材生成。

## 3. LLM 决策逻辑

model_router.py 是思考层，不是视频编辑器。

每个创意阶段可以单独指定 ModelProfile：
- provider
- base_url
- model
- api_key
- enabled
- 输入/输出价格

因此不同功能可以使用不同模型。

核心原则：
模型决定“做什么、为什么这么做”；程序决定“怎么执行、怎么保存、怎么计费”。

## 4. 多创意方案

create_plans(product, constraints, count):
1. 生成第一个方案。
2. 将前面方案的策略摘要传给后续方案。
3. 要求后续方案主动避开已经使用的机制。
4. 每个方案仍独立经过创意决策链。
5. UI 只激活当前方案，项目保存全部方案。
6. 切换方案后重新绑定 shots 和成本预估。

方案不是行业模板。模型必须根据当前商品决定适合的广告机制。

## 5. 素材解析逻辑

每个 Shot 可以声明：
- actor_requirements
- scene_requirements
- product_asset_requirements
- generation_if_missing

解析顺序必须保持：

本地资产库搜索
→ 找到合适素材：复用
→ 已有素材可本地加工：加工后复用
→ 没有合适素材：允许生成
→ 生成后注册本地资产库
→ Shot 绑定稳定 asset_id

当前代码已经有“本地优先/缺失生成/入库”的框架，但“已有素材是否可加工”的自动判断链仍属于未完全实现能力；不能伪称已完成。

## 6. 资产持久化

LocalLibrary：
- root
- assets/
- library.json

资产必须有稳定 ID。

资产库路径可以独立于项目目录，由桌面端保存到 library-location.json。

生成的新资产必须写入资产库，而不是只放在当前项目临时目录。

## 7. 成本逻辑

成本分四类：
- 视频生成
- 演员生成
- 场景生成
- 商品素材生成

estimate_asset_generation 会对相同资产需求去重。

用户输入项目预算只是决策约束，不是自动降级器。

如果预计总成本 > 用户预算：
- 明确显示超预算
- 询问是否继续
- 用户继续：按原方案执行
- 用户取消：不进入正式生成阶段

禁止自动换模型、删镜头、降质量。

## 8. 云端/本地边界与硬件自适应

系统不得把任何具体显卡型号作为最低配置、架构边界或固定执行方案。

hardware.py 动态检测 CPU、RAM、GPU厂商/型号/显存、CUDA/ROCm/Metal/CPU 后端、FFmpeg硬件编码器，并给出 local_first / hybrid / cloud_first 执行策略。

原则：
- 本地计算设备能高效完成的 → 本地执行。
- 本地能力不足或缺少兼容运行时的 → 云端执行。
- 两边都能完成时 → 根据能力、成本和稳定性选择。
- 显卡型号只是检测结果，不是系统规则。

gpu.py 仅保留兼容入口，不再包含4050专属逻辑。



本地计算设备：
- 资料处理
- 创意编排
- 素材匹配
- 视频预处理
- 画幅/裁切/缩放
- 字幕
- 音频
- FFmpeg
- NVENC
- 最终合成

云端：
- 本地难以生成的高质量人物
- 高质量场景
- 高质量视频镜头
- 必要时的高质量语音

不要假设浏览器或Vercel可以直接知道用户本机GPU。

## 9. 镜头版本

单镜头独立生成：
shot-01/v1
shot-01/v2
shot-03/v1

重新生成一个镜头不应强制重做其他镜头。

最终成片只使用当前确认版本。

## 10. 音视频后处理

postprocess.py 根据 Shot 参数执行：
- aspect_ratio
- focus_x/focus_y
- speed
- transition
- subtitle
- audio/BGM

ffmpeg.py 根据实际硬件动态选择可用 H.264 硬件编码器（NVENC/AMF/QSV/VideoToolbox），无硬件编码器时使用 CPU 编码。

## 11. Provider 原则

providers.py 是通用视频Provider接口。

asset_generation.py 是通用素材生成接口。

不同厂商协议不同，必须新增真实适配器后才能称为“已接通”。

如果 Provider 仍是 stub：
- UI 可以显示配置入口
- 成本可以估算
- 但不能声称真实生成已经成功。

## 12. 状态与持久化

项目工程、资产库、成本账本是三个不同持久化边界：
- 项目：项目目录
- 资产：用户指定资产库
- 调用成本：usage ledger

不要把临时生成文件误当成永久资产。

## 13. 修改模块时的依赖判断

| 修改区域 | 必须重新检查 |
|---|---|
| app.py | 所有UI、项目创建、预算、方案切换、生产入口 |
| model_router.py | 模型路由、成本、JSON结构、方案数量 |
| creative_engine.py | Shot字段、验证、分镜数据契约 |
| library.py | 资产ID、匹配、持久化 |
| production.py | 资产解析、镜头生成、版本、最终合成 |
| engine.py | 成本估算、资产去重 |
| asset_generation.py | 真实Provider能力、价格、入库 |
| providers.py | 云视频Provider、状态轮询、价格 |
| postprocess.py | 硬件能力、FFmpeg后处理 |
| ffmpeg.py | 编码、NVENC、拼接 |
| product_parser.py | 商品资料来源和回退 |
| usage_ledger.py | 调用记录和成本 |
| hardware.py / gpu.py | 硬件能力检测与兼容接口 |

## 14. AI 修改后的必做闭环

阅读 AGENTS.md
→ 阅读 PROJECT_LOGIC.md
→ 阅读 HELP.md
→ 阅读目标模块
→ 修改代码
→ 更新 PROJECT_LOGIC.md
→ 更新 HELP.md
→ 更新限制/更新记录
→ 运行测试
→ 检查文档同步
→ 提交

## 15. 判断“任务完成”的标准

只有同时满足以下条件，才算完成：
- 代码实现完成
- 真实能力边界已核实
- 测试通过或已明确记录失败原因
- PROJECT_LOGIC.md 已同步
- HELP.md 已同步
- 更新记录已增加
- 未把stub说成已接通

# 更新记录

## 2026-10-08
### 硬件能力自适应
移除4050作为架构边界，新增通用硬件能力检测与动态执行策略；FFmpeg不再只依赖NVENC。
建立系统级代码逻辑地图、AI接手规则和文档同步强制机制。
