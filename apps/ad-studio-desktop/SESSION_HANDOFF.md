# 【当前接手入口｜2026-10-15｜规划控制体系优先】

- 仓库：`konggu888/ecommerce-agent`；项目：`apps/ad-studio-desktop`；分支：`feat/product-drama-visual-review`；PR #32 必须保持 Open / unmerged。
- **唯一权威进度与下一项**：`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`。当前进入 PLAN-003 全量跨来源语义去重、状态冲突裁决与依赖/证据边界复核；A0–A112 台账及分批静态映射已存在，不能重建或重复从 A50 开始。
- 本轮修改前 HEAD：`9b514be490a56037c0ff4c700ac3084ea5180793`；该 SHA 的 PR-triggered CI/doc-sync 状态应以实时 Actions 查询为准。Push-triggered 两项未由当前查询独立核实。提交后必须重新检查新 HEAD。
- 本轮不开发产品功能，不继续 UXS-2 专项细节，不删/重编号 A0–A112，不赋权、不计算总体完成率。真实 Windows、真实素材、Provider/扣费、剪映现场、真实投放与商业效果验证继续暂缓。
- **七层结果证明标准已纳入全项目证据规则**：软件运行、功能行为、端到端流程、普通用户可用、商品表达真实安全、商业成片质量、真实商业效果；详细定义和禁止替代关系见总进度台账及执行控制协议。台账规范化时逐项映射，不新增正式验收 ID。
- **用户自由度已纳入 PLAN-003**：规范化 A0–A112 台账时必须映射选择/控制/知情/撤回纠正四个维度，核对模型与 Provider 选择、自动回退授权、数据外发告知、费用不确定性、密钥保存、缓存/历史隔离及取消后外部调用为零的证据。详见 UXS-2 与执行控制协议；不新增正式验收 ID，不启动产品功能开发。
- 下方历史快照仅供追溯；其中的旧 SHA 和“下一项”不得作为当前执行指令。冲突以总进度台账为准。

---

# 【历史接手快照｜UXS-2 用户旅程证据映射｜2026-10-15｜不可覆盖总进度台账】

- 审查入口：`docs/AD_STUDIO_USER_EXPERIENCE_SAFETY_AUDIT.md`；本轮已完成“创建入口、商品输入、费用授权顺序、项目持久化”的首轮静态证据映射（第 3A 节）。这是审计，不是新产品功能开发。
- 首个重要合同/证据冲突候选：`App.create()` 在显示 `AI创意与项目预算确认` 前调用 `create_plan/create_plans`；`ModelRouter.create_plan()` 对九个阶段调用 `complete_json()`。HELP/PROJECT_LOGIC 当前允许确认前进行 AI 分析，但用户费用授权范围是否覆盖收费规划模型调用尚待裁决。若所有收费云端模型调用都必须先确认，则是 P0 候选阻断；若只限制视频/资产生成 Provider，则需核实规划调用费用是否披露/计入预算。实际收费影响依赖模型路由，当前未修复、未新增验收编号、未改产品代码。
- 已查测试证据：`test_setup_form_grid_rows_do_not_overlap` 为 AST 布局检查；`test_product_parser.py` 覆盖解析器异常/回退；`test_budget_policy` 与 `test_cost_breakdown_is_auditable_and_configurable` 覆盖费用计算；`test_project_save_load`、`test_project_lifecycle_isolated_between_projects` 覆盖持久化/隔离。未发现 `test_desktop.py` 直接调用 `App.create()` 的测试；`test_a33_full_flow.py` 仅测试模拟最终交付，不证明创建前确认顺序。
- 本文件已与 UXS-2 首轮映射、进度台账和 AI handoff 同步；最新审查文档 SHA 需以 GitHub 分支实时 HEAD 为准。开始基线 `3bd083e73ea51aec26b2ab66c755aa6c83a929cf` 的 PR CI `38695479000` 与 PR docs-sync `38695478983` success；Push-triggered 两项未独立核实。每次新提交后重查可用的当前 SHA 工作流。
- 上述 UXS-2 任务文字属于历史接手快照，不能覆盖总进度台账。当前唯一任务以 `docs/AD_STUDIO_PROGRESS_DASHBOARD.md` 顶部为准：PLAN-003 全量跨来源关系/状态冲突裁决。只审计和记录；不得删/重编号 A0–A112，不计算总体完成率。
- 状态口径保持：`code_test_evidence_reviewed_ids=113` 仅表示已开始映射；`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false`。Windows 真机、真实素材、Provider/实际扣费、剪映现场和真实投放/商业效果验证继续暂缓；PR #32 不合并。

---

# 【PLAN-003 最新接手状态｜A100–A112 部分证据映射｜2026-10-15】

- 本轮开始基线 `14ac6d153cf2f9027d02ff71a82ff8facc643768`：CI Push、CI PR、docs-sync Push、docs-sync PR 四项均 success；PR #32 Open / unmerged。新提交后必须重查最新 SHA 的四项工作流。
- 本轮完成 A100–A112 静态代码/测试证据映射；全部仅部分映射，不代表每项正式验收完成。台账 `code_test_evidence_reviewed_ids=113`（A0–A112 均已开始映射），`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false`。
- 重点裁决：A100/A101/A103 单镜头淡化与音画同步分开；A104 是跨镜头 xfade/acrossfade；A105/A106/A107 分别是 pacing、角色决策、运行时字段执行；A108 字幕生成与 A112 实际 cue 保护分开；A109/A110/A111/A112 的音乐卡点链路仍保留独立合同。1080P 输出尺寸不等于真实细节增强。
- 已找到专项测试线索：A100–A103 在 test_postprocess.py；A104 在 test_ffmpeg.py；A105–A107 在 test_creative_engine.py；A108 在 test_subtitles.py；A109–A112 在 test_music_sync.py；最终 1080P/媒体 QC 在 test_desktop.py。所有这些仍是静态证据映射，真实素材、Windows、真实口播/听感和商业质量暂缓。
- 下一步唯一主任务：全量跨来源去重与状态裁决，对照 A0–A112 正式验收计划、路线图、未来功能备忘、验收 SOP、任务登记表和执行控制文档；核对重复段落、转义换行和历史状态冲突。不得删 ID、补造编号、计算总体完成率或开发新产品功能。

---

# 【PLAN-003 最新接手状态｜A83–A99 部分证据映射｜2026-10-15】

- 本轮开始基线：`a2dd27fa6df1fb17cdaf2914b7633649809bd901`；CI Push、CI PR、docs-sync Push、docs-sync PR 四项均 success。新提交之后必须按最新 SHA 重查四项检查。PR #32 保持 Open / unmerged。
- 本轮完成 A83–A99 静态代码/测试/文档证据映射；全部仅部分映射，不宣称正式验收完成。台账 `code_test_evidence_reviewed_ids=100`、`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false`。
- 重要裁决：A83/A84 单集与跨集承诺承接分开；A85/A86/A87 状态持久化、因果闭环、可观察表演分开；A88 多人物依赖独立于可选状态台账；A89–A96 文本锁定/物理 ID/失效保护/恢复重试分层；A97/A98 恢复摘要稳定性分开；A99 成功账本下清除未计费兄弟镜头陈旧成本，和 A57/A59 相关但不合并。
- A84–A87 计划仍有未勾选项；A89–A96 的通过记录来自历史 SHA，当前 HEAD 需重新验证；A97/A98/A99 的直接测试名已找到，但要确认所有断言及当前 SHA 运行结果。A88 计划/逻辑文档中的重复段落与字面量转义换行已在本轮统一清理；仍需按最新 SHA 检查文档同步和 CI。
- 下一步：完成新 SHA 四项 CI/doc-sync 检查；全绿后继续 A100–A112 并检查商业剪辑专项/A102 1080P 条款。若失败先读日志修复。不得开发新产品功能、不得计算总体完成率；真实 Provider/扣费、Windows 真机、真实素材、剪映与真实投放继续暂缓。

---

# 【PLAN-003 最新接手状态｜A68–A82 部分证据映射｜2026-10-15】

- 本轮开始基线：`c6c6294f0d1626cf6a8f65ccd364ae476a2e5520`；CI Push、CI PR、docs-sync Push、docs-sync PR 四项均 success。提交新 SHA 后必须重新查询四项检查。PR #32 保持 Open / unmerged。
- 本轮已对 A68–A82 完成静态代码/测试/文档证据映射，全部仅部分映射。台账 `code_test_evidence_reviewed_ids=83`、`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false`。
- 主要证据：A68 后续集影响报告；A69/A70 故事引擎与结构审查；A71/A72 备选方向和人物动机；A73/A74 因果链与文本证据；A75/A76 商品事实/卖点覆盖；A77–A82 镜头事件、行动依据、人物绑定、关系变化、状态连续性和知识时间线。
- 重要缺口：A77–A80 在正式验收计划中仍有未勾选/开发中状态。不得因逻辑文档写有实现说明、测试文件里有相关用例或旧 SHA CI 曾绿，就改写为当前验收完成；需逐项核验专门正反例、调用链和最新 SHA 证据。A81/A82 的历史 SHA 记录不自动替代当前 HEAD 证据。
- 下一项：完成新 SHA 四项 CI/doc-sync 核验；全绿后继续 PLAN-003 A83–A99。若失败先查日志修复。不得开发新产品功能、不得计算总体完成率；真实 Provider/账单、Windows 真机、真实素材、剪映和真实投放继续暂缓。

---

# 【PLAN-003 最新接手状态｜A50–A67 部分证据映射｜2026-10-15】

- 本轮开始基线：`707758608e105840f21d4945aa40b3eb89b00522`；该 SHA 的 CI Push、CI PR、docs-sync Push、docs-sync PR 均 success。新提交 `707758608e105840f21d4945aa40b3eb89b00522` 之后，四项新 SHA 工作流尚待核验；不要沿用旧 SHA 的绿灯结论。PR #32 保持 Open / unmerged。
- 本轮对 A50–A67 完成静态证据映射，全部只是部分映射，不宣称正式验收通过。台账 `code_test_evidence_reviewed_ids=68`、`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false`。
- 关键证据：A50/A56 提示词真实换行行为合同与后续回归修复；A51 费用预估输入校验；A52 失败尝试成本去重；A53/A54 旧视频有效性与恢复；A55/A57/A59/A60/A61/A63/A64/A65 成本账本/恢复/迁移保护；A66/A67 人工视觉证据有效性与失效复查。
- 保留裁决：A50/A56 不合并；A57 在正式计划中有两个独立场景（成本待核对 UI、项目恢复与成本对账）；A61/A62 不合并。A66 文件校验不能代替商品真实性判断，A67 历史 passed 状态不能覆盖证据失效。
- 下一项：完成新 SHA 的四项 CI/doc-sync 检查；全部成功后继续 PLAN-003 A68–A82。若失败先读取日志并修复。不得开发新产品功能、不得计算整体完成率；真实 Provider/账单、Windows 真机、真实素材、剪映与真实投放继续暂缓。

---

# 【PLAN-003 最新接手状态｜A34–A49 部分证据映射｜2026-10-15】

- 当前最新提交：`b48f7a9859476ed639bc9220035c986cd5e77c37`；该 SHA 的 CI Push、CI PR、docs-sync Push、docs-sync PR 四项均成功；PR #32 Open / unmerged。
- 本轮已对 A34–A49 做静态代码/测试/文档证据映射，全部仅部分映射，不宣称正式验收通过。台账 `code_test_evidence_reviewed_ids=50`、`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false`。
- 重点证据：A34 AI 视觉对比的差异拦截/不自动批准/输入校验测试；A35/A36 单镜头修复、可编辑草稿与费用/版本防护；A43–A49 旧视频恢复、稳定短剧镜头映射、失败状态 UI、素材解析失败、裁剪安全输出与多段临时文件清理测试。
- 仍需逐项确认实际调用链、失败边界、UI 状态、跨项目/跨镜头隔离和每项直接断言；相关任务不因链路相连而合并。A37 草稿换行不等同于 A50/A56 视频提示词换行回归。
- 注意：接手文档下方有历史 SHA、PR 状态与旧任务指令，均为历史记录；新会话以本段、实时 GitHub HEAD/PR/四项 CI 和进度台账为准。PR #32 不合并。
- 唯一下一项：PLAN-003 继续 A50–A67 代码/测试证据审计，特别保留既定的 A50/A56、A57 内两个独立场景、A61/A62 不合并裁决。暂不开发产品功能、不计算整体完成率；Windows 真机、真实素材、真实 Provider/扣费、剪映和真实投放继续暂缓。

---

# 【PLAN-003 当前进度｜2026-10-15｜本段优先于下方历史记录】

- 最新完整核验基线（本次接手前）：`1fd6d08dac970cb7886c59239b05c4f6e2128cf9`；CI Push `38691577983`、CI PR `38691582839`、docs-sync Push `38691577999`、docs-sync PR `38691582806` 均 success。PR #32 当前 Open / unmerged；任何新提交后必须重新核验四项结果。
- A0–A5 本轮证据映射（未正式验收）：A0 `App.create()` 入口存在，缺专门启动/创建 UI 操作覆盖；A1 缺任务级稳定性矩阵；A2 有项目隔离与 save/load 测试，缺直接 `App.create()` 编排测试；A3 有布局 AST、三类任务策略和 task_type 持久化测试，完整 UI 流程未验收；A4 有扫描、不可解析素材记录、重复素材评分、废片归档及保护引用源文件测试，覆盖矩阵仍不完整；A5 已实现关键帧提取/视觉清单，但已检查的 desktop `test*.py` 未发现 `extract_keyframes()` / `build_visual_manifest()` 专项测试，视觉分析失败回退也待核验。

---

---

# 【最新接手指令｜规划体系优先｜2026-10-14】

- 规划体系实施前 HEAD：`7cfabb23e9ab0c05c6189d31dcf6b7410f7934c7`；该 SHA 的 CI Push 38571014259、CI PR 38571022693、docs-sync Push 38571014277、docs-sync PR 38571022758 均 success。规划体系新提交后必须重新查询 HEAD 与四项工作流。
- PR #32 保持 Open / unmerged。Windows 真机、真实素材、真实 Provider/扣费、剪映现场、真实投放数据继续暂缓。
- 用户已批准先建立完整计划与 AI 执行控制体系。执行协议：`docs/AD_STUDIO_EXECUTION_CONTROL.md`；总进度：`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`；战略路线图：`docs/AD_STUDIO_PRODUCT_ROADMAP.md`。
- A112 已完成自动化阶段；下方“下一项 A112”等旧文字均为历史记录，不得用作当前指令。
- 当前唯一任务：PLAN-003，全量盘点 A0–A112、路线图任务、未来功能备忘和 SOP 检查点；去重映射、核验代码/测试/当前 SHA 证据。完成前不计算整体完成百分比。
- 每轮开始前重新检查当前 HEAD、PR #32 和 CI Push、CI PR、docs-sync Push、docs-sync PR；一次只执行一个有明确停止条件的任务。
- 桌面代码变更同一提交同步八份强制文档；规划变更同步所有受影响入口，避免无意义重复提交。

---

# 【最新接手状态｜A112 自动化 CI 已通过｜2026-10-14】

- 仓库：konggu888/ecommerce-agent；分支：feat/product-drama-visual-review；PR #32 保持 open/unmerged。
- 当前已完成 A112：SRT 实际 cue 时间窗在证据有效时进入音乐卡点内容保护；缺失/损坏/越界/版本不匹配时安全回退。经修正后代码基线 SHA e8deb1ec4ef9edf7d999c79539762ea2627affab 的 CI Push、CI PR、docs-sync Push、docs-sync PR 四项均 success。任何后续提交必须重新检查新 SHA。
- A112 代码基线 SHA e8deb1ec4ef9edf7d999c79539762ea2627affab 四项检查均 success：CI Push 38570453607、CI PR 38570460103、docs-sync Push 38570453565、docs-sync PR 38570460195。后续提交必须重新核验。
- 首轮 A111 CI 曾失败 3 个旧断言，根因是断言仍要求整组回退，与 A111 局部回退设计冲突；修复测试预期与审计原因后，最终 SHA 四项检查全部成功。没有隐瞒中间失败。
- 代码、测试与八份强制文档/路线图已同步。A112 自动化阶段完成；下一步先复核阶段 2 剩余退出条件与路线图，不将自动化绿灯误当作商业成片验收。
- Windows 真机、真实素材、真实 Provider/扣费、剪映现场、真实听感和商业效果仍暂缓。PR #32 不合并。

---

---

---

---

---

---

# 【历史接手状态｜2026-10-14｜已由文件顶部 PLAN-003 当前状态取代】

> 本段优先级高于下方旧历史记录；如果下方内容提到旧 PR、旧 SHA 或旧任务，请以本段和 GitHub 实时状态为准。

## 历史路线图执行指令（2026-10-14；当前执行以文件顶部 PLAN-003 为准）
- 唯一战略路线图：`docs/AD_STUDIO_PRODUCT_ROADMAP.md`。所有 AI 接手后必须按该路线图执行，不可直接沿用旧备忘录里的开发顺序。
- 历史基线为 `83549d4ca428adc233d61da292e2f245d498da0d`；该记录仅供历史追溯，不是当前 HEAD。当前最新完整核验基线为 `464977a54e9784fff375ffe081985624688261e9`，四项 CI/doc-sync 均 success。
- 历史主攻记录：阶段 2“商业级剪辑决策层”；A109“音乐节拍与画面切点真实联动”已提交自动化实现。该记录不覆盖当前 PLAN-003；接手者先检查最新 HEAD、完整 CI 与 docs-sync，再修复任何失败。实现涉及项目级统一 BGM、节拍分析、实际镜头时长计划、同步变速、拼接后统一混音和 1080P 输出；真实音乐/口播/Windows 质量验收仍暂缓。
- A108 是字幕基础时间轴与密度风险提示，不代表语义口播对齐、真实画面可读性或商业成片质量已验收。
- PR #32 保持 open/unmerged。Windows 真机、真实素材、真实 Provider/扣费、剪映现场与真实投放数据验证继续暂缓。

- 仓库：`konggu888/ecommerce-agent`
- 项目：`apps/ad-studio-desktop`
- 分支：`feat/product-drama-visual-review`
- 商业剪辑焦点定位功能提交：`fe3dcfde8e78f7d5d079fcbc1ed99d6265a79dbb`
- 该功能提交对应的 CI push、CI PR、docs-sync push、docs-sync PR 均已 success；此后若 HEAD 有变化，必须重新检查最新 SHA 的四项结果。
- PR #32 保持 open/unmerged，未经用户明确许可不得合并。
- 用户最新优先级：暂停费用对账/单镜头重试保护检查线，继续推进未来路线图第 5 项“商业级剪辑决策层升级”。
- 用户新增硬性画质要求：最终导出最低为 1080P 级。A102 已实现最终拼接后统一归一化转码：9:16 1080×1920、16:9 1920×1080、1:1 1080×1080，并由 ffprobe 拒绝低于该尺寸的交付结果。注意这保证像素尺寸，不代表已实现 AI 超分/细节恢复；A102 当前 SHA 的 CI/doc-sync 需检查。
- 已完成的小步：修正 `focus_x/focus_y` 语义，让它们表示缩放后源画面中的主体/视觉焦点归一化位置；裁切窗口在合法边界内尽量将焦点放到输出画面中心。新增 `test_postprocess.py` 检查实际 FFmpeg 参数、边界夹紧及非法/非有限输入回退。
- 商业剪辑决策层 A106 已新增：`resolve_editing_intent()` 根据分镜文本角色补齐缺省时长/节奏/转场，并将理由与参数来源存入 `editing_intent`；显式参数优先。A106 基线 `884c45dd8524abf4c4ebf7ee7fc8daa67987f686` 的 CI Push/PR 与 docs-sync Push/PR 均 success；A107 本轮修改提交后必须重新核验四项。
- 本轮目标不是宣称商业剪辑整体完成。文本关键词规则不等于画面理解；画面驱动节奏、音乐卡点、字幕密度、商品展示节奏和剪后反馈仍待开发/验收。
- 这只是“焦点参数真正影响裁切”的单项修复，**不是商业剪辑整体完成**。下一步应建立/完善可追溯的商业剪辑决策层：解释镜头商业角色、选择理由、节奏/时长理由、转场理由，并保证决策确实影响实际执行；后续再做字幕信息密度、音乐卡点、镜头衔接与剪后反馈。
- 先读本段，再读 `docs/AD_STUDIO_AI_HANDOFF.md`、`PROJECT_LOGIC.md`、`HELP.md`。每次代码修改必须同步 HELP、PROJECT_LOGIC、本文件、验收计划、验收 SOP、AI handoff 和未来功能备忘。
- Windows 真机、真实 Provider/实际扣费、剪映现场验收继续按用户要求暂缓；不得把 CI 绿灯或命令字符串测试等同于真实商业成片质量验收。

---

# SESSION_HANDOFF.md — 桌面项目跨会话接手入口

> **新会话必须先读本文件，再读 `docs/AD_STUDIO_AI_HANDOFF.md`、`PROJECT_LOGIC.md` 和 `HELP.md`。** 本文件记录当前工作现场，不代表功能已验收。

## 当前仓库状态
- 仓库：`konggu888/ecommerce-agent`
- 项目：`apps/ad-studio-desktop`（本地 Python/Tkinter 桌面程序，不是 Web 应用）
- 工作分支：`feat/product-drama-visual-review`
- 最近一次完整 CI 与 docs-sync 均验证通过的 SHA：`d976c34a48ff20af65648983be7855589ba2deca`（CI run `38162555687`、docs-sync run `38162555622` 均 success；后续提交必须重新验证最新 SHA）。
- PR：[#31](https://github.com/konggu888/ecommerce-agent/pull/31)，保持 open、未合并；没有用户明确许可不得合并。
- `443f713cd3721eab528eb9bb17faf599d55ef3ce` 的完整 CI 已成功：前端语法、桌面 Python 语法、桌面单测、TypeScript 检查、引擎测试和风险控制器测试均通过；同一 SHA 的 docs-sync 也成功。已将 `.github/workflows/ci.yml` 的 push 触发范围改为所有分支。任何后续提交都必须按最新 SHA 重新核实，不能把此基准结果直接套用到新 SHA。

## 最近完成
1. 商品短剧支持人工视觉核验，证据绑定具体生成图片/视频文件。
2. 支持视觉模型对照商品参考图与生成图片/视频抽帧；AI 未发现明确问题时也只进入待人工复核，不自动批准。
3. 商品短剧支持只修复所选镜头：用户写明修正要求、先确认费用；保留旧版本/旧视频/核验历史，新版本重置为 `not_checked`。
4. A36：从上次视觉比对摘要与问题列表预填可编辑修正草稿；费用必须是有限非负数，旧版本号必须有效。
5. A37：修正草稿使用真实换行；有回归断言。
6. 已同步 HELP、PROJECT_LOGIC、完整验收计划/SOP、AI handoff 和未来功能备忘；文档同步检查通过。

## 本轮必须继续做的事
1. 先重新读取 GitHub 当前 branch HEAD 和 PR #31，不要假设 HEAD 未变化。
2. 查看当前 HEAD 的 GitHub Checks/Actions；确认完整 CI 是否运行。若没有运行，查明触发原因并通过受支持方式让完整 CI 对当前提交执行；不能用旧 SHA 的 CI 冒充当前结果。
3. 审查并实际运行 `python3 -m unittest discover -s apps/ad-studio-desktop -p 'test_*.py'`、`python3 -m compileall -q apps/ad-studio-desktop/ad_studio`（若当前执行环境可访问仓库）；否则明确说明未运行，不要声称通过。
4. 继续核对 AI 视觉比对异常处理、单镜头重生成的版本映射/保存/成本记账，以及失败后恢复；只处理问题镜头，不重生成整部短剧。
5. 每次改代码，同一提交同步 HELP.md、PROJECT_LOGIC.md、验收计划、验收 SOP、接手文件和未来功能备忘，并增加回归测试。
6. PR 保持 open/unmerged。Windows 真机、真实视频 Provider/真实扣款、剪映现场验收仍按用户要求暂缓。

## 不得误报的边界
- 文档同步通过 ≠ 全量 CI 通过。
- 单元测试未执行 ≠ 测试通过。
- AI 视觉比对不是商品真实性认证；最终需人工核验。
- 当前实现不是已经验收的商业成片流程；真实机器/Provider 验收仍待后续。


## A39：CI 触发范围
CI 的 push 触发器现覆盖所有分支；每次提交后仍须查询当前 SHA 的 checks，等待完整 `typecheck-and-test` 工作流结束。此项改动本身的完整 CI 结果待当前提交的工作流返回。


## A40：已解决的 CI 路径失败
完整 CI 曾因 `test_ai_handoff.py` 的仓库根目录相对路径错误失败；现已修复为 `ROOT / "docs" / ...` 和 `ROOT / "apps" / "ad-studio-desktop" / ...`，并在 SHA `443f713cd3721eab528eb9bb17faf599d55ef3ce` 上完整 CI 成功。


## A41：已解决的文案断言
路径修复后曾剩下一个断言短语与文档不一致；已将测试改为匹配实际文案“不要把 docs-sync”，并在 SHA `443f713cd3721eab528eb9bb17faf599d55ef3ce` 上完整 CI 成功。


## A42：最新完整 CI 结果
完整 CI `38120824822` 在基准 SHA `443f713cd3721eab528eb9bb17faf599d55ef3ce` 结论为 success；docs-sync `38120824802` 也为 success。该结果覆盖：前端语法检查、桌面 Python 语法检查、桌面单元测试、TypeScript 类型检查、引擎测试和风险控制器测试。若当前 HEAD 与此 SHA 不同，必须重新查询当前 HEAD 的结果。

# SESSION_HANDOFF.md — 桌面项目跨会话接手入口

> **新会话必须先读本文件，再读 `docs/AD_STUDIO_AI_HANDOFF.md`、`PROJECT_LOGIC.md` 和 `HELP.md`。** 本文件记录当前工作现场，不代表功能已验收。

## 当前仓库状态
- 仓库：`konggu888/ecommerce-agent`
- 项目：`apps/ad-studio-desktop`（本地 Python/Tkinter 桌面程序，不是 Web 应用）
- 工作分支：`feat/product-drama-visual-review`
- 最近一次完整 CI 验证通过的基准 SHA：`443f713cd3721eab528eb9bb17faf599d55ef3ce`（当前分支若有新提交，必须重新查询并验证最新 SHA）。
- PR：[#31](https://github.com/konggu888/ecommerce-agent/pull/31)，保持 open、未合并；没有用户明确许可不得合并。
- `443f713cd3721eab528eb9bb17faf599d55ef3ce` 的完整 CI 已成功：前端语法、桌面 Python 语法、桌面单测、TypeScript 检查、引擎测试和风险控制器测试均通过；同一 SHA 的 docs-sync 也成功。已将 `.github/workflows/ci.yml` 的 push 触发范围改为所有分支。任何后续提交都必须按最新 SHA 重新核实，不能把此基准结果直接套用到新 SHA。

## 最近完成
1. 商品短剧支持人工视觉核验，证据绑定具体生成图片/视频文件。
2. 支持视觉模型对照商品参考图与生成图片/视频抽帧；AI 未发现明确问题时也只进入待人工复核，不自动批准。
3. 商品短剧支持只修复所选镜头：用户写明修正要求、先确认费用；保留旧版本/旧视频/核验历史，新版本重置为 `not_checked`。
4. A36：从上次视觉比对摘要与问题列表预填可编辑修正草稿；费用必须是有限非负数，旧版本号必须有效。
5. A37：修正草稿使用真实换行；有回归断言。
6. 已同步 HELP、PROJECT_LOGIC、完整验收计划/SOP、AI handoff 和未来功能备忘；文档同步检查通过。

## 本轮必须继续做的事
1. 先重新读取 GitHub 当前 branch HEAD 和 PR #31，不要假设 HEAD 未变化。
2. 查看当前 HEAD 的 GitHub Checks/Actions；确认完整 CI 是否运行。若没有运行，查明触发原因并通过受支持方式让完整 CI 对当前提交执行；不能用旧 SHA 的 CI 冒充当前结果。
3. 审查并实际运行 `python3 -m unittest discover -s apps/ad-studio-desktop -p 'test_*.py'`、`python3 -m compileall -q apps/ad-studio-desktop/ad_studio`（若当前执行环境可访问仓库）；否则明确说明未运行，不要声称通过。
4. 继续核对 AI 视觉比对异常处理、单镜头重生成的版本映射/保存/成本记账，以及失败后恢复；只处理问题镜头，不重生成整部短剧。
5. 每次改代码，同一提交同步 HELP.md、PROJECT_LOGIC.md、验收计划、验收 SOP、接手文件和未来功能备忘，并增加回归测试。
6. PR 保持 open/unmerged。Windows 真机、真实视频 Provider/真实扣款、剪映现场验收仍按用户要求暂缓。

## 不得误报的边界
- 文档同步通过 ≠ 全量 CI 通过。
- 单元测试未执行 ≠ 测试通过。
- AI 视觉比对不是商品真实性认证；最终需人工核验。
- 当前实现不是已经验收的商业成片流程；真实机器/Provider 验收仍待后续。


## A39：CI 触发范围
CI 的 push 触发器现覆盖所有分支；每次提交后仍须查询当前 SHA 的 checks，等待完整 `typecheck-and-test` 工作流结束。此项改动本身的完整 CI 结果待当前提交的工作流返回。


## A40：已解决的 CI 路径失败
完整 CI 曾因 `test_ai_handoff.py` 的仓库根目录相对路径错误失败；现已修复为 `ROOT / "docs" / ...` 和 `ROOT / "apps" / "ad-studio-desktop" / ...`，并在 SHA `443f713cd3721eab528eb9bb17faf599d55ef3ce` 上完整 CI 成功。


## A41：已解决的文案断言
路径修复后曾剩下一个断言短语与文档不一致；已将测试改为匹配实际文案“不要把 docs-sync”，并在 SHA `443f713cd3721eab528eb9bb17faf599d55ef3ce` 上完整 CI 成功。


## A42：最新完整 CI 结果
完整 CI `38120824822` 在基准 SHA `443f713cd3721eab528eb9bb17faf599d55ef3ce` 结论为 success；docs-sync `38120824802` 也为 success。该结果覆盖：前端语法检查、桌面 Python 语法检查、桌面单元测试、TypeScript 类型检查、引擎测试和风险控制器测试。若当前 HEAD 与此 SHA 不同，必须重新查询当前 HEAD 的结果。


## A44：短剧镜头映射防漂移（待本轮 CI）
新建短剧制作项目时保存 `short_drama_shot_number`；重生成/修正草稿不再盲用项目显示序号。旧项目仅在标题和集数唯一时回退定位，歧义则拒绝操作。本轮新 SHA 的完整 CI/doc-sync 尚待确认。


## A45：失败恢复状态显示
已修复桌面 UI 在 Provider/实拍裁剪失败后无条件覆盖状态、导致“已保留上一版本”提示丢失的问题。新 UI 状态判断同时检查恢复标记和旧版文件是否存在且非空；当前提交后的 CI/doc-sync 必须按新 SHA 查询。


## A46：编辑镜头也保留上一版（待当前 SHA CI）
发现编辑窗口保存镜头时仍直接清空 `video_path` 并递增版本，没有把旧路径保存到 `previous_video_path`，会绕过 A43 的失败恢复保护。现改为复用 `mark_regenerate()`，并添加 UI 集成路径回归断言。提交后必须重新查询完整 CI 与 docs-sync；PR #31 仍保持 open/unmerged。


## A46：CI 文案断言修复记录
SHA 2450e2d5b74bba26cd76ac3ef3ef5639499523f2 的完整 CI 暴露 1 个 handoff 测试断言：测试要求 AI 接手文档明确包含“旧版视频”，而原句只写“旧视频路径”。现已把接手文档改为“旧版视频文件路径”，保留测试断言与旧版保护语义。必须等待新 SHA 的完整 CI 和 docs-sync 结果后再确认 A46 自动化验收。


## A47：素材解析失败恢复（待当前 SHA CI）
已把视频生成前的素材解析步骤纳入旧版本恢复边界，防止素材自动生成/匹配阶段报错时留下空的活动视频路径。输出替换也不再先删除目标文件。新增测试覆盖素材解析失败、Provider 不被调用及旧视频重载仍存在。当前提交需重新检查完整 CI 与 docs-sync。


## A48：实拍裁剪旧文件保护（待当前 SHA CI）
实拍镜头现在先写同目录临时输出，确认文件非空后再替换正式成片；裁剪失败只清理临时片段并恢复旧版路径。新增失败模拟测试，验证旧文件内容和项目重载路径保持不变。提交后需查询当前 SHA 的完整 CI 与 docs-sync。


## A49：多段实拍中断清理（待当前 SHA CI）
项目恢复清理规则已扩展到多段裁剪产生的 `.partNN.mp4`；素材源缺失时也会清理遗留分段文件，并保留有效旧视频。新增中断恢复与素材缺失回归测试。当前提交后需按最新 SHA 查询完整 CI 和 docs-sync。


## A50：视频提示词换行回归（待本轮 CI）
检查 A47 的生成异常边界重构时发现 prompt 被改成字面量反斜杠+n，已修复并新增捕获 Provider 请求的测试。A49 在 SHA 953e40694aa2a28b2d164fc49800c639b45bebb8 的完整 CI 与 docs-sync 已通过；A50 的新 SHA 仍待完整 CI/doc-sync。


## 最新 CI 基准（A47–A50）
- 代码 SHA：`58de7ce984cf9df73bad2c99444d75a0624059c3`
- 完整 CI：success，覆盖桌面 Python 语法、桌面核心测试、TypeScript、Engine 和 Risk Controller：https://github.com/konggu888/ecommerce-agent/actions/runs/38121500267
- docs-sync：success：https://github.com/konggu888/ecommerce-agent/actions/runs/38121500259
- A47–A50 自动化阶段通过；Windows 真机、真实 Provider、真实素材和实际扣款仍暂缓。
- 以上是代码基准提交的结果。任何新的提交都必须重新查询最新 HEAD 和对应工作流。


## A51：费用预估前置校验
A47–A50 的自动化 CI 与 docs-sync 已在代码 SHA `58de7ce984cf9df73bad2c99444d75a0624059c3` 的完整工作流中通过。A51 新增局部重生成费用弹窗前报价校验；必须检查本次提交的新 SHA 和工作流，不能把之前的绿灯直接沿用。


## A52：失败尝试账本与成本去重（待本轮 CI）
A52 为视频 Provider 失败调用增加本地账本记录；失败报价不计入实际花费，成功重试独立记录且实际成本只计成功记录。新增失败+成功重试回归。新 SHA 的完整 CI/doc-sync 尚待确认；真实 Provider 的超时扣款/账单对账仍暂缓。

## A53：恢复时拒绝零字节旧视频（待验收）
发现恢复逻辑只将“文件不存在”视为旧版失效，没有处理“文件存在但大小为零”的情况。现已改为只恢复真实存在且非空的上一版视频；否则清除无效路径、加入 `missing_media` 并标记待重新生成，新增持久化回归测试。必须重新查询本次提交的完整 CI 与 docs-sync，不能沿用 A52 的结果。

## A54：活动视频零字节恢复保护（待验收）
进一步复查发现，A53 只覆盖上一版路径为零字节的情况，活动 `video_path` 自身若指向零字节文件也可能被当作存在的输出。现将活动文件检查改为“是文件且非空”；若旧版有效则恢复旧版，无旧版则清除无效路径并标记待重新生成。新增两项回归测试，本次提交必须重新跑完整 CI 与 docs-sync。


## A55：Provider 成功后账本故障保护
A51 费用预估校验、A52 失败尝试账本、A53 零字节旧版拒绝和 A54 活动视频零字节校验均已在验收计划记录的 SHA 上通过完整 CI/doc-sync。A55 将 Provider 有效输出安装与成本记账分离；账本异常时保留已生成视频、标记“成本待核对”并写恢复记录，不误报 Provider 失败。A55 当前 SHA 的 CI/doc-sync 需重新确认。


## A56：提示词换行回归修复（待本轮 CI）
SHA 18b958a269757781af4f062211d2a54485658e6e 的 CI 因 test_a50_video_prompt_uses_real_line_breaks 失败，确认 A55 重构把分隔符再次改成字面量反斜杠+n。已恢复真实换行；新 SHA 的完整 CI/doc-sync 尚待确认。

## A57：成本待核对 UI 对齐（待验收）
A55 已把有效新视频与成本记账异常分离，A56 修复了提示词换行回归。继续审查发现，桌面 `generate_shot()` 在返回后仍无条件展示“项目实际累计”，即使镜头状态是“已生成（成本待核对）”。现加入状态分支：待核对时显示明确提醒与账本路径提示，正常累计数字仅在成本状态正常时显示。新增 UI 回归测试，当前 SHA 的完整 CI/doc-sync 待确认。


## A57：打开项目自动恢复与成本对账（待本轮 CI）
此前 recover_project() 没有 UI 调用入口。A57 将它接入“打开已有项目”，显示恢复摘要，并按成功用量账本同步项目/镜头实际成本；没有账本记录的旧项目保留旧成本。当前 SHA 的完整 CI/doc-sync 尚待确认。

## A58：视觉核验输入格式保护（待验收）
A57 的项目打开恢复与成本对账已在 SHA `ba07c8d1a03440f1b4e40371011f1ea5c2234339` 的完整 CI 与 docs-sync 中通过。继续审查商品视觉核验时发现参考图/生成文件只检查存在性，空文件和不支持格式可能进入 FFmpeg/模型路由。现增加格式及非空校验，并加入短剧回归和 handoff 文档断言。本次提交仍须重新检查 CI/doc-sync。

## 最新自动化验收基准（2026-10-11）
- 当前代码与文档基准 SHA：`8773905c7293c76309938e633e761206ca3447ca`。
- 完整 CI：success，运行 `38122183446`：https://github.com/konggu888/ecommerce-agent/actions/runs/38122183446
- 商品视觉输入校验代码提交 `58e9b106a07151b0a9c1855f8d7599e8d9fc9a48` 的 docs-sync：success，运行 `38122132231`：https://github.com/konggu888/ecommerce-agent/actions/runs/38122132231
- A55–A58 自动化阶段通过；真实 Provider/账单、Windows 真机、真实素材与商业成片验收仍未完成。
- PR #31 保持 open/unmerged。后续任何代码变更仍需重新查询最新 SHA 的完整 CI 与 docs-sync。


## A60：失败-only 账本成本保护（待本轮 CI）
A60 修复失败-only 账本可能把旧项目实际成本清零的问题：至少存在成功记录才按账本重建；否则保留旧项目/镜头成本与分类摘要。当前 SHA 的完整 CI/doc-sync 尚待确认。


## A59：项目成本汇总去重
A56 提示词换行修复、A57 成本待核对 UI、A57 打开项目恢复/成本对账和 A58 视觉核验输入校验均已在验收计划所列 SHA 的完整 CI/doc-sync 中通过；最新基准 SHA `e2c1642fcc599bf6e7320460ff1216276e9f16e6` 的完整 CI 与 docs-sync 也均成功。A59 将本地 usage ledger 的成功记录汇总作为项目实际成本总额唯一来源，并同步 project cost_estimate；当前提交需重新查询完整 CI/doc-sync。


## 最新自动化验收基准（2026-10-11）
- 当前 HEAD：`cd6c853c5931af77d64b89bb0435cc31895034d7`。
- 完整 CI success：`38122328825`；docs-sync success：`38122328836`。
- A59 项目成本汇总去重与 A60 失败-only 账本兼容已通过自动化测试。
- PR #31 继续 open/unmerged。真实 Provider 账单对账、Windows 真机、真实素材和商业成片仍未验收。


## A61：旧项目成本迁移与镜头账本统一（待本轮 CI）
A61 为首次成功记账前的旧成本迁移增加原子批量账本写入，并把镜头实际成本统一为成功 ledger rows 汇总；移除资产/视频路径先增量再记账的差异。新增旧成本迁移和原子写入回归；当前 SHA 的完整 CI/doc-sync 尚待确认。


## A62：A61 handoff 断言修复（待本轮 CI）
A61 的 224 项桌面测试中 1 项失败：测试期望“历史成本迁移”，文档用“历史实际成本迁移”。现将断言对齐文档术语，成本迁移代码未改；A62 新 SHA 的完整 CI/doc-sync 尚待确认。


## A61：CI 文案断言失败处理
SHA `a760909be7927025a83a1f3fc5ae219acbd80ac0` 的完整 CI 因 `test_handoff_mentions_a61_legacy_cost_migration` 断言根级 AI 接手文档必须包含“历史成本迁移”而失败；224 项测试中仅该断言失败。已在根级接手文档明确写入旧项目历史成本迁移步骤，保留测试断言。修复后的新 SHA 必须重新查询完整 CI 与 docs-sync。


## A63：迁移基线持久化保护（待本轮 CI）
A63 在旧成本迁移批量写入成功后，立即同步项目与镜头实际成本快照。若后续新费用写入失败，历史成本仍可保存并重载。新增 A63 回归，当前 SHA 的完整 CI/doc-sync 尚待确认。


## A64：素材成本账本故障保护（待本轮 CI）
A61-A63 已在 SHA e6b4789d70cfa0abebfe2b20105b80049154dcbe 完整 CI 与 docs-sync 通过。A64 为 resolve_assets 和 generate_missing_asset 共用成本记账安全入口；账本失败时保留已生成素材，标记成本待核对并记录恢复动作。当前 SHA 的完整 CI/doc-sync 尚待确认。


## A65：用量账本原子写入与完整历史（待 CI）
发现 `record()` 直接覆盖正式 JSON，而批量写入虽原子替换却把账本限制为最后 2000 行。磁盘写入失败可能损坏现有账本；长期运行则会丢失早期成本，导致项目汇总被低估。A65 统一原子写入并保留完整历史，新增两项回归。当前 SHA 的完整 CI 与 docs-sync 需确认；不代表真实供应商账单已经对账。


## A66：人工商品画面核验证据防护（待最新 CI 确认）
- 人工核验现在拒绝缺失、零字节或扩展名不受支持的证据文件，并保存规范化绝对路径。
- 回归测试覆盖无效证据与有效临时图片文件。
- 最新分支 HEAD 和对应 CI 必须在本次文档提交后重新查询；不能用此前 SHA 的成功结果代替。
- PR #31 保持 open/unmerged；Windows 真机、真实视觉/视频 Provider 和真实扣款继续按用户要求暂缓。
- 下一步：确认本次 HEAD 的完整 CI 与 docs-sync；随后继续检查单镜头修复的成本账本、版本映射与视觉核验失败恢复边界。


## A67：短剧核验审查防止过期证据误通过
- 修复发现：人工核验入口会验证真实文件，但之后文件可能被移动/删除；审查函数此前只检查路径字符串、人工方式和备注，可能继续接受旧的 `passed` 状态。
- `audit_short_drama()` 现重新验证证据扩展名、文件存在及非零大小；证据失效会触发 `PRODUCT_VISUAL_NOT_VERIFIED`。
- 增加回归：伪造/失效路径必须触发提示；有效非空临时图片必须通过此项证据检查。
- 本轮代码/测试已提交，完整 CI 与 docs-sync 必须以最终最新 SHA 重新确认。
- PR #31 保持 open/unmerged；Windows 真机、真实视觉/视频 Provider、真实扣款与真实素材验收继续暂缓。


## A68：短剧后续剧情影响分析（功能推进）
- 在跨集连续性台账窗口增加“分析后续剧情影响”按钮，可指定一集分析其对后续集的影响。
- 调用 AI 短剧编导模型，输出受影响集、风险级别、具体依据、建议动作和暂未发现影响的理由；验证受影响集编号只能指向真实后续集。
- 报告保存到短剧方案的 `continuity_impact_reports`，不自动改写剧本；需要人工确认。
- 自动化回归已补充；当前提交的完整 CI/doc-sync 状态必须重新查询。真实模型质量、Windows 真机与真实素材验收仍按计划放到统一验收阶段。


## A69：AI 编导故事引擎与留存设计（功能推进）（CI 已发现并修正提示词回归断言；文档与代码将在同一提交同步。）
- 新增短剧生成质量契约：明确人物目标、阻力、失败代价、冲突升级、转折、伏笔兑现、情绪回报和开场留存设计。
- 新生成结果缺少 `story_engine` / `hook_design` 或升级/留存步骤不足时，会被拒绝保存；旧方案读取保持兼容。
- 新增提示词与负向回归测试；统一验收阶段还需验证真实模型能否持续产出好故事，结构字段本身不代表故事精彩。


## A70：短剧故事结构检查（功能推进）
- 确定性审核报告新增故事引擎和留存设计的结构性提醒：目标/阻力/代价/转折/伏笔兑现/情绪回报、冲突升级、开场疑问、结尾兑现、留存装置。
- 该检查为警告，不替代语义质量判断或真实观众反馈；回归测试与 HELP/PROJECT_LOGIC 同步更新。


## A71：备选故事方向差异化（功能推进）
- 新增备选方向字段：冲突来源、主角关键选择、反转机制、商品角色、受众吸引点与转化路径。
- 新生成方案必须提供至少两个方向并通过必填字段和核心机制重复检查；补充负向回归测试。
- 自然语言语义相似度仍需在统一验收阶段结合真实模型输出人工评估。


## A72：人物动机与关系动力（功能推进）
- 新增人物深层动机、恐惧/秘密、关系动态、决策压力字段，并要求主要人物的行动可追溯到目标/动机/压力。
- 新生成方案缺字段会被拒绝；旧方案仅提示 warning，保持向后兼容。
- 已补充负向测试；下一步继续推进事件因果链与分镜剧情一致性。真实模型写作质量尚未做人工/真机验收。


## A73：剧情事件因果链（功能推进）
- 已加入事件前因、人物选择、直接后果和状态变化的显式因果链要求。
- 新生成方案缺失/不完整会被拒绝；旧方案只告警，兼容历史项目。
- 下一步继续做因果链与剧本/分镜的一致性检查，防止只填结构而故事实际没有体现。


## A74：因果链与剧本/分镜证据对齐（功能推进）
- 新生成短剧的每个因果步骤必须引用完整剧本中的原文证据，并关联根级 storyboard 中至少一个真实分镜位置。
- 缺少证据、证据不在剧本、分镜引用越界会被拒绝；旧方案仅生成 warning，保持兼容。
- 下一步继续推进人物选择、反转和商品功能与镜头动作之间的语义一致性；当前规则不能宣称已经理解画面内容。


## A75：商品事实锁与剧情内容交叉审查（功能推进）
- 已确认商品事实缺少商品资料中的直接文本依据时产生警告。
- 未核实信息被写成肯定主张且附近没有明确不确定性标记时产生警告。
- 已增加回归测试；规则是文本风险筛查，不是事实认证。下一步继续推进人物选择、反转与商品真实功能的一致性检查。


## A76
- Added warning code `PRODUCT_SELLING_POINT_NOT_SHOWN` when confirmed selling points are absent from storyboard action, product integration, dialogue, and generation prompt text.
- This is a text coverage check, not visual verification. Recheck CI and docs-sync for the new SHA.


## 2026-10-11 接手进度：A77

- 基线：A76 文档同步提交 `95b57fcb32860c02c0deece035684b4004ba07f6`；当时 CI 与 docs-sync 均成功，PR #31 未合并。
- 本轮目标：短剧关键因果事件、故事转折与伏笔兑现是否真正落到可拍摄分镜；增加提示词字段 `narrative_function` / `story_event_reference` 与审查警告。
- 约束：文本匹配仅为遗漏筛查，不可宣称完成真实语义判断、生成画面核验或 Windows 真机验收。
- 继续步骤：运行短剧专项测试与完整 CI，检查 docs-sync；失败必须读日志修复后再确认最新 HEAD。


## 2026-10-11 接手进度：A78

- 基线：A77 提交 `60a76cb12bc11ba914dd4d3eeed43379f933a453`；CI 与 docs-sync 均通过，PR #31 未合并。
- 本轮目标：要求分镜逐人物说明行动依据，并检查人物所依赖的信息来源能否在完整剧本定位、关键选择是否落实到引用镜头。
- 新增检查代码：`CHARACTER_ACTION_BASIS_MISSING`、`CHARACTER_ACTION_BASIS_INCOMPLETE`、`CHARACTER_KNOWLEDGE_SOURCE_UNTRACEABLE`、`CHARACTER_CHOICE_NOT_SHOWN`。
- 限制：仅结构/文本审查；不能声称完成心理语义判定、真实生成画面核验或 Windows 真机验收。

- A78 首轮 CI 暴露审查代码执行顺序问题（`shot_texts` 未初始化）；已调整到文本索引构建后运行，并同步帮助/逻辑文档，需以修复后最新 CI 为准。

### A79：人物行动依据绑定检查
- 基线：A78 修复后的 HEAD 311686b8fe962a5276aa603422911f45d612c52e，CI 与 docs-sync 均成功。
- 本轮新增检查：行动依据不能绑定到当前镜头未出现的人物，也不能引用角色设定表中不存在的人物。
- 回归测试覆盖两类错误绑定；仍需以本次提交对应的完整 CI 与 docs-sync 结果为准。

### A80：人物关系变化审查
- 基线：A79 SHA 787447a849457ecb65540edb48d3f2fb9fcde720，CI 与 docs-sync 通过。
- 新增 relationship_change 字段及两项 warning，回归覆盖缺少关系变化说明、关系变化未落实到引用镜头。
- 该字段在审查阶段保持兼容；旧方案缺少字段时仅在多人物方案给出警告。
- 必须以本轮最终 HEAD 的 CI 与 docs-sync 结果为准。

- A80 首轮 CI 失败原因：关系审查执行时引用了尚未构建的 character_names；修复为读取 checked["characters"]，并同步文档。必须继续确认修复 SHA 的 CI。


## 最近推进｜A80 与 A81
- A80：因果链人物关系变化说明及其分镜落地审查；修复初始化顺序后，SHA `ecd7259205cd77b99516e958d89d7022a9f2ab3b` 的完整 CI 与 docs-sync 通过。
- A81（本轮）：新增 `state_continuity`，将因果事件造成的人物状态/信息/承诺/误解/关系后果追踪到后续分镜；覆盖未说明、未知人物、未展示、引用镜头顺序/位置等 warning。
- CI 首轮发现角色名集合初始化顺序错误，已修复；第二轮发现“无后续影响”测试夹具只覆盖单一步骤，已改为逐步声明状态连续性。
- 最终验证 SHA `d976c34a48ff20af65648983be7855589ba2deca`：完整 CI run `38162555687` success；docs-sync run `38162555622` success。PR #31 保持 open、未合并。


## A82｜人物信息掌握与时间线一致性（已提交并验证）
- 代码提交：`8756b773c3b2ee3bf08b80bf3b31992b7081a606`。
- 完整 CI：run `38306392896` success；docs-sync：run `38306392892` success。
- 规则区分剧情内获得的信息（来源镜头必须有效且早于行动镜头）与故事开始前已知的信息；旧方案缺少字段时只产生 warning。
- PR #31 已于 2026-10-11 合并，不要重复合并；A82 后续提交位于 `feat/product-drama-visual-review` 分支。

## A83｜人物承诺、误解与行动结果一致性（自动化阶段通过）
- 最终代码提交：`f57c0eb02249439ea42cc3d46dd2d94e87bab1c1`。
- 完整 CI push run `38307672489` success；PR CI run `38307795562` success。
- docs-sync push run `38307672505` success；PR docs-sync run `38307795710` success。
- A83 已加入 `narrative_obligations`，并覆盖承诺兑现/未兑现、误解与行动后果的来源证据、人物引用、镜头先后和后续文本覆盖回归。
- PR #32 已创建，状态 open/unmerged；不要自动合并。
- 仍需统一验收真实剧情语义、人物心理、画面表演、Windows 真机、真实 Provider 和真实扣款。


## 当前接手状态覆盖（2026-10-13；以本节为准）
- 当前工作分支：`feat/product-drama-visual-review`。
- PR #32 继续保持 open/unmerged；未获用户明确许可不得合并。PR 链接：https://github.com/konggu888/ecommerce-agent/pull/32
- A83 已完成并在最终 SHA `dc24957d5d773bd87bce648b00ea40c412a15da8` 上通过完整 CI 与 docs-sync（CI push `38307988335`、CI PR `38307994797`、docs-sync push `38307988310`、docs-sync PR `38307994904` 均 success）。
- A84 已增加跨集承诺/误解/行动后果的显式承接检查与 3 项回归测试；当前代码提交为 `00ad0d00a9747ca9ef666981b4e592bef6bde543`。此提交及后续文档提交的完整 CI 与 docs-sync 必须重新核验，不能沿用 A83 的绿灯。
- A84 专项：`cross_episode_required=true` 时要求事项引用来源集之后的镜头；仍为 open 的事项必须进入来源集承接状态，并在下一集开场状态/未解线索中延续。未声明该字段的旧方案兼容。
- 仍暂缓：Windows 真机、真实 Provider、真实扣款/账单核对、剪映现场验收。不得将自动化文本审查称为商业成片或语义验收。


## A84 当前验证状态（2026-10-13；本节为最新记录）
- A84 代码、测试及 HELP/PROJECT_LOGIC 同提交 SHA：`00ad0d00a9747ca9ef666981b4e592bef6bde543`。
- 完整 CI push `38308777852` success；完整 CI PR `38308783208` success。
- docs-sync push `38308777939` success；docs-sync PR `38308783195` success。
- PR #32 保持 open/unmerged；不得未经用户明确许可合并。
- A84 仅做跨集结构与文本承接审查；Windows 真机、真实 Provider、真实扣款/账单核对、剪映现场验收仍暂缓。


## A85｜人物长期状态与关系跨集一致性（待最新 CI）
- 新增可选每集字段 `continuity_state.character_state_ledger`，追踪人物认知、秘密、承诺、心理与人物关系等必须延续的状态。
- 对 `must_persist=true` 且未解决的状态，检查下一集是否继续记录；状态描述变化必须声明 changed/resolved，changed 必须提供在剧本/分镜中可定位的 transition_evidence。
- 增加状态缺失、关系无解释重置、转变证据缺失、非布尔持久标记、证据不可定位等回归测试。
- 本轮代码 SHA 与其后文档同步提交的 CI/doc-sync 必须重新确认，不能复用 A84 绿灯。
- 旧方案不提供此可选台账时兼容；Windows 真机、真实 Provider、真实账单与画面验收仍暂缓。


## A85 验证结果更新
- 代码与测试提交：`6128fabc3c530c6072dfe72e05a956fe7733065f`。
- 完整 CI push `38309397555`、PR `38309402963` 均 success；docs-sync push `38309397567`、PR `38309403129` 均 success。
- 本节记录只覆盖代码/测试 SHA；此后的文档提交仍需以最终最新 SHA 重新核验。


## A86｜人物状态变化因果闭环（接续事项）
- 新增 changed 状态的触发事件→变化→人物反应→后续影响字段和时序校验。
- 已添加有效闭环、缺少触发、触发晚于变化、反应/后果缺失或顺序错误等回归测试；需以最新 SHA 的 CI/docs-sync 结果确认。
- PR #32 仍保持 open/unmerged；Windows 真机、真实 Provider、真实扣款/账单与剪映现场验收继续暂缓。


## A87｜人物状态到分镜表演（接手记录）
- 对 `status=changed` 增加 `observable_manifestation` 与 `observable_storyboard_indices`，检查状态变化是否被具体动作、台词、表情或互动体现，而不只是心理标签。
- 新增测试：有效可观察表演、仅有抽象情绪标签、表演描述无法在引用镜头中定位。
- 本节记录的是实现目标；提交后必须以最终 SHA 的 CI 和 docs-sync 结果更新验证状态。
- PR #32 保持 open/unmerged；Windows 真机、真实 Provider、真实扣款/账单和剪映现场验收仍暂缓。


## A88｜多人物状态依赖一致性
- 新增每集可选 `continuity_state.cross_character_dependencies`，声明人物间知识、关系或承诺依赖。
- 检查双方人物、规则、证据和镜头引用；`same_understanding` 陈述不一致时警告，`asymmetric_knowledge` 缺少原因时警告。
- `different_beliefs_allowed` 允许不同信念，不将合理误解自动判成矛盾。
- 新增直接冲突、不同信念、知识不对称、未知人物和无效镜头引用测试。提交后以最终 SHA 核验 CI/docs-sync。
- PR #32 保持 open/unmerged；真实 Provider、Windows 真机、扣款/账单及剪映现场验收仍暂缓。


## A89｜跨集演员/场景资产锁定（自动化阶段）
- 新增根级可选 `series_asset_locks`，可为重复人物/场景定义稳定 key、规范外观/布景描述和适用集数。
- 锁定描述进入对应分镜的演员/场景需求，供既有资产调度链使用；下一集续写上下文保留该锁定列表。
- 新增锁定注入、集数范围、非法 schema、无目标命中警告测试。
- 限制：这是需求文本锁定，不宣称已复用同一物理素材文件或保证生成画面身份一致。PR #32 保持 open/unmerged。


### A89 CI 修复追踪
- 首轮 CI 发现锁定注入调用位置不正确、集号范围测试夹具与单集方案集数不一致，已根据日志修复。
- 当前修复提交必须重新等待 push/PR CI 与 docs-sync push/PR；不得沿用之前 SHA 的失败或通过状态。


## A89｜跨集演员/场景资产文本锁定（2026-10-14 自动化验证通过）
- 当前工作分支：`feat/product-drama-visual-review`；PR #32 保持 open/unmerged。
- 最终代码 SHA：`9bcb19ac950f0addcc5a0bfab599dd060c11ec1e`。
- `series_asset_locks` 已加入短剧输出 schema；`validate_short_drama()` 将锁定描述注入匹配分镜的 actor/scene requirements；续写上下文携带锁定列表；未匹配目标产生 warning。
- A89 回归覆盖演员/场景锁定注入、生产行传递、适用集数、非法集号与目标未命中；299 项 Desktop Core 测试全部通过。
- CI push `38465502064`、CI PR `38465509232`、docs-sync push `38465502037`、docs-sync PR `38465509210` 均 success。
- 限制：仅文本/资产需求层约束，不等于同一物理素材文件复用，不保证生成画面身份绝对一致。Windows 真机、真实 Provider、真实扣款/账单、剪映现场验收仍暂缓。


## A90：跨集物理素材 ID 绑定（待最新 SHA 自动化验收）
跨集演员/场景锁定可选指定本地素材库 asset_id，并将精确 ID 传入制作行。生产解析按 ID 验证资产存在、启用、可复用且类型匹配；无效时明确返回 SERIES_LOCKED_ASSET_INVALID，禁止静默替换或自动生成。未提供 ID 的 A89 旧方案保持标签匹配兼容。此约束只保证素材调度选择，不保证生成画面像素级一致。最新 SHA 的完整 CI/docs-sync 必须重新核验；PR #32 保持 open/unmerged，Windows 真机与真实 Provider 验收继续暂缓。


## 当前接手状态覆盖（2026-10-14；以本节为准）
- 当前分支：`feat/product-drama-visual-review`；PR #32 保持 open/unmerged，不得自动合并。
- A90 SHA：`8baa4339618f6a40fac4cdf0191eecf4eb0208cf`。以下 A91 提交的完整 CI 与 docs-sync 必须以最新 SHA 重新核验。
- A91：项目重新打开、任务恢复、单镜头生成/重生成前复核跨集锁定素材；失效时 fail-closed，保留原 asset_id 并记录恢复原因。
- Windows 真机、真实 Provider、实际扣款/账单核对、剪映现场验收继续暂缓。
- A91 补充保护：镜头素材解析先预检锁定 ID；一旦锁定失效，在任何其他缺失素材生成之前 fail-closed。

## A92 接手状态
- A91 最新 SHA `9e0dc1c89539444af7203fdcf88882fabfcd750f` 的 PR CI 与 PR docs-sync 已通过；push CI 曾出现长时间 in_progress，后续接手需再次核对是否结束。
- A92 新增端到端回归：两集目标镜头必须落到相同锁定 actor/scene ID，忽略相似标签替代素材，并在保存/重新打开后保留绑定。
- PR #32 继续 open/unmerged；Windows 真机、真实 Provider、实际扣款和剪映现场验收仍暂缓。

## A92 CI 修正待验证（2026-10-14）
- 首次 A92 CI 在保存/重载断言失败：测试调用 `resolve_assets()` 后直接 `load()`，遗漏 `store.save(project)`。
- 已识别为测试步骤遗漏；后续提交会在 reload 前保存已解析的项目，修复后的 SHA 需要重新确认 CI/docs-sync。
- 当前分支 head 为 A92 SHA `0758bfe5604ae31f604988bd3a320ede7f1b7ece`，该 SHA 的 PR CI 失败，不能标记 A92 通过；PR #32 继续 open/unmerged。


## A92 CI 根因与修复（2026-10-14）
- SHA `e01003444a268a2b8fa70a031d0bd2155ac062e7` 的 CI 失败位置为重载后 `restored.shots[1].actor_id` 为 `None`。
- 根因：`new_project()` 创建的默认镜头数不止一个；测试追加的第二集镜头并不一定处于列表位置 1，导致按位置断言检查错了镜头。
- 已修正夹具为仅包含 `first` 和 `second` 两个镜头；解析后明确断言两镜头绑定的 actor/scene ID 均为指定锁定值；重载后按稳定 `shot.id` 检查。
- 新 SHA 的完整 CI/docs-sync 未通过前，A92 仍不得验收完成。PR #32 保持 open/unmerged；真机、真实 Provider、账单与剪映验收继续暂缓。


## A93｜Provider 边界回归（新增，待最新 SHA 验证）
- 目标：直接调用单镜头 Provider 渲染入口，在锁定演员素材已停用时验证 fail-closed，而不只测试 resolve_assets() 的返回值。
- 验收点：Provider 调用次数为 0；抛出 SERIES_LOCKED_ASSET_INVALID；原锁定 ID 保留；不绑定相似素材；其他镜头状态/已有输出路径不变。
- 同镜头其他缺失素材不得在锁定失败前触发自动生成。
- 必须以新 SHA 的 CI push/PR 和 docs-sync push/PR 验证；PR #32 保持 open/unmerged。Windows 真机、真实 Provider、账单和剪映现场验收继续暂缓。


### A92/A93 自动化验收结果（2026-10-14；以本节为准）
- 最终代码与测试 SHA：`db8c2a4e80bdbd6a5d308848e84905c1c2a348d0`。
- CI push run `38470175403`、CI PR run `38470184669`、docs-sync push run `38470175408`、docs-sync PR run `38470184505` 均 success。
- A92 跨集锁定 actor/scene 精确 ID 已验证解析绑定、相似标签不覆盖、保存/重开后绑定持久化。
- A93 从 `_render_with_provider()` 入口验证失效锁定素材在 Provider 调用前拦截，Provider 调用次数为 0；保留原锁定 ID，不绑定替代演员，不影响其他镜头已有状态/路径。
- PR #32 保持 open/unmerged。以上仅为自动化测试；Windows 真机、真实 Provider、真实账单/扣款、剪映现场及生成画面视觉一致性继续暂缓。


## A94｜原锁定素材恢复后的重试（待最新 SHA 验证）
- 先停用原锁定演员，确认返回 SERIES_LOCKED_ASSET_INVALID 且不自动生成。
- 恢复同一 ID 的 active/reusable 状态，并保留一个标签相同的相似演员作为干扰项。
- 再次解析后必须绑定原 actor-fixed ID，source 为“跨集锁定素材复用”，generation_if_missing 为 false。
- 不允许因之前有失效恢复记录而永久阻断，也不允许改绑相似资产。
- 最新 SHA 的完整 CI push/PR 与 docs-sync push/PR 通过后才能标记完成。PR #32 保持 open/unmerged。


### A94 自动化验收结果（2026-10-14；以本节为准）
- 代码与测试 SHA：`289cc0954cb93ce1a218436d2a6137317a7c6130`。
- CI push run `38470748908`、CI PR run `38470757428`、docs-sync push run `38470748944`、docs-sync PR run `38470757442` 均 success。
- 失效阶段确认锁定素材错误并关闭生成；恢复同一 asset_id 后可重试并精确绑定原 ID，即使存在同标签相似资产也不替换；锁定 ID 仍禁止 fallback/自动生成。
- PR #32 保持 open/unmerged；真实 Provider、Windows 真机、账单/扣款、剪映现场与画面视觉一致性仍暂缓。


## A95｜损坏素材索引保护（待最新 SHA 验证）
- 使用无效/截断 JSON 模拟本地 `library.json` 损坏。
- 预期错误码为 `SERIES_LOCKED_ASSET_LIBRARY_UNAVAILABLE`，不得误报为单个资产不存在。
- `resolve_assets()` 必须 fail-closed，不处理同镜头其他素材，不触发补素材。
- `_render_with_provider()` 必须在 Provider 调用前拦截，计数型 Provider 调用次数为 0。
- 原锁定 ID 与其他镜头已有状态/输出路径必须保持不变。
- 最新 SHA 的 CI push/PR、docs-sync push/PR 全部通过后方可标记通过；PR #32 保持 open/unmerged。


### A95 自动化验收结果（2026-10-14；测试代码 SHA `6b225e09adac63265d53b27eae3ed6a54a51f49e`）
- CI push run `38471501401`、CI PR run `38471510428`、docs-sync push run `38471501250`、docs-sync PR run `38471510506` 全部 success。
- 无效/截断 `library.json` 返回 `SERIES_LOCKED_ASSET_LIBRARY_UNAVAILABLE`；素材解析提前停止，不继续处理其他素材；Provider 调用次数为 0。
- 原锁定 ID 保留，非目标镜头状态及已有输出路径保持不变。
- PR #32 保持 open/unmerged。真实 Provider、Windows 真机、实际账单/扣款、剪映现场和生成画面视觉一致性继续暂缓。


## A96｜索引修复后重试（待最新 SHA 验证）
- 先把 `library.json` 截断，确认返回 `SERIES_LOCKED_ASSET_LIBRARY_UNAVAILABLE` 且不自动生成。
- 修复索引，重新写入原锁定 ID，并保留同标签相似资产作为干扰项。
- 再次解析应成功绑定原 ID，来源为跨集锁定素材复用，`generation_if_missing` 仍为 false。
- CI push/PR 与 docs-sync push/PR 必须以最新 SHA 全部通过；PR #32 不合并。


### A96 自动化验收结果（2026-10-14；测试代码 SHA `fc01ace4eeb90ccb2f2df10b44a57f8b3c69f134`）
- CI push run `38471876626`、CI PR run `38471884325`、docs-sync push run `38471876601`、docs-sync PR run `38471884345` 全部 success。
- 索引损坏时返回 `SERIES_LOCKED_ASSET_LIBRARY_UNAVAILABLE` 并禁止 fallback；索引恢复后，重新解析精确绑定原锁定资产 ID，标签相似资产不能替换，且不触发自动生成。
- PR #32 继续保持 open/unmerged。真实 Provider、Windows 真机、账单/扣款、剪映现场与生成画面视觉一致性继续暂缓。


## A97｜单镜头恢复隔离（2026-10-14，待最新 SHA CI 验证）
新增回归覆盖项目恢复时仅重置缺失成片的目标镜头；有效兄弟镜头的输出路径、状态、版本和费用必须保持，保存/重开后仍一致。完成后需检查最新 SHA 的 push/PR CI 与 docs-sync 四项结果；PR #32 保持 open/unmerged。真实 Provider、Windows 真机、账单和剪映验收继续暂缓。


## A98｜恢复摘要幂等性（2026-10-14，等待最新 SHA 验证）
新增修复：项目第一次恢复发现缺失成片后，即使后续再次打开并恢复，尚未处理的镜头仍出现在 `missing_media` 中；普通未生成镜头不误报；有效兄弟镜头路径/状态/版本保持不变。修改后需检查最新 SHA 的 push/PR CI 与 docs-sync 四项结果。PR #32 保持 open/unmerged；真实 Provider、Windows 真机、账单与剪映现场验收继续暂缓。


## 2026-10-14：A99 已提交，CI 待验证
最新提交：`c8252dc58995289d8ca38dfd15dc8e66f8001eeb`。A99 修复恢复阶段的逐镜头费用快照残留：只要存在成功的实际费用账本记录，就以账本逐镜头对账；没有成功费用记录的镜头归零，防止单镜头显示旧金额而项目总额已更新。新增 `test_a99_successful_ledger_clears_stale_cost_on_unbilled_sibling_shot`，覆盖账本金额、未计费兄弟镜头归零及保存/重载。已同步 HELP.md 与 PROJECT_LOGIC.md。当前该 SHA 的 CI 与 docs-sync push workflow 已排队，不能提前宣称通过；下一步先确认该 SHA 的 CI、docs-sync push/PR 全部结束，再继续检查单镜头重试的版本与计费联动。PR #32 保持 open/unmerged；Windows 真机和真实 Provider/账单验收仍暂缓。


---

# 2026-10-14 接手状态更新：转向商业剪辑能力主线

> **下一位 AI 必须先读本段，再读本文件其余内容。** 旧段落中出现的历史 SHA、PR 编号和“本轮必须继续做的事”可能过期；以下面的当前状态和 GitHub 实际检查为准。

## 当前工作现场
- 仓库：`konggu888/ecommerce-agent`
- 分支：`feat/product-drama-visual-review`
- 本轮起始基线：`4713c6b024b2a4f407b3b9b4ac8fc4f2b6077597`
- 当前优先级已由用户明确调整：**暂停费用对账/单镜头重试保护检查线，优先推进未来路线图第 5 项“商业级剪辑决策层升级”。**
- Windows 真机测试、真实视频 Provider/真实扣款、剪映现场验收继续暂缓；PR 不得擅自合并。
- 已发现并修复：`postprocess.process_shot()` 原先接收 `focus_x/focus_y`，但 FFmpeg crop 仍固定居中，导致 AI 焦点参数没有影响实际输出构图。
- 代码变更：新增 `_normalized_focus()` 与 `_focus_crop_filter()`，把归一化焦点坐标实际写入 FFmpeg crop 的 x/y；越界坐标夹紧，NaN/Infinity/非法值回退中心。
- 新增回归测试：`apps/ad-studio-desktop/test_postprocess.py`，验证生成的 FFmpeg 命令包含焦点坐标，并覆盖边界/异常值。
- 本轮代码提交：`6beb0786b2cf94dedfc146bd7672e2be3bdeac76`；测试提交：`3c47efafb317b42157c7a4054ff4b9d479250b63`；帮助文档提交：`c5b0634b88e1e2df2333d358ddacf4942aa44704`。后续文档提交和 CI 状态必须按最新 SHA 重新确认。
- 下一步严格顺序：检查最新 HEAD/PR 与 CI/docs-sync；运行新增焦点裁切回归测试及桌面全量单测/语法检查（若无法运行必须如实说明）；再继续商业剪辑决策链审计。
- 后续重点：目标驱动的镜头节奏、真实动态裁切/焦点执行、镜头衔接与转场判断、字幕信息密度、音画节奏/音乐卡点、商品展示节奏、剪后质量反馈。
- 每次代码修改必须同步 HELP、PROJECT_LOGIC、SESSION_HANDOFF、验收计划、验收 SOP、`docs/AD_STUDIO_AI_HANDOFF.md` 和根目录未来功能备忘。
- 不得把基础 FFmpeg 拼接、结构化参数或 CI 通过描述为“商业级剪辑已完成”。路线图第 5 项继续保留，直到各能力实现并正式验收。


## 2026-10-14 最新接手更新：商业剪辑焦点语义校正
- 接手时必须重新查询分支 `feat/product-drama-visual-review` 的最新 HEAD、PR #32 和该 SHA 的 CI/docs-sync；当前修正基于起始 HEAD `728e786a7adcbdab1e110c86e4dd99fbf08d9033`，不能沿用起始 SHA 的 CI 作为新提交验收。
- 继续暂停费用对账/单镜头重试保护线；当前主线是商业剪辑决策层。
- 焦点坐标语义明确为“缩放后源画面中的主体/视觉焦点归一化位置”，不是裁切窗口偏移量。裁切窗口尽可能把该焦点放在目标画面中心，并用 FFmpeg 的 max/min 表达式限制在画面边界内；没有多余画面可裁的轴保持边界位置。
- `adapt_aspect()` 是独立的中心裁切工具，不声称执行 AI 焦点；需要焦点驱动的单镜头处理应走 `process_shot()`。
- `test_postprocess.py` 验证实际传给 FFmpeg 的 `-vf` 字符串、焦点定位表达式、边界夹紧及非法/非有限输入回退。它不等于真实视频画面已视觉验收。
- 下一步：检查最新提交四项 CI/docs-sync；在可用的本地仓库环境运行桌面全量单测与语法检查；随后继续审查目标驱动的节奏、镜头衔接、字幕密度、音画卡点和剪后反馈。
- 必须同步维护 HELP、PROJECT_LOGIC、本文件、验收计划、验收 SOP、`docs/AD_STUDIO_AI_HANDOFF.md` 和根目录未来功能备忘。PR #32 保持 open/unmerged；Windows 真机、真实 Provider/扣费和剪映现场验收继续暂缓。

## 2026-10-14 最新接手补充：文档同步 CI 扩围（本次变更后需重新查 CI）
- 已发现旧的 `tools/check_ad_studio_docs.py` 只强制检查 HELP.md 与 PROJECT_LOGIC.md，覆盖范围小于项目既定接手规则。
- 本次将其扩展为要求同一桌面代码/测试变更同时修改八个规则/文档文件，并增加自动化契约测试。
- 变更后必须重新查询本分支最新 HEAD 对应的 CI push、CI PR、docs-sync push、docs-sync PR；不能把本次变更前 SHA 的绿色结果当作本次结果。
- 文档检查只验证规定文件是否出现在同一差异中，不证明文档内容语义完全正确；仍需审阅差异，并将 docs-sync 与完整 CI 分开报告。
- PR #32 继续保持 open/unmerged；不执行合并。


## 2026-10-14｜A100 商业剪辑淡出修正（本轮待 CI）
- 起始 SHA：`7358148776e10775edff98b69273c5d29fab7ec5`；该 SHA 的 CI push/PR 与 docs-sync push/PR 已全部 success。
- 本轮修正 `postprocess.process_shot()`：旧“淡出”滤镜从 0 秒开始，实际会在镜头开头淡出。现在先读取输入时长，再按速度计算输出时长，将淡出放到处理后镜头尾部；极短镜头会缩短淡出时长。
- 新增 `test_postprocess.py` 两个回归：变速后的末尾淡出、短片段边界。
- 本次新 SHA 的完整 CI 与 docs-sync push/PR 必须重新核验，未通过前不标记 A100 自动化验收完成。
- 后续继续商业剪辑决策层：镜头节奏、真实镜头间转场、字幕信息密度、音画节奏/卡点、商品展示节奏、剪后质量反馈。不能把本次局部滤镜修正说成商业级剪辑已完成。
- PR #32 保持 open/unmerged；Windows 真机、真实 Provider/扣费和剪映现场验收继续暂缓。


## 2026-10-14｜A101 变速音画同步修正（本轮待 CI）
- 前置提交 `523dd66bd09b6892aa3c5ac862d531493d115a01` 的完整 CI push/PR 与 docs-sync push/PR 均已通过，A100 自动化验收完成；Windows 真实画面/听感仍暂缓。
- 本轮在 `postprocess.process_shot()` 为非 1.0 倍速增加 `atempo`，使原音轨与 `setpts` 调整后的画面时长保持一致；正常速度不加音频变速滤镜。
- 新增两个回归测试，分别覆盖 1.25 倍速和 1.0 倍速。
- 新 SHA 的完整 CI 与 docs-sync push/PR 需要重新核验后，才能确认 A101 自动化验收。
- 商业剪辑路线图仍未完成：真实镜头间衔接、字幕信息密度、音乐卡点、商品展示节奏、剪后质量反馈；不要把基础变速修复描述为商业剪辑整体完成。
- PR #32 保持 open/unmerged；Windows 真机、真实 Provider/扣费和剪映现场验收继续暂缓。


## A102：最终成片最低 1080P 级输出（待 CI）
- 最终拼接结果先进入临时文件，再经 `normalize_output_resolution()` 归一化转码后成为交付输出。
- 最低输出：9:16 1080×1920；16:9 1920×1080；1:1 1080×1080。ffprobe 质检拒绝尺寸不足的输出。
- 新增测试：后处理命令覆盖竖屏/横屏/方形配置；最终媒体质检覆盖 720×1280 竖屏拒绝。
- 这只是最低像素尺寸保障，不等于 AI 超分、去噪或细节恢复。Windows 实机画质检查仍暂缓。
- 当前提交 SHA 的完整 CI 与 docs-sync push/PR 结果待确认；PR #32 必须保持 open/unmerged。

A102 后续修正：首轮 CI 暴露测试夹具没有模拟归一化阶段输出文件、以及一条 FFmpeg 参数断言检查错位置；已修复夹具并调整断言。当前最新 SHA `cf21060274bf1eb3dc0b1b37e19ae81aec3d1b05` 的 CI/doc-sync 需重新确认。


## A103：镜头淡入/淡出音画同步（待 CI）
- 修改 `ad_studio/postprocess.py`：淡入/淡出时同时处理视频和原音轨，按变速后的输出时长计算窗口，短镜头自动缩短淡化时长。
- 新增测试覆盖变速淡出音频滤镜、短片段淡入及常速淡出。
- 这项是单镜头淡化；相邻镜头交叉溶解、节奏分析和音乐卡点仍未完成。
- 当前提交的完整 CI 与 docs-sync push/PR 结果待确认；PR #32 保持 open/unmerged。


## A104：相邻镜头真实交叉溶解（当前提交待 CI）
- 最新改动在 ffmpeg.concat_with_transitions() 中使用真实 xfade 画面交叠和 acrossfade 音频交叠，按镜头实际时长计算 offset；无音轨输入生成等长静音。
- ProductionStore.build_final() 仅在非首镜头的 transition == “交叉溶解”时启用；其他项目保留原 concat。
- 新增 test_ffmpeg.py 覆盖滤镜图、无音轨补静音与配置数量校验。
- 当前提交的 CI push/PR 与 docs-sync push/PR 尚待核验。PR #32 必须保持 open/unmerged；Windows 真机、真实 Provider/扣费和剪映现场验收继续暂缓。


## A105：分镜节奏默认值接入实际播放速度（当前提交待 CI 核验）
- `creative_engine.validate_plan()` 现在将 pacing 标签映射为可执行速度默认值：慢 0.85x、标准 1.0x、快 1.15x、极快 1.3x。
- schema 中 `speed` 可省略；显式 `speed` 优先，未知 pacing 回退“标准”。新增 `test_creative_engine.py` 覆盖四档映射、显式速度覆盖和未知标签回退。
- 下一步先核验当前最新 SHA 的 CI Push/PR 与 docs-sync Push/PR。不要把此基础映射描述为画面理解、情绪节奏或音乐卡点已完成。PR #32 保持 open/unmerged；Windows 真机验收继续暂缓。


## A106 接手记录：商业镜头角色驱动默认剪辑决策（待最新 SHA CI）
新增 `resolve_editing_intent()`，将分镜文本归类为 hook、product_detail、demonstration、proof、pain_point、reaction、cta 或 story_beat；仅在字段缺失时补齐默认时长、节奏/速度与转场，显式参数优先。决策理由、规则依据和参数来源写入 `CreativeShot.editing_intent`。新增测试覆盖主要角色、末镜 CTA 淡出和显式参数覆盖。首轮 CI 暴露未知 pacing 标签回退规则需兼容 A105，已修正为“标准”，并补充最终生效参数审计字段。修复提交后必须重新查询当前 SHA 的 CI Push/PR 与 docs-sync Push/PR；PR #32 保持 open/unmerged。文本规则不代表视觉理解，商业剪辑整体与真实素材验收仍未完成。

## A107 接手记录：商业角色时长进入运行时生成请求
A106 的角色默认时长没有从 `CreativeShot` 复制到运行时 `Shot`，导致视频 Provider 请求可能继续使用默认 3 秒。A107 新增 `runtime_shot_editing_fields()` 并由 `app._activate_plan()` 消费，映射 duration_seconds/pacing/speed/transition；测试覆盖商品细节镜头默认 4 秒。提交后核对当前 SHA 的 CI Push/PR、docs-sync Push/PR 四项。PR #32 保持 open/unmerged；Windows 真机、真实 Provider/实际扣费、剪映现场验收继续暂缓。商业剪辑整体仍未完成，下一步继续推进音乐卡点、字幕信息密度和真实内容驱动的剪后优化。


## A108 接手记录：字幕按实际镜头时长与信息密度自适应（修复提交后待重新核验）
`subtitles.py` 新增时间轴规划和密度分析；字幕加工 UI 使用 FFprobe 实际时长，不再固定 `duration=3`，按时长/文本长度切分 SRT，尽量在标点处断句，并在短镜头减少快速切换、提示高字/秒风险。请检查当前 SHA 的 CI Push/PR、docs-sync Push/PR 四项。PR #32 保持 open/unmerged；真实素材、Windows 真机和字幕可读性验收继续暂缓。下一项商业剪辑可继续推进音乐节拍与画面卡点，但不得宣称字幕高级优化已完成。

## A109｜音乐节拍与画面切点真实联动（本轮实现，须按最新 HEAD 复核 CI）
- BGM 由逐镜头混音改为项目级统一音轨：字幕加工时保存选择，最终拼接后一次性混入，避免同一歌曲在每个镜头重启。
- 新增 `ad_studio/music_sync.py`：本地 PCM 节拍候选分析、置信度、保守切点规划、音画同步变速和最终统一 BGM 混音。
- `ProductionStore.build_final()` 消费切点计划并渲染临时变速镜头；超出安全边界时保持原切点；最终归一化到既有 1080P 级配置。
- 新增 `test_music_sync.py` 覆盖合成节拍、静音、低置信度、调整边界、音画同步命令和全局 BGM 命令。
- 必须查询最新 SHA 的 CI/doc-sync Push/PR；本轮自动化实现不等于真实音乐/口播/字幕视觉质量验收。PR #32 仍不得合并，真实环境验收继续暂缓。

### A109 旧项目音轨兼容边界
A109 兼容边界：旧项目中已把 BGM 烧录进镜头音轨的成片，无法仅凭现有文件可靠分离旧音乐。重新使用全局 BGM 前，应从未混入 BGM 的镜头源重新执行字幕处理；否则可能叠加旧音乐。

### A109 转场安全补充
A109 转场安全补充：当前切点变速遇到显式“交叉溶解”时保守回退原镜头时长，仍保留既有交叉溶解与全局连续 BGM；待单独建模转场重叠时长后再开放这类边界的卡点调整。
\n\n## A112｜字幕实际时间窗接入（本轮代码提交后必须重新核验）\n已实现候选代码：字幕烧录后保存当前视频版本与 SRT 的绑定；严格解析 cue 时间窗并校验镜头时长；有效证据才进入音乐卡点保护，异常/缺失/不匹配写入逐镜头回退审计。新增 parser 和最短 cue 保护测试。代码基线 SHA e8deb1ec4ef9edf7d999c79539762ea2627affab 的 CI Push/PR、docs-sync Push/PR 已全部 success；仅自动化阶段通过，真实 Windows/素材/听感验收仍暂缓。真实 Windows/素材/听感验收仍暂缓。\n\n## A112 CI 中间结果与修复记录\n首个 A112 提交的 docs-sync Push 曾失败，原因是随后修正 SRT 转义的代码提交未同时触及强制文档；该提交的 PR docs-sync 通过不能替代 Push 结果。现重建为包含 SRT 解析修正和全部强制文档更新的单个提交链，必须检查新 SHA 的 CI Push、CI PR、docs-sync Push、docs-sync PR 四项。此记录保留失败事实，不得删除。



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



## 2026-10-15 接手更新｜用户自由度 / 模型与 Provider 接入审计
- 当前审计分支 HEAD 基线：`aa825eaa106810e6a56b463b894053145f719864`。开始本轮时 PR #32 仍为 Open / unmerged；本轮提交后必须重新核对 PR head 与分支 ref 是否一致，不能沿用旧 SHA 状态。
- 已对 `model_router.py`、`providers.py`、`capability.py`、`app.py::model_settings` 与 `test_model_router.py` 做静态首轮审查，并将发现写入 `docs/AD_STUDIO_USER_EXPERIENCE_SAFETY_AUDIT.md` 的 UXS-2 专项节。
- 当前可证实：多模型池、按功能路由、自定义 Base URL / 模型 ID / API Key、OpenAI-compatible 本地服务通道、部分通用 REST 视频/资产 Provider；不能把它描述为任意模型/任意 API 无条件即插即用。
- 重点风险：规划模型可能在预算确认前调用；路由可能自动切换本地/云端；模型配置 JSON 保存完整 API Key；usage/价格缺失时成本估算可能为 0；外发数据告知、端点安全、换 Provider 后缓存/历史隔离证据不足。
- 证据限制：本轮为静态审查，没有运行测试，没有连接真实模型/Token 代理，没有核对实际账单。不得声称这些风险已修复或完成正式验收。
- 正式 ID 规则：不新增 A113+，不删/改号 A0–A112；先做语义去重和跨来源映射。完成率继续关闭，`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false` 保持不变。
- 唯一下一步：继续 UXS-2 / PLAN-003，检查路由回退授权、密钥存储/导出、预算授权时点、外发数据提示、缓存键/历史项目可迁移性，并逐项映射 A0–A112。暂不开发产品功能；PR #32 必须保持 Open / unmerged；Windows 真机、真实 Provider/代理、真实账单、剪映和投放验证继续暂缓。


## 本轮审计提交链说明（2026-10-15）
- 模型/Provider 用户自由度首轮审计的完整证据与风险矩阵以 `docs/AD_STUDIO_USER_EXPERIENCE_SAFETY_AUDIT.md` 的 UXS-2 专项节为准；本接手文件仅保留执行摘要与下一步，避免复制整份审计导致版本漂移。
- 该审计当前只证明静态代码中存在相关配置/路由路径，不证明真实模型、代理、费用或 UI 已通过现场验收。下一步必须继续映射现有 A0–A112，不新增正式 ID。
