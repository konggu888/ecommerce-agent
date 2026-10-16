# 【交接一致性修复｜权威状态与连续性规则｜2026-10-16】

> **这是接手协议和最近核实的历史基线，不是替代实时 GitHub 查询的静态快照。** 每次新会话必须先查询分支 HEAD、PR #32 和该 HEAD 的四项工作流；无论本段 SHA 是什么，都不得直接假定它仍是 HEAD。若 HEAD 不同，先识别新增提交及状态，更新交接记录后再继续任务。严禁从历史快照推断当前状态。

- 仓库：`konggu888/ecommerce-agent`
- 工作分支：`feat/product-drama-visual-review`
- 最近一次确认的代码/测试基线：`55f0202da0db941c3b45ddaa55fc197c10c6d769`（DEDUP-013，A57/A60 成本恢复保存/重载断言）；该基线四项检查曾成功：CI Push #38788160714、CI PR #38788169343、docs-sync Push #38788160480、docs-sync PR #38788169267。它不是后续文档提交的 CI 证明。
- 此后只为修复交接连续性，已更新进度看板、AI handoff、SESSION_HANDOFF；上次查询看到的交接元数据提交为 `d92128a07b0b1e8e2439ce7fd06b27a313abca49`，其 CI #2225 与 docs-sync #1904 当时为 in_progress。由于本段更新本身会产生新的文档提交，**当前 HEAD 与检查状态必须重新实时查询**；不能把这些 in_progress 结果沿用到新 SHA。
- PR #32：最后核实为 Open、未合并；新会话必须重新查询。禁止合并，除非用户明确授权。
- DEDUP-013：A57「无账本旧项目恢复后保存/重载仍保留项目/镜头成本」与 A60「failed-only 账本恢复后保存/重载仍保留项目/镜头成本及成本分类汇总」断言已补强。曾发生一次 docs-sync Push 失败，后续补齐要求文档并修复；保留失败历史，不得抹去。A57、A60、A99 仍为 `not_audited`。A99「成功账本权威后清除未计费兄弟镜头陈旧成本」为独立合同，不与 A57/A60 合并。
- **当前唯一下一步：**审计并收紧 `CapabilityRouter.decide_asset/decide_video` 的本地/云端回退：明确用户如何允许/拒绝目的地变更；用 mock 覆盖本地服务不可用、云端候选可用/不可用、用户拒绝后调用计数为 0，并验证费用确认先于 Provider 调用。随后补未知费用语义和 endpoint 历史追溯。不新增 A113+，PR #32 不合并。
- **上一阶段记录：**A52/A55 已完成部分源码/测试证据映射，但仍为 `not_audited`；详细缺口见总进度看板。
- 不新增 A113+；不删除、合并或重编号 A0–A112；全局语义去重和完整代码/测试审计仍未完成；整体完成率关闭。
- Windows 真机、真实素材、真实 Provider/实际扣费与账单、剪映现场、真实投放/商业效果继续暂缓。自动化测试和 CI 绿灯不等于真实环境验收完成。
- **防止再次断档：**当前状态唯一权威入口是本文档顶部和 `docs/AD_STUDIO_PROGRESS_DASHBOARD.md` 顶部。AI handoff 与其他历史记录只作背景，不得维护互相冲突的“下一步”。新会话必须先读本文、查 HEAD、PR、四项工作流，再核对 dashboard；如果某项无法查询，明确写“未核实”。文档/代码每次提交后都必须重新验证其自身 SHA 的 CI Push、CI PR、docs-sync Push、docs-sync PR，分别记录成功/失败/运行中/未运行。

---

# 当前接手状态｜PLAN-003 DEDUP-013 已验证｜2026-10-16

- 分支 `feat/product-drama-visual-review`；已验证基线 `c8797e4b8d65580a7c124903d4a9c8f6e188f41a`；PR #32 Open/unmerged。
- 上一修复 SHA 的四项工作流均成功：CI Push 38787892022、CI PR 38787902592、docs-sync Push 38787891485、docs-sync PR 38787902562。
- DEDUP-013 增加 A57 无账本旧项目、A60 failed-only 账本恢复后的保存/重载断言；CI 已运行通过。初始 docs-sync Push 失败已通过补齐 AGENTS.md、HELP.md、PROJECT_LOGIC.md 修复。
- A99 成功账本清除陈旧兄弟镜头是独立合同；A57/A60/A99 均未正式验收，真实 Provider 账单、Windows 真机、真实素材继续暂缓。
- 下一步继续 PLAN-003 有界源码/测试审计。任何新提交都必须重新检查四项 CI/docs-sync。不新增 A113+，不改 A0–A112，不合并 PR #32；整体完成率关闭。

---


---


---


---


---


---


---

- 源码/测试审计基线 `c77704d86d6131d13501448af76ce24afc56ad7b`；最后一次明确核验成功的工作流 HEAD `47479d41725cf726e1543524bda012fee8bdf890`（CI PR 38730727069 / docs-sync PR 38730727058）成功；本轮文档更新后的 HEAD `143d01f87c3161deee04cd2d3c821b1e915084d1`（CI PR 38731016045 / docs-sync PR 38731016172）也成功。Push 未独立核实。# 【历史快照｜PLAN-003 A110–A112 部分证据映射｜2026-10-15】

- 唯一权威进度：`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`；PR #32 Open/unmerged。
- 源码/测试基线 `c77704d86d6131d13501448af76ce24afc56ad7b`；文档更新前最近 HEAD `a9fe2d93d186bac79dafee294e518209d963f420` 的 CI PR / docs-sync PR success（38730727069 / 38730727058），Push 未独立核实。
- A110–A112 重新审计后均标记 partial_evidence_mapping/not_audited，不继承历史 automation_passed。缺口：A110 CTA 下限专测与生产集成；A111 最终 build_final 整链测试/真实 FFmpeg；A112 字幕 applied/fallback 生产级回归。真实素材、Windows、音画与字幕可读性继续暂缓。
- A0–A112 已无新编号任务；下一步回到 PLAN-003 全量语义去重、证据冲突核对和未审计范围复核。不得新增 A113+，不合并 PR #32。

---

# 【历史快照｜PLAN-003 A100–A104 证据映射补充｜2026-10-15】

- 唯一权威进度：`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`；PR #32 Open/unmerged。
- 源码/测试审计基线：`c77704d86d6131d13501448af76ce24afc56ad7b`。CI PR [38729441932](https://github.com/konggu888/ecommerce-agent/actions/runs/38729441932) 与 docs-sync PR [38729441851](https://github.com/konggu888/ecommerce-agent/actions/runs/38729441851) 成功；Push 工作流未独立核实。
- A100–A104 已完成源码/专项测试证据映射，但正式验收均保持 `not_audited`。实际 FFmpeg 渲染、Windows 真机、真实素材和视听质量仍暂缓；A102 尺寸放大不等于 AI 超分；A104 filter graph 目前由 mock 断言。
- 下一批 A105–A109。文档提交后先核验最新 SHA 的四项 CI/docs-sync。只推进 PLAN-003，不开发新功能、不新增 A113+、不删/合并/重编号 A0–A112。

---

# 【历史快照｜PLAN-003 A95–A99 部分证据映射｜2026-10-15】

- 唯一权威进度：`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`；PR #32 Open/unmerged。
- 本轮源码/测试审计基线：`c77704d86d6131d13501448af76ce24afc56ad7b`。源码 blob `e53968f47a6b8fd23df773dbd3a4ad553753e1e0`；测试 blob `357c54dad99f61b99891bcc365dd2f9efc1a1009`。该基线 CI PR 与 docs-sync PR success；Push 工作流未独立核实。文档提交后必须重新核验最新 SHA。
- A95–A99 仅完成部分源码/测试映射，正式验收均为 `not_audited`。关键未覆盖项：A95 目录/权限异常；A96 修复后保存重载/并发修改；A97 更多中断分支；A98 普通待生成镜头误报；A99 失败账本与旧项目无成功账本两类成本边界。
- 下一批 A100–A104。继续只做 PLAN-003，不开发新功能、不新增 A113+、不删/合并/重编号 A0–A112。Windows 真机、真实素材、Provider/扣费、剪映现场和商业效果验收继续暂缓。

---

# 【历史快照｜PLAN-003 A90–A94 部分证据映射｜2026-10-15】

- 唯一权威进度：`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`；PR #32 Open/unmerged。
- 源码/测试审计基线 HEAD `a6e052fa7edefa7e2fb794166684547436ff90f6`；本轮文档更新后的最新 HEAD `64857c4f93a4b648c207328299e690f1ef932dca`。源码 blobs：production.py `e53968f47a6b8fd23df773dbd3a4ad553753e1e0`、short_drama.py `2506410d9621840ec34464fce1fa2746c7d798f4`；测试 blobs：test_desktop.py `357c54dad99f61b99891bcc365dd2f9efc1a1009`、test_short_drama.py `2995b5764f7a86ee8c274b6359ff2f09cdf7a288`。
- 该 SHA 的 CI PR 与 docs-sync PR 成功（runs 38728582030 / 38728581662）；Push 工作流对本 SHA 尚未独立核实。文档提交后必须重新检查最新 SHA。
- A90–A94 仅部分证据映射，正式验收状态保持 not_audited。下一批 A95–A99。台账覆盖指标和每项边界见总进度看板。
- 不开发新功能、不新增 A113+、不删/合并/重编号 A0–A112；Windows 真机、真实素材、Provider/扣费、剪映现场和商业效果验收继续暂缓。

---

# 【历史快照｜PLAN-003 A85–A89 部分证据映射｜2026-10-15】

- 唯一权威进度：`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`；PR #32 保持 Open / unmerged。
- 本轮开始 HEAD `2b92072a1dd5335fe803955ffca11881ebf2dec3`；源码/测试快照 `4063ba5a452c0c883ff39c8ea1ce33499a80eaf4`，`short_drama.py` / `test_short_drama.py` blobs 分别为 `2506410d9621840ec34464fce1fa2746c7d798f4` / `2995b5764f7a86ee8c274b6359ff2f09cdf7a288`。该快照的 CI Push/PR 与 docs-sync Push/PR 四项均 success；本轮文档提交后必须重新核验最终 SHA 的四项。
- A85–A89 已完成部分源码/测试映射，不等于正式验收：A85 人物长期状态；A86 状态变化因果闭环；A87 可观察表演；A88 跨人物状态依赖；A89 跨集演员/场景锁定。详细正反例和缺口见总进度台账。
- 台账覆盖数：需求复核 113；source/test/CI/workflow 指针 90；任意 evidence 102；路线图映射 113/113；源码/测试快照绑定 32；最终文档 HEAD 精确绑定 0；完整代码/测试审计 0；完整审计 0；语义去重未完成。权重和总体完成率关闭。
- 不开发新产品功能，不新增 A113+，不删/合并/重编号 A0–A112。真实素材、Windows、Provider/扣费、剪映现场与商业效果验收继续暂缓。
- 下一批 A90–A94；先核验文档提交后最新 HEAD 的四项 CI/docs-sync，再继续。

---

# 【历史快照｜PLAN-003 A80–A84 部分证据映射｜2026-10-15】

- 唯一权威进度：`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`；PR #32 保持 Open / unmerged。
- 源码/测试快照 `4063ba5a452c0c883ff39c8ea1ce33499a80eaf4` 的 `short_drama.py` / `test_short_drama.py` blob 分别为 `2506410d9621840ec34464fce1fa2746c7d798f4` / `2995b5764f7a86ee8c274b6359ff2f09cdf7a288`；该 SHA 四项 CI/docs-sync 均 success。文档提交后必须重查最新 HEAD 四项。
- A80–A84 已完成部分映射，正式验收未完成：关系变化/后果、人物状态连续性、信息时间线、承诺/误解/行动结果、跨集承接事项。主要剩余风险是正向路径不足、语义字符串匹配局限，以及最终集/保存重载等边界。
- 台账覆盖数：需求复核 113；source/test/CI/workflow 指针 85；任意 evidence 97；路线图阶段映射 113/113；源码/测试快照绑定 27；最终文档 HEAD 精确绑定 0；完整代码/测试审计 0；完整审计 0；语义去重未完成。权重和总体完成率关闭。
- 不开发新产品功能，不新增 A113+，不删/合并/重编号 A0–A112。真实素材、Windows、Provider/扣费、剪映现场与商业效果验收继续暂缓。
- 下一批 A85–A89。先核验最终文档 HEAD 的 CI Push、CI PR、docs-sync Push、docs-sync PR 全部完成且 success。

---


---


---


---


---


# AI 接手当前状态｜PLAN-003 A50–A53 部分证据映射｜2026-10-15

- 唯一权威进度与下一项：docs/AD_STUDIO_PROGRESS_DASHBOARD.md。本轮 A50–A53 只完成部分路线图/源码/测试映射，不是正式验收。
- A50 视频提示词真实换行、A51 费用预估校验、A52 失败 Provider 尝试成本去重、A53 零字节旧视频恢复均归阶段1「可靠的生产底座」。重叠关系只登记不裁决，不合并 ID。
- 证据边界：A50 是捕获请求的确定性测试；A51 是费用值 helper 校验；A52 是本地 ledger 的失败/成功重试夹具；A53 是零字节 previous_video_path 恢复测试。均不证明真实 Provider、实际扣费、Windows 或真实媒体行为。
- 证据快照与最终文档 HEAD 不同，因此 4 个任务绑定源代码/测试快照，不代表绑定当前最终 HEAD；最终 HEAD 精确证据任务数保持 0。
- 指标：需求文本级复核 113；source/test/ci/workflow 指针记录 54；任意 evidence 记录 66；路线图映射 97；待映射 16；当前 HEAD 精确证据 0；完整代码/测试审计 0；完整审计 0；语义去重未完成。不得发布总体完成率、不得赋权。
- 审计快照 `c14b9bf10ae80379c45e80b42224722aab8c31d7` 四项 CI/doc-sync 均 success；文档提交后重新检查最终 HEAD 四项。下一批 A54–A57。PR #32 保持 Open/unmerged；不新增 A113+，不开发产品功能，真实环境验证继续暂缓。
---

- 仓库/项目：`konggu888/ecommerce-agent/apps/ad-studio-desktop`；分支 `feat/product-drama-visual-review`；PR #32 保持 Open / unmerged。
- 唯一权威当前任务、下一项、状态和进度：`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`。当前是 PLAN-003 全量跨来源语义去重、状态冲突裁决与依赖/证据边界复核；A0–A112 台账和分批静态映射已存在，不重建、不重复从 A50 开始。当前不开发产品功能。
- 执行规则：`docs/AD_STUDIO_EXECUTION_CONTROL.md`；战略阶段与退出条件：`docs/AD_STUDIO_PRODUCT_ROADMAP.md`；正式范围：`docs/AD_STUDIO_ACCEPTANCE_PLAN.md`；验收方法：`docs/AD_STUDIO_ACCEPTANCE_SOP.md`。
- 最近一次已完整核验通过的基线：`8e2a714abfc77e6ce9f7e136a0ba41195f2c8fae`；该 SHA 的 PR-triggered CI 与 docs-sync success，Netlify deploy-preview success。之后又提交了审计/帮助/逻辑文档更新，因此这不是当前 HEAD 的通过证明。接手时必须实时查询最新 HEAD、CI、docs-sync 与部署状态；Push-triggered CI/docs-sync 未独立核实前必须明确注明。
- 下方旧执行快照仅为历史证据，不能作为当前“下一项”指令。遇到冲突先登记到总进度台账，不自行选择旧任务、不扩展范围。
- 禁止删除/重编号 A0–A112；规范化台账、去重、依赖和证据审计完成前不赋权、不计算总体完成率。真实环境/Provider/扣费/剪映/投放验证继续暂缓。
- **七层结果证明标准已纳入全项目证据规则**：软件运行、功能行为、端到端流程、普通用户可用、商品表达真实安全、商业成片质量、真实商业效果；详细定义和禁止替代关系见总进度台账及执行控制协议。台账规范化时逐项映射，不新增正式验收 ID。
- **用户自由度已纳入 PLAN-003 台账映射要求**：选择自由、控制自由、知情自由、撤回/纠正自由。预算/数据目的地确认必须先于任何可能收费或外发数据的云端调用，包括 LLM 分析/规划；取消后所有外部调用计数必须为 0。不得静默跨 Provider/本地转云端，不得把未知费用当作零成本。此为既有合同的严格解释与审计维度，不新增正式验收 ID，不启动产品功能开发。

---

# 【历史接手快照｜UXS-2 用户旅程证据映射｜2026-10-15｜不可覆盖总进度台账】

- 当前审查计划：`docs/AD_STUDIO_USER_EXPERIENCE_SAFETY_AUDIT.md`，第 3A 节已记录创建入口、商品输入、费用授权顺序、项目持久化的首轮静态映射。
- 重要待裁决的合同/证据冲突：`App.create()` 在显示 `AI创意与项目预算确认` 前调用 `ModelRouter.create_plan/create_plans`；`ModelRouter.create_plan()` 对九个创意阶段调用 `complete_json()`。HELP/PROJECT_LOGIC 允许确认前进行 AI 分析，但用户费用授权是否覆盖收费的规划模型调用尚未明确。若所有收费云端模型调用都须先确认，则是 P0 候选阻断；若仅限制视频/资产生成 Provider，则需核实规划调用费用是否披露/计入预算。需进一步核对路由/计费并映射到 A0/A2 与既有正式合同；不开发产品功能、不新增正式编号、不声称已发生实际扣费。
- 已查专项测试线索：布局 AST、商品解析器失败/回退、预算计算、项目保存/加载与项目隔离；未找到直接调用 `App.create()` 的 `test_desktop.py` 测试。完整模拟交付测试不覆盖创建前费用确认顺序。
- 本轮开始基线 `3bd083e73ea51aec26b2ab66c755aa6c83a929cf` 的 PR CI `38695479000` 和 PR docs-sync `38695478983` success；Push-triggered 两项未独立核实。文档更新后以 GitHub 实时 HEAD 为准重查当前 SHA 工作流。
- 上述 UXS-2“下一项”属于历史快照；当前执行顺序只看 `docs/AD_STUDIO_PROGRESS_DASHBOARD.md` 顶部。当前任务为 PLAN-003 全量跨来源关系与状态冲突裁决；全量审计完成前不计算总体完成率。
- 保持 `code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false`。Windows 真机、真实素材、真实 Provider/扣费、剪映现场、真实投放/商业效果继续暂缓；PR #32 不合并。

---

# 用户体验与产品安全完整性审查更新｜2026-10-15

本轮用户提出：现有规划可能没有完整覆盖用户体验、真实用户使用流程与功能安全。已将该议题纳入 PLAN-003 的规划完整性审查，不开发新产品功能。

- 审查计划：`docs/AD_STUDIO_USER_EXPERIENCE_SAFETY_AUDIT.md`。
- 当前阶段 UXS-1：确立八个审查维度、从首次启动到交付的用户旅程、P0–P3 风险分类、与 A0–A112 的映射规则和退出条件。
- 后续：UXS-2 用户旅程证据映射 → UXS-3 安全与跨功能依赖矩阵 → UXS-4 与 A0–A112 及路线图/SOP/未来备忘/台账跨来源裁决 → UXS-5 统一纳入规划。
- 本轮开始基线 `04d27368a305d37ab3a42a82f96e42fc756463da`；CI Push `38693984581`、CI PR `38693988861`、docs-sync Push `38693984682`、docs-sync PR `38693988917` 均 success。文档提交后必须重查新 SHA 四项工作流。
- PR #32 保持 Open / unmerged；Windows 真机、真实素材、Provider/实际扣费、剪映现场、真实投放/商业效果仍暂缓。
- A0–A112 静态映射不是正式验收。保持 `code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false`，不分配权重、不计算整体完成率。

---



## PLAN-003 审计进度更新｜A100–A112｜2026-10-15

A100–A112 已完成静态代码/测试证据映射：淡出时间窗、变速音画同步、最低 1080P 输出、淡入/淡出、xfade/acrossfade、pacing、商业角色决策、运行时时长、字幕密度、音乐节拍、内容保护、逐边界局部回退和 SRT cue 时间窗。已定位专项测试文件：test_postprocess.py、test_ffmpeg.py、test_creative_engine.py、test_subtitles.py、test_music_sync.py、test_desktop.py。

本批全部仅部分证据映射，不等于每项正式验收完成；1080P 尺寸放大不等于 AI 细节增强，真实素材/Windows/真实音乐口播/剪映与商业效果仍暂缓。台账 `code_test_evidence_reviewed_ids=113`，完整证据审计仍为 0、语义去重未完成、总体完成率关闭。下一步进入 A0–A112 与路线图、未来备忘、SOP、任务登记表、执行控制的全量跨来源去重/状态裁决。PR #32 保持 Open / unmerged。
# 【PLAN-003 当前进度｜2026-10-15｜本段优先于下方历史记录】

- 最新完整核验基线（本次接手前）：`1fd6d08dac970cb7886c59239b05c4f6e2128cf9`；CI Push `38691577983`、CI PR `38691582839`、docs-sync Push `38691577999`、docs-sync PR `38691582806` 均 success。PR #32 保持 Open / unmerged；任何新提交后必须重新核验四项结果。
- A0–A5 证据映射（未正式验收）：A0 `App.create()` 入口存在，缺专门启动/创建 UI 操作覆盖；A1 缺任务级稳定性矩阵；A2 有项目隔离与 save/load 测试，缺直接 `App.create()` 编排测试；A3 有布局 AST、三类任务策略和 task_type 持久化测试，完整 UI 流程未验收；A4 有扫描、不可解析素材记录、重复素材评分、废片归档及保护引用源文件测试，覆盖矩阵仍不完整；A5 已实现关键帧提取/视觉清单，但已检查的 desktop `test*.py` 未发现 `extract_keyframes()` / `build_visual_manifest()` 专项测试，视觉分析失败回退也待核验。

---

---

# 【历史接手指令快照｜规划体系优先｜2026-10-14｜当前执行顺序以总进度台账为准】

先读取 `apps/ad-studio-desktop/SESSION_HANDOFF.md`，再读本文件、`docs/AD_STUDIO_EXECUTION_CONTROL.md`、`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`、路线图、AGENTS、HELP、PROJECT_LOGIC、验收计划与 SOP。
规划体系实施前 HEAD：`7cfabb23e9ab0c05c6189d31dcf6b7410f7934c7`，四项 CI/doc-sync 均 success；新提交后必须重新查询最新 HEAD 与四项状态。
PR #32 保持 Open / unmerged。真实 Windows、素材、Provider/扣费、剪映现场、真实投放/商业效果继续暂缓。
A112 已完成自动化阶段。旧正文中的“下一项 A112”等均为历史内容。
当前唯一下一项 PLAN-003：全量盘点 A0–A112、路线图、未来备忘与 SOP 检查点，去重并核验状态/证据。盘点完成前不发布总体完成百分比，也不推进新的产品功能。
每轮一个主要任务；任务外非阻断想法登记待办，不顺手实现。

---

# 【历史执行快照｜A111/A112｜2026-10-14｜已被文件顶部 PLAN-003 当前状态取代】

- 仓库：konggu888/ecommerce-agent；分支：feat/product-drama-visual-review；PR #32 保持 open/unmerged。
- 当前 HEAD：fc445e75e40fd34e5b16868369700e685e2db276。A111 逐边界局部音乐卡点已进入最终生产规划函数；相邻边界冲突时局部撤销位移、保留其他安全边界，保持总时间轴长度；审计记录调整/回退边界序号。
- 最新 HEAD 四项检查均 success：CI Push 38567371929、CI PR 38567378825、docs-sync Push 38567371969、docs-sync PR 38567379230。
- 首轮 A111 CI 曾失败 3 个旧断言，根因是断言仍要求整组回退，与 A111 局部回退设计冲突；修复测试预期与审计原因后，最终 SHA 四项检查全部成功。没有隐瞒中间失败。
- 代码、测试与八份强制文档/路线图已同步。此处“下一项路线图 A112”是已被顶部 PLAN-003 当前状态取代的历史记录；不得据此继续开发 A112。
- Windows 真机、真实素材、真实 Provider/扣费、剪映现场、真实听感和商业效果仍暂缓。PR #32 不合并。

---

---

---

---

---

---

# 【当前接手状态｜2026-10-14】

> 本段是新 AI 接手时的当前优先级入口；下文历史记录用于背景参考，遇到冲突以本段和 GitHub 当前状态为准。

## 当前路线图指令（2026-10-14，强制）
- 产品路线与阶段退出条件：`docs/AD_STUDIO_PRODUCT_ROADMAP.md`。
- 历史主攻阶段记录：商业级剪辑决策层；A109“音乐节拍与画面切点真实联动”已提交自动化实现。此旧记录不覆盖文件顶部 PLAN-003 当前状态。先重新核验最新 HEAD、CI 与 docs-sync；如果失败，先读日志并修复，不能直接推进后续任务。
- 先核验最新分支 HEAD、PR #32、完整 CI 与 docs-sync Push/PR 四项状态；当前记录的旧 SHA 不能代替新 SHA 的验证。
- 代码/测试更新必须同一提交同步八份规则/产品/验收/接手文档；路线图发生变化时同时更新路线图文件。
- PR #32 不合并；Windows 真机、真实素材、真实 Provider/扣费、剪映现场和真实投放数据验收继续暂缓。

- 仓库：`konggu888/ecommerce-agent`；项目：`apps/ad-studio-desktop`。
- 分支：`feat/product-drama-visual-review`；PR #32 保持 open/unmerged，不得擅自合并。
- 商业剪辑焦点定位代码提交：`fe3dcfde8e78f7d5d079fcbc1ed99d6265a79dbb`。该 SHA 的 CI push、CI PR、docs-sync push、docs-sync PR 四项均已 success；任何新提交都必须重新核对最新 SHA。
- 用户已明确要求暂停费用对账/单镜头重试保护线，优先推进未来路线图第 5 项“商业级剪辑决策层升级”。
- 新增硬性要求：最终成片最低 1080P 级（9:16 1080×1920、16:9 1920×1080、1:1 1080×1080）。A102 将最终拼接结果转码到该尺寸并由 ffprobe 检查；尺寸放大不等于 AI 细节增强。A102 代码已准备，需以最新 SHA 的 CI 与 docs-sync 四项运行结果为准。
- 已修复 `process_shot()` 忽略 AI 焦点的问题：`focus_x/focus_y` 是缩放后源画面中的主体/视觉焦点归一化位置，不是裁切窗口偏移比例；系统在合法边界内尽量将焦点放到输出画面中心。新增回归测试验证实际 FFmpeg `-vf` 参数及异常输入处理。
- A106 已加入基于分镜文本的商业角色默认决策；A107 修复推断时长未复制到运行时 Shot 的执行断点，现由 `runtime_shot_editing_fields()` 将 duration/pacing/speed/transition 一起传入生产镜头。最新基线 HEAD `884c45dd8524abf4c4ebf7ee7fc8daa67987f686` 的 CI Push/PR 与 docs-sync Push/PR 均 success；A107 仍待本轮提交后重新核验。规则只基于文本，不代表视觉语义理解。
- 当前仍未完成商业剪辑整体能力。后续继续推进真实画面驱动节奏、镜头衔接、字幕密度、音乐卡点、商品展示节奏及剪后反馈。
- 接手必做：重新查询分支 HEAD、PR #32、最新 SHA 的 CI 和 docs-sync；在仓库可用时运行 `python3 -m unittest discover -s apps/ad-studio-desktop -p 'test_*.py'` 和 `python3 -m compileall -q apps/ad-studio-desktop/ad_studio`。没有实际执行就不能声称本地测试通过。
- Windows 真机、真实 Provider/扣费、剪映现场和真实成片视觉验收继续暂缓。CI 绿灯不代表商业质量已验收。

---

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

产品战略顺序唯一以 `docs/AD_STUDIO_PRODUCT_ROADMAP.md` 为准；专项验收项与证据以 `docs/AD_STUDIO_ACCEPTANCE_PLAN.md` 为准。不要把下方历史记录或旧“下一步”当作当前执行顺序。

- 当前分支：`feat/product-drama-visual-review`；PR #32 open/unmerged，不得合并。
- 当前已核对基线：`464977a54e9784fff375ffe081985624688261e9`；CI Push `38692014399`、CI PR `38692013047`、docs-sync Push `38692014528`、docs-sync PR `38692013000` 四项均 success。
- 当前唯一主攻：PLAN-003 全量任务盘点、跨来源去重和当前 HEAD 代码/测试证据审计；商业级剪辑开发暂缓，待 PLAN-003 完成后再复核阶段退出条件。
- 历史兼容快照（仅保留旧 handoff 测试所需文字，不代表当前状态）：A34：AI 辅助商品画面对比（待最新 CI 验收）；A35：单镜头局部修复第一阶段已实现。当前实际进度以本节上方路线图指令、当前代码与最新 CI 为准。
- 下一项具体工作：继续 PLAN-003，完成全量跨来源重复/状态映射，并按正式台账逐项核验代码、专项测试、失败路径和当前 SHA 证据；不得据此启动新的产品功能。
- A108 只覆盖按实际镜头时长生成字幕时间轴、长文案标点分段、短镜头减少切换并提示信息密度风险；不代表口播语义对齐、真实画面可读性或商业成片质量已验收。
- 最低输出尺寸为 1080P 级（9:16 1080×1920、16:9 1920×1080、1:1 1080×1080）；放大输出不等于恢复真实细节。
- Windows 真机、真实素材、真实 Provider/实际扣费、剪映现场及真实投放数据验收继续暂缓。

## 4. 验收计划与路线图

- 产品阶段、先后顺序、阶段退出条件：`docs/AD_STUDIO_PRODUCT_ROADMAP.md`。
- 正式专项验收范围和清单：`docs/AD_STUDIO_ACCEPTANCE_PLAN.md`。
- 验收操作规程：`docs/AD_STUDIO_ACCEPTANCE_SOP.md`。
- AI 接手时必须独立找到：项目目标、架构、当前进度、当前路线、测试入口、安全边界、下一项任务。
- 进入下一阶段前先确认当前阶段退出条件；不得把“功能代码存在”或“CI 绿灯”视为商业成片质量验收。

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

**apps/ad-studio-desktop/SESSION_HANDOFF.md → 本文件 → docs/AD_STUDIO_PRODUCT_ROADMAP.md → AGENTS.md → PROJECT_LOGIC.md → HELP.md → AD_STUDIO_ACCEPTANCE_PLAN.md → AD_STUDIO_ACCEPTANCE_SOP.md → 目标代码/测试 → 安全边界**

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


## A46：编辑镜头路径旧版保护
编辑窗口此前绕过安全版本切换，直接清空活动视频路径并递增版本。现改为调用 `mark_regenerate()`，让旧版视频文件路径进入 `previous_video_path`，以便失败/中断恢复。新增测试检查 UI 编辑回调不再执行破坏性赋值。此项须以本次新 SHA 的 CI 与 docs-sync 为准。


## A47：素材解析失败保护
素材解析本身可能触发资产生成，现已纳入 `_render_with_provider()` 的失败恢复边界；解析异常时恢复旧版视频且不继续调用视频 Provider。输出替换不先删除目标文件。A47 自动化测试已添加，等待本次最新 SHA 的完整 CI 与 docs-sync。


## A48：实拍裁剪安全输出
实拍素材剪辑已改为临时文件生成、非空校验、成功后原子替换；失败时不直接删除正式输出。A48 新增裁剪失败回归测试。当前提交的 CI 与 docs-sync 需按最新 SHA 查询。


## A49：多段实拍临时文件清理
恢复流程现识别普通 `.part.mp4` 和多段裁剪的 `.partNN.mp4` 临时文件；源素材缺失时也会清理分段残留并恢复旧版。新增两类回归测试，当前 SHA 的 CI 与 docs-sync 待确认。


## A50：视频提示词换行回归（待 CI）
A47 的异常边界重构意外将 prompt 拼接改成字面量反斜杠+n；已恢复真实换行并增加捕获 Provider 请求文本的回归测试。A49 在 SHA 953e40694aa2a28b2d164fc49800c639b45bebb8 的完整 CI 与 docs-sync 均成功；A50 新 SHA 的完整 CI/doc-sync 必须重新查询。


## A50：视频提示词换行回归结果
提示词中的标题、画面、文案已恢复为真实换行；新增捕获 Provider 请求内容的回归。代码 SHA `58de7ce984cf9df73bad2c99444d75a0624059c3` 的完整 CI 与 docs-sync 均成功（CI https://github.com/konggu888/ecommerce-agent/actions/runs/38121500267；docs-sync https://github.com/konggu888/ecommerce-agent/actions/runs/38121500259）。真实 Provider 的实际提示词效果仍待现场验收。


## A51：费用确认前置校验
新增局部重生成报价校验，拒绝非数字、NaN/无穷、负数和空值，避免显示无效费用。必须查询本次最新 SHA 的 CI/doc-sync 后再标记自动化验收通过。


## A52：失败尝试账本与成本去重（待 CI）
Provider 调用失败会生成失败尝试记录，但失败报价不计入实际花费；成功重试单独记账，实际成本只按成功记录汇总。新增失败+成功重试回归。当前新 SHA 的完整 CI 与 docs-sync 必须重新查询；真实 Provider 账单对账仍未验证。

## A53：零字节旧视频恢复边界（待当前 SHA CI）
`recover_project()` 现在只恢复真实存在且非空的上一版视频。上一版文件缺失或为零字节时，清空无效路径并把镜头列入 `missing_media`；回归测试验证状态、路径和重载结果。必须以当前 HEAD 的完整 CI 与 docs-sync 结果决定自动化验收状态。

## A54：活动视频零字节边界（待当前 SHA CI）
恢复流程现检查活动 `video_path` 是否真实存在且非空。活动视频为零字节时，优先恢复有效的上一版；无有效上一版则清除路径并标记待重新生成。新增回归测试覆盖这两条分支，必须按当前 HEAD 查询完整 CI 与 docs-sync。


## A55：成本账本故障保护
Provider 已生成有效视频后，成本账本写入异常不能被当成 Provider 生成失败。新输出应保留，镜头标记“已生成（成本待核对）”，并记录核账步骤；人工先核对账本是否已有成功行，避免重复计费。A55 仍需以当前 SHA 的完整 CI 与 docs-sync 为准。


## A56：修复 A55 引入的提示词回归（待 CI）
A55 的 Provider/成本异常边界重构再次引入了字面量反斜杠+n。SHA 18b958a269757781af4f062211d2a54485658e6e 的 CI 因 A50 提示词回归失败（210 项测试中 1 项失败）。当前修复将分隔符恢复为真实换行；本次新 SHA 的完整 CI 与 docs-sync 仍待确认。

## A57：成本待核对界面保护（待当前 SHA CI）
如果视频已成功生成但成本记账异常，`generate_shot()` 不得显示正常的“项目实际累计”金额。待核对状态显示专门警告，要求先检查 `usage-ledger.json` 和恢复记录；正常成功路径继续显示累计成本。新增静态 UI 回归测试，需按当前 SHA 确认 CI/doc-sync。


## A57：打开项目自动恢复与成本对账（待 CI）
之前 recover_project() 只有后端方法，没有被“打开已有项目”界面调用。现在打开时先执行恢复并显示恢复摘要；恢复时按成功账本重建项目/镜头实际成本，同时兼容无账本历史的旧项目。新增 A57 自动化测试，本次 SHA 的完整 CI/doc-sync 待确认。

## A58：商品画面对比输入证据校验（待当前 SHA CI）
视觉对比现在在模型调用前拒绝空参考图、非图片参考文件、空生成文件及不支持的文件格式（未知生成格式）。支持常见图片和明确的视频扩展名；失败输入不会调用模型，也不应修改核验状态。新增回归测试，必须按最新 SHA 检查完整 CI 与 docs-sync。

## 最新自动化验收基准（2026-10-11）
- 当前代码与文档基准 SHA：`8773905c7293c76309938e633e761206ca3447ca`。
- 完整 CI：success，运行 `38122183446`：https://github.com/konggu888/ecommerce-agent/actions/runs/38122183446
- 商品视觉输入校验代码提交 `58e9b106a07151b0a9c1855f8d7599e8d9fc9a48` 的 docs-sync：success，运行 `38122132231`：https://github.com/konggu888/ecommerce-agent/actions/runs/38122132231
- A55–A58 自动化阶段通过；真实 Provider/账单、Windows 真机、真实素材与商业成片验收仍未完成。
- PR #31 保持 open/unmerged。后续任何代码变更仍需重新查询最新 SHA 的完整 CI 与 docs-sync。


## A60：失败-only 账本保护（待 CI）
A57 成本重建初版把“存在任何账本行”当作可重建依据，可能让仅有失败行的旧项目成本归零。现改为至少存在成功记录才重建；失败-only 项目保留原有项目/镜头成本与分类摘要。新增 A60 回归测试，本次 SHA 的完整 CI/doc-sync 待确认。


## A59：成本汇总单一事实源
项目实际成本以 usage ledger 的成功记录汇总为准，禁止对可能过期的项目总额做增量累加。失败尝试的报价单价不计入实际花费；同步检查 cost_estimate.actual 与 actual_cost_rmb。A59 的 CI/doc-sync 必须以最新 SHA 结果为准。


## A59/A60 自动化结果
A59 项目成本总额以成功用量账本汇总为准，A60 失败-only 账本不清零旧项目成本；两项均在 SHA `cd6c853c5931af77d64b89bb0435cc31895034d7` 的完整 CI 与 docs-sync 中通过。真实 Provider 账单对账仍需现场验证。


## A61：旧项目成本迁移（待 CI）
当旧项目存在成本快照但账本没有成功实际金额时，第一次成功记账前会将历史镜头成本与项目未分配差额一次性原子迁移到 ledger；随后项目与镜头成本均以成功 ledger rows 汇总，避免覆盖旧成本或重复增量。新增 A61 回归测试，当前 SHA 的完整 CI/doc-sync 待确认。


## A62：修复 A61 handoff 文案断言（待 CI）
A61 的完整 CI 因 test_handoff_mentions_a61_legacy_cost_migration 期待“历史成本迁移”而文档写“历史实际成本迁移”失败。已将断言统一为精确术语；A61 代码逻辑未变，A62 新 SHA 的完整 CI/doc-sync 待确认。


## A61：旧项目历史成本迁移
对于已有成本快照、但旧用量账本中没有成功实际金额的项目，第一次成功记账前先执行历史成本迁移：汇总各镜头历史成本，并将项目总成本与镜头合计之间的未分配差额一次性迁移入 ledger。迁移使用批量临时文件替换，避免部分写入；之后项目与镜头成本以成功账本记录为准。不得把历史成本直接清零，也不得重复迁移。


## A63：迁移基线持久化保护（待 CI）
A61 的迁移行可能成功写入，但如果紧接着本次新费用写入失败，项目内存快照还没同步，调用方保存可能保留旧的错误值。A63 在迁移批量写入后立即从 ledger 更新项目/镜头成本快照，并新增后续记账失败回归。当前 SHA 的完整 CI/doc-sync 待确认。


## A64：素材成本账本故障保护（待 CI）
A61-A63 自动化 CI 与 docs-sync 已通过。A64 将素材生成成功与成本记账失败分开处理：保留已入库素材，状态标为“已生成并入库（成本待核对）”，记录 recovery.history 与对账动作，不误报生成失败或诱发重复生成。当前新 SHA 的完整 CI/doc-sync 待确认。


## A65：账本完整性
单条与批量用量记录均通过同目录临时文件原子替换正式账本；替换失败保留原账本。不得在持久化层静默截断历史记录，因为项目实际成本依赖完整成功账单行。新增原子替换失败与 2000 行以上历史保留回归；当前 SHA 的完整 CI/doc-sync 待确认。


## A66：人工视觉核验证据文件校验
人工商品画面核验必须绑定可访问的真实证据文件：受支持图片/视频扩展名、文件存在且非零字节，并保存规范化绝对路径。无效证据拒绝写入状态；回归覆盖无效和有效文件。此校验不检查图片内容，也不构成商品真实性认证。以当前分支最新 SHA 的完整 CI 与 docs-sync 作为自动化结论。


## A67：短剧人工核验证据失效保护
短剧质量审查每次运行时都会重新验证保存的证据路径是否仍指向支持的图片/视频格式、真实存在且非空的文件。证据文件丢失、清空或格式失效时，即使历史字段仍为 `passed`，也会报告 `PRODUCT_VISUAL_NOT_VERIFIED`。自动化回归覆盖有效和失效证据；当前 SHA 的完整 CI 与 docs-sync 必须重新核验。该检查不代表画面内容已被自动证明真实。


## A82/A83 接手进度（2026-10-13）
- A82 已在开发分支 SHA `8756b773c3b2ee3bf08b80bf3b31992b7081a606` 通过完整 CI（run `38306392896`）与 docs-sync（run `38306392892`）。
- A83 增加 `narrative_obligations`，追踪人物承诺、误解与行动后果，并核验来源证据、人物引用、镜头顺序和后续文本覆盖。
- A83 变更后的完整 CI/doc-sync 尚待 GitHub Actions 对最终新 SHA 执行；不可沿用 A82 的通过记录。
- 本规则是结构/文本审查，不是完整语义理解或真实画面验收；Windows 真机、真实 Provider 与真实扣款继续暂缓。


## A82/A83 自动化验证记录（2026-10-13）
- A82 代码基线 SHA `8756b773c3b2ee3bf08b80bf3b31992b7081a606` 的完整 CI（run `38306392896`）与 docs-sync（run `38306392892`）通过。
- A83 代码基线 SHA `f57c0eb02249439ea42cc3d46dd2d94e87bab1c1` 的完整 CI push run `38307672489`、PR CI run `38307795562`、docs-sync push run `38307672505`、PR docs-sync run `38307795710` 均 success。
- PR #32 已创建且保持 open/unmerged；任何合并操作都必须等待用户明确要求。
- 真实剧情语义、Windows 真机、真实 Provider 与真实扣款未由上述自动化检查覆盖。


### A84：跨集剧情承接一致性
A84 在 A83 的 `narrative_obligations` 上增加可选 `cross_episode_required` 标记。对显式要求跨集延续的事项，按根级 storyboard 的 episode_number 检查后续引用是否确实落在后续集；若状态仍为 open，还需核对来源集的未解线索/下一集要求/集末状态和下一集开场状态/未解线索。新增 warning code：`NARRATIVE_OBLIGATION_CROSS_EPISODE_TARGET_MISSING`、`NARRATIVE_OBLIGATION_CROSS_EPISODE_FOLLOW_THROUGH_MISSING`、`NARRATIVE_OBLIGATION_NOT_IN_EPISODE_HANDOFF`、`NARRATIVE_OBLIGATION_NOT_CARRIED_FORWARD`。未声明字段的旧方案兼容。该检查是结构/字符串匹配，不证明语义合理性。代码 SHA `00ad0d00a9747ca9ef666981b4e592bef6bde543` 的 CI/doc-sync 尚待最新结果。


### A84 自动化验证结果（2026-10-13）
A84 代码/测试/HELP/PROJECT_LOGIC 同提交 SHA `00ad0d00a9747ca9ef666981b4e592bef6bde543` 已通过完整 CI 和 docs-sync 的 push 与 PR 工作流：CI `38308777852`、`38308783208`；docs-sync `38308777939`、`38308783195`。这不证明人物心理/剧情语义自然，也不替代真实画面核验。


### A85：人物长期状态与关系跨集一致性
A85 为每集可选的 `continuity_state.character_state_ledger` 建立跨集审查，跟踪人物认知、心理、秘密、承诺与关系等维度。显式标记 `must_persist=true` 的未解决状态必须在下一集继续出现；状态描述变化需要声明 changed/resolved，changed 必须提供可在剧本/分镜定位的 transition_evidence。旧方案兼容；文本审查不等于完整语义理解或视觉核验。


### A85 自动化验证结果
代码/测试 SHA `6128fabc3c530c6072dfe72e05a956fe7733065f` 已通过完整 CI push/PR 与 docs-sync push/PR：CI `38309397555`、`38309402963`；docs-sync `38309397567`、`38309403129`。文本规则不替代人物心理语义与视觉核验。


### A86：人物状态变化因果闭环
对人物状态台账中 `status=changed` 的记录，要求模型提供触发事件/镜头、状态改变镜头、人物反应及后续行动后果证据。确定性审查会检查证据可定位性与镜头顺序，并对缺失触发、触发晚于变化、反应缺失或后果缺失/顺序错误给出 warning。旧方案兼容。该规则只能核对结构和文本证据，不能证明心理变化自然，也不能证明视频实际演出了状态变化。


### A87：人物状态与可观察表演一致性
为 `status=changed` 的人物状态要求明确写出可观察动作/台词/表情/互动及对应分镜位置，检查描述是否能在引用镜头文本中定位，拦截只有抽象心理标签的记录。此为文本层预审，不代表已验证生成画面。验收需包含有效表现、抽象标签、引用镜头不匹配、字段缺失和旧方案兼容。
\n\n### A88：多人物状态依赖一致性\n可选 `cross_character_dependencies` 记录两个人物对同一信息、关系或承诺的状态陈述及证据。只在声明为 `same_understanding` 却陈述不同时报告直接矛盾；知识不对称必须说明原因，`different_beliefs_allowed` 保留合理误解与不同信念。此为显式结构/文本审查，不代表系统完全理解叙事语义。\n

### A89：跨集演员/场景资产锁定
多集方案可用根级 `series_asset_locks` 声明重复人物/场景的稳定标识、规范描述与适用集数。验证时将描述注入相应镜头的演员/场景需求，供现有资产调度使用；无匹配目标会警告。此为提示词/需求层约束，不代表相同素材文件已被复用，也不保证生成视频中的身份/布景绝对一致。


### A89 验证基准（2026-10-14）
当前验证 SHA `9bcb19ac950f0addcc5a0bfab599dd060c11ec1e`；CI push `38465502064`、CI PR `38465509232`、docs-sync push `38465502037`、docs-sync PR `38465509210` 均成功，299 项 Desktop Core 测试通过。PR #32 保持 open/unmerged。A89 是文本/资产需求层约束；不能据此声称物理素材复用或视觉一致性验收完成。


## A90：跨集物理素材 ID 绑定（待最新 SHA 自动化验收）
跨集演员/场景锁定可选指定本地素材库 asset_id，并将精确 ID 传入制作行。生产解析按 ID 验证资产存在、启用、可复用且类型匹配；无效时明确返回 SERIES_LOCKED_ASSET_INVALID，禁止静默替换或自动生成。未提供 ID 的 A89 旧方案保持标签匹配兼容。此约束只保证素材调度选择，不保证生成画面像素级一致。最新 SHA 的完整 CI/docs-sync 必须重新核验；PR #32 保持 open/unmerged，Windows 真机与真实 Provider 验收继续暂缓。


## A91 接手注意事项
跨集演员/场景锁定必须在项目重新打开、任务恢复和每次单镜头生成/重生成前重新校验。锁定 ID 失效或本地索引不可读取时必须 fail-closed，保留原 ID、记录原因并阻止受影响镜头调用 Provider；不能用标签匹配、自动补素材或重生成整部短剧绕过锁定。
- 解析顺序要求：先校验当前镜头所有锁定 ID；任一失效立即返回，不应先触发同镜头其他素材的自动补齐。

## A92 AI 接手规则
新增或修改跨集物理锁定逻辑时，必须同时验证锁定 ID 是否最终写入实际 `Shot.actor_id` / `Shot.scene_id`，不能只检查创意方案中的 `asset_resolution` 文本字段。测试应包含相似标签的干扰素材与保存/重开项目场景。

### A92 CI 失败修正步骤
首次 CI 失败点是测试调用镜头素材解析后直接重载项目，没有先保存，因此不能证明持久化绑定。修正测试：先 `store.save(project)`，再 `store.load(project.id)`，随后断言两集 actor/scene ID 保留。修复 SHA 必须重新执行全套检查。


### A92 CI 根因修正
测试原先按 `restored.shots[1]` 查找追加镜头，但新项目本身已有多个默认镜头。现在只保留两个目标镜头，并按 `shot.id` 查找重载记录；所有检查必须基于新的最终 SHA。


## A93 接手规则：验证真实 Provider 调用边界
不要只验证 resolve_assets() 返回错误。必须从 _render_with_provider() 生产入口使用计数型 fake Provider 验证失效锁定在 provider.generate() 之前拦截（调用次数 0），保留原锁定 ID，不静默选择相似资产，也不触发同镜头其他素材的自动生成；同时确认其他镜头状态和输出路径未变。所有改动同步 HELP、PROJECT_LOGIC、SESSION_HANDOFF、验收计划、SOP、AI handoff 与 future memo。


### A92/A93 自动化验收结果（2026-10-14；以本节为准）
- 最终代码与测试 SHA：`db8c2a4e80bdbd6a5d308848e84905c1c2a348d0`。
- CI push run `38470175403`、CI PR run `38470184669`、docs-sync push run `38470175408`、docs-sync PR run `38470184505` 均 success。
- A92 跨集锁定 actor/scene 精确 ID 已验证解析绑定、相似标签不覆盖、保存/重开后绑定持久化。
- A93 从 `_render_with_provider()` 入口验证失效锁定素材在 Provider 调用前拦截，Provider 调用次数为 0；保留原锁定 ID，不绑定替代演员，不影响其他镜头已有状态/路径。
- PR #32 保持 open/unmerged。以上仅为自动化测试；Windows 真机、真实 Provider、真实账单/扣款、剪映现场及生成画面视觉一致性继续暂缓。


## A94 接手规则：原资产恢复后再试
对锁定素材失效的修复路径，必须验证恢复同一 asset_id 后可安全重试；不能因为旧恢复记录永久阻断，也不能转而选择同标签资产。恢复后的解析仍须禁用自动生成。CI 与 docs-sync 必须在最新 SHA 上重新确认。


### A94 自动化验收结果（2026-10-14；以本节为准）
- 代码与测试 SHA：`289cc0954cb93ce1a218436d2a6137317a7c6130`。
- CI push run `38470748908`、CI PR run `38470757428`、docs-sync push run `38470748944`、docs-sync PR run `38470757442` 均 success。
- 失效阶段确认锁定素材错误并关闭生成；恢复同一 asset_id 后可重试并精确绑定原 ID，即使存在同标签相似资产也不替换；锁定 ID 仍禁止 fallback/自动生成。
- PR #32 保持 open/unmerged；真实 Provider、Windows 真机、账单/扣款、剪映现场与画面视觉一致性仍暂缓。


## A95 接手规则：索引损坏不是素材缺失
本地 `library.json` 不可读取或 JSON 解码失败时，跨集锁定校验必须 fail-closed 并返回 `SERIES_LOCKED_ASSET_LIBRARY_UNAVAILABLE`。不要尝试从标签匹配或自动生成来绕过。先修复/恢复索引，再针对受影响镜头重试。需使用生产入口级计数型 Provider 测试并验证非目标镜头隔离。


### A95 自动化验收结果（2026-10-14；测试代码 SHA `6b225e09adac63265d53b27eae3ed6a54a51f49e`）
- CI push run `38471501401`、CI PR run `38471510428`、docs-sync push run `38471501250`、docs-sync PR run `38471510506` 全部 success。
- 无效/截断 `library.json` 返回 `SERIES_LOCKED_ASSET_LIBRARY_UNAVAILABLE`；素材解析提前停止，不继续处理其他素材；Provider 调用次数为 0。
- 原锁定 ID 保留，非目标镜头状态及已有输出路径保持不变。
- PR #32 保持 open/unmerged。真实 Provider、Windows 真机、实际账单/扣款、剪映现场和生成画面视觉一致性继续暂缓。


## A96 接手规则：索引修复后必须可恢复
索引损坏的 fail-closed 不应演变成永久失败。补充测试：修复 `library.json` 并恢复原资产后，重新解析应绑定原锁定 ID，不得因存在相似资产而换人，也不得触发 fallback。必须在最新 SHA 上重跑 CI 与 docs-sync。


### A96 自动化验收结果（2026-10-14；测试代码 SHA `fc01ace4eeb90ccb2f2df10b44a57f8b3c69f134`）
- CI push run `38471876626`、CI PR run `38471884325`、docs-sync push run `38471876601`、docs-sync PR run `38471884345` 全部 success。
- 索引损坏时返回 `SERIES_LOCKED_ASSET_LIBRARY_UNAVAILABLE` 并禁止 fallback；索引恢复后，重新解析精确绑定原锁定资产 ID，标签相似资产不能替换，且不触发自动生成。
- PR #32 继续保持 open/unmerged。真实 Provider、Windows 真机、账单/扣款、剪映现场与生成画面视觉一致性继续暂缓。


## 最近进展：A97 项目恢复隔离
新增自动化回归，检查恢复时只重置缺失成片的目标镜头，不影响其他有效镜头的输出路径、状态、版本与费用，并覆盖保存/重新打开。必须等最新提交 SHA 的四项 CI/docs-sync 全绿后再标记通过；PR #32 保持 open/unmerged，真实 Provider 与 Windows 真机仍暂缓。


## A98 项目恢复摘要幂等性
修复了重复恢复时丢失缺失镜头提示的问题：已明确标记为“待重新生成/重新选择素材”的镜头，在真正处理前重复恢复仍会出现在 `missing_media`；普通“待生成”镜头不误报。有效兄弟镜头保持不变。最新 SHA 的 CI push/PR 与 docs-sync push/PR 全部通过后才能标记通过。


## 2026-10-14 当前优先级：商业剪辑决策层升级
用户已明确要求暂停费用对账/单镜头重试保护检查线，优先核查并升级未来路线图第 5 项“商业级剪辑决策层”。本轮具体修复是 `postprocess.process_shot()` 不再忽略 `focus_x/focus_y`：FFmpeg crop 现在根据归一化坐标定位；非法/非有限坐标回退中心，越界值夹紧；新增 `test_postprocess.py` 回归测试。此项不等于商业剪辑能力整体完成。

接手必做：
- 先读取 `apps/ad-studio-desktop/SESSION_HANDOFF.md` 最新更新，再检查当前分支 HEAD 和 PR。
- 检查本轮最新 SHA 对应的完整 CI、docs-sync；必要时运行 `python3 -m unittest discover -s apps/ad-studio-desktop -p 'test_*.py'` 与 `python3 -m compileall -q apps/ad-studio-desktop/ad_studio`。
- 继续沿“AI决策 → 参数校验/持久化 → 实际剪辑执行 → 输出检查”审计，逐项标记有代码+测试证据、部分实现、未实现/未验证。
- 后续重点是节奏、镜头衔接、字幕密度、音乐卡点、商品展示节奏和剪后反馈。每次代码修改必须同步 HELP、PROJECT_LOGIC、SESSION_HANDOFF、验收计划、验收 SOP、本文件和根目录未来备忘。
- Windows 真机、真实 Provider/扣费、剪映现场验收仍按用户要求暂缓；PR 保持 open/unmerged。不得把 CI 绿灯或结构化剪辑参数等同于商业成片质量。


## 最新接手补充（2026-10-14）：商业剪辑焦点坐标语义
这是对本文件先前“焦点坐标实际控制 crop 位置”描述的精确定义，后续以本段为准：
- 当前分支：`feat/product-drama-visual-review`；PR #32 必须保持 open/unmerged。
- 用户已要求暂停费用对账/单镜头重试保护检查线，优先推进未来路线图第 5 项“商业剪辑决策层升级”。
- `focus_x/focus_y` 表示缩放后源画面中的主体/视觉焦点归一化位置（0–1），不是 crop 偏移比例。裁切窗口尽量将焦点放到输出画面中心，并限制在源画面边界内。
- `adapt_aspect()` 仍是中心裁切工具；`process_shot()` 是焦点驱动裁切入口。
- 新增/更新的 `apps/ad-studio-desktop/test_postprocess.py` 应断言实际 FFmpeg `-vf` 参数中的 max/min 焦点定位表达式，覆盖边界夹紧、NaN/Infinity/非法输入回退。
- 接手后必须重新读取 `apps/ad-studio-desktop/SESSION_HANDOFF.md`，查询当前 HEAD、PR #32、当前 SHA 的完整 CI 与 docs-sync；本次修正之后的 SHA 结果不得继承旧提交的绿色结果。
- 继续逐项实现并验收动态节奏、镜头衔接、字幕信息密度、音乐卡点、商品展示节奏与剪后反馈。不要把焦点定位这一小项说成商业级剪辑整体完成。
- Windows 真机、真实 Provider/扣费和剪映现场验收按用户要求继续暂缓。

## 2026-10-14：文档同步 CI 覆盖范围修正
- 旧脚本只要求 HELP.md、PROJECT_LOGIC.md 同步，未覆盖接手规则中的其他关键文件。
- 已将文档同步契约扩展为八个文件，并增加契约测试，防止清单回退。
- 本次提交后必须重新核验最新 SHA 的完整 CI push/PR 与 docs-sync push/PR；PR #32 不得合并。
- 接手后仍须阅读 SESSION_HANDOFF.md 并人工确认文档内容；文件路径被更新不等于语义已完整同步。


## A100 接手记录：商业剪辑淡出时间窗
本轮在 `postprocess.py` 修复“淡出”固定从 0 秒开始的问题。新实现以 FFprobe 时长除以播放速度得到后处理时长，再计算末尾 0.25 秒淡出窗口；更短的镜头使用实际镜头时长。`test_postprocess.py` 新增变速与超短片段回归。接手 AI 必须先检查最新 SHA 的完整 CI/docs-sync push/PR 四项状态，再决定验收；真机视觉/听感验证仍暂缓。商业剪辑路线图第 5 项继续未完成。


## A101 接手记录：变速音画同步
本轮 `process_shot()` 在非 1.0 倍速时同步添加 FFmpeg `atempo` 音频滤镜，避免只改视频时间戳而音轨仍保持原时长；正常速度不增加滤镜。两个回归测试检查了两种情况。先核验本次 SHA 的完整 CI/docs-sync push/PR 四项结果，再决定自动化验收；真实素材的音画同步和听感检查继续暂缓。


## A102：最终导出最低 1080P 级尺寸（待 CI）
最终拼接后统一归一化转码，并以 ffprobe 校验最低尺寸：竖屏 1080×1920、横屏 1920×1080、方形 1080×1080。低于最低值的输出拒绝交付。测试覆盖 FFmpeg 参数和低分辨率质检。尺寸放大不等于 AI 超分/真实细节恢复；Windows 真机画面验收继续暂缓。先查当前 SHA 的 CI/doc-sync push/PR 四项结果，再继续商业剪辑路线图。

A102 首轮 CI 暴露测试夹具未模拟归一化阶段的目标文件，并有一处 FFmpeg 参数断言位置错误；已修复。后续接手必须重新核对最新 SHA 的完整 CI 和 docs-sync push/PR 运行结果。


## A103：淡入/淡出音画同步（待 CI）
继续推进商业剪辑时已修复淡入/淡出只作用于画面、原音轨可能突然截断的问题。`process_shot()` 现在配对使用 `fade`/`afade`，变速时先 `atempo` 再执行按输出时间计算的音频淡化，短镜头缩短淡化窗口。测试及 CI/doc-sync 结果需按最新 SHA 核对。注意这不等于实现相邻镜头交叉溶解。


## A104 当前接手补充：相邻镜头真实转场
当前代码已将“交叉溶解”接入最终成片构建：非首镜头显式选择后，使用 FFmpeg xfade 与 acrossfade；默认硬切仍走原拼接路径。先检查最新 SHA 的 CI/docs-sync 四项状态，再决定自动化验收。真实媒体兼容性、视觉连续性与听感尚未在 Windows 实机验证，不能宣称商业剪辑整体完成。PR #32 保持 open/unmerged。


## A105 接手记录：让 pacing 不再只是描述字段
最新代码将分镜节奏映射到实际速度默认值：慢 0.85x、标准 1.0x、快 1.15x、极快 1.3x；schema 允许省略 `speed`；显式 `speed` 优先，未知标签回退标准。新增单测覆盖默认映射、显式覆盖与非法标签。先检查最新 SHA 的 CI/docs-sync 四项状态，再继续商业剪辑主线。尚未实现画面动作/情绪驱动节奏、音乐节拍检测、字幕信息密度和剪后反馈；PR #32 保持 open/unmerged。


## A106 接手记录：商业镜头角色默认剪辑决策（待当前 SHA CI）
本轮新增 `creative_engine.resolve_editing_intent()`，根据分镜文本推断商业角色并补齐缺失的时长、pacing/speed、transition；显式参数优先。决策保存角色、理由、依据边界及参数来源，并复用现有生成/后处理/最终拼接链。新增角色映射、末镜 CTA 淡出、显式覆盖回归测试。下一步先查本轮最终 SHA 的 CI Push/PR 与 docs-sync Push/PR；PR #32 保持 open/unmerged。该规则只基于文本关键词，不是画面理解；真实素材/Windows 验收、音乐卡点、字幕密度与剪后反馈仍未完成。


A106 首轮 CI 修复说明：自动化测试发现未知 `pacing` 标签必须继续回退“标准”，不能使用推断角色的默认节奏。代码现已修正，并把最终生效的时长、节奏、速度、转场写入 `editing_intent`；需以修复后的 SHA 重新检查 CI Push/PR 与 docs-sync Push/PR 四项结果。

## A107 接手记录：商业角色时长进入运行时生成请求
A106 的时长推断曾只保存在 CreativeShot 中；运行时 `Shot` 构造未传入 duration_seconds，视频生成请求因此可能仍用 3 秒默认值。A107 新增 `runtime_shot_editing_fields()` 并在 `_activate_plan()` 中使用，使时长、pacing、speed、transition 一起进入实际运行时对象。新增回归测试验证商品细节角色默认 4 秒及字段映射。下一步检查最新 SHA 的 CI Push/PR、docs-sync Push/PR 四项；PR #32 保持 open/unmerged。Provider 是否严格遵守请求时长仍须真实素材验收，Windows/Provider 验收按用户要求暂缓。


## A108 接手记录：字幕密度基础执行闭环（修复提交后待重新核验）
`write_srt()` 按实际片长生成多段 SRT，`analyze_subtitle_density()` 返回字/秒和风险提示；字幕 UI 使用 FFprobe 实际时长并把结果传入真实烧录路径。短镜头会减少字幕切换次数，但可能需要更精简文案；系统只提示，不改写原文。新提交后必须重新核验 CI/doc-sync Push/PR 四项，PR #32 保持 open/unmerged。真实素材可读性、音乐卡点与剪后反馈仍是未完成商业剪辑能力。

## A109｜音乐节拍与画面切点真实联动
本轮在生产链实现全局 BGM 与保守节拍切点联动：`finish_selected()` 将选择持久化到项目级；`ProductionStore.build_final()` 分析 BGM、规划实际镜头时长、必要时临时变速并保持原音轨同步，拼接后统一混入一条连续 BGM，最后继续 1080P 归一化。专项测试位于 `apps/ad-studio-desktop/test_music_sync.py`。下一 AI 必须重新核对最新 HEAD、CI 和 docs-sync，不得把代码存在视为测试通过；真实素材/Windows 听感验收仍暂缓。

### A109 旧项目音轨兼容边界
A109 兼容边界：旧项目中已把 BGM 烧录进镜头音轨的成片，无法仅凭现有文件可靠分离旧音乐。重新使用全局 BGM 前，应从未混入 BGM 的镜头源重新执行字幕处理；否则可能叠加旧音乐。

### A109 转场安全补充
A109 转场安全补充：当前切点变速遇到显式“交叉溶解”时保守回退原镜头时长，仍保留既有交叉溶解与全局连续 BGM；待单独建模转场重叠时长后再开放这类边界的卡点调整。
\n\n## 最新接手任务状态｜A112 字幕 cue 时间窗\nA112 的候选实现把 A108 SRT 真实 cue 起止时间接入 A111 音乐卡点规划：仅对与当前镜头路径和时长相匹配的 SRT 施加最短 cue 0.65 秒保护；缺失、格式损坏、时间轴越界/不匹配或版本变化均保守回退并留审计。接手后必须先读取最新 SESSION_HANDOFF、确认 PR #32 open/unmerged，再检查当前 HEAD 的 CI Push/PR 与 docs-sync Push/PR 四项；不要把提交前结果当成通过。\n\nA112 提醒：曾出现一次 docs-sync Push 失败，原因是 SRT 转义修复单独形成代码提交、未同提交更新强制文档。后续应核验重建提交的新 SHA 四项工作流，不能把后续结果追溯宣称为失败 SHA 已通过。

## A112 自动化验收结果｜2026-10-14
代码基线 e8deb1ec4ef9edf7d999c79539762ea2627affab 的 CI Push 38570453607、CI PR 38570460103、docs-sync Push 38570453565、docs-sync PR 38570460195 均 success。PR #32 继续 open/unmerged。后续任务先复核阶段 2 退出条件；Windows 真机、真实素材、Provider/扣费和商业效果继续暂缓。

## PLAN-003 最新执行记录｜A3 布局修复与 A0–A5 证据审计（2026-10-15）
当前 HEAD `f20bf426594a55ac74267641b53d9166acef6798` 的 CI Push/PR 与 docs-sync Push/PR 四项均成功。A3 设置区字段与操作按钮已分容器，新增 AST 布局回归测试；只代表自动化布局合同通过，不代表完整 A3 或 Windows UI 验收完成。A0–A5 证据映射已启动但仅部分完成：A0 启动链缺专门测试，A1 稳定性缺任务级矩阵，A2 缺 App.create() 直接编排测试，A4 缺损坏素材/扫描失败的完整测试映射，A5 缺视觉帧提取/分析失败回退的确定性测试映射。本段为历史证据记录；A68–A74 与 A99 的历史任务身份已恢复。下一步按文件顶部 PLAN-003 状态完成跨来源合并映射并继续逐项当前 HEAD 证据审计。PR #32 保持 open/unmerged；总体完成率关闭；真实环境验收继续暂缓。


## 历史编号调查更新｜A99 已找回（2026-10-15）
历史提交 `c8252dc58995289d8ca38dfd15dc8e66f8001eeb` 明确标记 A99，HELP.md、PROJECT_LOGIC.md 和 `test_a99_successful_ledger_clears_stale_cost_on_unbilled_sibling_shot` 均提供证据。台账已恢复正式标题并移除 A99 缺口标记；它与 A57/A59 相关但不重复。本段为历史调查记录；后续调查已恢复 A68–A74 正式任务身份。A68–A74 与 A99 当前 HEAD 的完整验收仍待审计。




## 历史接手状态｜2026-10-15｜已由文件顶部 PLAN-003 状态取代
- 本段旧基线：3801204559bb05cb617a13ef249fe35db0030a50；它不是当前 HEAD，不能用来证明最新提交 CI。当前状态以文件顶部 PLAN-003 段和 GitHub 实时 Actions 为准。PR #32 仍须 Open / unmerged。
- A3 设置区布局修复与 AST 回归测试已提交，自动化 CI 全绿；仍未完成 Windows 真机验收，也未宣称完整 A3 验收完成。
- A68–A74 已从历史实现提交和 HELP/PROJECT_LOGIC/SESSION_HANDOFF 找回，正式验收计划/SOP及未来备忘已补回；A99 也已找回。113 个编号均有任务标题，编号缺口为 0。
- 需求文本级复核已记录 113 个编号，但最终跨来源重复/状态段合并审计尚未完成；代码/测试证据审计仅 A0–A5 部分映射，fully_audited=0、权重为空、总体完成率关闭。
- 下一项：继续 PLAN-003 最终跨来源去重和 A0–A5 逐项证据审计；不要顺手扩展产品功能。此 handoff-only 状态提交完成后仍需重新核验新 SHA 的四项 CI/doc-sync。


## PLAN-003 最新接手状态｜A12–A17 部分证据映射｜2026-10-15

- 最新提交基线：`177088ee6a743253d61dfe3ecb74842babe8e2a9`；上一基线四项 CI/doc-sync 已全部通过，PR #32 仍 Open / unmerged。新提交后仍必须重新核验四项工作流。
- A12：已定位 `hybrid_router.py` 的缺口分类、证据保护与预算路由；需补分类误报/漏报及 UI 提示映射。
- A13：已定位生成桥接、Provider 不可用与商品证据拦截测试、失败和人工复核闭环；真实 Provider/实际扣费暂缓。
- A14：已定位混合来源、待复核、最终渲染排除与 A23 闭环测试；最终逐镜头来源可追溯性仍需补证。
- A15：共享生产组件、音频、字幕、输出质检和 1080P 尺寸测试存在，但尚未证明全链业务目标一次性通过。
- A16：商品事实保护有相关测试；主体清晰、遮挡、细节、顺序与参数一致性没有在本轮证明已完成专项验收。
- A17：创意版本隔离和创意分析有测试；Hook/卖点/证明/CTA 的最终产物断言及真实投放效果未验收。
- 所有 A12–A17 只标记“证据已部分映射”，不代表正式验收通过。台账 `code_test_evidence_reviewed_ids=18`，`code_test_evidence_audit_completed_ids=0`；总体完成率关闭。
- 唯一下一项：继续 PLAN-003，审计 A18–A33 的计划、代码、专项测试、依赖/重复关系与当前 SHA；不开发新产品功能。Windows 真机、真实素材、真实 Provider/扣费、剪映现场及真实投放继续暂缓。


## PLAN-003 最新接手状态｜A18–A33 部分证据映射｜2026-10-15

- 本轮开始时基线：`53800b7845a9db49c329242506d80f6a1747281c`；该 SHA 的 CI Push、CI PR、docs-sync Push、docs-sync PR 均 success；PR #32 Open / unmerged。
- A18–A19：已映射版本状态隔离、物理输出路径、创意机制差异和禁止虚构投放指标的测试；原始版本追溯、实验设计字段需继续核验。
- A20–A25：已有事实边界、安全闸门、媒体质量、1080P 尺寸和无效输出拦截测试线索；逐条覆盖和当前基线独立复核仍未完成。
- A26–A30：已有历史修订独立性、交付复查、项目持久化、数据来源边界及失败恢复专项测试；不能推定正式清单全部子项都已覆盖。
- A31–A32：接手文档测试存在，但文本存在性/关键字段测试不能证明全部说明始终与最新实现一致。
- A33：三类用户流程离线回归存在，但媒体拼接、归一化和探针使用夹具/mock；不等于真实端到端或 Windows 实机验收。
- 本轮共覆盖 A18–A33 的部分映射；台账 `code_test_evidence_reviewed_ids=34`，`code_test_evidence_audit_completed_ids=0`，总体完成率关闭。
- 唯一下一项：PLAN-003 继续审计 A34–A49；不开发新产品功能。PR #32 保持 Open / unmerged。真实素材、Provider/扣费、Windows、剪映现场和真实投放继续暂缓。


## PLAN-003 审计进度更新｜A34–A49｜2026-10-15

本轮对 A34–A49 完成静态代码/测试/文档证据映射，基线 `b48f7a9859476ed639bc9220035c986cd5e77c37` 的四项 CI/doc-sync 均成功。A34–A36 有视觉比对、问题镜头局部修复、修正草稿与费用/版本校验测试线索；A43–A49 有旧视频恢复、稳定短剧镜头映射、恢复 UI 状态、素材解析失败保护、实拍裁剪安全输出和多段临时文件清理测试线索。A37 的视觉修正草稿换行不能仅凭 A50 视频提示词换行测试视为等价；A38–A42 需继续核对接手文档与正式计划状态是否一致。

此批 16 项均只记“部分证据映射”，不改变正式验收状态。进度台账的 `code_test_evidence_reviewed_ids=50` 仅表示 A0–A49 已开始映射；完整审计仍为 0，语义去重未完成，整体完成率保持关闭。下一步是 A50–A67；保留 A50/A56、A57 内两个独立场景、A61/A62 不合并的裁决。PR #32 保持 Open / unmerged；真实环境验收按用户要求暂缓。


## PLAN-003 审计进度更新｜A50–A67｜2026-10-15

本轮完成 A50–A67 静态代码/测试证据映射。A50/A56 的真实换行回归合同与修复相关但不合并；A57 在正式计划中包含两个独立场景（成本待核对 UI、项目恢复与成本对账），必须分别保留；A61/A62 分别是历史成本迁移与文案断言修复，不能合并。A51–A65 覆盖费用输入、失败尝试审计、旧视频恢复、Provider 成功/账本失败分离、成本单一事实源、旧成本迁移、素材账本保护和原子写入/历史完整性；A66/A67 分别验证人工视觉证据文件和审查时证据失效保护。

本批 18 个编号全部仅为“部分证据映射”，不等于正式验收通过。更新后 `code_test_evidence_reviewed_ids=68` 仅表示 A0–A67 已开始映射；完整审计仍为 0、语义去重未完成、整体完成率关闭。下一步是 A68–A82；不开发新产品功能。新提交的四项 CI/doc-sync 必须绑定最新 SHA 重新核验，PR #32 保持 Open / unmerged。真实 Provider/扣费、Windows 真机、真实素材、剪映和真实投放继续暂缓。


## PLAN-003 审计进度更新｜A68–A82｜2026-10-15

已完成 A68–A82 静态代码/测试/文档证据映射。A68 后续剧情影响、A69/A70 故事结构、A71/A72 故事方向/人物动机、A73/A74 因果链证据、A75/A76 商品事实和卖点覆盖，以及 A77–A82 镜头事件、行动依据、角色引用、关系变化、状态连续性和知识时间线均找到不同程度的代码/测试线索。A77–A80 在正式验收计划中仍未勾选或标为开发中，必须保留该状态并继续核验；不能只凭逻辑文档或旧 SHA 的 CI 结果宣布完成。

本批 15 个编号仅为部分证据映射。台账 `code_test_evidence_reviewed_ids=83` 只表示 A0–A82 已开始映射；完整审计为 0、语义去重未完成、整体完成率关闭。下一步是 A83–A99。PR #32 保持 Open / unmerged；新提交的 CI/doc-sync 必须按最新 SHA 重查。继续暂缓真实 Provider/扣费、Windows 真机、真实素材、剪映和真实投放。


## PLAN-003 审计进度更新｜A83–A99｜2026-10-15

已完成 A83–A99 静态证据映射。A83–A88 涵盖承诺/误解、跨集承接、人物长期状态、状态变化因果闭环、可观察表演、多人物依赖；A89–A96 覆盖跨集演员/场景文本锁定、精确 asset_id、锁定失效阻断、恢复重试；A97/A98 覆盖缺失镜头恢复隔离和重复恢复摘要；A99 独立规定成功账本成为权威来源后清除未计费兄弟镜头的陈旧实际成本。

本批全部仅部分证据映射。A84–A87 计划仍有未勾选项；A89–A96 的历史通过记录不能代替当前 SHA CI；A97–A99 需核对完整断言和最新运行。台账 `code_test_evidence_reviewed_ids=100` 仅表示 A0–A99 已开始映射，完整审计仍为 0、语义去重未完成、整体完成率关闭。下一批 A100–A112，并检查商业剪辑专项及 A102 1080P 条款。PR #32 保持 Open / unmerged；真实 Provider/扣费、Windows 真机、真实素材、剪映和真实投放继续暂缓。



## 当前执行状态追加（2026-10-15）｜模型/Provider 用户自由度审计
- 本轮审计结论已写入 `docs/AD_STUDIO_USER_EXPERIENCE_SAFETY_AUDIT.md` UXS-2 专项节。当前实现支持模型池、按功能路由、可配置 OpenAI-compatible endpoint/API Key，以及有限的通用 REST 视频/资产 Provider；并非任意模型/专有 API 的自动即插即用。
- 高优先级待裁决/核实：预算确认前的规划模型调用；不可用时自动路由可能切换到云端/本地；API Key 在模型配置 JSON 中明文保存；单价/usage 缺失时成本可能被记为 0；请求前数据外发告知和端点安全；切换模型后的缓存与历史可复现性。
- 这只是静态代码证据映射，未运行本地测试、未连真实 Provider/代理、未核对真实账单。没有产品代码修改、没有新正式验收编号、没有完成率变化。
- 下一步唯一任务：继续 UXS-2 / PLAN-003，完成上述风险的 UI、调用路径、专项测试、HELP/PROJECT_LOGIC 和 A0–A112 映射；在完成去重前禁止新增 A113+，PR #32 保持 Open / unmerged，真实环境验收继续暂缓。


## PLAN-003 最新接手补充｜路由回退与外发边界｜2026-10-15

本轮 dashboard 已记录以下源码证据：模型路由在显式模型不可用时可选择其他模型；资产/视频能力路由存在本地转云端分支；文本/视觉请求向配置 Base URL 发送提示词或图像数据；单价/usage 缺失可能使成本估算为 0；API Key 存在普通 JSON 写入路径。以上均为静态审计发现，不是功能修复或正式验收通过。

下一步必须对照 A0–A112 原始合同逐项确认覆盖关系，验证拒绝回退/取消后零外部调用、未知费用展示、数据目的地告知、端点安全和凭据日志/导出/备份路径。不得新增正式编号；保持 code_test_evidence_audit_completed_ids=0、fully_audited=0、semantic_dedup_completed=false，不发布总体完成率。PR #32 保持 Open / unmerged；真实环境验收继续暂缓。


## 当前执行状态补充｜异常文本持久化与预算授权顺序｜2026-10-15

- `complete_json()` 的请求失败文本写入本地 usage ledger；转写 HTTP 错误会带入截断响应正文，实拍编排可能把转写异常保存到项目 creative plan；成本结算恢复路径也可能保存异常文本。
- 目前没有证据证明错误正文包含真实 API Key；安全结论只能是“异常文本可能持久化，脱敏行为尚未验收”。需要使用假密钥和模拟错误响应验证，不连接真实服务。
- `App.create()` 的创意规划调用、实拍视觉分析及可选转写发生在预算确认弹窗之前；取消弹窗不能撤销此前可能发生的模型调用。当前静态检查的相关测试中，未找到预算前零外部调用与异常正文脱敏的直接专项测试。
- 以上是 PLAN-003 静态证据，不是功能修复或正式验收。下一步对照 A0–A112 原始合同，重点 A13、A29、A30、A51–A65；不新增 A113+，保持完整审计与语义去重未完成，PR #32 Open / unmerged。


## 接手提醒｜PLAN-003 发现台账指标口径冲突｜2026-10-15

- 当前权威 dashboard 声称 A0–A112 的跨文档部分证据映射已开始（计数 113）；但规范 JSON 台账仅有 18 个任务含 evidence、其中 6 个编号含 source/test/CI/workflow 证据，且没有证据 SHA 绑定当前 HEAD。
- JSON 台账仍有 70 个任务的 `roadmap_phase=待路线图映射`，与 dashboard 中“阶段 2–6 分批依赖映射已写入”的概括存在逐项落库/统计口径冲突。
- 这是台账/指标一致性问题，不是产品功能验收。下一步逐项把已存在的映射和可定位证据同步到规范 JSON，区分跨文档已审阅数、台账结构化证据数和当前 HEAD 证据数；不要猜填阶段、不要把旧 CI 当当前证据。
- 继续保持 `fully_audited=0`、`semantic_dedup_completed=false`、`code_test_evidence_audit_completed_ids=0`；不新增 A113+、不赋权、不发布总体完成率。PR #32 Open / unmerged，真实环境验收继续暂缓。


## PLAN-003 最近一次实质落库｜A0–A6 主阶段映射、A0–A4 当前 SHA 证据｜2026-10-15

- 最新审计基线为 `c5497fd29ab2aafd071dfc6acc80fcef4558b5a1`。本轮核对产品路线图、验收计划及当前源文件/测试文件。
- 规范 JSON 台账已把 A0–A6 的主路线图阶段写为“阶段1｜可靠的生产底座”；A5 的 A4 输入依赖已落库。只记录明确前置依赖，不把关联任务随意变成依赖。
- A0–A4 的 source/test/workflow 证据已刷新到当前 HEAD，并关联当前 CI Push/PR 与 docs-sync Push/PR 成功记录。此证据刷新不等于这些任务正式验收通过。
- 当前仍有 63 个任务待路线图阶段映射；全量代码/测试证据审计完成数仍为 0；语义去重与总体审计均未完成。不新增 A113+，不赋权、不发布总体完成率。
- 下一步继续对照路线图阶段退出条件，按任务逐条映射依赖和证据边界；真实 Windows、真实素材、Provider/扣费、剪映现场和真实投放继续暂缓。PR #32 保持 Open / unmerged。


## PLAN-003 最新推进｜A0–A8 阶段/依赖与证据增量落库｜2026-10-15

- 当前审计基线：`b11ab5306e4b4992b982fe2f2393fac43861d93e`。A0–A8 的主路线图阶段与对应源码/测试证据已逐项写入规范台账；A0–A6 归阶段1，A7–A8 归阶段3。
- 已明确登记 A5→A4、A7→A6、A8→A7 的直接输入依赖。其他“相关/共享组件”关系不自动升级为依赖。
- 九个任务的源码/测试证据绑定到当前分支树；CI Push/PR 与 docs-sync PR 当前 SHA 已通过。当前 SHA 的 docs-sync Push 记录未找到，不能宣称四项均通过。
- 仍有 61 个任务待主阶段映射；全量代码/测试审计完成数为 0，语义去重未完成；不新增 A113+、不赋权、不发布总体完成率。
- 下一步继续 A9–A17 的阶段退出条件、依赖与证据映射；真实 Windows、真实素材、Provider/扣费、剪映现场和真实投放仍暂缓。PR #32 Open / unmerged。


## PLAN-003 最新推进｜A8 阶段纠正、A9–A17 证据增量落库｜2026-10-15

- A8「剪辑策略」已纠正为阶段2「商业级剪辑决策层」；A7 仍属阶段3。
- A9–A17 已归入阶段1，源码/专项测试路径、部分自动化证据和剩余缺口已写入规范 JSON 台账。
- 依赖记录：A12→A5/A8，A13→A12，A14→A13，A15→A8/A9/A10/A11，A16→A8/A10/A11，A17→A7/A8/A9/A10/A11。依赖不代表验收通过。
- 重点未证实项：ASR准确率、免费商用音乐/字体授权、字幕与口播及商品事实一致、AI画面商品一致、混合素材来源追溯、三类成片完整端到端质量。
- 本轮修改前基线 `5138685b3489fd249be5469fe86821b6374edde0` 的 CI Push/PR 与 docs-sync Push/PR 均成功；本轮新提交工作流需重新检查。
- 不新增 A113+；全量代码/测试审计仍为 0，语义去重未完成，不赋权、不发布总体完成率。真实 Windows、素材、Provider/扣费、剪映现场和真实投放继续暂缓。PR #32 保持 Open / unmerged。


## PLAN-003 增量审计记录｜A105–A109｜2026-10-15

- **源码/测试审计基线**：`c77704d86d6131d13501448af76ce24afc56ad7b`；文档更新前最近检查的分支 HEAD 为 `57ed689911025f2e31241ddf487e70143ffedbe0`。该 HEAD 的 CI PR [38730155209](https://github.com/konggu888/ecommerce-agent/actions/runs/38730155209) 与 docs-sync PR [38730155147](https://github.com/konggu888/ecommerce-agent/actions/runs/38730155147) 均 success；Push 触发工作流未被当前查询接口独立返回，不能宣称四项均已核实。PR #32 Open/unmerged。
- **A105｜分镜节奏映射**：慢/标准/快/极快默认速度、显式速度优先、未知标签回退有单测；后处理命令同步 setpts/atempo。真实渲染和完整 UI 到成片链未集成测试。
- **A106｜商业角色默认剪辑**：源码按分镜文本关键词推断角色、时长/节奏/速度/转场，并记录 rationale/basis/参数来源；测试覆盖 hook、商品细节、演示、证据和末镜 CTA，以及显式参数优先。pain_point/reaction/story_beat 等角色与歧义关键词未全面测试；不是视觉语义识别。UI 仅发现展示转场值，未找到明确的可编辑转场选择器。
- **A107｜推断时长进入生成请求**：CreativeShot → runtime Shot 的字段映射存在，生产入口将 runtime `duration_seconds` 传入 GenerationRequest；目前测试止于 runtime mapping，没有直接断言 Provider 请求最终收到推断时长。真实 Provider 仍不调用。
- **A108｜字幕自适应**：按 FFprobe 实际时长生成 SRT，拆分长文案、限制短镜头字幕切换并显示密度警告；桌面路径可见 probe → analyze → write_srt → burn_subtitles。单测覆盖规划器/SRT，但没有 app 级整链集成测试；真实阅读舒适度和 Windows 烧录效果未验证。
- **A109｜音乐节拍与实际切点**：生产源码把节拍分析、切点规划、内容/字幕保护、镜头变速、拼接后一次性混入全局 BGM 接入最终导出链；专项测试覆盖合成节拍、静音/低置信度回退、时长变化、内容保护、变速命令和 BGM 混音命令。但没有直接测试最终 build_final 的完整调度链，实际 FFmpeg 渲染/视听仍未验证。台账中历史 `automation_passed` 已降为 `partial_evidence_mapping` / `not_audited`，因为验收计划四项 workflow gate 尚未完整核实，且生产集成证据仍有缺口。
- A105–A109 均为 `partial_evidence_mapping` / `not_audited`。映射覆盖：113 个编号任务；source/test/CI/workflow 指针任务 110；任意 evidence 任务 112；路线图映射 113/113；源码/测试快照绑定任务 52；最终文档 HEAD 精确绑定 0；完整代码/测试审计 0；完整审计 0；语义去重未完成；权重与总体完成率关闭。
- 本轮不改产品代码。Windows 真机、真实素材、Provider/扣费、剪映现场与商业效果继续暂缓。PR #32 不合并；不新增 A113+，不删除/合并/重编号 A0–A112。
- 下一批按既有编号进入 **A110–A112**。文档提交后先核验最新 SHA 的 CI Push、CI PR、docs-sync Push、docs-sync PR；Push 若无法独立查询须明确记录未核实。


## PLAN-003 增量审计记录｜A110–A112｜2026-10-15

- **源码/测试审计基线**：`c77704d86d6131d13501448af76ce24afc56ad7b`；文档更新前最近检查 HEAD `a9fe2d93d186bac79dafee294e518209d963f420` 的 CI PR [38730727069](https://github.com/konggu888/ecommerce-agent/actions/runs/38730727069) 与 docs-sync PR [38730727058](https://github.com/konggu888/ecommerce-agent/actions/runs/38730727058) 均 success。Push 触发工作流未独立核实，PR #32 Open/unmerged。
- **A110｜商业剪辑内容保护**：源码把口播/屏幕文字/商品角色/CTA 停留时间作为音乐卡点下限，低置信度和不安全计划回退；测试覆盖对话、屏幕文字、商品停留与安全回退。CTA 专门下限尚无独立断言，生产链整合测试缺失。
- **A111｜逐边界局部音乐卡点规划**：算法逐镜头验证最短时长、最大变化、变速约束，仅回退冲突边界并记录 adjusted/reverted 边界；专项测试覆盖单/多相邻保护、无关安全边界仍可调整、总时长保持、低置信度和交叉溶解回退。尚无 build_final 整链测试或实际 FFmpeg 渲染。
- **A112｜字幕实际时间窗参与内容保护**：SRT 解析校验 cue 顺序/范围/结束时间，最短 cue 时长进入卡点保护；生产代码检查字幕记录是否绑定当前源视频路径和时长，异常时回退。单测覆盖解析和 helper 边界，但没有生产级 applied/fallback 整链回归。
- A110–A112 历史 `automation_passed` 不直接继承；本轮全部改为 `partial_evidence_mapping` / `not_audited`，因为本轮源码/测试复核发现专项集成证据缺口，且当前查询未独立核实 Push 工作流。真实素材、Windows 真机、真实音画/字幕可读性与商业成片质量仍暂缓。
- 映射覆盖：编号任务 113；任意 evidence 任务 113；source/test evidence 任务 112；源码/测试快照绑定任务 55；完整代码/测试审计 0；完整审计 0；语义去重未完成；权重与总体完成率关闭。
- 本轮未改产品代码。PR #32 不合并；不新增 A113+，不删除/合并/重编号 A0–A112。下一步不再有新的编号任务；应回到 PLAN-003 对 A0–A112 做语义去重、证据冲突与未审计范围的统一核对，不得凭空扩展编号。

## PLAN-003 增量审计｜A52 / A55 源码与测试证据边界｜2026-10-16

- 审计源码/测试快照：分支当前已核实的 HEAD `e4fa3365b4a44aa7ddb62a492826afc66a2a191b`；产品代码未修改。PR #32 仍 Open / unmerged。
- **当前 SHA 的 PR 触发工作流**：CI #2230 success，docs-sync #1907 success；部署预览 status success。当前可用 connector 的 commit-workflow 查询只返回 PR 触发项，Push 触发的 CI 与 docs-sync 未独立核实，因此不得宣称四项都已核实通过。
- **A52｜Provider 失败尝试与成本去重：部分证据映射，not_audited。** `production.py::_render_with_provider` 在 Provider 调用开始后捕获生成异常，尝试写 failed video ledger row；失败报价进入 `unit_cost_rmb`、`estimated_cost_rmb=0`，成功行才进入实际成本汇总。专项测试 `test_a52_failed_video_attempt_is_auditable_without_double_counting_actual_cost` 覆盖一次失败+一次成功重试、失败行类别/报价字段、失败成本为零及成功成本仅计一次。**未直接断言**失败行的 project_id/shot_id/provider/error 全字段，失败后旧视频仍可用，以及重新创建 Store/重新加载后失败行仍存在；不能把“账本文件写入实现”代替这些行为断言。
- **A55｜视频成功但成本记账失败：部分证据映射，not_audited。** 源码把 Provider 生成/替换和成功记账分成两个异常边界；账本异常时保留输出路径，设置“已生成（成本待核对）”，记录 recovery history 并尝试保存项目。专项测试 `test_a55_ledger_failure_does_not_turn_successful_video_into_provider_failure` 覆盖新视频文件、活动路径、待核对状态、恢复记录和项目重载后的视频路径/状态。**尚未直接断言**该场景不会新增 failed Provider 记录、不会产生重复 success ledger 行，以及账本恢复后对账动作是否安全幂等；真实账单核对仍暂缓。
- 本轮没有发现足以证明生产实现必须立即修改的缺陷；发现的是正式验收断言缺口。因此不改产品代码、不把 A52/A55 标为正式通过，也不继承验收计划中历史 SHA 的自动化通过标签作为当前 HEAD 的完整证据。
- **后续主线**：回到 PLAN-003 对 A0–A112 的跨来源语义重复、状态冲突、依赖和证据边界做统一裁决；A52/A55 的上述缺口作为待补证据保留。不得新增 A113+、删/合并/重编号既有任务、赋权或发布总体完成率。Windows 真机、真实 Provider/扣费账单、剪映和真实投放仍暂缓。

## PLAN-003 当前进度｜A52/A55 映射完成，转入 UXS-2 合同核对｜2026-10-16

- 源码/测试基线 `e4fa3365b4a44aa7ddb62a492826afc66a2a191b`；最新文档 HEAD `fd7b25b86aa3f3bc5f68f474afb1aa92389612be`。CI #2235 运行中、docs-sync #1910 success；Push 触发项未独立核实。每次接手仍必须实时查询当前 HEAD 和四项工作流。
- A52/A55 仅完成部分证据映射，保持 `not_audited`；不继承历史验收勾选。
- **唯一下一步：**按 UXS-2 / PLAN-003 核对 A13、A29、A30、A51–A65 正式验收合同与测试，先裁决费用授权、路由静默回退、API Key 明文存储、未知费用和数据目的地告知的映射关系。先审计，不改产品代码，不新增 A113+。
- P0 候选：`App.create()` 的创意规划调用先于预算确认；P1 风险：模型回退、密钥存储、费用未知状态、请求前数据目的地告知。实际扣费/泄漏未被本轮证明。
- PR #32 保持 Open/unmerged；真实 Provider/代理、账单、Windows 真机、剪映和投放验收继续暂缓；整体完成率关闭。

## PLAN-003 最新状态｜A13/A29/A30/A51–A65 合同对照｜2026-10-16

- 审计基线 `b678560d0f0c97ff7e632ace2be9c39e848edefa`。该 SHA 的 CI PR #2251 与 docs-sync PR #1920 已成功；Push 工作流未独立核实。当前新文档提交的工作流必须重新查询，禁止沿用旧 SHA 绿灯。
- A13/A29/A30/A51–A65 的合同范围、测试证据和状态冲突见 `docs/AD_STUDIO_USER_EXPERIENCE_SAFETY_AUDIT.md`。A13 路由测试只证明九个 create_plan 阶段；A29 数据来源测试不等于外发授权；A30 恢复测试不等于拒绝后零调用；A51 数值校验不等于费用未知语义；账本持久化不等于密钥加密。
- P0 候选：`App.create()` 在预算确认前调用创意规划模型；P1 风险：自动路由回退、API Key JSON 明文保存、未知费用、请求前数据目的地告知。
- **唯一下一步：**核对资产/视频 CapabilityRouter、视觉与转写入口、模型设置 UI，以及缓存/历史模型标识的调用链与测试，继续映射现有 A0–A112；先审计，不改产品代码、不新增 A113+。
- PR #32 不合并；真实 Provider/代理/账单、Windows 真机、剪映和投放继续暂缓；整体完成率关闭。

## PLAN-003 路由与 Provider 入口审计｜2026-10-16

- 审计基线：d48a3af0f68f357c1b32abeb92503a17be7f09aa。该 SHA 的 PR CI #2267 与 docs-sync #1930 曾成功；Push 工作流未独立核实。最新文档提交必须重新检查其 SHA。
- 详见 `docs/AD_STUDIO_USER_EXPERIENCE_SAFETY_AUDIT.md`：`resolve_route()` 可能静默切换模型；视觉分析把关键帧作为 data URI 发往自定义 Base URL；语音转写使用单独 endpoint，且 helper 无条件要求 API Key，与本地无 Key 路由不一致；模型/视频/资产配置以 JSON 保存密钥；缺失 usage/价格按 0 估算但 UI 有非免费提示；自定义资产库路径可能与资产配置文件路径分离，视频/资产历史记录不足以复原实际 endpoint/model。
- **唯一下一步：**把 UXS-2 静态发现转成不联网的 mock 测试矩阵，逐项映射现有 A0–A112：路由回退授权/零调用、预算确认前调用计数、本地转写无 Key、自定义资产库配置路径、各 Provider payload/目的地、未知费用语义、项目重载后的路由可追溯性。合同裁决前不改产品代码、不新增 A113+。
- PR #32 不合并；A0–A112 不删除/合并/重编号，不计算整体完成率。真实 Provider、账单和 Windows 真机继续暂缓。


## UXS-2 首批 mock 修复与当前唯一下一步｜2026-10-16

- 已修复：本地 `local_openai` 转写可无 Key 请求且不添加 Authorization；远程无 Key 在请求前拒绝。自动资产解析改为从应用配置根目录读取 `asset-generation.json`，不随用户自定义 `library_root` 改变。
- 新增测试：本地无 Key 转写成功（mock URL），远程无 Key 零请求，自定义资产库目录下资产配置路径稳定。源码/测试提交 `d6d78cec8368065975aa64cfdd913ec1e152a4c2` 的 CI #2305 与 docs-sync #1958 均通过；其后的文档同步提交必须重新查最新 HEAD 的检查结果。
- 这两项最小修复不代表 UXS-2 完成，不改变 A0–A112 正式状态；没有真实 Provider 请求、账单验证或 Windows 真机测试。
- **唯一下一步：**优先修复 P0 费用授权时序。当前 `App.create()` 在预算确认弹窗前调用 `create_plan/create_plans`，可能先向云端发出规划请求。应先在任何外部模型/Provider 调用前取得明确授权，再在计划生成后显示视频、演员、场景、商品素材的详细费用并取得生成授权。用编排级 mock 计数断言：每个拒绝/取消分支之后文本、视觉、转写、资产、视频调用计数为 0，且没有未确认的新项目落盘。
- 不新增 A113+；不合并 PR #32；A0–A112 不删除/合并/重编号；Windows 真机、真实 Provider/扣费继续暂缓。


## UXS-2 最新状态与下一步｜2026-10-16

- 本地转写：仅 `local_openai` 允许无 API Key，空 Key 请求不附加 Authorization；远程无 Key 在请求前拒绝。
- 资产配置：`ProductionStore.resolve_assets()` 从应用配置根目录读取 `asset-generation.json`，不再随用户自定义资产库目录改变路径。
- 创建前授权：`App.create()` 在商品解析/创意规划前显示当前路由、endpoint、配置单价和潜在回退目标；URL 显示去除 query/userinfo；拒绝后不执行被门控的商品解析操作。计划后详细费用确认仍保留。
- 测试包括：本地转写无 Key、远程无 Key 零请求、自定义资产库路径、拒绝授权零操作、授权信息不暴露 URL query/API Key、源码顺序检查。中间测试夹具失败已经修正，失败历史保留；请从实时最新 HEAD 查询 CI/docs-sync。
- **尚未正式验收：**完整 GUI/各 Provider 运行时调用计数、逐个回退目标的拒绝路径、未知费用语义、实际 endpoint 历史追溯、密钥静态存储保护。
- **唯一下一步：**收紧模型与资产/视频 Provider 自动回退，定义用户逐次允许/拒绝规则；为云→云、云→本地、无可用模型增加 mock 测试，拒绝后外部调用必须为 0，并记录实际目标。之后处理未知费用和端点历史追溯。
- PR #32 Open/unmerged；A0–A112 不删除/合并/重编号；不新增 A113+；真实 Provider/扣费、Windows 真机继续暂缓。

## UXS-2 路由状态更新｜2026-10-16

- 文本/视觉模型：`ModelRouter.resolve_route()` 已改为 fail-closed；所选模型不可用时不再自动切换到另一云端/本地模型。三类离线回归覆盖云→云、云→本地、无可用替代模型。
- 创建授权：已加入前置目的地/配置单价告知与拒绝零操作 helper；计划完成后保留详细费用确认。完整 GUI/各 Provider 运行时调用计数尚未正式验收。
- 资产库路径：自动素材解析读取应用配置根目录的 `asset-generation.json`；本地转写无 Key 仅对 `local_openai` 放行且不发送 Authorization；远程无 Key 仍在请求前拒绝。
- **唯一下一步：**审计 `CapabilityRouter.decide_asset/decide_video` 的本地/云端回退并增加拒绝后零调用 mock；之后处理未知费用语义、endpoint 历史追溯与密钥存储合同。
- PR #32 Open/unmerged；A0–A112 不删除/合并/重编号；不新增 A113+；真实 Provider/扣费、Windows 真机继续暂缓。

## UXS-2 最新接手状态｜2026-10-16

- 单镜头视频生成按钮已增加逐次目的地/费用确认；拒绝时在镜头状态变更前返回，同意后将确认时的 ExecutionDecision 快照传给生产层，避免再次路由。
- 测试覆盖脱敏 endpoint、云端数据边界、取消不改状态的顺序与路由快照传递。
- 当前 SHA bb337ce7be236ad5148a9dd59120defd0efd67e5 尚待 CI/docs-sync。不要把此前 d1f7e54db2f511ba2dde900a14d848657adbbc3d 的绿灯用于当前代码。
- 下一步：资产 Provider 逐次授权。重点检查 ProductionStore.resolve_assets()→AssetGenerator.generate() 和 generate_missing_asset()；授权前不发外部请求，拒绝后 Provider 调用计数为 0、无素材落盘/镜头绑定。随后覆盖批量成片与短剧商品镜头重生成。
- PR #32 保持 Open/unmerged；A0–A112 不新增/删除/合并/重编号；真实 Provider/扣费与 Windows 真机继续暂缓。

## UXS-2 资产授权闸门接手说明｜2026-10-16

- 资产云端生成层已要求 authorize_cloud 回调；无回调/拒绝时不调用云端 Provider、不创建生成文件、不绑定资产/改镜头状态。
- 该回调尚未接入正式 UI，因此云端资产自动生成目前 fail-closed；本地服务路径仍可使用。
- 单镜头视频已有端点/费用确认与确认时路由快照传递。
- 当前 SHA 77ccc7a6e978fc8c6144a18b8f2958bf981ad2d6 的 CI/docs-sync 待最终结果；此前首轮 CI 失败是旧测试夹具不兼容与目录创建假设错误，已修正。
- **下一步：**接入资产 Provider 授权 UI；展示脱敏 endpoint、数据类别、配置价格与未知费用提醒；拒绝时 Provider 调用为 0，且没有素材文件、资产库记录、镜头 ID/状态变化。之后覆盖批量视频与短剧商品镜头重生成。
