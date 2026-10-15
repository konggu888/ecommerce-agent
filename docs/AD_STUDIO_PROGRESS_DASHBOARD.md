# 【规划与进度控制体系盘点｜2026-10-15｜权威当前状态】

> **本文件是唯一权威进度源。** 当前任务、阶段状态、任务台账、依赖、权重、证据和下一项只以本文件为准。`SESSION_HANDOFF.md` 与 `docs/AD_STUDIO_AI_HANDOFF.md` 只提供接手入口和短摘要；路线图定义战略与阶段退出条件；验收计划定义范围；SOP 定义验收方法；执行控制协议定义 AI 行为。其他文件中的“当前状态/下一项”若与本文件冲突，一律视为历史快照，先登记冲突，不据此启动任务。

- 仓库：`konggu888/ecommerce-agent`；项目：`apps/ad-studio-desktop`；分支：`feat/product-drama-visual-review`；PR #32 保持 Open / unmerged。
- 本轮修改前实时核验 HEAD：`c1644db81457e4993dc4ec55b94c62a40a285e6c`；PR-triggered `CI` 与 `ad-studio-doc-sync` 均 completed/success，Netlify deploy-preview status success。此为修改前基线，不代表本轮新提交结果；Push-triggered 两项未由当前工作流查询接口独立核实。
- 当前唯一主线仍属 PLAN-003：**对 A0–A112 全量跨来源关系、状态冲突和证据边界作最终裁决**。控制体系盘点、113 个编号槽位的规范化登记及 A0–A112 部分静态证据映射已经存在；不得重复启动“重新建立台账”或从 A50 重新做同一批映射。
- 当前已核实的核心问题：A0–A112 的 113 个槽位已有标题索引、规范化登记和分批静态证据映射；`code_test_evidence_reviewed_ids=113` 只代表每个编号均开始映射，绝不代表完成审计。真正未完成的是跨来源语义去重/状态冲突的全量裁决、任务依赖与阶段退出条件的逐项关联、证据局限与状态字段完整性复核，以及后续权重/自动一致性检查。多个接手文件与路线图顶部仍保留过时“当前任务/下一项”，正是本轮要收敛的循环来源。
- **本轮唯一任务**：修正权威入口中的过时“当前任务/下一项”，明确当前进度已进入 PLAN-003 的全量跨来源关系与状态冲突裁决；逐项核对正式计划、SOP、路线图、未来备忘、帮助/逻辑文档、接手文件和已登记证据，避免重复做已完成的批次。完成该冲突收敛后，下一阶段才是 PLAN-004 权重审定与 PLAN-005 状态段清理；不得跳过 PLAN-003 的语义去重和依赖/证据审计。
- 不删/重编号 A0–A112，不自行增加正式验收 ID。真实 Windows、真实素材、真实 Provider/扣费、剪映现场、真实投放与商业效果验证继续暂缓。

## 控制体系盘点结果（首轮）

| 控制组件 | 当前已有内容 | 发现的缺口 / 纠偏方向 |
|---|---|---|
| 战略路线图 `docs/AD_STUDIO_PRODUCT_ROADMAP.md` | 产品终点、阶段顺序、各阶段目标与退出条件 | 历史实现状态和当前优先级容易混读；当前执行顺序必须只从本台账读取 |
| 正式验收范围 `docs/AD_STUDIO_ACCEPTANCE_PLAN.md` | A0–A112 正式检查点和阶段范围 | 检查点尚未全部与唯一任务记录、依赖、当前 SHA 证据、验收层级逐项关联 |
| 验收 SOP `docs/AD_STUDIO_ACCEPTANCE_SOP.md` | 验收步骤、代码反推、专项测试、CI 和文档要求 | 执行方法已较详细，但无法替代规范化任务台账与证据索引 |
| 进度台账（本文件） | 任务字段要求、开发/验收状态、计算公式、阶段初步状态 | 全量任务记录、语义去重、依赖映射、权重依据与可复算进度尚未完成；PLAN-006 自动一致性检查待执行 |
| AI 执行控制 `docs/AD_STUDIO_EXECUTION_CONTROL.md` 与 `AGENTS.md` | 单任务范围、禁止联想式扩展、停止条件、文档同步、CI 闸门 | 需明确冲突裁决顺序：状态/下一项由本台账唯一决定，接手文件不得另立并行“当前下一项” |
| 接手入口 `apps/ad-studio-desktop/SESSION_HANDOFF.md`、`docs/AD_STUDIO_AI_HANDOFF.md` | 有当前状态和详细历史背景 | 多个顶部快照反复追加，存在过时 SHA 与互相冲突的“下一项”，容易让 AI 继续旧任务而形成循环 |
| 未来功能备忘 `docs/AI_AD_STUDIO_FUTURE_FEATURE_MEMO.md` | 记录未来与暂缓能力 | 必须逐项映射到正式范围和代码证据；不能仅凭备忘文字推断已实现/未实现 |
| UX/安全审计 `docs/AD_STUDIO_USER_EXPERIENCE_SAFETY_AUDIT.md` | UXS-1 至 UXS-5 审查方法与用户旅程线索 | 它应作为 PLAN-003 的一个子工作流，而不是覆盖整个规划控制体系的唯一当前任务 |
| `HELP.md` / `PROJECT_LOGIC.md` | 面向用户的功能说明和面向 AI 的实现逻辑 | 作为代码行为/功能事实证据，不作为项目进度或当前下一项的权威来源 |

## 七层结果证明标准与规划控制体系的关系（已纳入，2026-10-15）

用户体验/安全审计文件已定义七层结果证明标准；本台账将它作为**全项目通用的证据分类与验收边界**，而不是另一条并行任务线。规范化 A0–A112 台账时，凡相关任务必须映射到适用层级，并明确“当前证据证明了什么、不能证明什么、尚缺什么”。七层为：

1. **软件运行正确**：启动、运行、异常处理的证据。
2. **功能行为正确**：单项功能是否符合需求的代码/测试证据。
3. **端到端流程正确**：完整链路及状态衔接证据。
4. **普通用户可用**：入口可发现、提示可理解、失败可恢复的用户旅程证据。
5. **商品表达真实、安全**：商品外观、结构、功能、使用方式及风险处理有依据的证据。
6. **商业成片质量达标**：画面、声音、字幕、节奏、清晰度和交付质量的成片证据。
7. **真实商业效果有效**：按预先定义的业务目标验证实际投放结果的证据。

**不可互相替代：** CI 通过不能证明用户可用；代码/模拟测试不能冒充真实环境验收；1080P 输出不能单独证明细节真实增强；成片观感不能证明真实投放有效。当前真实 Windows、Provider/实际扣费、剪映现场、真实投放与商业效果验证仍属暂缓/待验证，不能因文档建立了标准就标记通过。

在规范化台账中为每项保留“适用结果层级、证据类型/链接、证据绑定 SHA、证据能证明的结论、不能证明的范围、剩余验证、是否暂缓”字段。层级不适用时必须写明理由；不得将未验证的层级计为通过。


## 用户自由度与用户授权控制（已纳入 PLAN-003，2026-10-15）

用户自由度是跨任务审查维度，不是独立产品开发路线，也不新增/删除/重编号 A0–A112。现有 UXS-2《用户体验与安全审计》已包含模型、Provider 与 Token 中转站的静态证据和风险；规范化台账必须把它逐项映射到既有正式验收合同，区分“代码存在”“自动化验证”“端到端验证”“真实服务/账单验证”。

必须逐项盘点以下四类自由度：

1. **选择自由**：用户可配置/选择模型、Provider、Token 中转站、本地或云端执行方式，并按功能选择模型；明确哪些能力只支持 OpenAI 兼容协议或特定 REST 约定，不能宣称任意模型均可接入。
2. **控制自由**：用户能否决定何时调用、是否继续、是否接受费用、是否允许回退；用户指定的模型/Provider/本地模式不可用时，不能在不知情的情况下改用其他模型或把数据转发到云端。
3. **知情自由**：调用前应以用户可理解的方式说明目标服务/数据目的地、将发送的数据类别、预计费用与估算不确定性；未知费用不能显示成确定的零成本。记录 API Key 掩码与实际存储安全的区别。
4. **撤回与纠正自由**：用户取消/拒绝后应停止该次调用；需要核验外部调用计数为零、失败可恢复、切换模型后的项目/缓存/历史不串用，并且操作状态可理解。

### 台账映射与证据要求

- 为相关 A0–A112 任务记录：自由度维度、原始需求来源、对应正式 ID、UI 入口、真实调用链、授权/取消/回退行为、费用与数据披露、密钥存储、项目/缓存隔离、专项正反例、证据 SHA、剩余风险及真实验证是否暂缓。
- 对“用户拒绝回退/外发”场景，优先核验是否存在明确提示与同意；拒绝后须有测试证明相关外部调用计数为 0。不能只凭设置界面或静态代码认定通过。
- 区分文本模型路由与图像、视频、语音/转写等独立 Provider 能力；某一类可切换，不代表所有生成环节都可任意切换。
- 已发现的费用授权时点、自动回退/云端外发、API Key 明文落盘、费用估算低估、数据去向告知、Provider 兼容边界与路由测试覆盖口径，先映射并裁决是否由现有合同覆盖；不得未经全量语义去重就创建新正式编号。
- 真实 Provider、代理站、实际扣费/账单、Windows 真机等验证仍按既定范围暂缓。静态审计、模拟测试、CI 通过不能替代这些证据。

当前结论：**用户自由度已进入专项审计，但尚未完成 A0–A112 逐项映射和验收裁决。** PLAN-003 的跨来源映射与证据审计必须包含本维度；在映射完成前不宣称用户自由度整体通过、不计算总体完成率，也不因此启动产品功能开发。

---

### 控制体系必须补齐的缺口（按依赖顺序）

1. **状态唯一性**：当前状态/下一项统一从本文件读取；接手文件改为短摘要与指针，历史内容明确标记为历史。
2. **规范化任务台账**：保留全部 A0–A112 原 ID，为每个槽位建立唯一记录，字段至少包括来源映射、阶段、父任务/依赖、开发状态、验收状态、当前证据 SHA、测试与 CI 链接、剩余条件、阻塞/暂缓原因、重复关系、最后核验日期。
3. **跨来源语义去重与状态裁决**：重复引用映射到 canonical 任务记录；不得静默删除或合并独立验收合同。
4. **依赖与阶段门槛**：把路线图阶段目标/进入条件/退出条件映射到任务及证据，明确阻塞关系。
5. **权重与进度公式**：完成任务审计和依赖映射后再审定权重；开发实现、自动化验收、模拟端到端、真实环境验收分别统计；暂缓项保留在总范围。
6. **一致性自动检查（既有 PLAN-006）**：检查 ID 唯一、状态合法、依赖引用有效、权重和公式可复算、证据绑定 SHA、暂缓项未被误计为通过。
7. **阶段退出复核（既有 PLAN-007）**：逐项证据化复核阶段 2；不以 A109–A112 CI 绿灯替代阶段退出或商业质量验收。

### 本轮停止条件

- 上述控制组件与缺口已记录。
- 唯一权威来源与冲突裁决顺序已写清。
- 当前任务和下一项在本文件只有一个版本。
- 不在本轮给 A0–A112 赋权、不计算总体完成率、不开发产品功能。
- 下一项正式任务：**PLAN-003｜完成 A0–A112 全量跨来源语义去重、状态冲突裁决与依赖/证据边界复核**；现有任务台账和分批映射作为输入，不重建、不从头重跑。

---

# AI 商品广告工厂｜总进度与任务台账

版本日期：2026-10-15；仓库：`konggu888/ecommerce-agent`；项目：`apps/ad-studio-desktop`；分支：`feat/product-drama-visual-review`；PR #32 必须 Open / unmerged。

## PLAN-003 历史证据快照｜2026-10-15｜以文件顶部权威状态和任务顺序为准

- A0–A5 当前代码/测试证据映射（核验到 SHA `1fd6d08dac970cb7886c59239b05c4f6e2128cf9`；仅证据盘点，不代表正式验收）：A0：`ad_studio/app.py` 中存在 `App.create()` 用户操作入口，但已检查的 desktop 测试未发现专门启动/创建操作端到端测试；A1：当前 CI 覆盖多个测试集，但台账仍缺任务级稳定性矩阵与可追溯的逐项证据；A2：`test_desktop.py` 有 `test_project_lifecycle_isolated_between_projects`、`test_project_save_load`，但未发现直接调用 `App.create()` 的编排测试；A3：有 `test_setup_form_grid_rows_do_not_overlap`、`test_three_task_types_have_distinct_deterministic_policies`、`test_task_type_is_persisted_and_not_replaced_by_platform`，但不能替代三类任务完整 UI 流程验收；A4：`test_footage.py` 覆盖素材排序扫描、不可解析文件注记、重复素材评分、废片归档与保护被引用源文件（`test_archive_analyzed_waste_protects_currently_referenced_source`），仍需对照验收清单补齐路径异常、源文件保护等完整矩阵；A5：`footage.py` 实现 `extract_keyframes()`、`build_visual_manifest()`、`footage_analysis_public()`，但全仓已检查的 desktop `test*.py` 未找到对前两者的直接专项测试，需补关键帧提取失败、清单生成失败与模型视觉分析失败/回退覆盖。六项均不标记正式验收通过。

- A0–A112 共 113 个编号槽位的四份规划来源标题索引已建立；需求文本级语义复核覆盖 113 个已登记槽位。A68–A74 与 A99 的历史任务身份已从历史提交、测试及项目文档中恢复，不能再描述为“未知编号缺口”；但历史实现不等于当前 HEAD 已验收。
- 当前仍未完成的是全量跨来源重复/状态材料合并审计，以及逐项代码、测试和当前 HEAD 证据审计。已确认的 A50/A56、A61/A62、A57、A99 关系仅为局部裁决；台账仍为 `fully_audited=0`、`semantic_dedup_completed=false`、`code_test_evidence_audit_completed_ids=0`；`code_test_evidence_reviewed_ids=113` 表示已开始部分映射，不表示六项已正式验收。权重仍为空，总体完成率保持关闭。
- A88 是标题解析假缺口，已修正。跨来源关系的初步裁决（仍待全量核对）：A50/A56 是原始行为合同与回归修复，关联但不合并；A61/A62 是历史成本迁移能力与迁移相关断言修复，关联但不合并；A57 内含两个独立验收场景，必须分别核验；A99 的成功账本清除未计费兄弟镜头陈旧成本有独立行为与专项测试，与 A57/A59 相关但不重复。A80、A84/A85、A89、A92/A93、A111 等历史/状态材料及 A90–A98、A100–A112 的独立执行合同仍需逐项核对。此为保守初步映射，不代表全量语义去重完成，不授权删除任何 ID 或验收条件。
- A0–A5 的代码/测试证据审计仅有部分映射，未正式验收。A3 设置区布局重叠问题已在 `f20bf426594a55ac74267641b53d9166acef6798` 修复并增加 AST 布局回归测试；`0bc079178c569502dc8f722ad04544a581f20290` 是该阶段的历史核验基线，不是当前 HEAD。当前最新完整核验基线为 `1fd6d08dac970cb7886c59239b05c4f6e2128cf9`，其 CI Push `38691577983`、CI PR `38691582839`、docs-sync Push `38691577999`、docs-sync PR `38691582806` 均 success。下一步不重复修复已解决的 A3 布局问题，而是继续 PLAN-003：完成跨来源重复/状态段审计，再逐项核验 A0–A5 及后续任务的代码、专项测试与当前 SHA 证据。

## 1. 当前结论
**目前不发布全产品完成百分比。** 现有验收计划包含 A0–A112 大量检查点，路线图、未来备忘、SOP 和接手文件有重复任务与历史状态。完成逐项去重、代码/测试证据核验、依赖映射与权重审定前，给出总体百分比会造成伪精确。已有文档、CI 绿灯和暂缓项目均不能直接换算成产品完成率。

## 2. 指标定义（完成审计后启用）
- 开发实现率 = 满足开发完成定义的任务权重之和 / 全部纳入范围任务权重之和 × 100%。
- 验收通过率 = 达到各任务规定验收层级且证据有效的任务权重之和 / 全部纳入范围任务权重之和 × 100%。
- 另列真实环境验收率与暂缓任务权重，避免自动化通过掩盖真实环境未验收。
- 暂缓项保留在总范围中；只有用户批准删除范围并记录依据后才能调整分母。
- 权重必须基于价值、风险、依赖与工作量审定并说明依据；不可为了得到好看的比例临时分配。

开发状态：未盘点、未开始、进行中、代码完成、阻塞、暂缓、取消。
验收状态：未验收、自动化待运行、自动化失败、自动化通过、模块集成通过、模拟端到端通过、待真实环境验收、正式验收通过、部分通过。

每项至少记录唯一 ID、名称、阶段、父任务/依赖、权重、开发状态、验收状态、证据 SHA、测试/CI 链接、剩余条件、阻塞原因、暂缓原因、重复项映射、最后核验日期。CI/doc-sync 证据绑定 SHA；新提交必须重查四项。

## 3. 当前基线

- 本轮文档修改前的核验基线：`9b52642fc2608fe24b0d4dba4ba0ef36d3ca8e67`；PR #32 Open / unmerged。该基线之后的提交需单独查询，不继承其 CI 结果。
- 该 SHA 的 PR-triggered CI `38700695789` 与 PR-triggered docs-sync `38700695499` success；Netlify deploy-preview success。Push-triggered 两项未独立核实。
- 任何新提交后都必须重新查询当前 SHA 的可用 CI/doc-sync；旧 SHA 证据不得继承为新 SHA 通过。

## 4. 阶段状态（初始盘点；暂不计算完成率）
| 阶段 | 目标 | 状态 | 需要核对的重点 | 完成率 |
|---|---|---|---|---|
| 0 | 路线与证据基线 | 进行中 | 全量任务去重、状态与证据核验 | 暂不计算 |
| 1 | 可靠生产底座 | 待逐项核验 | 主链、持久化、版本隔离、失败恢复、成本与交付 | 暂不计算 |
| 2 | 商业级剪辑决策层 | A109–A112 自动化阶段通过；阶段未退出 | 对照阶段退出条件逐条核实真实生产链和剩余缺口 | 暂不计算 |
| 3 | AI 广告编导 | 待逐项核验 | 商品理解→策略→剧本/分镜→生产的可追溯链 | 暂不计算 |
| 4 | AI 短剧 | 待逐项核验 | 商品短剧与非商品多集短剧分别盘点 | 暂不计算 |
| 5 | 资产与制作效率深化 | 待逐项核验 | 资产、免费商用音乐/字体、模型调度、工作模式等去重 | 暂不计算 |
| 6 | 真实环境与商业验证 | 按用户要求暂缓 | 只维护计划与准备条件，未经许可不启动 | 暂缓，不折算完成 |

## 4A. 全量任务登记表初次扫描（尚未完成审计）

已从路线图、验收计划、验收 SOP、未来功能备忘及历史实现证据建立任务台账，涵盖 A0–A112 共 113 个编号槽位；此数字不代表 113 项均为独立功能或已完成验收。A68–A74 与 A99 的历史任务身份均已恢复并补回正式检查清单，编号缺口为 0。A88 是标题解析造成的假缺口，已修正。最终跨来源重复/状态材料合并审计、路线图阶段映射复核和当前 HEAD 逐项代码/测试证据审计仍未完成；不能将历史实现或旧 CI 当作当前验收。A109–A112 有自动化阶段证据，其他任务仍须逐项核验。所有权重暂空，总体完成率继续关闭。

## 5. 规划体系任务清单
| ID | 任务 | 状态 | 验收条件 |
|---|---|---|---|
| PLAN-001 | 建立 AI 执行边界协议 | 本轮实施中 | 协议包含任务单、范围控制、停止规则和证据要求 |
| PLAN-002 | 建立统一进度入口与计算口径 | 本轮实施中 | 开发/验收/真实环境分开；不发布未经审计的总体百分比 |
| PLAN-003 | 全量任务盘点与去重 | 进行中 | A0–A112、路线图、未来备忘和 SOP 检查点逐项映射，状态/证据有依据 |
| PLAN-004 | 审定权重并建立可计算台账 | 待执行 | 权重依据透明、可复算；未完成审计前不启用百分比 |
| PLAN-005 | 清理过时/重复的当前状态段 | 待执行 | 入口只有一个权威当前状态，历史清楚标注 |
| PLAN-006 | 增加台账一致性自动检查 | 待执行 | ID 唯一、状态合法、权重/证据约束、暂缓可见、公式可复算 |
| PLAN-007 | 复核阶段 2 退出条件 | 待执行 | 每项退出条件均有代码/测试/CI 证据或明确缺口 |

## 6. 唯一下一项：PLAN-003｜全量跨来源语义去重与状态冲突裁决

1. 以现有 A0–A112 规范化台账和 A0–A112 分批静态证据映射为输入；不得再次把“建立台账”或“按编号逐批初次映射”当作当前任务。
2. 对照正式验收计划、SOP、路线图、未来功能备忘、HELP、PROJECT_LOGIC、SESSION_HANDOFF、AI handoff、执行控制与 UX/安全审计，裁决每项是独立合同、相关但不合并、重复引用、历史记录、状态冲突或证据缺口。
3. 不删/重编号 A0–A112，不把相关任务自动合并；保留 A50/A56、A61/A62、A99 与 A57/A59、A57 双场景等已知裁决并逐项验证其余关系。
4. 对每项检查当前状态文字是否与代码/测试映射相符，证据是否绑定到当前 HEAD、证据能证明什么/不能证明什么、依赖与阶段退出条件是否有映射。历史 SHA 只作历史证据。
5. 先消除权威入口中会诱发重复执行的旧“当前任务/下一项”冲突，再进入 PLAN-004 权重审定、PLAN-005 状态段清理、PLAN-006 自动一致性检查、PLAN-007 阶段 2 退出复核。
6. 在语义去重、依赖和证据审计完成前，保持 `fully_audited=0`、`semantic_dedup_completed=false`、`code_test_evidence_audit_completed_ids=0`；不赋权、不发布总体完成率、不开发产品功能。

## 7. 固定边界
PR #32 不合并。Windows 真机、真实素材、真实 Provider/扣费、剪映现场、真实投放和商业效果验收继续暂缓。最终输出至少 1080P 级。自动化通过不等于真实环境或商业质量通过。


## PLAN-003 跨来源覆盖盘点｜2026-10-15｜部分完成，不代表去重完成

本轮按当前分支读取并比对以下来源的任务编号出现情况：验收计划、验收 SOP、产品路线图、未来功能备忘、HELP、PROJECT_LOGIC、进度台账与执行控制协议。编号出现仅用于发现覆盖差异，不等同于内容一致、代码存在或验收通过。

| 来源 | 检出的 A 编号数 | 盘点结论 |
|---|---:|---|
| `docs/AD_STUDIO_ACCEPTANCE_PLAN.md` | 112 | 正式验收清单；已登记 A0–A112，A99 之外的编号均存在，A99 已恢复；需继续核对每项当前状态与证据 |
| `docs/AD_STUDIO_ACCEPTANCE_SOP.md` | 112 | 与正式验收编号总体覆盖相近；SOP 的重复叙述和历史验收记录需与计划逐项区分，不能把出现次数当独立任务数 |
| `docs/AD_STUDIO_PRODUCT_ROADMAP.md` | 14 | 只提及少量阶段锚点/代表任务，属于路线图层级，不要求逐个重复所有 A 编号；需把阶段目标、依赖、退出条件映射到正式任务 |
| `docs/AI_AD_STUDIO_FUTURE_FEATURE_MEMO.md` | 74 | 大量历史与未来条目交错；需逐项标识已实现、自动化通过、正式验收、待开发、暂缓和历史记录 |
| `apps/ad-studio-desktop/HELP.md` | 107 | 编号提及覆盖较广但不完整；未出现编号不能直接推断帮助内容缺失，需按功能主题与代码对照 |
| `apps/ad-studio-desktop/PROJECT_LOGIC.md` | 104 | 编号提及覆盖较广但不完整；未出现编号不能直接推断架构说明缺失，需按功能主题与代码对照 |
| `docs/AD_STUDIO_PROGRESS_DASHBOARD.md` | 28 | 只应包含关键状态/风险/关系，不以覆盖全部编号为目标 |
| `docs/AD_STUDIO_EXECUTION_CONTROL.md` | 0 | 执行规则文件，不承担 A 编号清单职责 |

### 本轮关系裁决（仍为局部）

- A50/A56：关联但不合并；原始行为合同与回归修复需保留各自验收维度。
- A61/A62：关联但不合并；历史成本迁移能力与迁移相关断言修复不是同一验收点。
- A57：单一编号含两个独立验收场景，逐场景核验。
- A99 与 A57/A59：相关但不合并；A99 的成功账本清除未计费兄弟镜头陈旧成本有独立行为/测试证据。
- A80、A84/A85、A89、A92/A93、A111，以及 A90–A98、A100–A112 的状态、依赖与独立执行合同仍需逐项核验。当前不能删除或静默合并任何 ID。

### 下一步

1. 按批次核对 A6–A17、A18–A33、A34–A67、A68–A89、A90–A112：每项记录计划原文、路线图/备忘/SOP 对应项、当前代码路径、专项测试、当前 SHA 证据、剩余验收条件。
2. 先做语义关系与状态来源裁决，不以编号提及统计代替内容审计。
3. 完成全量任务与依赖审计前，`fully_audited=0`、`semantic_dedup_completed=false`、`code_test_evidence_audit_completed_ids=0` 保持不变；不分配权重、不发布总体完成率。


## PLAN-003 当前代码/测试证据审计：A6–A11｜2026-10-15｜部分映射

核验基线为当前分支 SHA `464977a54e9784fff375ffe081985624688261e9`。本表只记录已查看的实现与测试线索；未运行本地测试，CI 通过只证明该 SHA 的工作流通过，不代表以下每项正式验收。

| ID | 已查看的实现/测试证据 | 目前可作出的结论 | 仍需核验/补证 |
|---|---|---|---|
| A6 商品资料 | `ad_studio/product_parser.py` 有平台识别、HTML/浏览器 Skill 回退、商品资料保存、独立 `product-library` 持久化与用户确认事实合并；`test_product_parser.py` 覆盖无效 URL、平台识别、浏览器回退、项目资料保存；`test_desktop.py` 有 `test_product_library_round_trip_preserves_user_facts` 与 `test_product_library_merge_does_not_invent_missing_facts` | 存在商品解析/持久化实现与若干离线回归 | 未证明淘宝/京东/拼多多/1688/抖音真实链接均可解析；需核对缺失资料 UI 提示、用户资料与素材关联、各字段异常/损坏文件恢复；不以网络夹具冒充真实平台验证 |
| A7 内容理解 | `test_desktop.py` 有 `test_ai_stage_prompts_preserve_product_fact_boundary`、`test_ai_create_plan_runs_full_understanding_to_asset_pipeline` | 存在阶段提示词事实边界与流水线路由测试 | 尚未证明真实模型语义质量、卖点排序正确性、镜头价值/重复镜头/口播价值判断准确；需逐条对应正式 A7 清单 |
| A8 剪辑策略 | `test_desktop.py` 有 `test_three_task_types_have_distinct_deterministic_policies`、`test_footage_planner_uses_only_supplied_assets_and_respects_task_rules`、`test_footage_planner_rejects_missing_plan_output` | 已有三类任务策略、限定素材引用与无效计划失败路径的自动化证据 | 用户自定义条件覆盖、无法确定时人工确认、商品类型策略、自动时长与镜头排序仍需逐项映射；策略正确性与真实商业效果未验收 |
| A9 真人口播 | `test_desktop.py` 有 `test_footage_plan_enforces_speech_filler_cleanup_and_timestamp_ranges`；`ad_studio/transcription.py` 实现音频提取及 OpenAI-compatible 转写入口 | 存在口播废话处理合同与转写入口 | 未发现本轮已核验到的转写失败/时间戳错位/核心卖点误删专项覆盖；真人与 AI 声音冲突规则需查明实际实现和测试；真实音频识别质量暂缓现场验收 |
| A10 音频 | `ad_studio/audio.py` 实现 FFmpeg 人声轻度降噪、响度归一、循环 BGM 混音与缺失 FFmpeg 错误；`test_desktop.py` 有 `test_audio_mixing_preserves_voice_and_lowers_bgm` | 有混音主路径测试与 FFmpeg 缺失的显式错误路径实现线索 | 尚未看到独立覆盖所有音频失败、损坏输入、BGM 不存在/时长异常、降噪和响度归一质量的完整矩阵；用户音乐库、AI 配音的实际接入需单独确认 |
| A11 字幕 | `ad_studio/subtitles.py` 与 `test_subtitles.py` 覆盖字幕分段、真实片段时长、密度警告、SRT cue 解析及无效/越界时间窗；`test_desktop.py` 有 `test_subtitles_use_real_timestamps_and_segment_long_speech` | 字幕时间窗与密度的离线回归证据较明确 | 尚未由本轮证据证明字幕与真实口播逐字一致、商品事实一致、字体授权来源可追踪及仅使用免费商用字体；中文可读性和真实成片效果待真实素材验收 |

### A6–A11 状态纪律

- 以上六项均是“证据已部分映射”，不是“正式验收通过”。
- 未把测试名称或实现函数直接视为整项验收完成；缺少专项测试的项目记录为待补证/待核验，不在本轮直接增加或执行新的产品功能。
- 本轮不改变 `fully_audited=0`、`semantic_dedup_completed=false`、`code_test_evidence_audit_completed_ids=0`；不分配权重、不发布总体完成率。
- 下一批继续按正式验收计划核验 A12–A17（缺口判断、AI 生成、实拍+AI 混合制作、三类成片生产），并记录当前 SHA、测试路径与未覆盖条件。


## PLAN-003 当前代码/测试证据审计：A12–A17｜2026-10-15｜部分映射

核验基线：`177088ee6a743253d61dfe3ecb74842babe8e2a9`。依据当前代码、测试文件与正式验收计划进行静态证据映射；不代表本轮在本地重新运行了所有测试，也不等于逐项正式验收。

| ID | 已查看的实现/测试证据 | 目前可作出的结论 | 仍需核验/补证 |
|---|---|---|---|
| A12 缺口判断 | `ad_studio/hybrid_router.py` 的 `route_footage_gap_tasks()` 对商品/真人证据、真人口播辅助画面、通用画面、Provider 可用性和预算进行分流；`test_desktop.py` 有 `test_hybrid_gap_router_blocks_product_evidence_and_respects_budget` | 存在确定性缺口路由与预算/证据保护的专项测试线索 | 关键词规则是否覆盖语义变体、分类误报/漏报矩阵、UI 是否清楚显示“需要补拍/人工确认”仍需核验；不能把路由建议等同于实际补拍已完成 |
| A13 AI 生成 | `ad_studio/hybrid_generation.py` 接入配置的视频/图片 Provider、预算闸门与费用账本；`test_hybrid_generation.py` 覆盖 Provider 未配置不冒称成功及商品证据生成拦截；`test_desktop.py` 有生成失败状态、待复核阻止交付和预算测试 | 已有能力缺失、证据拦截、失败状态和待复核闭环的自动化线索 | 真实 Provider 请求/轮询/超时/扣费对账、输出媒体有效性、每种错误恢复及图片生成预算边界仍需逐项检查；真实 Provider/实际扣费按用户要求暂缓 |
| A14 实拍+AI 混合制作 | 混合路由与生成桥接保存来源类型、生成路径、费用和待复核状态；`test_desktop.py` 有 `test_hybrid_generated_shot_requires_human_review_before_acceptance`、`test_reviewed_hybrid_task_persists_into_project`、`test_final_render_inputs_are_ordered_and_pending_hybrid_is_excluded`、`test_a23_hybrid_review_to_final_render_is_closed_loop` | 自动化证据覆盖来源/审核状态持久化及待复核素材不得进入最终输出的关键路径 | 需进一步逐项确认实拍来源同样保留、最终成片逐镜头来源清单是否完整、跨项目/版本/异常恢复后来源和审核状态是否始终一致；真实混合成片检查暂缓 |
| A15 电商短视频生产 | `test_desktop.py` 有三类任务策略、素材计划、音频混音、字幕时间戳、最终输出媒体质检、1080P 级尺寸检查和输出清单相关测试；生产代码包含镜头渲染、拼接、后处理和最终门禁 | 主链组件与若干交付安全合同有自动化证据 | 尚不能证明 A15 全部要求（自动选片、镜头排序、卖点表达、真人口播、字幕、音频、画幅、时长、成片输出）在一个完整场景中全部通过；需建立逐项到测试/输出证据的映射 |
| A16 商品主图视频生产 | 共用商品资料、镜头规划、商品事实边界和最终渲染链；已有 `test_product_library_merge_does_not_invent_missing_facts`、`test_ai_stage_prompts_preserve_product_fact_boundary` 等相关测试 | 有商品事实保护与通用生产链证据，但尚未发现本轮核验到的 A16 专项视觉验收测试 | 商品主体持续清晰、不被字幕遮挡、展示顺序、细节镜头有效性、参数一致性和画面适配均需单独验收；不得仅凭共享渲染链宣称商品主图视频合格 |
| A17 广告投放视频生产 | `test_desktop.py` 有创意版本独立状态、创意差异机制分析、禁止虚构投放指标、性能指标计算/持久化及版本切换隔离等测试 | 多版本状态隔离与创意分析有自动化证据 | Hook、卖点组合、证明方式、CTA 与创意差异是否在最终产物中可辨识，需映射到明确输入/输出断言；CTR/CVR 的计算或模拟数据不代表真实投放效果，商业验证仍暂缓 |

### A12–A17 状态纪律

- 六项均标记为“证据已部分映射”，不标记正式验收通过。
- 相关测试可能覆盖共享生产组件，不等于 A15/A16/A17 每个业务目标均被完整验证。
- 进度台账的 `code_test_evidence_reviewed_ids` 更新为 18（A0–A17 已进行部分映射）；`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false` 保持不变。该计数只表示开始查看过的编号数，不代表覆盖完整或验收完成。
- 下一批按计划审计 A18–A33，并同步检查各编号是否独立、相关或疑似重复；不删编号、不加新产品功能、不分配权重、不计算整体完成率。


## PLAN-003 当前代码/测试证据审计：A18–A33｜2026-10-15｜部分映射

核验基线：`53800b7845a9db49c329242506d80f6a1747281c`。本轮已检查正式验收计划 A18–A33、`test_desktop.py`、`test_a33_full_flow.py`、`test_ai_handoff.py` 与逻辑文档中的相关说明。以下是静态证据映射；历史验收记录、当前测试名称或 CI 绿灯本身均不自动构成本轮逐项重新验收结论。

| ID | 已找到的代码/测试证据 | 本轮结论与仍需核验 |
|---|---|---|
| A18 多版本 | `test_desktop.py`: `test_creative_variants_keep_independent_variant_state`、`test_variant_state_survives_plan_switch`、`test_batch_generation_captures_original_variant_before_preflight`、`test_variant_render_paths_are_physically_isolated`；逻辑文档记录 `variant_shot_cache` / `variant_outputs` | 有版本状态隔离、切换和物理路径隔离证据。仍需映射原始版本可追溯及每版本独立输出的完整合同，并检查版本缺镜头、失败恢复、输出清单之间的关系。 |
| A19 创意实验设计 | `test_creative_variant_audit_distinguishes_mechanism_from_surface_changes`、`test_creative_variant_analysis_does_not_assume_platform_or_fabricate_metrics`；版本性能指标有独立持久化测试 | 投放前创意机制差异和不虚构平台指标有证据。仍需逐条核验单机制/多机制/仅表层/无明显差异分类、测试目的/观察项/下一轮建议的结果字段和边界；真实平台效果不在本轮验收范围。 |
| A20 创意事实检查 | 相关测试包括 `test_a20_final_delivery_safety_gate_blocks_unverified_risks`、商品事实边界提示词测试 | 最终闸门能拦截部分未验证风险；仍需把卖点依据、禁用词、绝对化表达、资料缺失提示和不编造商品事实分别映射到输入与断言，不能仅以最终闸门代替全部创意事实检查。 |
| A21 分镜事实检查 | `test_ai_stage_prompts_preserve_product_fact_boundary` 与最终交付安全相关测试 | 有商品事实边界与交付安全证据；分镜每项功能/外观的来源追溯、字幕事实一致性以及“文本检查不冒充视觉检查”仍需独立核验。 |
| A22 视觉事实检查 | `test_a20_final_delivery_safety_gate_blocks_unverified_risks`、`test_a24_final_safety_gate_blocks_all_explicit_risk_classes`；项目包含视觉复核相关数据与人工核验能力 | 有安全闸门阻断和复核状态证据；遮挡、模糊、抖动、实际素材映射、风险追踪及未分析不标为确认，需逐项核验其真实输入、状态转换和测试覆盖。 |
| A23 风险控制 | `test_a24_final_safety_gate_blocks_all_explicit_risk_classes`、`test_a24_build_final_cannot_write_output_when_safety_gate_blocks`、`test_a23_hybrid_review_to_final_render_is_closed_loop` | 风险阻断、未复核镜头不进入最终渲染的关键路径有测试。权限等级、人工批准、dry-run、audit log 与未授权真实写操作需按正式 A23 原文逐项映射，不能仅凭最终安全闸门断言整项完成。 |
| A24 最终安全闸门 | `test_a24_final_safety_gate_blocks_all_explicit_risk_classes`、`test_a24_build_final_cannot_write_output_when_safety_gate_blocks` | 有显式风险分类和禁止写出最终文件的专项测试。仍需确认每个风险来源都被汇总、原因可追踪、不同风险组合不会被覆盖；历史通过记录需在当前 HEAD 独立重核。 |
| A25 媒体质量检查 | `test_a25_media_qc_rejects_missing_empty_and_no_video_stream`、`test_a25_media_qc_rejects_zero_duration_and_invalid_dimensions`、`test_a25_media_qc_failure_never_marks_manifest_deliverable`、`test_a25_build_final_deletes_invalid_output_and_writes_no_manifest`；另有 1080P 级尺寸测试 | 文件/视频流/时长/尺寸/失败交付状态有专项证据。尺寸归一化、ffprobe 复核和 AI 细节增强的区别必须分别核验；1080P 像素尺寸不能证明细节恢复或商业画质。 |
| A26 成片版本历史 | `test_a26_final_output_history_keeps_revisions_independent`、`test_final_output_history_is_separated_by_variant_and_aspect` | 版本、画幅及修订历史独立有测试证据。历史字段是否完整覆盖输出路径、时长、镜头数、交付状态和创建时间，需逐字段检查。 |
| A27 成片交付中心 | `test_a27_delivery_recheck_reports_blocker_then_recovers_without_regeneration`、`test_final_delivery_repair_routes_point_back_to_correct_stage` | 阻塞报告、修复路由、复查不触发重新生成有证据。仍需检查 UI 呈现、每类问题定位与恢复路径映射；纯数据层测试不等于 Windows UI 验收。 |
| A28 本地项目数据 | `test_a28_project_persistence_restores_versions_material_status_review_and_output_history`、`test_a28_two_projects_do_not_share_persistent_state` | 项目隔离及版本、素材、审核、输出历史恢复有专项测试。异常/部分损坏数据、升级兼容、用户自定义路径及跨版本持久化边界仍需核验。 |
| A29 数据边界 | `test_a29_real_data_boundary_requires_explicit_user_provenance_and_unverified_status`；逻辑文档规定用户提供来源与 `verification_status=unverified` | 用户输入数据与系统验证状态的边界有专项证据。仍需检查所有指标/来源入口是否统一执行边界，不将用户提供误标为平台 API 已验证；真实平台数据仍暂缓。 |
| A30 失败恢复 | `test_a30_recovery_records_failures_without_losing_project_state`、`test_a30_recovery_cleans_interrupted_assets_and_marks_corrupt_outputs`、`test_a30_budget_and_non_retryable_failures_have_explicit_next_actions` | 中断恢复、损坏输出、预算与不可重试失败有专项证据。正式清单中的全部故障注入项（路径失效、AI 调用/生成失败、输出失败、重开、中途退出等）需逐项核对覆盖，不推定全覆盖。 |
| A31 帮助文档 | `test_a31_handoff_docs_contain_project_map_progress_acceptance_tests_and_safety_boundaries`；计划中有 HELP/PROJECT_LOGIC/关键文档同步要求 | 有接手文档内容测试。仍需验证每次相关代码/流程变更后文档确实同步到当前 SHA，文档覆盖检查不等于内容语义永远正确。 |
| A32 AI 接手能力 | `test_ai_handoff.py` 包含 `test_a32_history_blind_ai_can_recover_required_project_context` 及多项 handoff 约束检查 | 自动化检查会验证接手入口、架构、进度和安全边界等关键文本；它不能单独证明文档所有状态都与最新代码一致，因此本次接手文件与实时 HEAD 仍需持续校准。 |
| A33 完整用户流程 | `test_a33_full_flow.py` 覆盖三类任务正常、异常、安全拦截、修复复查和交付；测试对 concat、normalize 与 ffprobe 使用 mock/夹具 | 有离线流程合同证据，但该测试明确模拟媒体操作，不是完整真实媒体端到端，更不是真实模型、Provider、Windows 桌面或商业成片验收。三类流程的实际素材与现场验证仍按用户要求暂缓。 |

### A18–A33 审计状态与后续

- A18–A33 共 16 项均只标记为“证据已部分映射”；本轮不重新盖章为正式验收通过。
- A20–A25 的安全/交付检查存在交叉覆盖，但不因此合并 ID；A26–A30 分别涉及历史、交付交互、持久化、数据边界和恢复，不能以单一通用测试替代。
- A31/A32 是文档与接手能力合同；A33 是夹具隔离的离线流程回归。两者都不能替代真实环境验收。
- `code_test_evidence_reviewed_ids=34` 表示 A0–A33 已开始证据映射，不代表 34 项审计完整；`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false` 继续保持。未分配权重，不计算整体完成率。
- 下一批按既定顺序继续 A34–A49；每项仍需检查正式原文、当前实现、专项测试、任务依赖与是否重复，并保留历史验收记录与当前基线的区别。


## PLAN-003 当前代码/测试证据审计：A34–A49｜2026-10-15｜部分映射

本轮开始基线：`b48f7a9859476ed639bc9220035c986cd5e77c37`；该 SHA 的 CI Push、CI PR、docs-sync Push、docs-sync PR 四项均成功，PR #32 为 Open / unmerged。审计来源包括正式验收计划、桌面测试、短剧测试、PROJECT_LOGIC、AI handoff 与当前进度台账。下列是静态证据映射，不是对每项重新执行测试后的正式验收。

| ID | 已找到的代码/测试/文档证据 | 审计结论与剩余核验 |
|---|---|---|
| A34 商品画面对比 | `test_short_drama.py` 有 `test_ai_visual_comparison_flags_mismatch_without_auto_approval`、`test_ai_visual_comparison_never_auto_approves_a_match`、`test_ai_visual_comparison_rejects_missing_reference_and_wrong_mode`、`test_ai_visual_comparison_rejects_empty_and_unsupported_files`；也有模型路由、证据和待复核状态相关实现 | 有疑似不匹配拦截、匹配也不自动通过、输入错误防护的测试证据。需进一步核验视频代表帧提取与清理、独立模型路由配置、费用取消无副作用、持久化全字段和当前 SHA 下的专项执行结果。Windows/真实 Provider 暂缓。 |
| A35 问题镜头仅重生成 | `test_product_drama_regeneration_changes_only_selected_shot_and_preserves_history`、`test_product_drama_regeneration_rejects_wrong_mode_and_empty_correction`；验收计划记录确认费用后仅准备待重生成，不自动调用 Provider | 单镜头作用域和历史保留有测试证据。失败恢复、未选中镜头/其他项目/原始资产不变的完整矩阵需独立映射；不得把“准备重生成”说成已完成真实生成。 |
| A36 视觉结果辅助修复 | `test_product_visual_correction_suggestion_uses_review_findings_as_editable_draft`、`test_product_drama_regeneration_rejects_non_finite_cost_and_invalid_version` | 可编辑修正草稿、异常费用/版本防护有专项测试线索。仍需确认取消无版本变化、费用确认前零 Provider 调用、核验历史保留和当前版本状态重置全部有直接断言。 |
| A37 草稿换行 | `test_a50_video_prompt_uses_real_line_breaks` 与短剧修正草稿生成相关测试；handoff 记录真实换行回归历史 | 有真实换行回归测试线索，但 A37 目标是视觉修正草稿显示，不能仅凭 A50 视频提示词测试视为完全等价。需确认 A37 测试直接覆盖摘要和 issues 的实际换行显示。 |
| A38 跨会话接手 | `test_ai_handoff.py` 检查 handoff 章节、CI 边界和接手约束 | 接手文档关键结构有测试。当前文件仍包含多个历史 SHA/PR 状态段落；顶部当前状态与实时 HEAD 对齐很重要，后续应在全量审计中检查历史段落是否可能误导新 AI。 |
| A39 功能分支 CI | 当前分支已触发 CI Push 与 CI PR，且本轮开始基线四项检查全绿；执行控制协议规定所有新 SHA 重新核验 | 当前基线证明分支触发有效；正式计划里 A39 仍是待勾选的历史条目，需在台账中区分“当前 CI 事实已观察到”与“正式验收记录/计划勾选已同步”。 |
| A40 接手测试路径 | `test_ai_handoff.py` 有路径基准相关约束，handoff 记录了此前路径失败修复 | 有路径约束线索；仍需在全量审计中确认测试实际检查的是仓库根目录 ROOT 解析，不仅是文本存在性。 |
| A41 接手文案断言 | handoff 测试包含多条关键文案断言；历史记录记载曾修复文案断言失败 | 当前 CI 绿说明当前测试通过，但不等于所有断言都能抵抗语义漂移。后续需逐条核对计划中的关键断言和对应文件语句，不删除有效回归测试来换绿灯。 |
| A42 CI 绑定 SHA | 本轮重新核对实时 HEAD 与四项工作流，未把旧 SHA 结果套用到当前提交 | 本轮操作符合 A42 的原则；计划内的 `443f713...` 只是历史基准，不能作为当前 HEAD 的验收证据。 |
| A43 重生成失败恢复 | `test_a43_regeneration_failure_restores_previous_good_video_and_persists_it`、`test_a43_project_recovery_restores_previous_video_after_interrupted_regeneration`；计划记录旧视频路径、Provider 失败恢复和中断恢复 | 有旧视频保护、重载与中断恢复证据。仍需逐项核对旧文件缺失/空文件、临时文件清理、状态和错误原因等边界，部分内容由 A53/A54 后续任务补充，不可把相关任务合并。 |
| A44 短剧镜头映射 | `test_product_drama_shot_mapping_uses_stable_storyboard_index_after_insertions`、`test_product_drama_legacy_shot_mapping_uses_unique_title_and_episode`、`test_product_drama_ambiguous_legacy_mapping_fails_closed` | 稳定编号、旧项目唯一匹配与歧义拒绝有直接测试线索。仍需确认生成、修正草稿等所有调用点都使用该映射；不能用项目显示序号替代源 storyboard 编号。 |
| A45 失败恢复 UI | `test_a45_ui_failure_state_keeps_recovered_previous_video_status` | 已找到 UI 状态测试。仍需核验恢复标记、文件存在、文件非空三条件同时满足时才显示恢复成功，且缺失证据时不误报。 |
| A46 编辑镜头旧版保护 | `test_a46_edit_shot_routes_through_safe_regeneration_transition` | 编辑入口调用统一版本转换有测试线索。需检查保存旧视频路径、版本递增和编辑取消的边界；历史 CI 失败记录需与当前结果分开保留。 |
| A47 素材解析失败恢复 | `test_a47_asset_resolution_failure_restores_previous_video` | 有素材解析失败后恢复旧视频的测试。需核验失败时不调用视频 Provider、清理临时输出、重新加载状态准确。 |
| A48 实拍裁剪安全输出 | `test_a48_footage_trim_failure_does_not_delete_existing_output` | 有裁剪失败不破坏正式输出的测试。需核验临时文件、非空校验、原子替换及多段拼接异常边界；夹具测试不能替代真实素材验收。 |
| A49 多段实拍中断清理 | `test_a49_missing_footage_source_cleans_stale_split_parts_and_keeps_old_video`；计划记录项目恢复清理普通临时输出与多段分段文件 | 有源素材缺失后清理残留并保留旧视频的测试线索。需确认进程中断、项目重载、分段文件完整覆盖，以及不会误删仍被引用的源文件。 |

### A34–A49 关系与进度裁决

- A34–A49 共 16 项均为“部分证据映射”，不是本轮正式验收通过。A34/A35/A36 形成视觉核验→单镜头修复链路，但分别具有独立输入、费用、状态和安全合同，不合并。
- A43–A49 形成重生成失败恢复、稳定镜头映射、UI 状态、素材解析、裁剪输出和中断清理等连续修复链路；相互相关但失败阶段与回退条件不同，不合并任务 ID。
- A37 的草稿换行与 A50/A56 的 Provider 提示词换行是相关回归问题，但对象不同；不得仅凭名称相似就认定相同验收条件。
- A38–A42 是接手/CI/证据纪律类任务；实时 CI 绿灯是当前观察事实，但计划状态与历史文档一致性仍需核验。
- 台账更新为 `code_test_evidence_reviewed_ids=50`，表示 A0–A49 已开始映射；`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false` 保持不变。未分配权重，不计算整体完成率。
- 下一批按编号继续 A50–A67，重点保留 A50/A56（行为合同与回归修复）、A57（含两个独立场景）、A61/A62（历史迁移与断言修复）的既有“不合并”裁决，并继续核验 A68–A74 的历史身份及当前证据。


## PLAN-003 当前代码/测试证据审计：A50–A67｜2026-10-15｜部分映射

本轮开始基线：`707758608e105840f21d4945aa40b3eb89b00522`；CI Push、CI PR、docs-sync Push、docs-sync PR 四项均 success；PR #32 Open / unmerged。已检查正式验收计划 A50–A67、桌面测试、短剧测试、AI handoff 测试与逻辑文档。下列是静态证据映射，不等同于在本轮重新执行全部测试，也不自动改写正式验收状态。

| ID | 已找到的代码/测试证据 | 结论与剩余核验 |
|---|---|---|
| A50 视频提示词换行合同 | `test_a50_video_prompt_uses_real_line_breaks` 捕获 Provider 请求文本，断言标题/画面/文案真实分行 | 自动化合同有直接测试。仍需真实 Provider 提示词效果验证；文本换行通过不代表广告效果通过。 |
| A51 费用预估前置校验 | `test_a51_cost_estimate_is_validated_before_confirmation`；计划列明非数字、NaN、正负无穷、负数、空值 | 有非法费用拒绝测试线索；需核对每类输入是否逐一断言版本不变、Provider 零调用和 UI 错误反馈。 |
| A52 失败尝试与成本去重 | `test_a52_failed_video_attempt_is_auditable_without_double_counting_actual_cost` | 失败记录保留、失败估算不算实际成本、成功重试独立记账有证据；真实 Provider 账单对账仍暂缓。 |
| A53 旧视频恢复非空保护 | `test_a53_recovery_rejects_zero_byte_previous_video` | 有零字节旧视频拒绝与恢复回归。仍需核验缺失路径、非文件、持久化重载和 UI 状态的全边界。 |
| A54 活动视频无效回退 | `test_a54_recovery_restores_valid_previous_video_when_active_video_is_zero_byte`、`test_a54_recovery_clears_zero_byte_active_video_without_previous_video` | 有有效旧版回退及无旧版安全降级测试。真实磁盘异常和 Windows 文件占用仍需独立环境验收。 |
| A55 Provider 成功与账本失败分离 | `test_a55_ledger_failure_does_not_turn_successful_video_into_provider_failure` | 成功视频保留、状态转为成本待核对有专项测试；需继续检查账本修复后重新对账及恢复记录完整性。 |
| A56 提示词换行回归修复 | A50 同一测试覆盖真实换行；逻辑文档记录双重转义故障及修复 | 与 A50 相关但不合并：A50 是原始行为合同，A56 是后续重构引入回归后的修复。要保留历史失败和修复证据，不以当前绿灯抹去原因。 |
| A57 成本待核对 UI | `test_a57_generate_shot_ui_surfaces_cost_reconciliation_state` | 成功视频但成本异常时不显示正常实际累计金额有测试。 |
| A57 项目恢复与成本对账 | `test_a57_project_recovery_reconciles_actual_cost_from_ledger`、`test_a57_project_recovery_preserves_legacy_cost_when_no_ledger_rows_exist`、`test_a57_open_existing_project_runs_recovery_before_display` | 账本重算、旧项目无账本时保留成本、打开项目触发恢复均有测试线索。该编号包含两个独立验收场景（UI 状态与项目恢复/对账），本台账分别映射，不合并成单一断言。 |
| A58 视觉对比输入证据校验 | `test_ai_visual_comparison_rejects_missing_reference_and_wrong_mode`、`test_ai_visual_comparison_rejects_empty_and_unsupported_files` 等短剧测试 | 有无效参考/生成素材输入防护线索；真实视觉模型准确率、费用及真实生成素材验证仍暂缓。 |
| A59 成本汇总单一事实源 | `test_a59_project_cost_total_comes_from_success_ledger_rows` | 项目成本按成功账本汇总的专项测试存在；需继续核对分类成本、项目快照和镜头字段的所有写入入口是否统一。 |
| A60 失败-only 账本兼容 | `test_a60_failed_only_ledger_preserves_legacy_actual_cost` | 失败账本行不把旧项目实际成本清零，且估算失败成本不冒充实际支出有测试线索。 |
| A61 旧成本迁移 | `test_a61_legacy_costs_migrate_once_before_first_successful_charge`、`test_a61_record_many_migration_keeps_ledger_rows_atomic` | 首次成功记账前迁移历史成本、避免重复迁移、批量写入原子性有专项测试；真实账单对账暂缓。 |
| A62 迁移文案断言修复 | `test_handoff_mentions_a61_legacy_cost_migration` 及 AI handoff 文案约束测试；计划记录术语断言修复 | A61 是成本迁移行为，A62 是接手文案/测试断言修复；不合并。仍需保证测试词汇与文档语义一致，而非只追求字符串匹配。 |
| A63 迁移基线保留 | `test_a63_migrated_legacy_cost_survives_when_new_charge_record_fails` | 迁移成功、后续费用写入失败时保留历史成本与账本行有测试证据；需核验重启恢复和再次记账幂等性。 |
| A64 素材生成与成本记账分离 | `test_a64_asset_cost_record_failure_keeps_generated_asset_and_marks_reconciliation`、`test_a64_asset_generation_callers_distinguish_cost_failure_from_generation_failure` | 成功素材不会因账本失败被误报为生成失败，有调用入口测试；仍需核对所有素材类型与恢复入口一致性。 |
| A65 账本原子写入和历史完整性 | `test_a65_single_ledger_record_uses_atomic_replace_and_preserves_old_file_on_failure`、`test_a65_ledger_retains_more_than_2000_cost_history_rows` | 原子替换失败保护和超过 2000 行历史保留有专项测试；并发写、异常终止与真实文件系统边界仍需检查。 |
| A66 人工商品核验证据文件 | `test_manual_product_visual_review_rejects_missing_empty_or_unsupported_evidence`、`test_manual_product_visual_review_persists_real_evidence` | 无效证据拒绝、有效证据路径持久化有测试；文件存在只证明有证据文件，不证明商品外观/功能真实匹配。 |
| A67 短剧核验证据失效保护 | `test_audit_rejects_stale_or_missing_manual_visual_evidence`、`test_passed_visual_status_without_manual_evidence_is_still_flagged` | 审查时重新验证证据路径、历史 passed 不能覆盖证据失效有测试。仍需真实素材/视觉判断与 Windows 操作验收。 |

### A50–A67 关系与状态裁决

- A50/A56 相关但不合并：行为合同与回归修复的职责不同。
- A57 在正式计划中重复使用编号，但包含 UI 成本待核对状态与项目恢复/成本对账两个独立场景；本轮分别映射，后续应在跨来源索引中保留“同编号双场景”事实，不能自行重编号或丢掉任一场景。
- A61/A62 相关但不合并：历史成本迁移能力 vs 文案断言修复。A63 是迁移后续写失败时保护基线，A64 是素材成功与成本记账失败分离，A65 是账本持久化完整性，分别有独立合同。
- A66/A67 是人工商品视觉核验证据链：文件有效性与审查时证据仍有效不同，不能以文件扩展名校验冒充商品真实性认证。
- 本轮 A50–A67 全部标记为“部分证据映射”，不重新盖章正式验收通过。台账 `code_test_evidence_reviewed_ids=68` 表示 A0–A67 已开始映射，不代表 68 项已完成审计；`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false` 保持不变。未分配权重，不计算整体完成率。
- 下一步按既定计划继续 A68–A82；A68–A74 的短剧剧情结构、因果证据和商品事实边界要逐项核对当前代码/测试与正式计划。不要开发新产品功能；真实 Provider/扣费、Windows 真机、真实素材、剪映现场和真实投放继续暂缓。


## PLAN-003 当前代码/测试证据审计：A68–A82｜2026-10-15｜部分映射

本轮开始基线 `c6c6294f0d1626cf6a8f65ccd364ae476a2e5520` 的 CI Push、CI PR、docs-sync Push、docs-sync PR 均 success；PR #32 Open / unmerged。已查看验收计划、`test_short_drama.py`、`PROJECT_LOGIC.md` 和 AI 接手测试。以下只记录代码/测试证据线索及计划同步缺口，不将静态阅读等同于重新执行测试或正式验收。

| ID | 当前代码/测试证据线索 | 审计结论/待核 |
|---|---|---|
| A68 后续剧情影响分析 | `test_continuity_impact_analysis_reports_only_existing_downstream_episodes`、`test_continuity_impact_analysis_rejects_non_downstream_episode` | 影响报告限定真实后续集、要求人工复核且不直接改写剧情；模型分析质量仍待人工评审。 |
| A69 故事引擎与留存设计 | `test_generation_rejects_short_drama_without_causal_story_engine`、`test_generation_rejects_story_with_too_few_escalation_steps`、`test_generation_prompt_requires_causal_conflict_hook_and_payoff` | 新生成结构约束与缺项审查有直接测试；字段存在不代表故事精彩，旧项目兼容仍需单独保留。 |
| A70 故事结构检查 | `test_audit_flags_missing_story_engine_and_hook_design`、`test_audit_flags_weak_escalation_and_retention_design` | 缺项和薄弱结构告警有测试线索；误报/漏报需真实剧情样例复核。 |
| A71 备选故事方向差异化 | 验收计划和逻辑文档明确至少两个方向、必需字段及核心机制重复拦截；测试文件含方向字段缺失拒绝用例 | 已有结构测试线索；签名差异不能证明自然语言语义差异，需人工样例评审。 |
| A72 人物动机与关系动力 | 验收计划/逻辑文档定义动机、恐惧或秘密、关系动态、决策压力等字段及新旧方案兼容；测试覆盖生成结构校验 | 结构字段校验不等于人物心理可信；应检查旧方案只 warning 的具体回归。 |
| A73 剧情事件因果链 | `test_generation_rejects_missing_causal_chain`、`test_generation_rejects_causal_chain_with_invalid_storyboard_reference`、因果链缺失审查测试 | 因果链结构和引用校验有测试；结构合法不证明整体因果自洽。 |
| A74 因果链与剧本/分镜证据 | 因果链证据不匹配、无效分镜引用及旧方案审查告警测试 | 原文可追踪性有测试线索；不能证明实际镜头呈现了该事件。 |
| A75 商品事实锁 | `test_product_fact_lock_warns_when_confirmed_fact_has_no_source`、`test_product_fact_lock_allows_unknown_fact_marked_unverified` | 有无来源已确认事实与未核实声明的测试；文本匹配不代替商品资料语义审核或法律意见。 |
| A76 卖点与分镜覆盖 | `test_audit_warns_for_selling_point_not_in_shot_text` | 无分镜文本覆盖时产生 warning 有直接负向测试；文本覆盖不等于真实画面展示。正式计划仍留有“最新 HEAD CI/doc-sync”未勾选，须按当前 SHA 记录。 |
| A77 关键剧情事件落地 | `PROJECT_LOGIC.md` 已描述 `narrative_function`、`story_event_reference` 和 `CAUSAL_EVENT_NOT_SHOWN`、`TURNING_POINT_NOT_STORYBOARDED`、`SETUP_PAYOFF_NOT_STORYBOARDED`；测试文件对应审查逻辑存在 | **计划仍标开发中且检查项未勾选**。本轮证据映射不代替逐条核验提示词、三类 warning 的正反例和最新 CI。 |
| A78 人物行动依据/信息掌握 | `test_audit_warns_when_character_action_has_no_basis`、`test_audit_warns_for_incomplete_character_action_basis`、`test_audit_warns_when_character_knowledge_source_is_not_script_evidence`、`test_audit_warns_when_causal_character_choice_is_not_in_referenced_shot` | 代码与专项测试线索存在，但计划仍标开发中。还需核对生成提示对每个行动人物的要求、可追溯来源和正向有效案例。 |
| A79 行动依据与镜头人物绑定 | 逻辑文档列出 `CHARACTER_ACTION_BASIS_NOT_IN_SHOT`、`CHARACTER_ACTION_BASIS_UNKNOWN_CHARACTER`；当前已查看测试片段尚未确认这两种情形均有直接测试 | 计划未勾选；必须补查对应正反向测试和旧方案 warning 兼容，不能只依据实现说明认定完成。 |
| A80 人物关系变化与剧情后果 | 逻辑文档列出 `RELATIONSHIP_CHANGE_UNSPECIFIED`、`RELATIONSHIP_CHANGE_NOT_SHOWN`；历史记录说明首轮 CI 曾因角色名集合初始化顺序失败 | 计划仍未勾选。需确认两类 warning 各有直接回归测试，并以当前 SHA 的完整 CI/doc-sync 证明当前实现，而非沿用历史修复 SHA。 |
| A81 人物状态与剧情连续性 | 测试文件含状态连续性缺失、未知人物、有效后续引用及状态未承接测试；计划记录历史 SHA `d976c34a48ff20af65648983be7855589ba2deca` 的 CI/doc-sync | 有历史自动化验收记录，但需与当前 HEAD 的代码和测试对应关系分开；人物心理/真实表演不在自动化证明范围内。 |
| A82 人物信息掌握与时间线 | 测试文件含先前揭示、既有知识、来源非剧本证据等用例；计划记录历史 SHA `8756b773c3b2ee3bf08b80bf3b31992b7081a606` 的 CI/doc-sync | 有历史自动化记录；当前映射支持时间顺序/文本证据约束，但不代表人物认知语义自然度已验收。 |

### A68–A82 关系与台账裁决

- A68 是跨集影响报告；A69/A70 是生成结构约束与审查器；A71/A72 是故事方向和人物字段；A73/A74 是因果链及证据映射；A75/A76 是商品事实与卖点覆盖；A77–A82 逐层覆盖镜头叙事功能、人物行动依据、人物引用、关系变化、状态连续性和信息时间线。相互依赖但验收对象不同，不按同属“剧情一致性”而合并。
- A77–A80 在正式计划中仍有未勾选/开发中状态，即使逻辑文档已有实现说明或测试文件存在，也不能据此擅自改成完成；下一阶段需直接核对专项测试、实际审查调用链和当前 SHA CI 证据。
- 本批 A68–A82 全部只记录为部分证据映射。台账 `code_test_evidence_reviewed_ids=83` 表示 A0–A82 已开始映射；`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false` 保持不变。未分配权重，不计算整体完成率。
- 下一步按编号继续 A83–A99，优先辨别 A83/A84 跨集事项、A85–A87 人物状态因果闭环与 A90–A98 等历史身份，不合并相邻任务；继续核对 A99 独立账本行为。暂不开发新产品功能，真实 Provider/扣费、Windows 真机、真实素材、剪映和真实投放继续暂缓。


## PLAN-003 当前代码/测试证据审计：A83–A99｜2026-10-15｜部分映射

本轮开始基线 `a2dd27fa6df1fb17cdaf2914b7633649809bd901` 的 CI Push、CI PR、docs-sync Push、docs-sync PR 四项均 success；PR #32 Open / unmerged。已检查正式验收计划、`test_short_drama.py`、`test_desktop.py`、`PROJECT_LOGIC.md` 与当前台账。以下是静态证据映射，不代表本轮重新执行了所有测试，也不将旧 SHA 的通过记录视为当前 SHA 正式验收。

| ID | 代码/测试证据 | 状态及剩余核验 |
|---|---|---|
| A83 承诺、误解与行动结果 | `test_a83_accepts_commitment_with_visible_later_fulfillment`、`test_a83_warns_when_promise_is_not_followed_through`、`test_a83_warns_on_invalid_or_nonchronological_obligation_references`、`test_a83_warns_when_obligation_references_unknown_character`、提示词合同测试 | 有正反例及来源/时间顺序检查。人物动机合理性、误解可信度和实际表演仍待语义评审。计划历史记录有旧 SHA 的自动化结果；不能代替当前 HEAD 检查。 |
| A84 跨集剧情承接 | `test_a84_accepts_open_obligation_carried_across_episode_boundary`、`test_a84_warns_when_open_obligation_is_not_carried_to_next_episode`、无效标记及后续镜头引用测试 | 有跨集承接与断裂测试；正式计划多项仍未勾选，必须保留该状态，当前 SHA 的正式验收需复核。 |
| A85 人物长期状态与关系 | `test_a85_accepts_persisting_character_relationship_state`、状态消失/未声明变化/缺转变证据/无效 persistence flag 与不可追踪证据测试 | 有多种正反例；旧方案兼容、完整字段异常矩阵与当前 SHA 正式验收仍需按计划逐项核对。 |
| A86 状态变化因果闭环 | `test_a86_accepts_ordered_character_state_causal_chain`、触发缺失/顺序错误/反应与后果缺失测试、提示词字段合同测试 | 有因果顺序测试线索；需核对所有指定引用异常码与旧方案兼容，不等于剧情因果在语义上成立。 |
| A87 状态到可观察表演 | `test_a87_accepts_observable_performance_for_changed_state`、抽象心理标签告警、表现未出现在引用镜头告警 | 有正反例；仍是文本定位，不是实际生成画面中的动作/表情/表演质量验收。 |
| A88 多人物状态依赖 | `test_a88_checks_cross_character_consistency_but_allows_different_beliefs`、`test_a88_warns_for_unknown_character_and_invalid_reference` | 覆盖同理解矛盾、允许不同信念、认知不对称缺因和无效人物/镜头引用；需确认无人物状态台账时仍执行，且正式计划 CI 项状态。 |
| A89 跨集演员/场景文本锁定 | `test_a89_series_asset_locks_flow_into_production_requirements`、集号范围/非法 schema 与未命中目标测试 | 结构与生产需求注入有测试；文本锁定不等于复用同一物理素材 ID，也不保证画面身份一致。计划记录历史 SHA 自动化通过。 |
| A90 精确物理素材 ID | `test_a90_series_asset_ids_are_bound_to_production_rows`、`test_a90_legacy_series_asset_locks_keep_tag_matching` | 明确 ID 绑定和旧版无 ID 标签兼容有测试；需以当前 SHA 重核全部 CI，并区分调度绑定与最终画面一致。 |
| A91 锁定资产失效预检 | A93/A95 生产入口与索引损坏测试线索覆盖 fail-closed、Provider 调用为零、原 ID 保留 | 与 A93/A95 相关但不合并；A91 的重开项目/恢复/重生成预检及所有失效类型需独立核验。 |
| A92 锁定 ID 到实际镜头绑定 | A92/A93 历史验收记录：跨集精确 ID 绑定、相似标签不覆盖、保存/重开持久化 | 计划记录自动化完成，但当前 HEAD 仍须确认相关测试仍在、当前 CI 通过；真实画面身份一致继续暂缓。 |
| A93 Provider 调用前阻断 | 历史专项测试记录锁定失效时 Provider 调用次数为 0，保留原 ID，其他镜头不受影响 | 有明确独立边界；当前 SHA 的自动化证据需重核，真实 Provider 视觉验证暂缓。 |
| A94 恢复原资产后的安全重试 | 历史记录覆盖原 ID 恢复后重新绑定，禁止相似标签覆盖与 fallback | 自动化历史记录存在；需区分旧 SHA 记录与当前 HEAD 证据。 |
| A95 素材索引损坏保护 | 历史专项测试记录无效 JSON 返回 `SERIES_LOCKED_ASSET_LIBRARY_UNAVAILABLE`、不调用 Provider、不影响其他镜头 | 失效保护有历史自动化证据；损坏/重载/当前 SHA 完整 CI 仍需重核。 |
| A96 索引修复后重试 | 历史专项测试记录索引修复后恢复精确 ID、禁止标签替换和自动生成 | 自动化历史记录存在；当前 SHA 证据需要重核，真实资产库环境测试暂缓。 |
| A97 恢复只重置缺失镜头 | `test_a97_project_recovery_only_requeues_missing_shot_and_preserves_valid_sibling` | 直接测试覆盖目标镜头恢复、有效兄弟镜头隔离；需确认保存/重载后版本、状态、费用等断言全覆盖及当前 SHA CI。 |
| A98 重复恢复摘要稳定 | `test_a98_recovery_repeats_missing_shot_until_regenerated` | 测试覆盖未重新生成前持续列出缺失镜头；普通待生成镜头不应误报，需复核兄弟镜头保存/重载边界。 |
| A99 成功账本清除兄弟镜头陈旧成本 | `test_a99_successful_ledger_clears_stale_cost_on_unbilled_sibling_shot`；`PROJECT_LOGIC.md` 说明仅在存在成功账本行时以账本为权威来源 | A99 与 A57/A59 相关但不合并：A99 独立规定存在成功账本后未计费兄弟镜头的陈旧快照应归零；失败-only/无成功账本时仍保留旧成本兼容。需核对恢复、保存、重载和多镜头场景。 |

### A83–A99 关系与台账裁决

- A83/A84 是单集叙事事项跟进与跨集承接；A85–A87 是长期状态、因果闭环与可观察表现；A88 是多人物依赖关系（独立于可选人物状态台账）；A89–A96 是从文本锁定、物理 ID、失效 fail-closed 到安全恢复的不同层次；A97/A98 是恢复摘要边界；A99 是成功账本下的陈旧镜头成本清理。相关依赖不代表同一验收合同，保留所有编号。
- A84–A87 正式计划中仍存在未勾选项目；A88 计划文本出现字面转义换行与重复段落痕迹，需在跨来源文档清理阶段处理，不能将格式问题当成功能已验收。A89–A96 的历史 CI 记录绑定旧 SHA，不自动证明当前 HEAD。A97–A99 有直接测试名线索，仍需当前 SHA 运行和逐项断言审查。
- 本批 A83–A99 全部记为“部分证据映射”。台账 `code_test_evidence_reviewed_ids=100` 仅表示 A0–A99 已开始映射；`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false` 保持不变。没有分配权重，不计算整体完成率。
- 下一步继续审计 A100–A112，并同步检查商业剪辑专项和 A102 最低 1080P 导出条款的独立状态。仍不开发新产品功能；真实 Provider/扣费、Windows 真机、真实素材、剪映现场和真实投放继续暂缓。


## PLAN-003 当前代码/测试证据映射：A100–A112｜2026-10-15｜部分映射

本轮开始前已重新核对基线 `14ac6d153cf2f9027d02ff71a82ff8facc643768`：CI Push、CI PR、docs-sync Push、docs-sync PR 四项均 success；PR #32 Open / unmerged。本轮对验收计划、`PROJECT_LOGIC.md`、`test_postprocess.py`、`test_ffmpeg.py`、`test_music_sync.py`、`test_creative_engine.py`、`test_subtitles.py` 与 `test_desktop.py` 做静态证据映射。没有声称在本轮本地重新运行全部测试。

| ID | 已找到的代码/测试证据 | 审计结论与剩余边界 |
|---|---|---|
| A100 淡出时间窗 | `test_fade_out_happens_at_end_after_speed_change`、`test_short_clip_fade_out_does_not_exceed_clip_duration` | 覆盖变速后末尾淡出与短片段边界；FFmpeg 命令断言不等于真实视频观感验收。 |
| A101 变速音画同步 | `test_speed_change_keeps_audio_in_sync_with_video`、`test_normal_speed_does_not_add_unneeded_audio_tempo_filter` | 检查视频 setpts 与音频 atempo 命令参数；真实音画同步仍需媒体/Windows 验证。 |
| A102 最低 1080P 输出 | `test_final_output_normalizer_targets_1080_class_resolution_and_keeps_audio`、`test_final_output_normalizer_supports_landscape_and_square_profiles`、`test_final_output_inspection_rejects_below_1080_class_resolution`、最终输出媒体 QC 测试 | 有尺寸归一化命令和低尺寸拒绝线索。不能将放大到 1080P 说成 AI 细节增强；最终实际 FFprobe/真实媒体链仍应按正式计划逐项确认，计划中验收勾选不能因历史记录自动变更。 |
| A103 淡入/淡出音画同步 | `test_fade_in_synchronizes_video_and_audio`、`test_fade_out_synchronizes_audio_at_end_without_speed_change`、A100 变速淡出/短片段测试 | 有视频/音频滤镜合同；仍需核对缺失音轨、异常探测时长等边界是否在计划范围内。 |
| A104 相邻镜头交叉溶解 | `test_crossfade_builds_video_and_audio_overlap_filters`、`test_crossfade_rejects_mismatched_transition_count`、`test_final_builder_uses_crossfade_only_when_requested`；生产路径 `ProductionStore.build_final()` → `concat_with_transitions()` | 已找到 xfade/acrossfade 与显式触发测试；真实素材编码器、无音轨静音补齐、短镜头与转场听感仍待真机验证。 |
| A105 pacing 到实际速度 | `test_pacing_sets_executable_default_speed`、`test_explicit_speed_overrides_pacing_default`、`test_unknown_pacing_falls_back_to_standard`；后处理音轨同步测试 | 有映射和覆盖规则测试；仍需确认未知标签、schema 省略 speed 与运行时执行路径整体一致。 |
| A106 商业角色默认剪辑决策 | `test_role_defaults_drive_duration_speed_and_transition`、`test_last_cta_defaults_to_fade_out`、`test_explicit_editing_decisions_override_role_defaults` | 有角色默认、CTA 和显式值优先测试；依据是文本关键词，不是视觉识别；需核对 rationale/basis/参数来源与实际执行参数完整一致。 |
| A107 商业角色时长进入运行时请求 | `test_resolved_duration_and_editing_fields_reach_runtime_mapping` | 有运行时字段映射测试；不证明外部 Provider 严格按请求时长返回成片。 |
| A108 字幕密度与时间轴 | `test_short_caption_spans_actual_clip_duration`、`test_long_caption_is_split_and_timed_across_clip`、`test_short_shot_reduces_caption_switching_and_reports_density`、`test_high_density_warning_does_not_rewrite_caption_words` | 有字幕时间轴、密度提示和原文保护测试；真实可读性、ASR/口播语义同步与 Windows 画面验收仍暂缓。 |
| A109 音乐节拍与切点 | `test_detects_regular_synthetic_clicks`、`test_silence_has_no_confident_beats`、`test_low_confidence_preserves_original_timing`、`test_safe_beat_snap_changes_real_shot_durations`、`test_retime_command_keeps_audio_synced`、`test_global_bgm_uses_one_continuous_track_after_assembly`；生产路径含 `plan_beat_aligned_durations()`、`retime_clip()` 与全局 BGM 混合 | 有合成节拍、低置信度回退、时长变化、音轨同步和全局 BGM 测试线索；真实音乐、旧项目音轨兼容和主观听感仍未验收。 |
| A110 商业内容保护 | `test_content_protection_estimates_dialogue_text_and_product_hold`、`test_beat_snap_preserves_dialogue_and_product_holds`、`test_underlength_dialogue_prevents_music_retiming` | 有台词/商品停留保护线索；文本估算不能替代真实字幕阅读时长或实际口播时长，需核对所有保护类型及无效元数据矩阵。 |
| A111 逐边界局部卡点 | `test_local_beat_planning_keeps_safe_unrelated_boundary`、`test_multiple_protected_neighbors_revert_only_conflicting_boundaries`、`test_low_confidence_and_crossfade_still_fall_back`、`test_invalid_duration_and_extreme_speed_are_rejected` | 有局部回退、非冲突边界仍可调整、低置信度/交叉溶解保守回退测试；需要保持总时长、边界序号审计等合同与正式计划一致。 |
| A112 字幕 cue 时间窗保护 | `test_actual_srt_windows_protect_shortest_caption_display_time`、`test_actual_srt_windows_allow_safe_shortening_when_cues_are_long_enough`、`test_invalid_srt_windows_fall_back`；`test_parses_single_and_multiple_real_cue_windows`、`test_accepts_dot_timestamp_fraction`、`test_rejects_out_of_range_and_mismatched_timeline`、`test_rejects_malformed_empty_and_missing_srt` | 有 cue 解析、0.65 秒最短显示保护、无效 SRT 回退测试线索；仍需确认版本/路径/时长匹配证据真实进入生产规划，不能宣称完成 ASR 或视觉可读性验收。 |

### A100–A112 关系与状态裁决

- A100 是变速后淡出时间窗，A101 是变速视频与原音轨同步，A103 是淡入/淡出音画合同，三者关联但验收对象不同；A104 是跨镜头拼接转场，不与单镜头淡入/淡出合并。
- A105 pacing 映射、A106 文本角色默认决策、A107 将时长传入运行时请求是连续但独立的执行层；A108 字幕时间轴生成与 A112 将真实 SRT cue 送入内容保护也必须分别核验。
- A109 音乐切点、A110 内容保护、A111 局部边界回退、A112 字幕 cue 保护形成链路，但每项有独立失败条件和测试合同。历史 CI 记录不能代替当前 SHA 证据；当前基线四项工作流为绿只证明当前提交的 CI/doc-sync 通过，不代表真实成片质量验收。
- A102 1080P 尺寸底线与真实清晰度增强严格区分。路线图中阶段 2 仍未退出，真实音乐、真实口播、真实素材、Windows 播放/剪映与商业效果继续暂缓。
- 本批 A100–A112 全部记为“部分证据映射”。台账 `code_test_evidence_reviewed_ids=113` 仅表示 A0–A112 已开始映射；`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false` 保持不变。不分配权重，不计算整体完成率。
- 下一步转入全量跨来源去重与状态裁决：把 A0–A112 正式验收计划与路线图、未来功能备忘、验收 SOP、任务登记表及执行控制文档逐项交叉核对；优先处理已发现的重复段落/转义换行/历史状态冲突，并只在有来源证据时修正文档。不得删 ID、补造编号或开发新产品功能。

---

## PLAN-003｜A0–A112 单一任务台账规范化登记（2026-10-15｜第一轮登记，非验收结论）

本表为 113 个正式编号建立一行一个的 canonical 登记槽位，避免后续继续只在历史叙述中找任务。**本表目前完成的是槽位与来源存在性登记，不是全量语义去重、状态裁决或代码验收。** “标题/提及/未发现”仅表示在对应文件中是否找到以该 ID 为标题或正文引用；“提及”不等于该来源定义了独立验收合同，“未发现”也不授权补造需求。所有 ID 保留，不能据此合并、删除或重编号。

### 当前轮基线与源文件指纹

- 当前 PR #32 HEAD：`4a0c076887542dc6606a80c584c86add022ffed0`；PR 保持 open/unmerged。
- 当前 SHA 的 CI run `38701848155` 与 `ad-studio-doc-sync` run `38701848167` 均 success；Netlify deploy-preview status success。该结果只证明该 SHA 的 CI/doc-sync 与部署预览状态，不等于 113 项正式验收通过。
- 本次读取的源文件 blob：验收计划 `38ee73c3002f6142baef28f7a4845792cb144d3b`；验收 SOP `7f4a845c0ad70a190b1881aa976eb016a644f8b6`；未来功能备忘 `644415e15457248e946c9b1b07850413bb122571`；路线图 `98449f545548d59e9c035a720f662b97aaa0740c`；UX/安全审计 `fccaa3e7b0f7281d2ed605f7cb802bfe5d895dc4`。
- 任务台账权威文件仍为本文件。其余文档提供需求、方法、战略或证据，不可自行覆盖任务状态/下一项。

### 状态字段解释

- **跨源关系裁决**：本轮统一为“未裁决”；下一轮须逐项确定独立合同、关联依赖、重复引用、历史快照和真实冲突。未经证据确认不得静默合并。
- **当前代码/测试证据 SHA**：本轮统一为“待绑定”；旧 SHA 的历史测试记录不得继承成当前 HEAD 证据。应记录测试文件/用例、对应实现链、当前 SHA 及该证据能证明/不能证明的范围。
- **开发状态、验收状态、依赖/父任务、适用七层、剩余条件、暂缓理由、最后核验日期**：需在逐项证据与依赖审计中补齐；不以“未裁决”推断为未开发，也不以代码/测试存在推断为通过。
- **用户自由度**：选择、控制、知情、撤回/纠正四维度按既有规则映射至相关 ID，不新增正式编号。
- **进度统计**：本表登记 113 个槽位；不改变 `code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false`；不分配权重，不计算总体完成率。

| 正式 ID | canonical 名称（以正式验收计划为首要来源；缺项时暂用已登记标题） | 验收计划 / SOP / 未来备忘 / 路线图 / UX审计 | 跨源关系裁决 | 当前代码/测试证据 SHA |
|---|---|---|---|---|
| A0 | A0 · 启动、界面与基础工程 | 标题 / 标题 / 提及 / 提及 / 标题 | 初步裁决：独立启动/基础 UI 合同；与 A1 工程稳定性相关但不合并。UX 维度：控制入口/可理解性。 | `6714f2e044959e036ee5715686a5cd851908bef2`（当前 HEAD CI/doc-sync 通过；仅绑定静态映射基线） |
| A1 | A1 · 工程稳定性 | 标题 / 标题 / 未发现 / 提及 / 未发现 | 初步裁决：独立工程质量合同；与所有功能共享 CI 依赖，但不能替代功能验收。 | `6714f2e044959e036ee5715686a5cd851908bef2`（当前 HEAD CI/doc-sync 通过；仅绑定静态映射基线） |
| A2 | A2 · 新建项目 | 标题 / 标题 / 未发现 / 提及 / 提及 | 初步裁决：独立项目生命周期合同；与 A28 持久化/隔离相关但范围不同，须分别保留。 | `6714f2e044959e036ee5715686a5cd851908bef2`（当前 HEAD CI/doc-sync 通过；仅绑定静态映射基线） |
| A3 | A3 · 任务选择 | 标题 / 标题 / 标题 / 提及 / 未发现 | 初步裁决：独立任务选择合同；与 A8 策略和 A15 生产流程相关但不合并。UX 维度：选择自由与选择结果可理解。 | `6714f2e044959e036ee5715686a5cd851908bef2`（当前 HEAD CI/doc-sync 通过；仅绑定静态映射基线） |
| A4 | A4 · 原始素材管理 | 标题 / 标题 / 未发现 / 提及 / 未发现 | 初步裁决：独立原始素材导入/管理合同；与 A5 分析消费素材的关系为前置依赖，不合并。 | `6714f2e044959e036ee5715686a5cd851908bef2`（当前 HEAD CI/doc-sync 通过；仅绑定静态映射基线） |
| A5 | A5 · 素材视觉分析 | 标题 / 标题 / 未发现 / 提及 / 未发现 | 初步裁决：独立视觉分析合同；依赖 A4 素材输入，但分析输出正确性不能由素材管理验收代替。 | `6714f2e044959e036ee5715686a5cd851908bef2`（当前 HEAD CI/doc-sync 通过；仅绑定静态映射基线） |
| A6 | A6 · 商品资料 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 初步裁决：独立商品资料来源/字段/持久化合同；与 A7 内容理解为输入事实与理解推理关系，不合并。UX 维度：知情/纠正自由及不编造事实。 | `6714f2e044959e036ee5715686a5cd851908bef2`（当前 HEAD CI/doc-sync 通过；仅绑定静态映射基线） |
| A7 | A7 · 内容理解 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 初步裁决：独立商品/素材语义理解合同；依赖 A6 的资料事实，但真实模型判断质量不能由提示词/路由测试代替。 | `6714f2e044959e036ee5715686a5cd851908bef2`（当前 HEAD CI/doc-sync 通过；仅绑定静态映射基线） |
| A8 | A8 · 剪辑策略 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 初步裁决：独立剪辑策略决策合同；与 A7 理解和 A15 成片执行形成链路但不合并。UX 维度：用户指定条件覆盖 AI 默认策略。 | `6714f2e044959e036ee5715686a5cd851908bef2`（当前 HEAD CI/doc-sync 通过；仅绑定静态映射基线） |
| A9 | A9 · 真人口播 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 初步裁决：独立真人口播处理合同；与 A10 音频处理、A11 字幕时间轴互相依赖但验收对象不同。 | `6714f2e044959e036ee5715686a5cd851908bef2`（当前 HEAD CI/doc-sync 通过；仅绑定静态映射基线） |
| A10 | A10 · 音频 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 初步裁决：独立音频处理/混音合同；与 A9 口播内容及 A11 字幕同步相关但不合并。 | `6714f2e044959e036ee5715686a5cd851908bef2`（当前 HEAD CI/doc-sync 通过；仅绑定静态映射基线） |
| A11 | A11 · 字幕 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 初步裁决：独立字幕内容/时间窗/字体合同；与 A9 口播、A10 音频及 A112 内容保护有依赖关系，不合并。 | `6714f2e044959e036ee5715686a5cd851908bef2`（当前 HEAD CI/doc-sync 通过；仅绑定静态映射基线） |
| A12 | A12 · 缺口判断 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 初步裁决：独立缺口识别/分流合同；与 A13 实际生成是决策→执行关系，不合并。UX 维度：应明确建议补拍、人工处理或 AI 辅助，不冒称已解决。 | `6714f2e044959e036ee5715686a5cd851908bef2`（当前 HEAD CI/doc-sync 通过；仅绑定静态映射基线） |
| A13 | A13 · AI生成 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 初步裁决：独立 AI 生成执行合同；承接 A12 路由但另有费用、Provider、审核和失败状态要求，不合并。UX 维度：明确授权、费用知情、拒绝/取消后无调用。 | `6714f2e044959e036ee5715686a5cd851908bef2`（当前 HEAD CI/doc-sync 通过；仅绑定静态映射基线） |
| A14 | A14 · 实拍+AI混合制作 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 初步裁决：独立实拍+AI 混合制作合同；与 A13 共享生成组件但增加来源追踪、审核状态和混合编排要求，不合并。 | `6714f2e044959e036ee5715686a5cd851908bef2`（当前 HEAD CI/doc-sync 通过；仅绑定静态映射基线） |
| A15 | A15 · 电商短视频生产 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 初步裁决：独立电商短视频成片业务合同；依赖 A4–A14 多个组件，但共享组件测试不能替代完整生产流程验收。 | `6714f2e044959e036ee5715686a5cd851908bef2`（当前 HEAD CI/doc-sync 通过；仅绑定静态映射基线） |
| A16 | A16 · 商品主图视频生产 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 独立合同：商品主图视频必须围绕商品主体清晰度、遮挡、展示顺序、细节镜头、参数/卖点一致性和商品展示画面逐项验收。 依赖 A6 商品事实、A7 理解及共用生产链；与 A15 短视频、A17 广告投放有共享组件但目标不同。 | 历史静态映射 SHA `53800b7845a9db49c329242506d80f6a1747281c`；当前 HEAD `97fa622530fa806f7984ff580621888dd78e61e9` 的 CI/doc-sync/预览通过，但本项证据尚未逐项重绑 |
| A17 | A17 · 广告投放视频生产 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 独立合同：广告素材的多创意版本、Hook、卖点组合、证明方式、CTA、创意差异与投放前创意分析。 与 A18 多版本、A19 创意实验相关但不合并；明确不包括真实广告投放结果。 | 历史静态映射 SHA `53800b7845a9db49c329242506d80f6a1747281c`；当前 HEAD `97fa622530fa806f7984ff580621888dd78e61e9` 的 CI/doc-sync/预览通过，但本项证据尚未逐项重绑 |
| A18 | A18 · 多版本 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 独立合同：多创意版本的状态、镜头缓存、物理输出路径和版本隔离。 与 A17 的广告创意目标、A19 的差异分析、A26 的历史记录相关但不合并。 | 历史静态映射 SHA `53800b7845a9db49c329242506d80f6a1747281c`；当前 HEAD `97fa622530fa806f7984ff580621888dd78e61e9` 的 CI/doc-sync/预览通过，但本项证据尚未逐项重绑 |
| A19 | A19 · 创意实验设计 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 独立合同：判断创意差异是机制差异还是表面差异，并输出可审查的实验设计信息。 与 A17 创意生产、A18 版本管理相关但不合并；真实投放效果不属于本项离线验收。 | 历史静态映射 SHA `53800b7845a9db49c329242506d80f6a1747281c`；当前 HEAD `97fa622530fa806f7984ff580621888dd78e61e9` 的 CI/doc-sync/预览通过，但本项证据尚未逐项重绑 |
| A20 | A20 · 创意事实检查 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 独立合同：卖点依据、禁用词、绝对化表达、资料缺失提示和不编造商品事实。 与 A21 分镜事实、A22 视觉事实及 A24 最终安全闸门互相协作但不合并。 | 历史静态映射 SHA `53800b7845a9db49c329242506d80f6a1747281c`；当前 HEAD `97fa622530fa806f7984ff580621888dd78e61e9` 的 CI/doc-sync/预览通过，但本项证据尚未逐项重绑 |
| A21 | A21 · 分镜事实检查 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 独立合同：分镜的商品功能/外观/卖点必须能追溯到事实依据。 与 A20 创意文本、A22 实际画面和 A112 字幕时间窗内容保护相关但不合并。 | 历史静态映射 SHA `53800b7845a9db49c329242506d80f6a1747281c`；当前 HEAD `97fa622530fa806f7984ff580621888dd78e61e9` 的 CI/doc-sync/预览通过，但本项证据尚未逐项重绑 |
| A22 | A22 · 视觉事实检查 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 独立合同：核验实际视觉素材中的商品与画面风险，而不是只检查文本。 与 A20/A21 文本事实和 A24 汇总阻断相关但不合并。 | 历史静态映射 SHA `53800b7845a9db49c329242506d80f6a1747281c`；当前 HEAD `97fa622530fa806f7984ff580621888dd78e61e9` 的 CI/doc-sync/预览通过，但本项证据尚未逐项重绑 |
| A23 | A23 · 风险控制 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 独立合同：风险动作、权限等级、人工批准、dry-run、审计日志及禁止未授权真实写操作。 与 A24 最终安全闸门及 A13/A14 的审核闭环相关但不合并。 | 历史静态映射 SHA `53800b7845a9db49c329242506d80f6a1747281c`；当前 HEAD `97fa622530fa806f7984ff580621888dd78e61e9` 的 CI/doc-sync/预览通过，但本项证据尚未逐项重绑 |
| A24 | A24 · 最终安全闸门 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 独立合同：汇总显式风险类别并阻止不安全的最终文件写出。 与 A20/A21/A22 风险来源和 A23 风险控制相关，但汇总闸门不替代上游风险识别。 | 历史静态映射 SHA `53800b7845a9db49c329242506d80f6a1747281c`；当前 HEAD `97fa622530fa806f7984ff580621888dd78e61e9` 的 CI/doc-sync/预览通过，但本项证据尚未逐项重绑 |
| A25 | A25 · 媒体质量检查 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 独立合同：媒体文件、视频流、时长、尺寸、画幅、1080P 级最低导出和失败时不可交付；区分放大与 AI 细节增强。 与 A27 交付状态及 A100–A112 剪辑质量相关但不合并。 | 历史静态映射 SHA `53800b7845a9db49c329242506d80f6a1747281c`；当前 HEAD `97fa622530fa806f7984ff580621888dd78e61e9` 的 CI/doc-sync/预览通过，但本项证据尚未逐项重绑 |
| A26 | A26 · 成片版本历史 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 独立合同：保存可区分的成片版本修订历史及对应输出信息。 与 A18 创意版本、A27 交付中心和 A28 持久化相关但不合并。 | 历史静态映射 SHA `53800b7845a9db49c329242506d80f6a1747281c`；当前 HEAD `97fa622530fa806f7984ff580621888dd78e61e9` 的 CI/doc-sync/预览通过，但本项证据尚未逐项重绑 |
| A27 | A27 · 成片交付中心 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 独立合同：向用户展示历史成片、当前交付状态、阻塞原因、修复环节与重新检查结果。 与 A25 媒体质检、A26 历史及 A30 恢复相关但不合并。 | 历史静态映射 SHA `53800b7845a9db49c329242506d80f6a1747281c`；当前 HEAD `97fa622530fa806f7984ff580621888dd78e61e9` 的 CI/doc-sync/预览通过，但本项证据尚未逐项重绑 |
| A28 | A28 · 本地项目数据 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 独立合同：项目、版本、素材状态、审核状态和输出历史的本地持久化及项目隔离。 与 A2 项目生命周期相关但不合并；A2 偏操作生命周期，本项偏持久化数据范围。 | 历史静态映射 SHA `53800b7845a9db49c329242506d80f6a1747281c`；当前 HEAD `97fa622530fa806f7984ff580621888dd78e61e9` 的 CI/doc-sync/预览通过，但本项证据尚未逐项重绑 |
| A29 | A29 · 数据边界 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 独立合同：模拟/真实数据、AI 推演/真实事实、用户输入/系统推断明确分离；不得伪造外部平台结果。 与 A6 商品资料来源、A19 指标分析及 A33 离线流程相关但不合并。 | 历史静态映射 SHA `53800b7845a9db49c329242506d80f6a1747281c`；当前 HEAD `97fa622530fa806f7984ff580621888dd78e61e9` 的 CI/doc-sync/预览通过，但本项证据尚未逐项重绑 |
| A30 | A30 · 失败恢复 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 独立合同：针对素材损坏/路径失效、AI 调用或生成失败、预算不足、输出失败/损坏、重开和中途退出进行恢复。 与 A43–A49 等具体恢复回归相关但不合并；本项是跨阶段故障矩阵合同。 | 历史静态映射 SHA `53800b7845a9db49c329242506d80f6a1747281c`；当前 HEAD `97fa622530fa806f7984ff580621888dd78e61e9` 的 CI/doc-sync/预览通过，但本项证据尚未逐项重绑 |
| A31 | A31 · 帮助文档 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 独立合同：帮助文档、PROJECT_LOGIC 与关键文档随功能/流程变化保持同步。 与 A32 AI 接手能力相关但不合并；文档更新和新 AI 能否恢复上下文是不同目标。 | 历史静态映射 SHA `53800b7845a9db49c329242506d80f6a1747281c`；当前 HEAD `97fa622530fa806f7984ff580621888dd78e61e9` 的 CI/doc-sync/预览通过，但本项证据尚未逐项重绑 |
| A32 | A32 · AI接手能力 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 独立合同：无聊天历史的新 AI 能从长期项目文件找到目标、架构、进度、验收、测试、安全边界与下一步。 与 A31 文档同步相关但不合并；文档存在不保证内容始终正确。 | 历史静态映射 SHA `53800b7845a9db49c329242506d80f6a1747281c`；当前 HEAD `97fa622530fa806f7984ff580621888dd78e61e9` 的 CI/doc-sync/预览通过，但本项证据尚未逐项重绑 |
| A33 | A33 · 完整用户流程 | 标题 / 标题 / 提及 / 未发现 / 未发现 | 独立合同：三类业务流程的正常、异常、安全拦截、修复、复查和最终交付闭环。 与 A15/A16/A17 的业务产物目标相关但不合并；本项验证离线流程闭环，不替代真实 Provider、Windows 或商业质量。 | 历史静态映射 SHA `53800b7845a9db49c329242506d80f6a1747281c`；当前 HEAD `97fa622530fa806f7984ff580621888dd78e61e9` 的 CI/doc-sync/预览通过，但本项证据尚未逐项重绑 |
| A34 | A34 · AI辅助商品画面对比（第一阶段） | AI参考图对照生成画面；匹配也不得自动批准。 与 A22/A66/A67 相关但不合并。 | 初步裁决；证据基线 `3ca7ff00ea35742b461d72ec4317419ec0d0d39d`，静态映射，非本轮重跑 | test_short_drama.py：FakeRouter mismatch/no-auto-approve/invalid-input。 部分映射；真实视觉准确率、真实素材和人工复核体验未证明。 |
| A35 | A35 · 问题镜头定位与仅重生成（第一阶段实现，待验收） | 只准备并作用于所选镜头的重生成，保留旧版和核验历史。 依赖 A34；与 A36/A43 相关但不合并。 | 初步裁决；证据基线 `3ca7ff00ea35742b461d72ec4317419ec0d0d39d`，静态映射，非本轮重跑 | 测试覆盖目标镜头、其他镜头不变、历史保留及非法模式/空修正。 准备状态不等于真实生成；取消零调用、项目隔离和失败矩阵待核。 |
| A36 | A36｜AI视觉核验结果辅助单镜头修复（代码已提交，待 CI） | 将视觉核验结果变成用户可编辑的修正草稿，并校验费用和版本。 与 A35 前后依赖，不合并。 | 初步裁决；证据基线 `3ca7ff00ea35742b461d72ec4317419ec0d0d39d`，静态映射，非本轮重跑 | 测试覆盖摘要/问题列表草稿及无效镜头/模式、非有限费用、版本防护。 UI编辑/取消、费用确认前零 Provider 调用和保存状态待核。 |
| A37 | A37｜视觉修正草稿换行显示 | 视觉修正草稿必须显示真实换行。 与 A50/A56 提示词换行相关但对象不同。 | 初步裁决；证据基线 `3ca7ff00ea35742b461d72ec4317419ec0d0d39d`，静态映射，非本轮重跑 | 草稿字符串测试与 handoff 文案断言。 未找到直接 GUI 布局断言；真实窗口可读性未证明。 |
| A38 | A38｜跨会话接手信息完整性 | 跨会话新 AI 能恢复项目上下文与当前状态。 与 A31/A32 相关但不合并。 | 初步裁决；证据基线 `3ca7ff00ea35742b461d72ec4317419ec0d0d39d`，静态映射，非本轮重跑 | test_ai_handoff.py 检查章节/关键字符串。 SESSION_HANDOFF 历史段仍含旧 HEAD、PR #31 和旧下一项，可能误导。 |
| A39 | A39｜功能分支 CI 覆盖 | 功能分支 push/PR 应触发完整 CI。 与 A42 SHA 绑定相关但不合并。 | 初步裁决；证据基线 `3ca7ff00ea35742b461d72ec4317419ec0d0d39d`，静态映射，非本轮重跑 | 当前 PR CI/doc-sync success。 本轮未独立核实 Push-triggered 两项；workflow触发范围需再核。 |
| A40 | A40｜接手测试路径修复 | 接手测试使用稳定仓库根路径读取文档。 与 A38/A41 相关但不合并。 | 初步裁决；证据基线 `3ca7ff00ea35742b461d72ec4317419ec0d0d39d`，静态映射，非本轮重跑 | test_ai_handoff.py 用 Path(__file__).resolve().parents[2] 构建 ROOT 路径。 本轮未本地重跑；需确认当前 CI 已收集执行该测试。 |
| A41 | A41｜接手文案断言修复 | 接手关键文案有回归断言，不得删除测试换绿。 与 A40/A38 相关但不合并。 | 初步裁决；证据基线 `3ca7ff00ea35742b461d72ec4317419ec0d0d39d`，静态映射，非本轮重跑 | 测试直接断言多个关键文案和固定字符串。 CI成功；字符串存在不保证语义/当前状态正确。 |
| A42 | A42｜已确认基准 CI | CI 结果必须绑定具体 HEAD SHA。 与 A39 触发机制相关但不合并。 | 初步裁决；证据基线 `3ca7ff00ea35742b461d72ec4317419ec0d0d39d`，静态映射，非本轮重跑 | 当前 SHA 3ca7... PR CI/doc-sync/预览已实查成功。 测试/历史 handoff 仍保留 443f713... 旧基准；需避免误用历史绿灯。 |
| A43 | A43｜单镜头重新生成失败恢复 | 单镜头重生成失败/中断时恢复上一有效视频与状态。 与 A46/A47/A53/A54 相关但不合并。 | 初步裁决；证据基线 `3ca7ff00ea35742b461d72ec4317419ec0d0d39d`，静态映射，非本轮重跑 | test_desktop.py 有 Provider 失败与中断恢复测试。 缺失/空文件、临时输出清理、状态组合边界待核。 |
| A44 | A44｜短剧镜头映射稳定性 | 短剧项目镜头稳定映射到分镜；歧义时失败关闭。 与 A35 修复流程相关但映射是独立前置。 | 初步裁决；证据基线 `3ca7ff00ea35742b461d72ec4317419ec0d0d39d`，静态映射，非本轮重跑 | test_short_drama.py 覆盖稳定索引、旧数据唯一匹配、歧义拒绝。 需追踪所有生成/修正/审核调用点是否使用统一映射。 |
| A45 | A45｜失败恢复状态 UI 对齐 | 恢复后 UI 状态准确呈现旧视频已恢复。 与 A43 数据恢复相关但聚焦 UI 状态。 | 初步裁决；证据基线 `3ca7ff00ea35742b461d72ec4317419ec0d0d39d`，静态映射，非本轮重跑 | test_a45_ui_failure_state_keeps_recovered_previous_video_status。 恢复标记、文件存在/非空与重载状态组合及 Windows UI 未证明。 |
| A46 | A46｜编辑镜头时保护旧版本视频 | 编辑镜头通过安全重生成状态转换，不能提前清空旧视频/递增版本。 与 A43 共用恢复机制但入口合同不同。 | 初步裁决；证据基线 `3ca7ff00ea35742b461d72ec4317419ec0d0d39d`，静态映射，非本轮重跑 | test_a46 检查 mark_regenerate 调用及禁止破坏性赋值。 取消编辑、多次重试及实际失败边界待核。 |
| A47 | A47｜素材解析阶段失败恢复 | 素材解析失败时不调用视频 Provider，并保留旧视频/状态。 与 A43 相关但失败阶段不同。 | 初步裁决；证据基线 `3ca7ff00ea35742b461d72ec4317419ec0d0d39d`，静态映射，非本轮重跑 | 故障注入测试断言 Provider 未调用、旧文件保留、临时文件清理与重载。 真实 Windows 文件系统异常仍未验。 |
| A48 | A48｜实拍裁剪失败不破坏旧成片 | 实拍裁剪失败不破坏正式输出。 与 A49 多段清理、A43 AI生成恢复相关但不合并。 | 初步裁决；证据基线 `3ca7ff00ea35742b461d72ec4317419ec0d0d39d`，静态映射，非本轮重跑 | 故障注入测试检查旧输出内容、状态、临时文件与重载。 真实 FFmpeg/原子替换/真实素材未验。 |
| A49 | A49｜多段实拍中断文件清理 | 多段实拍源缺失/中断时清理残留分段并保留旧成片。 与 A48 单段裁剪及 A30 通用恢复相关但不合并。 | 初步裁决；证据基线 `3ca7ff00ea35742b461d72ec4317419ec0d0d39d`，静态映射，非本轮重跑 | test_a49 覆盖源缺失、残留分段清理和旧视频保护。 强制进程中断/重开、多种命名与引用文件保护矩阵待核。 |
| A50 | A50｜视频生成提示词换行回归 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A51 | A51｜费用预估弹窗前置校验 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A52 | A52｜视频 Provider 失败尝试与成本去重 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A53 | A53｜恢复流程拒绝零字节旧视频 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A54 | A54｜恢复时识别零字节活动视频 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A55 | A55｜成本记账异常不丢失成功视频 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A56 | A56｜提示词换行回归修复 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A57 | A57｜成本待核对状态界面对齐 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A58 | A58｜商品画面对比输入证据校验 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A59 | A59｜项目成本汇总单一事实源 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A60 | A60｜失败-only 账本兼容 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A61 | A61｜旧项目成本迁移与镜头成本对账 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A62 | A62｜历史成本迁移文案断言修复 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A63 | A63｜迁移基线在后续记账失败时保留 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A64 | A64｜素材成本账本失败保护 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A65 | A65｜用量账本原子写入与完整历史保留 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A66 | A66｜人工商品画面核验证据文件校验 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A67 | A67｜短剧人工核验证据失效保护 | 标题 / 标题 / 未发现 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A68 | A68｜AI 短剧后续剧情影响分析 | 标题 / 标题 / 标题 / 提及 / 未发现 | 未裁决 | 待绑定 |
| A69 | A69｜AI 编导故事引擎与留存设计 | 标题 / 标题 / 提及 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A70 | A70｜短剧故事结构检查 | 标题 / 标题 / 提及 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A71 | A71｜备选故事方向差异化 | 标题 / 标题 / 提及 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A72 | A72｜人物动机与关系动力 | 标题 / 标题 / 提及 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A73 | A73｜剧情事件因果链 | 标题 / 标题 / 提及 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A74 | A74｜因果链与剧本/分镜证据对齐 | 标题 / 标题 / 标题 / 提及 / 未发现 | 未裁决 | 待绑定 |
| A75 | A75：商品事实锁与剧情内容交叉审查 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A76 | A76: Selling-point storyboard coverage | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A77 | A77 · 短剧关键剧情事件与分镜落地（开发中） | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A78 | A78 · 人物动机与信息掌握一致性（开发中） | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A79 | A79｜人物行动依据与镜头角色绑定 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A80 | A80｜人物关系变化与剧情后果 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A81 | A81｜人物状态与剧情连续性审查（本轮新增） | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A82 | A82｜人物信息掌握与时间线一致性审查 | 标题 / 标题 / 提及 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A83 | A83｜人物承诺、误解与行动结果一致性审查（自动化阶段待最新 CI） | 标题 / 标题 / 提及 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A84 | A84｜跨集剧情承接事项一致性 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A85 | A85｜人物长期状态与关系跨集一致性 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A86 | A86｜人物状态变化因果闭环验收 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A87 | A87｜人物状态到可观察表演验收 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A88 | A88 多人物状态依赖 | 提及 / 提及 / 提及 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A89 | A89｜跨集演员/场景资产锁定验收 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A90 | A90：跨集物理素材 ID 绑定（待最新 SHA 自动化验收） | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A91 | A91｜跨集锁定素材失效检测验收项 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A92 | A92｜跨集物理素材绑定落地验收 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A93 | A93｜失效跨集锁定在 Provider 调用前拦截并隔离镜头 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A94 | A94｜恢复原锁定资产后的安全重试 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A95 | A95｜本地素材索引损坏时阻断生产 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A96 | A96｜修复素材索引后的安全重试 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A97 | A97｜项目恢复仅重置损坏镜头（自动化回归） | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A98 | A98｜重复恢复仍列出待处理的缺失镜头 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A99 | A99 成功账本清除兄弟镜头陈旧成本 | 未发现 / 未发现 / 未发现 / 提及 / 未发现 | 未裁决 | 待绑定 |
| A100 | A100｜商业剪辑淡出时间窗 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A101 | A101｜变速时音画同步 | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A102 | A102 · 最终导出最低 1080P 级分辨率（待 CI 验收） | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A103 | A103 · 镜头淡入/淡出音画同步（待 CI 验收） | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A104 | A104 · 相邻镜头真实交叉溶解（待 CI 验收） | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A105 | A105 · 分镜节奏标签必须影响实际播放速度（待 CI 验收） | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A106 | A106｜商业镜头角色驱动的默认剪辑决策（待当前 SHA 自动化验收） | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A107 | A107｜商业角色推断时长进入真实生成请求（自动化验收） | 标题 / 标题 / 标题 / 未发现 / 未发现 | 未裁决 | 待绑定 |
| A108 | A108｜字幕信息密度与时间轴自适应（当前 SHA 自动化验收中） | 标题 / 标题 / 标题 / 提及 / 未发现 | 未裁决 | 待绑定 |
| A109 | A109｜音乐节拍与画面切点真实联动 | 标题 / 标题 / 标题 / 标题 / 未发现 | 未裁决 | 待绑定 |
| A110 | A110｜商业剪辑内容保护（音乐卡点不可损害商品信息） | 标题 / 标题 / 标题 / 标题 / 未发现 | 未裁决 | 待绑定 |
| A111 | A111｜逐边界局部音乐卡点规划 | 标题 / 标题 / 标题 / 标题 / 未发现 | 未裁决 | 待绑定 |
| A112 | A112｜字幕实际时间窗参与内容保护 | 标题 / 标题 / 标题 / 标题 / 标题 | 未裁决 | 待绑定 |

### PLAN-003 第一批语义关系裁决｜A0–A15｜2026-10-15｜初步裁决，非正式验收

本批复核范围是“验收合同身份与跨来源关系”，不是重跑代码测试。正式验收计划与 SOP 均对 A0–A15 有独立标题；路线图主要提供阶段/目标层级，未来备忘只覆盖其中少数项目，UX/安全审计是横向风险来源而非 A0–A15 的替代清单。因此“来源未发现/只提及”不代表任务不存在，也不构成删除依据。

| ID | 合同边界初步裁决 | 主要依赖/相关任务（不合并） | 用户自由度/七层结果证明映射 | 当前证据判断 |
|---|---|---|---|---|
| A0 | 启动、界面与基础工程 | 与 A1 相关 | 可发现性/可理解性；第 1、4 层 | 历史静态映射记录 App.create() 入口；缺专门启动/创建操作端到端证据 |
| A1 | 工程稳定性 | 为全项目提供共同工程门槛 | 第 1 层 | 当前 SHA 的 CI 通过是工程检查证据，不等于各功能合同已验收 |
| A2 | 新建项目、保存/重开与项目隔离 | 与 A28 持久化/隔离相关 | 数据边界和纠正/恢复；第 1、2、3 层 | 历史映射含项目保存/加载与项目间隔离测试；App.create() 编排及异常恢复仍需补证 |
| A3 | 任务选择与设置区 | 与 A8 策略、A15 生产相关 | 选择自由；第 2、4 层 | 历史映射含三类任务策略、持久化与布局回归；不等于三类任务完整 UI 流程通过 |
| A4 | 原始素材管理 | A5 的输入前置 | 用户可理解素材可用/不可用状态；第 2、3 层 | 历史映射含扫描、不可解析文件、重复评分、废片归档及源文件保护测试；路径异常矩阵待核 |
| A5 | 素材视觉分析 | 依赖 A4，不与 A4 合并 | 第 2、3、6 层 | 已记录关键帧/视觉清单函数；对关键帧提取和清单构建的直接专项测试覆盖不足 |
| A6 | 商品资料解析、关联、持久化及事实边界 | 为 A7、A13、A14 提供事实输入 | 知情与纠正自由；第 2、3、5 层 | 历史映射有解析/持久化/不编造事实离线测试；真实平台链接和异常数据仍未证明 |
| A7 | 商品/素材内容理解和卖点推理 | 依赖 A6 的事实输入 | 用户可纠正输入；第 2、3、5 层 | 有提示词事实边界和理解流水线测试；真实语义质量/卖点排序未验证 |
| A8 | 剪辑策略生成及用户条件覆盖 | 与 A7、A15 形成决策链 | 用户指定条件覆盖 AI 默认值；第 2、3、4、6 层 | 有任务策略与素材约束测试；用户覆盖、人工确认与策略质量仍需逐项证明 |
| A9 | 真人口播识别、切分与内容保留 | 与 A10/A11 协同，不合并 | 内容可纠正；第 2、3、6 层 | 有口播清理/时间戳线索和转写入口；转写失败、错位、核心卖点误删矩阵未证明完整 |
| A10 | 音频降噪、响度与 BGM 混音 | 与 A9/A11 协同，不合并 | 用户音乐/配音选择；第 2、3、6 层 | 有混音主路径测试；损坏输入、缺失 BGM、音质及完整异常矩阵待核 |
| A11 | 字幕内容、时间窗、字体来源 | 与 A9/A10 及 A112 相关，不合并 | 字体授权知情；第 2、3、5、6 层 | 有字幕时间窗/密度离线测试；逐字一致、事实一致、免费商用字体证据及真实可读性未充分证明 |
| A12 | 缺口识别与补拍/人工/AI 分流 | 是 A13 的前置决策，不是生成本身 | 知情自由；不得把建议描述为已解决；第 2、3、4、5 层 | 有路由和预算保护测试线索；误报/漏报与 UI 状态仍待核 |
| A13 | AI 生成执行、预算闸门、失败与审核状态 | 承接 A12；与 A14 共用组件但合同不同 | 选择、控制、知情、撤回/纠正；第 2、3、4、5、6 层 | 有配置路由、预算/失败/待复核测试线索；真实 Provider、实际扣费和媒体质量仍按要求暂缓 |
| A14 | 实拍与 AI 混合编排、来源追踪及审核 | 依赖 A4/A13；与 A13 不合并 | 审核/撤回/纠正；第 2、3、5、6 层 | 有来源状态持久化和待复核阻止交付测试；实拍来源完整性与真实混合成片未验 |
| A15 | 电商短视频的完整业务成片合同 | 汇聚 A4–A14 多项能力 | 端到端可用性和商业成片质量；第 2、3、4、5、6 层 | 已有多个生产组件的自动化证据，但未证明所有 A15 条目在同一完整流程中全部通过 |

#### A0–A15 本批裁决边界

- **没有发现应当合并或删除的正式 ID。** 本批结论为“合同独立，存在依赖/协作关系”；这只是初步语义裁决，后续如原始需求/代码证据冲突，应补记冲突并保留两项合同。
- A2 与 A28、A4 与 A5、A6 与 A7、A7/A8/A15、A9/A10/A11、A12 与 A13、A13 与 A14 均是相关链路但验收对象不同，不合并。
- 用户自由度已按现有审计要求映射到相关合同；此处仅确定审查维度，不代表选择/授权/取消/费用/密钥安全整体通过。
- 当前 HEAD `6714f2e044959e036ee5715686a5cd851908bef2` 的 CI、doc-sync 和部署预览状态均通过。该证据绑定的是当前文档/代码提交的自动化基线；以上每项仍是“证据部分映射”，不能因此升级为正式验收通过。
- 当前台账计数维持 `code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false`。本批完成的是 A0–A15 的初步关系裁决，不代表代码/测试证据审计完成。



---

## PLAN-003 第二批语义关系裁决｜A16–A33｜2026-10-15｜初步裁决，非正式验收

### 本批范围与证据基线

本批将 A16–A33 的合同边界、依赖关系、用户自由度和七层证明层级写入权威台账。正式验收计划与 SOP 均为本批主要来源；路线图和未来功能备忘提供较高层级方向，不能取代逐项合同。历史代码/测试映射来自 SHA `53800b7845a9db49c329242506d80f6a1747281c`，只作为历史线索；本批开始前实时 HEAD `97fa622530fa806f7984ff580621888dd78e61e9` 的 CI、doc-sync 与部署预览均已通过。**本轮没有重新运行所有任务专项测试，也没有将旧 SHA 的测试证据冒充为当前 SHA 的逐项证明。**

### A16–A33 合同关系裁决

| ID | 正式合同边界 | 依赖/相关任务（保留独立编号） | 用户自由度与七层映射 | 证据结论与剩余条件 |
|---|---|---|---|---|
| A16 | 独立合同：商品主图视频必须围绕商品主体清晰度、遮挡、展示顺序、细节镜头、参数/卖点一致性和商品展示画面逐项验收。 | 依赖 A6 商品事实、A7 理解及共用生产链；与 A15 短视频、A17 广告投放有共享组件但目标不同。 | 用户知情/纠正；第 2、3、4、5、6 层 | 历史映射仅见商品事实边界与共享渲染测试；没有本轮直接核对到的 A16 专项视觉验收。真实商品外观与商业画质仍待真实素材验证。 |
| A17 | 独立合同：广告素材的多创意版本、Hook、卖点组合、证明方式、CTA、创意差异与投放前创意分析。 | 与 A18 多版本、A19 创意实验相关但不合并；明确不包括真实广告投放结果。 | 选择/知情；第 2、3、4、5、6 层；真实投放属第 7 层且暂缓 | 历史映射有版本隔离、创意差异及不虚构平台指标测试；仍需确认最终产物中 Hook/证明/CTA 的可辨识性。 |
| A18 | 独立合同：多创意版本的状态、镜头缓存、物理输出路径和版本隔离。 | 与 A17 的广告创意目标、A19 的差异分析、A26 的历史记录相关但不合并。 | 选择/纠正；第 2、3、4 层 | 历史映射有状态隔离、切换及物理目录隔离测试；版本缺镜头、失败恢复和输出清单关系待核。 |
| A19 | 独立合同：判断创意差异是机制差异还是表面差异，并输出可审查的实验设计信息。 | 与 A17 创意生产、A18 版本管理相关但不合并；真实投放效果不属于本项离线验收。 | 知情/纠正；第 2、3、5 层；商业效果属第 7 层且暂缓 | 历史映射有创意机制差异分类与不虚构平台指标测试；结果字段、各分类边界及下一轮建议仍待逐项核验。 |
| A20 | 独立合同：卖点依据、禁用词、绝对化表达、资料缺失提示和不编造商品事实。 | 与 A21 分镜事实、A22 视觉事实及 A24 最终安全闸门互相协作但不合并。 | 知情/纠正；第 2、3、5 层 | 有最终闸门和商品事实边界相关测试；每项输入/输出断言尚未全部映射，不能以闸门覆盖推定全项通过。 |
| A21 | 独立合同：分镜的商品功能/外观/卖点必须能追溯到事实依据。 | 与 A20 创意文本、A22 实际画面和 A112 字幕时间窗内容保护相关但不合并。 | 知情/纠正；第 2、3、5 层 | 有商品事实边界提示词测试；逐镜头来源、字幕一致性和文本检查/视觉检查的边界仍待核。 |
| A22 | 独立合同：核验实际视觉素材中的商品与画面风险，而不是只检查文本。 | 与 A20/A21 文本事实和 A24 汇总阻断相关但不合并。 | 知情/纠正；第 2、3、5、6 层 | 历史映射有安全闸门、视觉复核状态与人工核验能力；遮挡、模糊、抖动、素材映射及未分析状态需逐项核验。 |
| A23 | 独立合同：风险动作、权限等级、人工批准、dry-run、审计日志及禁止未授权真实写操作。 | 与 A24 最终安全闸门及 A13/A14 的审核闭环相关但不合并。 | 控制/撤回；第 1、2、3、5 层 | 历史映射有风险阻断和待复核素材不进入最终渲染的测试；权限与 dry-run/audit log 全合同仍需逐条对照。 |
| A24 | 独立合同：汇总显式风险类别并阻止不安全的最终文件写出。 | 与 A20/A21/A22 风险来源和 A23 风险控制相关，但汇总闸门不替代上游风险识别。 | 控制/知情；第 2、3、5 层 | 历史映射有显式风险分类和禁止写出测试；各来源覆盖、组合风险、可追踪原因及当前 HEAD 专项证据需复核。 |
| A25 | 独立合同：媒体文件、视频流、时长、尺寸、画幅、1080P 级最低导出和失败时不可交付；区分放大与 AI 细节增强。 | 与 A27 交付状态及 A100–A112 剪辑质量相关但不合并。 | 知情；第 2、3、5、6 层 | 历史映射有无效媒体、时长/尺寸、清单阻断及 1080P 尺寸测试；尺寸放大不能证明细节增强或商业画质。 |
| A26 | 独立合同：保存可区分的成片版本修订历史及对应输出信息。 | 与 A18 创意版本、A27 交付中心和 A28 持久化相关但不合并。 | 选择/纠正；第 2、3、4 层 | 历史映射有版本/画幅/修订独立测试；输出路径、时长、镜头数、交付状态、创建时间等字段完整性待核。 |
| A27 | 独立合同：向用户展示历史成片、当前交付状态、阻塞原因、修复环节与重新检查结果。 | 与 A25 媒体质检、A26 历史及 A30 恢复相关但不合并。 | 知情/控制/纠正；第 2、3、4 层 | 历史映射有阻塞报告、修复路由和不重新生成的复查测试；UI 真实可用性不能由数据层测试代替。 |
| A28 | 独立合同：项目、版本、素材状态、审核状态和输出历史的本地持久化及项目隔离。 | 与 A2 项目生命周期相关但不合并；A2 偏操作生命周期，本项偏持久化数据范围。 | 控制/纠正与数据边界；第 1、2、3 层 | 历史映射有状态恢复与项目隔离测试；损坏数据、升级兼容、自定义存储路径及跨版本边界待核。 |
| A29 | 独立合同：模拟/真实数据、AI 推演/真实事实、用户输入/系统推断明确分离；不得伪造外部平台结果。 | 与 A6 商品资料来源、A19 指标分析及 A33 离线流程相关但不合并。 | 知情/纠正；第 2、3、5 层 | 历史映射有来源 provenance 和 unverified 状态测试；所有入口是否一致遵循数据边界仍需核验，真实平台数据暂缓。 |
| A30 | 独立合同：针对素材损坏/路径失效、AI 调用或生成失败、预算不足、输出失败/损坏、重开和中途退出进行恢复。 | 与 A43–A49 等具体恢复回归相关但不合并；本项是跨阶段故障矩阵合同。 | 控制/撤回/纠正；第 1、2、3、4 层 | 历史映射有中断恢复、损坏输出、预算与不可重试失败测试；正式清单的故障注入项尚未逐项映射完整。 |
| A31 | 独立合同：帮助文档、PROJECT_LOGIC 与关键文档随功能/流程变化保持同步。 | 与 A32 AI 接手能力相关但不合并；文档更新和新 AI 能否恢复上下文是不同目标。 | 知情；第 1、4 层 | 历史映射有文档结构/内容约束测试；每次变更后的当前 SHA 内容一致性需持续核验。 |
| A32 | 独立合同：无聊天历史的新 AI 能从长期项目文件找到目标、架构、进度、验收、测试、安全边界与下一步。 | 与 A31 文档同步相关但不合并；文档存在不保证内容始终正确。 | 知情/控制；第 1、4 层 | 正式历史记录标为通过，且有 test_ai_handoff.py；本轮仍需把接手入口与实时 HEAD、唯一下一步保持同步，历史记录不自动替代当前核验。 |
| A33 | 独立合同：三类业务流程的正常、异常、安全拦截、修复、复查和最终交付闭环。 | 与 A15/A16/A17 的业务产物目标相关但不合并；本项验证离线流程闭环，不替代真实 Provider、Windows 或商业质量。 | 用户控制/知情/纠正；第 2、3、4、5 层 | 历史正式记录为离线自动化通过；test_a33_full_flow.py 对媒体操作使用 mock/夹具，不证明真实媒体、真实模型、Windows 实机或商业成片验收。 |

### 本批关系裁决结论

1. **未发现有证据支持删除或合并 A16–A33 中任何正式 ID。** 它们存在共享组件和依赖关系，但验收对象不同。
2. A16 与 A15/A17：同为视频生产，但商品主图的商品主体展示、广告投放素材的创意结构及通用电商短视频流程是不同合同。
3. A17/A18/A19：广告创意产物、多版本状态隔离、创意差异分析分别验收；不能用“版本存在”证明“创意有差异”，也不能用创意分析替代真实投放结果。
4. A20/A21/A22/A23/A24：分别对应创意文本事实、分镜事实、实际视觉核验、风险动作控制和最终安全闸门。下游闸门通过不证明上游所有事实/视觉风险都被识别。
5. A25/A26/A27/A28/A29/A30：分别对应媒体有效性、版本历史、交付体验、本地持久化、数据真实性边界、故障恢复。存在交叉数据字段，但不可互相代替。
6. A31/A32/A33：分别对应文档同步、新 AI 可接手、三类业务流程闭环。历史 A32/A33 通过记录保留为历史验收事实；其测试使用方式和当前文件同步状态仍需按当前 SHA 重新核验，不能推导出 Windows 真机/真实 Provider/商业成片通过。
7. 本批用户自由度映射只定义审查维度，不表示所有相关功能已通过。尤其涉及 Provider 切换、云端上传、费用、取消和密钥存储时，仍须核对真实调用链与负向测试。
8. 七层证明标准按合同适用层级登记。CI、单元测试或离线端到端夹具均不能替代第 4 层普通用户可用性、第 5 层产品真实性/安全呈现、第 6 层商业画质及第 7 层真实投放效果。
9. 计数继续保持 `code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false`。本批是初步关系裁决，不是完整代码/测试证据审计；不赋权、不计算总体完成率。

### 唯一下一步

A0–A49 已完成初步合同关系裁决或关系复核；继续 PLAN-003，按既定顺序进入 **A50–A67 的关系与当前证据复核**，并在之后按批次推进 A68–A89、A90–A112。不得为追求表面完成率跳过未核验项或删除暂缓的真实环境验收。



---

## PLAN-003 第三批关系与证据复核｜A34–A49｜2026-10-15｜部分映射，非正式验收

### 当前基线与范围

- 当前 PR #32 HEAD：`3ca7ff00ea35742b461d72ec4317419ec0d0d39d`，PR 保持 Open / unmerged。
- 本轮开始时该 SHA 的 PR-triggered CI、PR-triggered `ad-studio-doc-sync` 与 Netlify deploy-preview 均为 success。
- 静态核对文件：`test_short_drama.py` blob `2995b5764f7a86ee8c274b6359ff2f09cdf7a288`；`test_desktop.py` blob `357c54dad99f61b99891bcc365dd2f9efc1a1009`；`test_ai_handoff.py` blob `9a0c0283f11f9ec8024514907cb7a4058815c2bf`；`SESSION_HANDOFF.md` blob `afaa266649cb246185415d923ddf24a00dd9a04c`。本轮未本地重跑测试；CI 成功不等于各项合同重新验收通过。
- 本批只做规划、关系和证据边界审计，不改产品代码，不启动真实 Provider/扣费、Windows 真机、真实素材、剪映或投放验证。

### A34–A49 关系裁决

| ID | 合同边界与关系 | 当前证据 | 剩余条件 |
|---|---|---|---|
| A34 | AI参考图对照生成画面；匹配也不得自动批准。 与 A22/A66/A67 相关但不合并。 | test_short_drama.py：FakeRouter mismatch/no-auto-approve/invalid-input。 | 部分映射；真实视觉准确率、真实素材和人工复核体验未证明。 |
| A35 | 只准备并作用于所选镜头的重生成，保留旧版和核验历史。 依赖 A34；与 A36/A43 相关但不合并。 | 测试覆盖目标镜头、其他镜头不变、历史保留及非法模式/空修正。 | 准备状态不等于真实生成；取消零调用、项目隔离和失败矩阵待核。 |
| A36 | 将视觉核验结果变成用户可编辑的修正草稿，并校验费用和版本。 与 A35 前后依赖，不合并。 | 测试覆盖摘要/问题列表草稿及无效镜头/模式、非有限费用、版本防护。 | UI编辑/取消、费用确认前零 Provider 调用和保存状态待核。 |
| A37 | 视觉修正草稿必须显示真实换行。 与 A50/A56 提示词换行相关但对象不同。 | 草稿字符串测试与 handoff 文案断言。 | 未找到直接 GUI 布局断言；真实窗口可读性未证明。 |
| A38 | 跨会话新 AI 能恢复项目上下文与当前状态。 与 A31/A32 相关但不合并。 | test_ai_handoff.py 检查章节/关键字符串。 | SESSION_HANDOFF 历史段仍含旧 HEAD、PR #31 和旧下一项，可能误导。 |
| A39 | 功能分支 push/PR 应触发完整 CI。 与 A42 SHA 绑定相关但不合并。 | 当前 PR CI/doc-sync success。 | 本轮未独立核实 Push-triggered 两项；workflow触发范围需再核。 |
| A40 | 接手测试使用稳定仓库根路径读取文档。 与 A38/A41 相关但不合并。 | test_ai_handoff.py 用 Path(__file__).resolve().parents[2] 构建 ROOT 路径。 | 本轮未本地重跑；需确认当前 CI 已收集执行该测试。 |
| A41 | 接手关键文案有回归断言，不得删除测试换绿。 与 A40/A38 相关但不合并。 | 测试直接断言多个关键文案和固定字符串。 | CI成功；字符串存在不保证语义/当前状态正确。 |
| A42 | CI 结果必须绑定具体 HEAD SHA。 与 A39 触发机制相关但不合并。 | 当前 SHA 3ca7... PR CI/doc-sync/预览已实查成功。 | 测试/历史 handoff 仍保留 443f713... 旧基准；需避免误用历史绿灯。 |
| A43 | 单镜头重生成失败/中断时恢复上一有效视频与状态。 与 A46/A47/A53/A54 相关但不合并。 | test_desktop.py 有 Provider 失败与中断恢复测试。 | 缺失/空文件、临时输出清理、状态组合边界待核。 |
| A44 | 短剧项目镜头稳定映射到分镜；歧义时失败关闭。 与 A35 修复流程相关但映射是独立前置。 | test_short_drama.py 覆盖稳定索引、旧数据唯一匹配、歧义拒绝。 | 需追踪所有生成/修正/审核调用点是否使用统一映射。 |
| A45 | 恢复后 UI 状态准确呈现旧视频已恢复。 与 A43 数据恢复相关但聚焦 UI 状态。 | test_a45_ui_failure_state_keeps_recovered_previous_video_status。 | 恢复标记、文件存在/非空与重载状态组合及 Windows UI 未证明。 |
| A46 | 编辑镜头通过安全重生成状态转换，不能提前清空旧视频/递增版本。 与 A43 共用恢复机制但入口合同不同。 | test_a46 检查 mark_regenerate 调用及禁止破坏性赋值。 | 取消编辑、多次重试及实际失败边界待核。 |
| A47 | 素材解析失败时不调用视频 Provider，并保留旧视频/状态。 与 A43 相关但失败阶段不同。 | 故障注入测试断言 Provider 未调用、旧文件保留、临时文件清理与重载。 | 真实 Windows 文件系统异常仍未验。 |
| A48 | 实拍裁剪失败不破坏正式输出。 与 A49 多段清理、A43 AI生成恢复相关但不合并。 | 故障注入测试检查旧输出内容、状态、临时文件与重载。 | 真实 FFmpeg/原子替换/真实素材未验。 |
| A49 | 多段实拍源缺失/中断时清理残留分段并保留旧成片。 与 A48 单段裁剪及 A30 通用恢复相关但不合并。 | test_a49 覆盖源缺失、残留分段清理和旧视频保护。 | 强制进程中断/重开、多种命名与引用文件保护矩阵待核。 |

### 跨文档冲突候选（登记，不在本轮扩展修复范围）

1. **接手文件状态冲突：** `SESSION_HANDOFF.md` 顶部当前入口已指向 PR #32，但后续历史快照仍出现旧 HEAD、PR #31 和旧“下一项”。历史快照可用于追溯，却应明确不可执行，否则新 AI 可能误用。
2. **A38/A42 测试边界：** `test_ai_handoff.py` 主要断言固定章节/文案，并保留历史 SHA `443f713cd3721eab528eb9bb17faf599d55ef3ce`；这不能证明当前 handoff 的 HEAD/PR 状态实时正确。
3. **A39 证据分层：** 本轮已确认当前 SHA 的 PR CI/doc-sync 和部署预览成功；Push-triggered CI/doc-sync 未独立核实。本轮也未本地重跑 unittest。
4. **A37 UI证据不足：** 现有测试证明草稿字符串有换行，不证明 Windows 窗口缩放下实际布局和可读性。
5. **A34 视觉真实性边界：** FakeRouter 测试证明部分状态处理和不自动批准规则，不证明真实视觉模型判断商品外观/结构/功能/用法准确。

### 关系结论

- A34/A35/A36 分别是视觉比对、单镜头重生成准备、可编辑修正草稿；前后依赖但不合并。
- A37 与 A50/A56 都涉及换行，但分别针对修正草稿与 Provider 提示词，不合并。
- A38–A42 分别覆盖接手完整性、CI 触发范围、测试路径、文案断言、SHA 绑定；共用 handoff 测试不等于同一合同。
- A43–A49 分别覆盖重生成/中断恢复、稳定镜头映射、恢复状态 UI、安全编辑入口、素材解析失败、实拍裁剪失败、多段素材清理；故障阶段和回滚条件不同，全部保留。
- 所有结论仍是部分映射，不升级正式验收状态。保持 `code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false`；不赋权、不计算总体完成率。

### 下一项

A0–A49 已完成初步关系裁决或关系复核；下一批按既定顺序审计 **A50–A67**，重点核对 A50/A56 的行为合同与回归修复、A57 的 UI/恢复两个独立场景、A61/A62 的成本迁移与文案断言修复。

### 本轮登记后的唯一下一项

**PLAN-003 子任务：按 A0–A112 顺序做跨源语义裁决与证据绑定；A0–A49 已完成初步关系裁决/复核，下一批审计 A50–A67。** 对每项只确认：正式验收合同原文、各来源对应位置、是否独立/依赖/重复/历史状态、代码实现链、专项正反例、最新 SHA CI/doc-sync、适用七层、剩余验证与暂缓边界。每批审计完成后更新本表的关系裁决与证据 SHA，并保留未解决项；不得只因为标题相似就合并，也不得把历史快照直接覆盖为当前状态。

停止条件：不开发产品功能；不新增/删除/重编号 A0–A112；不启动真实 Provider、真实扣费、Windows 真机、真实素材、剪映现场或真实投放验证；不赋权、不计算总体完成率；不创建仅用于记录 CI 状态的提交。
