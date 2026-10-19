# 数学辅导项目 AI 执行控制协议

版本：1.0
适用范围：仅 apps/math-tutor/
权威基线：SESSION_HANDOFF.md、docs/IMPLEMENTATION_PLAN.md、docs/MATH_TASK_REGISTER.json、docs/PROGRESS_DASHBOARD.md、docs/ACCEPTANCE.md
当前 PR：#33（接手时必须重新查询）

## 1. 每个新窗口的强制接手顺序
1. 查询仓库当前分支、PR #33 的状态与 head SHA，不把聊天摘要当作最新事实。
2. 读取 apps/math-tutor/SESSION_HANDOFF.md。
3. 读取 docs/AD_MATH_EXECUTION_CONTROL.md、docs/IMPLEMENTATION_PLAN.md、docs/MATH_TASK_REGISTER.json、docs/PROGRESS_DASHBOARD.md、docs/ACCEPTANCE.md、docs/CHANGELOG.md。
4. 查询最新 head 的 CI/status、workflow runs、部署检查。分别记录 SUCCESS、FAILURE、RUNNING、PENDING、NOT_RUN、NO_DATA；空结果是 NO_DATA/未确认，不等于成功。
5. 检查上一步任务对应的源码、测试、验收证据和最新提交；发现文档状态与代码不一致时先纠正状态。
6. 明确本轮唯一任务、任务 ID、范围内/范围外、依赖、要修改的文件、测试方法、通过条件和停止条件，再执行。
7. 完成后复核 diff/提交、运行相关测试、更新任务登记、看板、变更日志、接手文件，并重新查询最新 head/CI。
8. 告知用户真实结果及未完成事项。不得仅因思考/工具调用中断而假定工作完成。

## 2. 权威来源与冲突解决
- 任务范围、权重和依赖以 IMPLEMENTATION_PLAN.md 为人类可读基线，MATH_TASK_REGISTER.json 为机器可读镜像；发现二者冲突，停止计进度，先修复并记录。
- 单项是否验收以 ACCEPTANCE.md 中对应要求和可复查证据为准。
- 当前提交/CI/PR 状态以最新 GitHub 查询为准；本文件里的 SHA 仅是上次快照。
- SESSION_HANDOFF.md 用于跨窗口快速恢复，但不能替代重新查询代码与 CI。
- 不从旧聊天、旧摘要、绿色旧 CI 或仅有的部署预览推断最新状态。

## 3. 固定范围与任务控制
- 固定 32 项 MATH-001 至 MATH-032，权重合计 100%；未经用户明确批准，不增加任务、不改变权重、不扩大首期范围。
- 本项目首期强制包含：有限学习时间、证据驱动任务排序、掌握后减少练习、试卷照片三种状态、低置信度人工确认、评分来源隔离、共享教学闭环、无效策略实际切换、学习效果测量。
- 试卷状态必须区分 blank、student_answered_ungraded、teacher_graded。
- 每题每回合最多 3 次主动提示；答错、用提示或看过解法的题须安排重做；重做不自动显示旧提示/解法。
- 用户已决定从头自研；OpenMath 缺少可复查许可证全文只意味着不得复制其源码，不阻塞自研。参考项目只借鉴设计/方法，第三方依赖与素材分别核查许可。
- 不修改 apps/ad-studio-desktop/；不自动合并 PR；不把未经确认的教材册次/目录标为已验证。

## 4. 任务开始前必须写明
- 任务 ID 和当前状态；
- 本轮唯一目标；
- 依赖与风险；
- 明确的范围内/范围外；
- 修改文件预期；
- 自动化测试/人工验收命令或步骤；
- 通过条件；
- 停止条件（例如许可证未确认、缺少用户数据、CI 未返回）。

没有先说明计划，不开始改代码或批量更新文档。

## 5. 证据与验收状态
允许状态：NOT_STARTED、IN_PROGRESS、BLOCKED、IMPLEMENTED_UNVERIFIED、VERIFIED、ACCEPTED、NOT_APPLICABLE（必须说明理由）。
- VERIFIED/ACCEPTED 必须附可复查证据：提交 SHA、测试命令/步骤、结果、必要日志或截图、验收日期。
- 只有 ACCEPTED 项可计入交付完成率。代码已写但测试未跑属于 IMPLEMENTED_UNVERIFIED。
- 失败、未运行、阻塞、无数据必须明确标记，不可用空值冒充成功。
- 文档更新、提交成功、CI 通过、部署成功分别只是各自层面的证据，不自动代表产品行为通过。
- 学习效果必须基于真实、可比、足量的数据；无数据写 NOT_MEASURED，不写成 0 分，也不推断有/没有进步。
- 真实学校成绩、系统确定性评分、AI 估分分别记录，不得混淆。

## 6. 进度计算
- 任务数始终 32；权重总和始终 100%。
- 已验收任务数 = 状态为 ACCEPTED 且证据完整的任务数。
- 加权完成率 = ACCEPTED 任务权重总和；不能按写了多少文档、提交数或代码行数计算。
- 另外分开报告：软件交付进度、教学闭环有效性、孩子真实学习效果。
- 修改任务状态时必须同步更新任务登记与进度看板；涉及验收规则时同步 ACCEPTANCE.md；每轮结束更新 CHANGELOG.md 和 SESSION_HANDOFF.md。
- 不能为了得到百分比而把大任务拆成新任务或修改分母。若用户批准计划变更，必须版本化记录前后差异与权重影响。

## 7. 用户自由度、安全与隐私
- DeepSeek provider/model/base URL 按计划可配置；密钥仅服务端保存。应用层不设 Token 预算上限，但错误重试必须有界、退避且可恢复。
- 不确定的 OCR、手写数学、图形、批改痕迹不得静默变成事实；低置信度要人工确认。
- 儿童数据最少收集、访问隔离、保留规则清楚、导出/删除可验证。
- 不以强制签到、排行榜或刷题量制造额外学习负担。
- 不承诺固定提分；没有进步时要如实报告并实际补弱、调整和复测。

## 8. 每轮结束检查清单
- [ ] 最新 PR/head SHA 已重新查询。
- [ ] 最新 CI/workflow/部署状态已分类，空结果未冒充成功。
- [ ] 修改范围符合唯一任务，无无关文件。
- [ ] 相关测试真实运行并记录输出；未运行项标明原因。
- [ ] 对应验收条件与代码证据一致。
- [ ] MATH_TASK_REGISTER.json 状态、权重、证据与 IMPLEMENTATION_PLAN.md 一致。
- [ ] PROGRESS_DASHBOARD.md 的 32 项分母、加权率、阻塞和状态快照正确。
- [ ] CHANGELOG.md 与 SESSION_HANDOFF.md 已更新。
- [ ] 未修改桌面广告项目，未自动合并 PR。
- [ ] 给用户汇报已完成、未完成、阻塞和下一项唯一任务。

## 9. 当前基线快照
截至 2026-10-19，计划版本 2.2，固定 32 项/100%，已验收 0/32、加权完成率 0%。MATH-002 为 IN_PROGRESS。Vue/Vite build/test 与 FastAPI/SQLite 基线已纳入 CI；照片识别、真实 DeepSeek 调用、手机端端到端和学习效果尚未验收。最新状态以每次接手重新查询为准。


## 10. 进度数据自动一致性守卫（2026-10-19）
- GitHub Actions 的 Python 测试步骤运行 `python -m pytest -q apps/math-tutor/tests`。
- `tests/test_progress_integrity.py` 自动核对任务 ID、32 项固定分母、100% 权重、ACCEPTED 证据门槛，以及任务登记表与看板的任务数/验收数/加权率一致。
- 若更新任务状态、权重或验收数，必须同步任务登记与看板；否则 CI 会阻止该提交通过。
- 这是一种防漂移机制，不会把未验收功能自动标为完成，也不会自动改写文件。AI 仍需先检查证据、更新状态与记录，再由 CI 验证一致性。
