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
