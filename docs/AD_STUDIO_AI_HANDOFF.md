# AI 商品广告工厂：独立 AI 接手入口

> 本文件是“完全不知道本项目历史的新 AI”使用的最短接手入口。它不依赖聊天记录、个人记忆或上一位 AI 的口头结论。

## 1. 项目目标

这是一个 Windows 本地的“AI 商品广告工厂”桌面项目。目标是让用户从商品资料/实拍素材开始，经 AI 分析与决策、本地程序编排执行、必要时调用云端生成能力，完成视频生产、事实/视觉/安全检查、成片交付与失败恢复。

产品目标和完整工作流以 apps/ad-studio-desktop/HELP.md 为用户侧说明，以 apps/ad-studio-desktop/PROJECT_LOGIC.md 为内部逻辑地图。

## 2. 架构与强制规则

先读根目录 AGENTS.md。核心原则：
- LLM 负责思考和决策。
- Python 桌面程序负责编排、执行、存储、版本、成本和硬件能力调度。
- 本地设备负责适合本地完成的加工；云端负责本地能力不足或不适合本地执行的高质量生成。
- 任何具体显卡型号都不是系统最低配置或架构边界。
- 修改桌面端代码必须同步更新 HELP.md 和 PROJECT_LOGIC.md，并通过文档同步检查。

## 3. 当前验收进度

以 docs/AD_STUDIO_ACCEPTANCE_PLAN.md 的正式顺序为准：

**A0–A33：既有阶段记录；A34：AI 辅助商品画面对比（待最新 CI 验收）；A35：单镜头局部修复第一阶段已实现，待专项测试/CI 验收。**

不要把历史文档中的旧“下一阶段”文字当成当前状态；以本文件和验收计划中最新的 A31/A32 记录为准。

## 4. 验收计划

唯一阶段顺序入口：docs/AD_STUDIO_ACCEPTANCE_PLAN.md

A32 是既有 AI 接手能力阶段；当前工作先核验 A34 提示词/测试和最新 CI，再验收 A35 单镜头局部修复。接手入口仍应让没有任何本项目聊天历史的新 AI 独立找到：
1. 项目目标
2. 架构
3. 当前进度
4. 验收计划
5. 测试方式
6. 安全边界
7. 下一步工作

## 5. 测试入口

桌面核心测试：python3 -m unittest discover -s apps/ad-studio-desktop -p 'test_*.py'

A32 专项自动化验收：apps/ad-studio-desktop/test_ai_handoff.py

A34 专项回归：apps/ad-studio-desktop/test_short_drama.py 中的 `test_ai_visual_comparison_*`；A35 局部重生成专项回归：`test_product_drama_regeneration_*`

文档同步检查：python tools/check_ad_studio_docs.py --base <base-ref> --head <head-ref>

CI 还会运行前端语法、Python 语法、Typecheck、Engine 和 Risk Controller 测试。

## 6. 安全边界

- 不把 TODO、stub、placeholder 或未适配 Provider 写成已接通。
- 不把模拟数据写成真实投放结果。
- 不凭空生成 CTR、CVR、CPA、ROAS 等真实平台指标。
- 商品事实、禁用词、高风险表达、视觉风险和待复核 AI 镜头必须遵守确定性安全闸门。
- AI 生成镜头默认待复核，未经人工审核不得进入最终成片。
- 真实 Provider/API 的具体接通状态以代码、测试和 HELP 中“当前已知限制”为准。

## 7. 新 AI 的固定接手顺序

**本文件 → AGENTS.md → PROJECT_LOGIC.md → HELP.md → AD_STUDIO_ACCEPTANCE_PLAN.md → 目标代码/测试 → 安全边界**

读完后，先检查当前最新 CI/失败日志和工作区状态，再决定是否继续修改。不得凭聊天记录或上一轮结论直接推进。

## 8. 接手结论

如果上述入口均可访问，且 A32 专项测试能从这些长期文件中独立验证七项信息，则项目具备“无聊天历史接手”的可验证基础。该能力属于项目可维护性/交接能力，不代表真实 AI Provider 或真实投放已经接通。

## 最近一轮接手补充（A36）
当前分支增加了“基于上次 AI 视觉比对结果生成可编辑修正草稿”的首阶段实现，并加强预计费用/旧版本号校验。草稿不会自动通过核验，也不会绕过费用确认。请从当前分支头检查 A36 回归测试和完整 CI；不得将仅有文档同步成功视为全量 CI 通过。


## A37 接手提醒
A37 修复修正草稿中换行符被显示为字面量的问题，并增加真实换行断言。检查当前 head 的 docs-sync 与完整 CI；不可将 docs-sync 单独视为完整测试通过。


## A38：会话接手
项目内 `apps/ad-studio-desktop/SESSION_HANDOFF.md` 是每次新会话继续工作前的首读文件；每轮提交后都要更新其 HEAD、CI 状态和下一步，且不能将 docs-sync 误报为完整 CI。


## A39：分支 CI
CI push 事件现在覆盖所有分支。接手者必须检查当前 SHA 上的完整 `typecheck-and-test`，不能只看文档同步工作流。


## A40：CI 路径失败
最近一次完整 CI 的 Python 语法检查通过，桌面测试因新加的 handoff 检查使用了错误的仓库根路径而失败。已修复测试引用，需等待新 SHA 的全量 CI 结果后再判断。


## A41：CI 文案断言
handoff 路径问题已修复；随后仅剩 1 个文案断言不一致，已对齐测试短语并保留防止夸报完整 CI 的约束。等待下一轮完整 CI 确认。


## A42：最新确认的自动化检查
基准 SHA `443f713cd3721eab528eb9bb17faf599d55ef3ce` 的完整 CI 与 docs-sync 均已成功；测试路径与文案断言问题已修复。新 AI 仍需查询当前 HEAD 是否等于该 SHA，若不一致则重新核实。


## A43：单镜头重生成失败恢复
重生成前把上一份有效视频路径保存在 `Shot.previous_video_path`。Provider/本地裁剪失败时恢复旧视频；进程中断后项目恢复会清理临时文件并恢复旧视频。新增 `test_a43_*` 回归测试。本次提交后的 CI 必须按新 SHA 查询，不能沿用 A42 的旧绿灯。


## A44：短剧镜头映射防漂移
项目列表的 `Shot.index` 会因补镜头插入而变化，不能用它直接当源短剧 storyboard 的数组下标。新项目保存 `short_drama_shot_number`；旧项目只做唯一标题/集数回退，歧义时停止操作。A43 已在 SHA `9e340604f9e71d020a4ba6dec5cfb57c154346c9` 的完整 CI 和 docs-sync 通过；A44 当前提交仍待新 SHA 验收。


## A45：失败恢复 UI 状态对齐
`ProductionStore` 在失败后恢复上一版时，UI 必须保留“已保留上一版本”状态；只有恢复标记、存在的路径和非空文件同时满足才显示旧版可用。A45 增加 `generation_failure_ui_state()` 回归测试，最新 SHA 的 CI 与 docs-sync 需重新确认。
