# 【最新接手状态｜A111 已通过自动化 CI；下一项 A112｜2026-10-14】

- 仓库：konggu888/ecommerce-agent；分支：feat/product-drama-visual-review；PR #32 保持 open/unmerged。
- 当前 HEAD：fc445e75e40fd34e5b16868369700e685e2db276。A111 逐边界局部音乐卡点已进入最终生产规划函数；相邻边界冲突时局部撤销位移、保留其他安全边界，保持总时间轴长度；审计记录调整/回退边界序号。
- 最新 HEAD 四项检查均 success：CI Push 38567371929、CI PR 38567378825、docs-sync Push 38567371969、docs-sync PR 38567379230。
- 首轮 A111 CI 曾失败 3 个旧断言，根因是断言仍要求整组回退，与 A111 局部回退设计冲突；修复测试预期与审计原因后，最终 SHA 四项检查全部成功。没有隐瞒中间失败。
- 代码、测试与八份强制文档/路线图已同步。下一项路线图 A112：审计并接通 A108 SRT cue 的实际时间窗到内容保护/卡点约束；先确认真实数据路径，不以字符数假装精确时间戳。
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
- 当前主攻阶段：商业级剪辑决策层；A109“音乐节拍与画面切点真实联动”已提交自动化实现。先重新核验最新 HEAD、CI 与 docs-sync；如果失败，先读日志并修复，不能直接推进后续任务。
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
- 当前已核对基线：A108 字幕基础自适应实现提交 `83549d4ca428adc233d61da292e2f245d498da0d`；路线图文件随后已提交，接手者必须重新查询当前 HEAD 及其 CI/doc-sync。
- 当前主攻：商业级剪辑决策层升级。
- 历史兼容快照（仅保留旧 handoff 测试所需文字，不代表当前状态）：A34：AI 辅助商品画面对比（待最新 CI 验收）；A35：单镜头局部修复第一阶段已实现。当前实际进度以本节上方路线图指令、当前代码与最新 CI 为准。
- 下一项具体工作：A109 音乐节拍与画面切点真实联动。先审计 BGM 在逐镜头处理、最终拼接和原音轨中的实际路径，再实现并测试真实时间轴联动。
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
