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

## 8.1 用户实拍视频视觉分析链

输入：
**商品 ProductInfo + CreativePlan + 用户视频文件夹**。

处理：
1. `footage.py.scan_footage` 用 ffprobe 获取视频技术元数据。
2. `build_visual_manifest` 为每个可解析视频均匀抽取低分辨率关键帧。
3. `ModelRouter.analyze_footage` 将关键帧作为图片输入交给“素材剪辑导演”路由模型。
4. 视觉模型输出逐素材评分、可用性、最佳时间段、画面标签、卖点对应、口播质量和总体建议。
5. `plan_footage` 把视觉分析与商品/创意方案合并，生成严格受素材清单约束的剪辑计划。
6. `validate_footage_plan` 校验 source、start、duration，越界时截断，清单外素材直接失败。
7. `ProductionStore.render_footage_shot` 只调用本地 FFmpeg 裁剪，不调用视频生成 Provider。

状态保存：
- 关键帧：项目目录 `projects/<project-id>/footage-analysis/`。
- 视觉分析：`Project.creative_plan["footage_visual_analysis"]`。
- 最终剪辑计划：`Project.creative_plan["footage_plan"]`。
- 每个镜头继续使用 `Shot.clip_source="filmed"`、`source_file`、`source_start`、`source_duration`。

本地/云端边界：
- 视频文件先在本机抽帧。
- 只有用户明确配置且启用视觉输入的模型，关键帧才会作为模型输入发送。
- 裁剪、画幅、字幕、BGM和最终拼接仍由本机执行。

失败策略：
- 没有视觉能力的素材剪辑导演模型会明确报错，不会把“文件名+时长分析”冒充为已经看过视频。
- FFmpeg抽帧失败则素材分析停止。
- 剪辑计划引用清单外文件则校验失败。


## 8.1.1 实拍重复镜头与最佳版本选择
视觉模型在观察关键帧时同时完成重复拍摄识别。输出 `duplicate_group`、`duplicate_confidence`、`take_rank`、`best_take`、`keep_reason`；`normalize_footage_analysis` 在本地规范字段并在模型未明确指定最佳版本时按同组优先级/评分选出最佳版本。`plan_footage` 将该结果作为硬约束之一，优先选择最佳版本。重复素材不会自动删除，只有 AI 明确 `usable=false` 或扫描阶段无法解析的素材才进入废片归档。

## 8.1.2 实拍废片自动归档
实拍项目 UI 新增 `footage_analysis_report`，直接读取项目持久化的 `footage_visual_analysis`、`footage_archive` 和 `footage_transcripts`，不重新调用模型；因此查看报告不会产生新的 AI 调用费用。

视觉分析完成后，`footage.py.archive_analyzed_waste`执行安全归档：
1. AI 返回 `usable=false` 的素材进入归档候选；扫描阶段 duration<=0、无法解析的视频也进入候选。
2. 归档目录为原实拍文件夹同级的 `05_废片库/<project-id>/`。
3. 使用 `shutil.move` 移动文件，不执行删除；目标文件名冲突时自动追加编号。
4. 每次归档写入 `archive-manifest.json`，保存原路径、目标路径、原因、评分和视觉标签。
5. 只有移动成功的素材从后续 `usable` 候选中剔除；移动失败则继续保留，避免误丢素材。
6. 若归档后没有任何可用素材，项目创建明确失败，并告知用户废片已归档位置。

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

## 12. 成本实际发生账本

`usage_ledger.py` 现在同时记录模型调用与实际资产/视频生成费用。资产记录包含项目ID、镜头ID、资产类型、Provider、状态和实际费用；视频记录包含项目ID、镜头ID、Provider和实际费用。ProductionStore 只有在生成成功后才记实际费用，并把项目实际成本汇总写入 `Project.actual_cost_rmb` / `Project.actual_cost_summary`。模型调用也会绑定当前项目ID；本地生成成本为0，云端成本按当前 Provider 配置价格记录。重新生成产生新的账目，不覆盖历史记录。

## 13. 状态与持久化

项目工程、资产库、成本账本是三个不同持久化边界：
- 项目：项目目录
- 资产：用户指定资产库
- 调用成本：usage ledger

不要把临时生成文件误当成永久资产。

## 14. 修改模块时的依赖判断

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

## 15. AI 修改后的必做闭环

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

## 16. 判断“任务完成”的标准

只有同时满足以下条件，才算完成：
- 代码实现完成
- 真实能力边界已核实
- 测试通过或已明确记录失败原因
- PROJECT_LOGIC.md 已同步
- HELP.md 已同步
- 更新记录已增加
- 未把stub说成已接通

## 2026-10-08：实拍废片自动归档
视觉分析结果现在直接驱动废片归档；明确 `usable=false` 或无法解析的素材移动到 `05_废片库/<project-id>`，生成归档清单并保留失败移动文件，随后仅用成功保留的素材进入口播转写与剪辑导演。

## 2026-10-08：实拍分析报告工作区
桌面 UI 增加实拍分析报告入口；报告只读取项目已有分析结果，不重复调用模型。扫描阶段无法解析的素材现在也会进入废片归档逻辑。

# 更新记录

## 2026-10-08：视觉模型默认能力同步
补充说明：现有默认 GPT 路由会自动启用视觉分析标记；已有本机模型配置也会在加载时兼容旧格式，不要求用户重新创建模型。

## 2026-10-08：实拍视频视觉分析链
新增本地关键帧抽取、视觉模型输入、逐素材视觉分析结果持久化，并让素材剪辑导演使用该分析结果规划起止时间；视觉能力未配置时明确失败，不降级冒充“看过视频”。

## 2026-10-08：实际成本账本闭环
模型、演员/场景/商品素材、视频镜头三类实际调用现在都可以按项目ID归集到同一本本地 usage ledger；项目保存累计实际成本与分类汇总。镜头成本不再被视频费用覆盖资产生成费用，v2重生成会新增历史账目而不是覆盖旧账。

## 2026-10-08
### 硬件能力自适应
移除4050作为架构边界，新增通用硬件能力检测与动态执行策略；FFmpeg不再只依赖NVENC。
建立系统级代码逻辑地图、AI接手规则和文档同步强制机制。


## 2026-10-08：硬件能力进入生产后处理
ProductionStore.postprocess_shot 会读取当前硬件能力画像，并在状态中记录本地执行策略；实际编码由 FFmpeg 的动态编码器选择器决定，不再固定使用 RTX 4050/NVENC。


## 2026-10-08：生成执行链修正
CapabilityRouter 已实际接入 LLM、素材生成、视频生成入口；本地素材生成兼容 SD WebUI 完整 endpoint 与基础 endpoint，避免重复拼接 `/sdapi/v1/txt2img`。系统状态中的素材调度明确指定资产类型，独立模型路由显示与实际 FUNCTIONS 数量一致。


## 2026-10-08：CI 修复
CI 的桌面 Python 语法检查发现 `ffmpeg.py` 的 concat 清单 `write_text` 括号错误，已修复为先完成 `join` 再传入 `encoding` 参数；功能逻辑不变。


## 2026-10-08：视频生成失败安全机制
视频生成统一入口现在先写 `.part.mp4` 临时文件，Provider 完整成功且文件非空后才替换正式版本。重新生成失败时保留上一版本的 `video_path`，并将镜头状态标记为“生成失败（已保留上一版本）”，避免单镜头失败污染已有成片。


## 2026-10-08：镜头参考素材传递
镜头生成请求现在同时解析演员、场景、商品素材的稳定 asset_id 与本地真实文件路径。Provider 可按自身协议使用这些引用；通用视频 Provider 支持通过 `embed_reference_assets=true` 将本地图片以内嵌 data URI 发送给支持该格式的云端接口。未声明支持参考图的第三方 Provider 仍需专用适配器，不能假定所有平台都会读取这些字段。


## 2026-10-08：实际成本字段统一
项目模型现在持久化 `actual_cost_rmb` 与 `actual_cost_summary`；ProductionStore 统一通过实际成本记录入口写入资产/视频费用，避免同一笔生成费用重复入账。

## 8.2 实拍口播转写接口
新增 `transcription.py`：先用 FFmpeg 从实拍视频提取单声道 16kHz WAV，再调用配置的 OpenAI-compatible transcription endpoint。优先解析 segment/word 时间戳；供应商不支持时间戳时仍保存文本，但不宣称已经具备逐词级裁剪。该模块只负责转写，废话删除和最终剪辑仍由素材剪辑导演决定。

## 8.3 口播转写进入实拍剪辑链
用户拍摄素材创建时，若“口播转写”路由已启用且模型支持转写，逐个视频提取音频并调用 `/audio/transcriptions`。结果写入 `footage_transcripts`，并随 creative_plan 提供给素材剪辑导演；失败只记录错误，不伪造文本。

## 8.4 视觉 + 口播联合决策
`plan_footage` 的输入同时包含 `footage_visual_analysis` 与 `footage_transcripts`。视觉模型负责画面事实，转写模型负责语言事实，素材剪辑导演负责最终镜头选择、顺序和口播取舍。

## 2026-10-08：转写接口语法修复
修复 `transcription.py` 的 multipart 请求字符串构造，避免换行被写入 f-string 导致语法错误。

## 8.5 实拍口播废话删除与多段镜头执行
素材剪辑导演读取 creative_plan.footage_transcripts。当需要删除口播废话/重复表达时，输出镜头 ranges=[[start,end],...]，这些区间使用原始素材时间轴。validate_footage_plan 会排序、合并重叠区间并限制在素材时长内；最终有效时长为各保留区间之和。models.Shot.source_ranges 持久化这些区间；ProductionStore.render_footage_shot 会分别裁剪每段并调用本地 concat 拼接，因此废话不会进入该镜头成片。

- 2026-10-08：口播转写上传层统一使用显式 CRLF multipart 边界，避免换行转换造成 Python 语法错误。


## 更新记录
- 2026-10-08：新增实拍重复镜头分组与最佳版本选择的数据规范、规范化逻辑及剪辑导演优先级规则。

- 2026-10-08：`footage_analysis_report` 展示 `duplicate_group` 与 `best_take`，报告只读取已保存结果，不新增模型调用。

- 2026-10-08：实拍素材池新增本地综合排名 `material_rank`/`selection_score`；基于 AI 原始评分、最佳版本、口播质量、画面标签和重复镜头惩罚排序，不覆盖原始 AI 评分，也不产生额外模型调用。


## 2026-10-08：实拍素材排名后的覆盖审计
新增 audit_footage_coverage。在素材池统一排名后，本地确定性检查卖点覆盖、开场候选和关键镜头缺口，并把结果保存到 creative_plan["footage_coverage"]。该步骤不调用模型；最终剪辑导演同时收到 footage_analysis 与 footage_coverage，因此“排名最高”不再机械等于“最终一定使用”，唯一能覆盖重要卖点的素材可以获得优先权。缺失的真人/场景、特写、演示、口播等镜头标记为待补拍，系统禁止编造不存在的实拍画面。


## 2026-10-08：最终实拍分镜复核链
`audit_final_footage_plan` 在 `validate_footage_plan` 之后运行。它读取最终分镜与素材排名/覆盖审计，把每个 Shot 与素材池信息重新关联，记录 sequence_index、material_rank、selection_score、duplicate_group、best_take、covered_selling_points，并检查 opening_candidate 是否实际使用、哪些重要卖点最终没有进入分镜、哪些重复拍摄组被多次使用。结果保存为 `creative_plan["footage_selection_audit"]`，不产生额外模型调用；它是最终生产前的确定性质量闸门，而不是另一个 AI 决策模型。`


## 2026-10-08：实拍缺口分类
新增 classify_footage_gaps。它读取 footage_coverage 的关键镜头/卖点缺口，根据缺口是否涉及商品事实、细节、操作、演示等内容确定“待补拍”；只有明确传入已接通的生成能力时才允许标记“待生成”，否则使用“待补素材”。当前实拍模式调用时明确 generation_connected=False，因此不会伪称视频生成已接通。结果写入 creative_plan["footage_gaps"] 并展示在创建项目摘要中。


## 2026-10-08：实拍缺口分类输入兼容修复
classify_footage_gaps 不再要求 missing_selling_points 必须同时存在于 footage_coverage.selling_points 详情映射；覆盖审计直接返回的缺失卖点名称现在也会进入 selling_point_gaps，保持缺口数量与实际缺口一致，并通过回归测试固定该数据契约。


## 2026-10-08：实拍缺口任务编排
新增 build_footage_gap_tasks：把 footage_coverage + footage_gaps 转成稳定的 GAP-001...任务清单。任务明确“待补拍/待补素材/待生成”、优先级、关联卖点、执行要求和验收标准；只负责编排，不执行拍摄或生成。项目保存到 creative_plan["footage_gap_tasks"]，UI 可直接查看。完成任务后应把新增素材放回原文件夹，再进入下一阶段的重新扫描闭环。


## 2026-10-08：实拍闭环重分析
新增 reanalyze_footage：在已有实拍项目上复用商品信息与创意约束，对当前素材文件夹重新执行完整素材处理链，并更新 footage_visual_analysis、footage_coverage、footage_gaps、footage_gap_tasks、footage_plan、footage_selection_audit 等项目状态。新增素材因此能够真正重新进入素材池，而不是只生成一份静态补拍清单。

## 17. AI 强制推进前检查闸门
“继续推进”不是无条件执行。任何 AI/Codex 准备修改代码前，必须先读取当前最新提交的 CI 状态，并在 CI 失败时读取失败 job/log，定位具体错误后优先修复。随后核对 AGENTS.md、PROJECT_LOGIC.md、HELP.md、目标代码和测试；完成本地可执行检查与文档同步检查后，才允许继续增加功能。

状态判断必须针对当前 HEAD：
- queued / in_progress = 未完成，不能说通过。
- completed + success = 当前检查通过。
- completed + failure = 必须先处理失败。
- 修复后的新提交必须重新等待/检查新的 CI，不能沿用上一提交结果。


## 2026-10-08：重新分析闭环提交检查
重新分析闭环的测试文件已清除误写的说明文本；本次文档同步与测试修复保持同一提交，确保代码、测试、HELP.md、PROJECT_LOGIC.md 的原子变更契约继续成立。后续推进必须重新检查最新 HEAD 的 CI，不复用旧提交结果。


## 2026-10-08：重新分析的引用保护
`reanalyze_footage` 在废片归档前收集当前项目 Shot 与 `footage_plan` 已引用的 `source_file`，传给 `archive_analyzed_waste(..., protected_paths=...)`。归档器对受保护素材只记录不可用判断，不移动源文件，从而保证重新分析不会破坏当前成片/分镜依赖。新增回归测试固定该行为。


## 2026-10-08：重新分析历史版本
新增 `append_footage_reanalysis_history`。每次重新分析覆盖当前结果前，先把上一轮视觉分析、覆盖审计、缺口任务、最终分镜方案单独写入项目历史目录；这样“补拍→重新分析”可以连续进行而不会丢失上一轮决策。


## 2026-10-08：分析历史 UI
新增 `footage_reanalysis_history_report`。它读取 `footage-reanalysis-history/` 中已保存的快照并展示覆盖率、缺口任务和历史镜头数，避免用户连续补拍后无法回看之前的决策；不新增模型调用。


## 2026-10-08：全桌面项目 UI 操作契约
UI 硬闸门升级为全项目规则：不再只检查少数固定功能。所有用户可执行功能必须使用 `@ui_action` 注册；`ui_contract.py` 从 AST 自动收集这些注册动作，并要求每个动作拥有真实 Tkinter Button command 入口。这样新增功能如果只写后端、不接 UI，会在自动检查阶段失败。该结构检查仍不能替代运行桌面端后的视觉验收，因此 AI 仍需检查实际界面、按钮状态、操作路径和结果展示。

## 2026-10-08：UI 操作契约支持 lambda 参数适配
`ui_contract.py` 的 AST 检查现在会继续解析 Tkinter Button 的 `command=lambda: self.xxx(...)`，把 lambda 内真正调用的用户操作纳入按钮绑定集合。这样全项目 `@ui_action` 硬闸门既能拦截后端孤立功能，也不会误伤合法的参数适配按钮。

## 2026-10-08：任务类型作为全链路硬约束
桌面端创建项目时必须选择且只选择一种任务类型：`电商短视频`、`商品主图视频`、`广告投放视频`。选择结果写入 `creative_plan.task_type`，并进入 `_creative_constraints()`，使创意规划、素材分析和后续出片共享同一任务目标，不能只在 UI 上显示而不影响 AI 决策。

## 2026-10-08：任务类型进入实拍剪辑导演
`plan_footage()` 现在接收 `creative_plan.task_type/task_rules`，并把任务类型作为镜头排序、素材取舍、时长和结尾策略的硬约束。这样“本次任务”不会停留在创建页面，而会贯穿 AI 实拍素材剪辑导演；缺失的商品证据继续进入缺口任务，不允许 AI 虚构画面。

## 2026-10-08：任务类型确定性闸门
validate_task_type_plan 在创意方案进入项目/成片前执行，防止 AI 忽略“本次任务”：电商短视频必须有 Hook；商品主图视频必须有商品本体/细节/功能展示；广告投放视频必须有转化/CTA。检查失败直接阻止错误结构进入生产链，并记录 task_validation。

## 2026-10-08：三种任务成片政策
`TASK_TYPE_POLICIES` 统一定义三种任务的时长边界和结构顺序，并写入 `creative_plan.task_policy`。它同时约束创意方案与实拍素材导演，避免 UI 选择与最终成片脱节。

## 2026-10-08：广告投放多版本 A/B 审计
广告投放视频的多方案现在按测试轴生成：Hook、核心卖点、证明方式、CTA。`audit_ad_variant_set()` 对方案的 Hook/策略/视频形式/脚本做确定性两两差异审计，结果写入 `variant_set_audit`，为后续投放实验提供版本矩阵基础，不增加额外 AI 调用。

## 2026-10-08：版本实验信息持久化
每个创意方案保存 `variant_test_axis`；方案集合的 `variant_set_audit` 也随项目保存，因此切换方案、单独生成镜头或重新打开项目时不会丢失 A/B 实验上下文。

- 2026-10-08 修复：A/B 多版本审计仅作为 ModelRouter 的辅助能力，不改变 `plan_footage()` 的类内作用域和原有实拍剪辑链。

- 2026-10-08：`variant_shot_cache` 保存各方案镜头状态，`variant_outputs` 保存各方案成片路径；最终渲染支持 `variant_index` 独立命名。

## 2026-10-08：投放版本矩阵
`variant_matrix_report()` 提供投放前版本总览，将 `creative_variants`、`variant_set_audit`、`variant_outputs` 汇总展示。它是只读审计界面，不重新调用模型，也不宣称真实投放效果。

## 2026-10-08：批量输出已完成版本
`batch_final_render()` 在版本矩阵之后提供安全的批量出片：逐方案恢复独立镜头状态，仅对所有镜头文件真实存在的版本执行最终渲染；缺失镜头的版本跳过并报告。该动作不触发新 AI 生成，避免未经预算确认产生额外成本。

## 2026-10-08：一键生成全部广告版本
`batch_generate_variants()` 是多版本真正的一键执行入口。它先做确定性的剩余镜头成本估算和预算闸门，再逐方案生成缺失镜头并分别最终渲染。已经存在的真实镜头不重复生成；失败镜头保留失败状态；每个版本继续使用独立 `variant_shot_cache` 与 `variant_outputs`。

## 2026-10-08：实拍素材多方案独立剪辑
实拍模式的公共素材分析与创意方案解耦：视觉分析/废片归档/转写只执行一次，而 plan_footage() 按每个 creative_variants 分别执行。结果保存为 variant_footage_plans、variant_footage_coverage、variant_footage_selection_audits、variant_footage_gaps、variant_footage_gap_tasks。

## 2026-10-08：实拍分析可解释性
实拍分析报告现在提供素材级解释面板：用户选择素材后可直接看到 AI 判断原因、推荐片段、画面标签、重复组、最佳 Take 和口播质量。该界面只展示已保存分析，不产生新的 AI 调用。

## 2026-10-08：实拍剪辑决策时间线
实拍分析报告提供只读决策时间线。它读取 `variant_footage_plans`（没有时回退到 `footage_plan`），按创意方案展示镜头顺序、素材、`ranges`、时长、镜头目的、画面/构图与决策依据；不触发新的 AI 调用。多段 `ranges` 保留口播去废话后的非连续片段。

## 2026-10-08：补拍指导闭环
补素材任务不仅记录缺口，还保存 `why`、`reason`、`shoot_or_generate`、`acceptance`。UI 选中任务后直接展示补拍动作和验收标准；完成后重新分析即可自动复核，不自动把缺失事实用虚构素材替代。

## 2026-10-08：补素材自动验收
重新分析时保存上一轮 `variant_footage_gap_tasks`，新一轮覆盖审计完成后用确定性规则逐任务对比。卖点缺口消失则标记“已完成”；仍在缺口中则“仍缺失”；无法稳定映射则“待复核”。不调用 AI，不虚构验收结果。
