# 数学辅导项目 AI 接手文件

最后更新：2026-10-19
计划版本：2.2
仓库：konggu888/ecommerce-agent
分支：feat/beishi-grade2-math-tutor
PR：#33（Draft、未合并；接手时必须重新查询当前状态）

## 1. 接手前必须做
1. 阅读本文件、README.md、docs/IMPLEMENTATION_PLAN.md、docs/PROGRESS_DASHBOARD.md、docs/CHANGELOG.md、docs/ACCEPTANCE.md、docs/AI_TUTORING_PROTOCOL.md、docs/PRODUCT_SPEC.md。
2. 查询最新 HEAD、PR、CI/checks 和部署状态；分开报告成功、失败、进行中、未运行。
3. 检查实际源码、测试和已有功能，不从聊天摘要推定完成。
4. 开始前说明本轮唯一任务、范围和验收条件。
5. 只在 apps/math-tutor/ 内工作；不修改 apps/ad-studio-desktop/；不自动合并 PR。

## 2. 产品最高目标
交付一个能帮助孩子真正独立掌握北师大版小学数学二年级知识，并用可比测评验证学习变化的闭环系统。每次错误需要有证据、有诊断假设、有教学策略和后续验证。策略无效时要调整，不可机械重复。
系统必须回答：孩子掌握什么、哪些还不会、证据是什么、可能原因是什么、系统采取了什么措施、措施是否有效、几天后是否仍然会、单元/期中/期末是否出现可比变化。

## 3. 不可违反的用户要求
- 从头自研；全网项目仅作框架/交互/OCR/儿童 UX/测试方法参考，不复制候选源码。不得因为框架或难度删除既定功能。第三方依赖和素材仍分别核查许可。
- 最终交付手机浏览器可用的中文响应式网站，不要求本地模型。
- 首选用户已有 DeepSeek API；应用层不设 Token 配额/预算上限；API Key 仅存服务端。技术故障退避重试且可恢复，避免死循环；不能将故障保护当作教学 Token 限额。
- 每题每回合最多 3 次主动提示，提示逐级深入。
- 答错、用提示或看过解法的题必须进入重做队列；默认间隔 3–5 道其他题后重做，或进入下次学习；重做先隐藏旧提示/解法。
- 练习正确、提示后答对、原题重做、新题迁移、无提示测验和延迟复测分开记录。
- 错误诊断必须有证据；不确定时标 unknown。系统通过鉴别题识别问题原因，并依据后续表现评估教学策略。
- 连续失败时考虑换策略或检查前置知识；逐步减少不必要提示，但不能机械拒绝合理求助。
- 每单元有基线、结束平行测验、延迟复测；期中/期末有覆盖已学内容的累积测验。
- 未提升时如实报告、补弱、调整和复测，不承诺特定分数。
- 固定计划为 32 项、权重 100%；不经用户批准不增任务、不改权重/分母。
- 软件完成率与孩子学习效果必须分开统计。

## 4. 固定计划与当前状态
路线图：docs/IMPLEMENTATION_PLAN.md（v2.1）。
产品需求：docs/PRODUCT_SPEC.md。
架构：docs/TECHNICAL_ARCHITECTURE.md。
教学闭环：docs/AI_TUTORING_PROTOCOL.md。
教材：docs/CURRICULUM_PLAN.md。
隐私/用量：docs/PRIVACY_AND_COST.md。
验收：docs/ACCEPTANCE.md。
看板：docs/PROGRESS_DASHBOARD.md。
变更记录：docs/CHANGELOG.md。
任务 32 项，已验收 0/32，加权完成率 0%。应用代码、DeepSeek 实际调用、手机端和学习效果测量均未运行。文档写完不等于应用功能完成。

## 5. 最新 GitHub 状态（接手时仍须重新查询）
- 本轮文档更新前核实 HEAD：`c8519a557bb4dabefad9ab74118c3fb05d929941`；PR #33 为 Open/Draft/未合并。
- 该 SHA 的 GitHub Actions CI run `39217632873` 为 completed/success；combined status 有 Netlify deploy-preview success。此结果仅对应文档更新前 SHA。
- 本轮对许可证门禁记录的文档提交会改变 HEAD；接手时必须查询新 HEAD 的 CI/status，不得继承旧 SHA 的成功状态。
- 计划仍为 32 项、已验收 0/32、加权完成率 0%；本轮文档证据更新不代表应用功能实现或进度增长。

## 6. 下一任务（不可跳过）
按用户最新决定从头自研。下一步执行调整后的 MATH-002：验证 Vue 3 + TypeScript + Vite、Python + FastAPI、SQLite、自动化测试与手机端开发路径；随后 MATH-003 冻结中国儿童视觉/交互系统，MATH-004 建立独立骨架并跑通 build/test/API/持久化 smoke test。OpenMath 缺少许可证全文只意味着不复制其代码，不再阻塞自研。

## 7. 任务验收规则
每项记录 ID、目标、范围内/外、依赖、文件、验证步骤、通过条件、结果证据、状态和提交 SHA。没有证据标未运行/阻塞，不算完成。每轮结束更新看板、变更日志和接手文件。CI 成功不等于应用或学习效果验收成功。

## v2.1 强制实现与验收约束

用户已明确要求这些目标必须实际实现，不能只写在计划中。后续接手 AI 不得把它们放回“以后再做”或缩成建议：
1. 时间效率：家长可设置每日学习时间上限；默认建议约 10 分钟但不要求学满；系统按证据排序，时间到后不再启动新任务，未完成项顺延。不得用每日固定题量或签到制造负担。
2. 智能优先级：综合知识掌握证据、反复失误、知识重要性、前置依赖和近期测评，选择有限时间内最值得学习的目标；掌握稳定后减少练习，必要时少量抽查。
3. 每题目的明确：题目必须服务于诊断、教学、独立验证、迁移或复习之一，避免无目的刷题。
4. 教学自适应：教学后无提示表现未改善时，系统实际切换策略或检查前置知识；保存策略变化及其结果。
5. 试卷拍照是首期核心入口：支持空白试卷、孩子已作答未批改试卷、老师已批改试卷。图片/多页处理、题号与题目结构化、手写答案/过程和批改痕迹识别、置信度与人工确认、知识点映射、评分分离、诊断辅导和复测必须形成可运行链路。
6. 三类试卷按状态分流：空白卷先独立作答；已作答未批改卷保留孩子原始独立作答证据；已批改卷记录老师原始分数和批改痕迹并优先分析错题。老师分数与系统测评分开。
7. 以上要求映射进现有 MATH-001–MATH-032 验收矩阵，不另造无限任务；任何能力未实现/未测试必须保持未验收，不能因为本轮文档更新而增加进度百分比。
8. 每轮只推进有边界的任务；许可证门禁仍先行。本次新增要求不授权绕过 OpenMath 许可检查、不授权合并 PR，也不允许修改 apps/ad-studio-desktop/。

## 8. 跨窗口/跨模型连续性文件（必须共同使用）

本项目的连续性管理文件已补齐。每个新 AI 窗口必须按以下顺序使用，不可只读本文件后凭记忆开发：
1. 本文件：产品硬约束、当前状态、下一任务。
2. docs/AD_MATH_EXECUTION_CONTROL.md：执行协议、证据标准、停止条件、每轮结束检查清单。
3. docs/IMPLEMENTATION_PLAN.md：人类可读的 32 项固定路线图、权重、依赖和验收。
4. docs/MATH_TASK_REGISTER.json：机器可读任务登记，必须核对 32 项/100% 权重、任务状态和证据。
5. docs/PROGRESS_DASHBOARD.md：当前软件进度、学习效果、教学闭环和 CI 状态。
6. docs/ACCEPTANCE.md：任务验收门槛。
7. docs/CHANGELOG.md：计划和执行变更历史。

交接纪律：
- 聊天摘要和旧 SHA 只是线索，不是最新事实；每个新窗口必须重新查询 PR #33、HEAD、CI/workflow 和部署状态。
- 最新 CI 查询空结果必须写 NO_DATA/未确认，不能写成功。
- 接手后先说明本轮唯一任务与验收条件，再执行；完成后更新任务登记、看板、变更日志和本文件。
- MATH_TASK_REGISTER.json 与 IMPLEMENTATION_PLAN.md 不一致时，暂停计进度并先修复一致性。
- 当前文档连续性补齐提交：执行控制协议 88b339987b7998202fb953d189d3f17b8686c138；任务登记表 dcc7120233c7a4f5110fe6ebbee127c766881665。它们不是当前 HEAD 的保证；接手时仍需查询最新提交。


## 2026-10-19 许可证门禁复核补充

本轮检查 OpenMath 当前公开 README 的 Apache 2.0 声明，并对 LICENSE、LICENSE.md、LICENSE.txt、COPYING、NOTICE 进行 GitHub 内容查询，均未找到。README 的声明不能在本项目既定门禁下替代可复查许可证全文/作者确认。MATH-001 标记 BLOCKED，不能开始复制/改编上游代码。上轮 CI `39217632873` 成功及 Netlify deploy-preview 成功仅对应文档更新前 SHA `c8519a557bb4dabefad9ab74118c3fb05d929941`；本轮提交后需重新查询最新 SHA 的 CI。


## 2026-10-19 回退候选初筛交接

本轮已完成两个替代候选的文件级初筛（不超过既定候选总数 3）：
1. `onemorepereira/math-tutor` / Number Ninja：根目录 MIT LICENSE 已读取；Vue 3/Vite 前端、AWS Lambda/DynamoDB/Bedrock 后端，README 声称手机适配、答题记录和提示。与私人 DeepSeek 目标不完全匹配，注册/排行榜等需删减；未 clone/运行测试。
2. `AyushDixit-21/MathTalk`：根目录 MIT LICENSE 已读取；React/Vite + FastAPI/SymPy，README 将其定位为原型且未验证教育效果。课程/试卷照片/二年级教学闭环不匹配；未 clone/运行测试。

初步优先级：下一步深入审查候选 1 的目录、测试、依赖、后端/前端实际完成度与改造成本；如果候选 1 明显不适合，再在既有两个候选中比较，不新增候选。OpenMath 仍因未找到许可证全文/作者确认而 BLOCKED，不复制其代码。选型和应用代码仍未完成；已验收 0/32、加权完成率 0%。

最新状态复核：HEAD `e7e10491fefea44327656ffaac3333fc10c45b69` 的 GitHub Actions CI run `39218343866` 为 completed/success；Netlify deploy-preview combined status 为 success。该状态仅对应此 SHA，任何后续提交均需重新查询。


## 2026-10-19 最新提交后复查（元数据更新前快照）
- 五份候选评估/交接文档已提交后，PR #33 HEAD 为 `59226c26e1997361a73dad0051308a1703ba1cc2`，PR 仍 Open/Draft/未合并。
- 该 SHA 的 GitHub Actions CI run `39218680024` 为 queued/running；combined status 尚无状态项。当前提交的 CI 不能标为成功。
- 该 SHA 的 JSON 任务登记已重新解析通过：32 项、权重总计 100%、已验收 0 项，MATH-001 仍 BLOCKED。候选评估不计入软件完成率。
- 这是元数据更新前的复查快照；本次记录本身会产生新 HEAD，接手时仍须重新查询最新 SHA 和 CI。


## 2026-10-19 — 候选 A 源码级静态审查补充

通过 GitHub 文件接口继续检查 `onemorepereira/math-tutor` 的具体源码（没有下载或运行仓库）：
- `frontend/src/views/GameView.vue`：是以题目进度、积分、提示显示和单题作答为核心的游戏式界面。
- `frontend/src/router/index.ts`：登录、注册、忘记密码/重置密码、游戏、成绩卡和统计路由；游戏/成绩等页面要求身份认证。
- `backend/src/functions/createGameSession.ts`：请求包含难度、题量、子类别，调用 Bedrock 生成题目，并经独立答案验证后保存到 DynamoDB；读取用户身份依赖 Cognito claims。
- `backend/src/functions/submitAnswer.ts`：记录单题答案、提示数和耗时；会拒绝同一问题的第二次提交，当前模式偏向一轮游戏评分，而不是原题重做与长期掌握证据队列。
- `backend/src/functions/requestHint.ts`：提示接口也依赖 Cognito、DynamoDB 与 Bedrock；尚未证实符合本项目每题每回合最多 3 次主动提示的完整教学协议。
- 找到 `backend/src/functions/submitAnswer.test.ts` 与 `backend/src/utils/answerMatcher.test.ts`，说明仓库包含部分后端单元测试；本轮未运行。
- 本次未找到可确认的试卷图片上传/OCR/教师批改痕迹识别实现；未找到北师大版二年级课程资产。此结论仅限已检查 README、关键前后端文件，不能替代全仓库测试。

运行限制：尝试在执行环境浅克隆候选仓库，失败原因为执行环境无法解析 `github.com`（网络/DNS 不可用），不是候选项目自身运行失败。因此本轮只能完成静态代码审查，未能安装依赖、跑测试或验证实际启动。候选 A 可作为可复用的 UI/部分答题流程参考，但不能直接认定为可运行基座；必须先获得可运行源码副本并执行基线测试，之后再决定复用范围。


## 下一步唯一任务
按用户最新决定从头自研。下一步执行 MATH-002：验证 Vue 3 + TypeScript + Vite 前端、Python + FastAPI 后端、SQLite、自动化测试和手机端开发路径；然后完成 MATH-003 儿童视觉/交互系统，MATH-004 自研骨架与前后端基线测试。不得再把候选项目运行作为开发门禁。


## 2026-10-19 用户确认：从头自研，功能不得删减
最新决定覆盖此前“优先复用成熟开源项目、OpenMath 必须先选型运行后才能开发”的方向。我们从头开发自己的数学辅导网站。可以全网研究和借鉴框架、儿童交互、OCR/视觉、教学设计、测试方法；不复制候选项目源码。第三方依赖/字体/图片/音效/教材素材仍要各自核查许可。OpenMath 缺许可证全文不再阻塞自研，但仍禁止复制其代码，除非未来单独核实许可。

### 全部既定功能必须保留
不因技术框架、实现难度或阶段安排删掉/降级任何此前确定的强制能力：多页试卷拍照与 blank / student_answered_ungraded / teacher_graded 分流、OCR/数学符号/手写过程/图表/老师批改识别、置信度与人工确认、老师/系统/AI 评分分离、DeepSeek 服务端配置、家长可设每日时间上限、证据驱动任务排序、掌握后减量、最多 3 次分层提示、错题重做、诊断与鉴别题、策略无效时实际换策略/查前置知识、迁移/间隔复习/延迟复测、单元/期中/期末测量、家长报告、持久化/导出/删除、儿童隐私、断网/识别失败恢复、自动化与真实手机端验收。保持 32 项/100% 的固定任务体系。

### 中国儿童视觉与交互基线
简体中文原生，符合中国小学教材语言和家庭学习场景；视觉温暖、清晰、灵动、耐看，不幼稚化、不堆叠动画；大字、明显按钮、手机单手操作、可选普通话朗读/安静模式；用数轴、分组、图形、操作演示等让趣味服务于理解。避免排行榜、强制签到、羞辱性反馈和用刷题量代替掌握。以上需落实为组件/样式/交互并经手机端验收，不是仅写在设计文档里的口号。

### 下一步唯一任务
按调整后的 P0 先做自研技术栈与开发环境基线：验证 Node/Vue/TypeScript 前端、Python/FastAPI 后端、SQLite 数据层、自动化测试和手机端开发路径；随后建立自研骨架。不得再花一轮只比较开源候选，也不得因 OpenMath 许可问题停住自研。开始实现前先告知本轮范围与验收条件，完成后更新固定 32 项的真实状态。


## 2026-10-19 最新决策补充：自主选择单元 + 当前执行状态

本节优先于本文件中更早的候选评估/许可证门禁快照。旧快照只保留历史记录，不代表当前下一步。

### 自主练习必须交付的行为
- 孩子可以只练一个单元、组合任意已学单元、累计复习全部已学单元，或调整当前单元与旧单元的出题比例。
- 自主练习与老师作业分开；老师作业范围不擅自扩大。
- 孩子可以暂停、跳过、返回旧单元、重学或探索未系统学习的单元。AI 可建议补前置知识，但不能把建议变成强制锁定。
- 未选择的单元不能静默混入；如建议复习，先说明理由并让孩子决定。
- 区分多单元混合练习与单题跨知识点综合应用；每题记录单元、知识点、前置依赖、练习目的、难度和版本。
- 数学答案/题目条件/歧义须尽可能独立校验；不确定时请求确认、允许跳过或恢复，不能把系统错误归咎于孩子。
- 上述要求映射到现有 MATH-007、MATH-008、MATH-021、MATH-025 等任务，不增加 32 项任务分母或权重。

### 当前执行决定
- 当前唯一任务仍为 MATH-002：自研技术栈与开发环境基线。已检查 GitHub 分支，未找到 `apps/math-tutor/package.json`、前端 `package.json`、`pyproject.toml` 或后端入口文件；因此当前尚无可运行的自研应用骨架，不能声称 Vue/FastAPI/SQLite 的 build/test 已通过。
- 由于本轮执行接口只能直接读取/写入 GitHub 文件，无法在本地运行 npm/pip/浏览器测试；MATH-002 不能据此验收。下一步必须取得真实构建/测试证据，不能用文档替代。
- 本轮更新了产品规格、验收、任务登记、README、路线图/看板相关状态与变更记录；这些文档更新不计软件完成率。
- 固定计划 32 项、权重 100%、已验收 0/32、加权完成率 0%。
- 本轮状态核验时 PR #33 HEAD 为 `2269f2e027b7c88eb94f9fb89844be75020415ee`，CI run `39220155670` 为 in_progress，Netlify deploy-preview 为 success。该快照仅对应该 SHA；接手必须查询更新后的 HEAD/CI。


## MATH-002 实测进展（2026-10-19，优先于此前状态描述）
- 已新增 `apps/math-tutor/tests/test_environment_baseline.py` 和 `apps/math-tutor/docs/STACK_BASELINE.md`。
- 当前容器实际运行同一基线测试：`pytest -q`，结果 `2 passed`；FastAPI TestClient 返回 HTTP 200，SQLite 最小写入/读取通过。
- 实测环境：Node v22.16.0、npm 10.9.2、TypeScript 5.8.3、Python 3.13.5、FastAPI 0.128.2、Starlette 0.50.0、pytest 9.0.2、SQLite 3.46.1。
- 未完成：Vite 未安装；Vue 3 + TypeScript + Vite 项目级依赖安装/build/test 未运行；手机浏览器/E2E 未运行。尝试 clone 仓库因当前容器 DNS 无法解析 github.com 失败，这是执行环境限制。
- MATH-002 状态为 IN_PROGRESS，不能验收；应用软件功能尚未开始，已验收 0/32、加权完成率 0%。
- 下一步：解决可复现的 Vue/Vite 构建与项目级测试验证，再推进 MATH-003/004；不得把 Python 环境 smoke test 夸大为完整技术栈验收。


## 2026-10-19 最新需求补充：AI 老师声音、黑板、积分奖励（优先级高）

用户明确询问网页是否有声音/鼓励声音、讲解时是否有 AI 老师形象、是否有黑板，以及是否能设置积分和兑换奖励。当前代码尚无已验收产品实现；已将以下内容加入 PRODUCT_SPEC.md 和 ACCEPTANCE.md，映射到既有任务，不增加 32 项分母：

- AI 数学老师形象在讲解/倾听/思考/鼓励时有清楚状态；普通话语音讲解与同步字幕；支持暂停、重播、音量、静音/安静模式。语音不可用时文字讲解仍完整，声音反馈真诚温和，鼓励努力、尝试和纠错，不只表扬答对。
- 可操作数学黑板逐步呈现算式、数轴、分组/图形和解题步骤；支持暂停、上一步/下一步/重播。内容必须与确认题目一致，空白试卷和无提示测验绝不能通过声音、动画或黑板泄露答案。
- 家长自由创建/编辑/停用奖励和积分门槛；10/20 分只是例子，不固定奖励。积分账户显示余额和获得原因，兑换前明确确认；兑换后扣除可用余额，但保留所有获得/兑换/调整流水、学习记录和兑换时奖励快照。余额不足/重复提交不得造成错误扣分或重复兑换。积分不能冒充数学掌握度。
- 归入 MATH-003、MATH-009、MATH-021、MATH-023、MATH-025、MATH-028；固定 32 项、权重 100% 不变。
- 这些仅是需求和验收标准，不是已完成软件功能；当前已验收 0/32、加权完成率 0%。


## 2026-10-19 最新视觉方向补充：更逼真的原创 AI 数学老师
用户明确表示可以参考豆包、学而思、作业帮等产品中较逼真的老师形象。把它理解为视觉方向参考，而不是复制任何品牌资产：目标是原创、高质量 3D/半写实数字教师，亲和、可信、自然，贴近中国小学老师气质，避免过幼稚卡通、恐怖谷、网红化或过度美颜。
- 设计阶段比较至少 2–3 种原创方案，并考虑手机端性能、加载速度、讲解状态表现能力和素材/声音许可。
- 首期可用原创头像/半身形象 + 轻量说话状态动画 + 普通话 TTS + 同步字幕；不强制实时视频或复杂口型。若做口型需同步音频。
- 不复制豆包、学而思、作业帮的具体角色、商标、独有界面、美术资产或声音。该视觉方向纳入 MATH-003、MATH-021 的验收要求，不新增任务数或权重。


## 2026-10-19 — 参考学而思/作业帮后的验收补漏
- 官方产品资料用于了解公开展示的 AI 老师伴学、个性化学习、学情诊断和交互答疑方向；仅参考抽象能力，不复制其品牌资产，也不将宣传内容当作效果证据。
- 本轮将当前题目内连续追问、上下文保持、测验防泄题、家长报告证据可信度、正式题目质量门禁、原图/OCR/确认题/AI 诊断分层留痕、故障恢复幂等性写入产品规格、验收和教学协议。
- 映射现有 MATH-010/014/015/016/019/021/022/024/025/028/030/031，不新增任务或权重。任务总数仍 32、总权重 100%、已验收 0/32、加权完成率 0%。
- 当前唯一工程任务仍为 MATH-002。不要再继续扩展竞品文档；下一步解决可复现的 Vue 3/TypeScript/Vite 项目级构建与测试验证，之后推进 MATH-003/004。CI 和 HEAD 必须重新查询。


## 2026-10-19 — MATH-002 基线测试 CI 化
- 新增 `apps/math-tutor/requirements-dev.txt`，固定 FastAPI 0.128.2、httpx 0.28.1、pytest 9.0.2。
- 更新 `.github/workflows/ci.yml`：配置 Python 3.13，安装数学辅导基线依赖，并运行 `python -m pytest -q apps/math-tutor/tests/test_environment_baseline.py`。
- 该改动刚提交时不能预先宣称 CI 通过；接手时需重新查询最新 HEAD 的 workflow。若 workflow 失败，检查日志并修复。
- MATH-002 仍 IN_PROGRESS：Vue/Vite 项目级 build/test、真实手机端/E2E 尚未验证。当前不标记任何软件任务验收通过。
- 竞品方向补漏已映射至现有任务；不要继续扩展竞品调研。下一步继续 MATH-002 的前端项目构建/测试与手机端路径验证。


## 2026-10-19 最新接手覆盖（优先于本文更早的状态快照）
- 当前分支：`feat/beishi-grade2-math-tutor`；PR #33 Open/Draft/未合并；最近核对的 HEAD 为 `666cc6cf7c63eb60ee67feae209476eea1079e05`。
- 该 HEAD 对应 CI run `39223512454` 在查询时为 queued，Netlify deploy-preview 为 pending；这是旧于本节交接提交的状态，接手时必须重查最终最新 HEAD 的 CI。
- 固定任务 32 项、权重总和 100%、已验收 0/32、加权完成率 0%；MATH-002 仍 IN_PROGRESS。不要因为 Vue/Vite 命令已加入 CI 就提前认定任务验收完成。
- 已新增 `tests/test_progress_integrity.py` 并将 CI 的 pytest 命令扩展为运行 `apps/math-tutor/tests` 全部测试。该测试校验固定分母/权重、只统计 ACCEPTED、验收证据存在及 dashboard 数字同步。
- 当前任务登记与看板必须一致；如 CI 因统计不一致失败，先修正数据/文档，不得绕过测试。
- 从头自研是当前方向。OpenMath 许可证不再是开发门禁；不得复制其源码。不得修改 `apps/ad-studio-desktop/`，不得自动合并 PR。
- 本轮范围：只补齐进度一致性自动检查和修正文档中遗留的许可证门禁冲突；未实现任何面向孩子的产品功能。下一唯一任务仍是完成 MATH-002 的技术栈基线验证，再按固定路线图推进 MATH-003/MATH-004。


## 2026-10-19 进度守卫已通过 CI（本节为已验证快照）
- 已验证 SHA：`dfc152a725dabb13b531ab4dd949921d170c5ae1`。
- PR #33 CI run `39223691429`：completed/success；Netlify deploy-preview：success。
- 该 CI 中 Vue 前端 build、前端测试、数学项目全部 Python 测试（含进度一致性守卫）和其余现有检查均通过。
- 新增的进度守卫会在 CI 中验证 32 个固定任务 ID、权重合计 100%、只把 ACCEPTED 计入完成率、验收证据非空，并要求看板数字与 JSON 登记一致。
- 当前软件验收仍为 0/32、加权完成率 0%；MATH-002 仍 IN_PROGRESS。该 CI 成功不是产品功能验收。
- 以上状态仅对应 SHA `dfc152a725dabb13b531ab4dd949921d170c5ae1`。接手时必须查询后来文档提交后的最新 HEAD 与 CI。


## 2026-10-19 MATH-002 状态更正（优先于旧的下一步描述）
- Vue 3 + TypeScript + Vite 项目构建与前端 helper 测试已在 GitHub Actions PR CI run `39223691429` 对应 SHA `dfc152a725dabb13b531ab4dd949921d170c5ae1` 成功。
- FastAPI/SQLite 基线测试与新增进度一致性测试也在该 CI 中通过。
- 因此，不要再把“Vite 未安装/前端 build-test 未运行”作为当前状态；它是前期历史记录。
- MATH-002 仍 IN_PROGRESS：真实手机浏览器/E2E、完整前后端集成及其余验收尚未验证。下一步应针对这些缺口给出可复现验证，不要重复做已经通过的 CI build/test。
- 以上 CI 结果仅对应 SHA `dfc152a725dabb13b531ab4dd949921d170c5ae1`；接手时仍要重新查询最新 HEAD 与 CI。


# 2026-10-19 最新权威接手状态（本节优先于文件中所有旧快照）
- 项目：`konggu888/ecommerce-agent` / `apps/math-tutor/`；分支 `feat/beishi-grade2-math-tutor`；PR #33 保持 Open/Draft/未合并。未经用户明确同意不得合并。
- 固定路线图：32 项、权重 100%；已验收 0/32、加权完成率 0%。当前 MATH-002 为 IN_PROGRESS。
- 自动进度机制：`scripts/update_progress.py --write` 根据任务状态和验收证据计算已验收数、加权完成率、状态分布，并同步 `MATH_TASK_REGISTER.json` 与看板；CI 运行 `--check`。更新任务状态后必须运行 `--write`；CI 会检查统计漂移。它不会自动验收任务。
- 已新增计算器单元测试，覆盖固定任务 ID/权重、状态变化时重新计算、无证据的 ACCEPTED 被拒绝、状态快照同步。
- MATH-002 已有的历史 CI 证据：SHA `dfc152a725dabb13b531ab4dd949921d170c5ae1` 的 CI run `39223691429` 成功，包含 Vue/Vite build、前端 helper tests 和 Python 基线测试。该 SHA 早于本轮新增 Playwright E2E 与进度计算器，不能用它证明新步骤通过。
- 本轮新增手机浏览器 E2E：`playwright.config.ts`、`e2e/mobile-home.spec.ts`，测试 390px 手机视口、首页关键入口、水平溢出和键盘操作；CI 安装 Chromium 并运行 `test:e2e`。必须重新查询最新 SHA 的 CI，确认这些步骤实际通过。
- README、STACK_BASELINE、看板和执行记录已修正旧说法：项目并非“完全没有前端”，而是只有早期首页 UI；后端业务 API、学习记录持久化、DeepSeek 实际调用、OCR、完整教学闭环仍未实现。
- 本轮未实现儿童学习功能，不得把进度计算器、文档或 CI 绿灯计入产品完成率。不得修改 `apps/ad-studio-desktop/`。
- 下一步唯一优先事项：查询本轮最新 HEAD/CI；若 Playwright 安装或测试失败，修复后重跑。若通过，检查前后端完整集成仍缺什么，并在不重复已通过检查的前提下继续 MATH-002。真实手机硬件验收仍需单独记录。


# 最新回合结束状态（2026-10-19；先读本节，再重查 GitHub）
- 本轮已实际修改代码：确定性进度计算器、进度计算单元测试、Playwright 手机 Chromium E2E、CI 对应步骤；并更新任务登记、看板、技术基线、README、变更记录和交接文件。
- 已验证的代码 SHA `79560df651e35d7148eecc30ff5109a6a2dcc75d` 的 PR CI run `39224952190` completed/success；Vue/Vite build、前端 helper tests、Chromium 安装、mobile E2E、Python 测试、进度快照 `--check` 和现有检查均通过。Netlify deploy preview 当时为 success。
- 之后提交了任务证据与文档更新（包括 `1b488951fba71a6ddc708eef693024bab29043c2`、`7bdafee1c29ec8e8ee9bba3497817dc0d7af9cf5`、`8043a5cb3f42433f6ba004be5e2f78d0d4f39fcd`），因此 CI 成功证据不等于当前最新 HEAD 的状态。接手时第一步查询最新 PR head、CI runs、job steps 和 deploy status。
- 进度计算命令：`python apps/math-tutor/scripts/update_progress.py --write`；CI 校验命令：`python apps/math-tutor/scripts/update_progress.py --check`。改变任务状态/证据后必须运行 `--write` 并提交同步的 JSON/看板；CI 会检查统计漂移。
- 固定范围 32 项/100%；已验收 0/32、加权完成率 0%；状态为 NOT_STARTED 31、IN_PROGRESS 1；MATH-002 仍 IN_PROGRESS。
- 已验证的移动端自动化是 Chromium 模拟 iPhone 13/390px 视口，不是物理手机验收。它只覆盖早期首页布局和交互，不代表数学学习功能已实现。
- MATH-002 仍剩余：前端到 FastAPI 业务 API 的真实集成、应用数据 SQLite 持久化路径，以及真实设备/人工验收。下一步优先核查这些缺口与 MATH-004 边界，避免重复已通过的 build/helper/mobile smoke tests。
- PR #33 保持 Open/Draft/未合并；未经用户明确许可不得合并。不得修改 `apps/ad-studio-desktop/`。本轮没有完成面向孩子的学习功能，不能增加软件完成率。


# MATH-002 最新技术验证补充（2026-10-19；接手仍须重查最新 SHA）
- 在已通过的前端/手机 E2E 基线之上，本轮新增实际 FastAPI + 文件 SQLite 验证：`backend/app.py` 提供 `create_app(database_path)` 与 `GET /health`；`backend/storage.py` 初始化文件型 SQLite schema 元数据；`tests/test_backend_api.py` 验证 HTTP 响应和重新初始化后持久化。
- 以上代码在 SHA `c622e4c67097bcecd5557e8dd3bd068bd788bf14` 的 PR CI run `39225650580` 中通过。该 run 还验证了 Vue/Vite build、前端 helper tests、Playwright mobile Chromium E2E、进度一致性检查和现有仓库测试；Netlify deploy preview 当时为 success。
- 随后新增了任务证据、STACK_BASELINE、看板和 CHANGELOG 文档提交，当前 HEAD 已变更；因此必须查询最新 HEAD 的 CI，不能把 SHA `c622e4c...` 的成功直接当成当前 HEAD 的结果。
- 当前软件任务仍为 32 项/100% 权重、已验收 0/32、加权完成率 0%；MATH-002 仍 IN_PROGRESS。进度计算器为 `python apps/math-tutor/scripts/update_progress.py --write`，CI 用 `--check`。
- 下一步唯一优先项：核查最新 HEAD CI；通过后，补齐前端到 FastAPI 的真实业务请求链路/集成验证。不要重复已经通过的 build、helper tests、移动浏览器首页 smoke test、FastAPI health 和 SQLite 技术基线。物理手机测试单独列为尚未执行。MATH-004 与 MATH-002 的边界需保持清楚，不能借基线测试宣称产品骨架完成。


# 2026-10-20 本轮最新接手状态（优先于前面所有旧快照）
## 本轮唯一任务：MATH-002 前端到 FastAPI 请求链路
本轮实际代码变更：
- 新增 `src/api.ts`：封装 `GET /api/health`，校验响应字段；非 2xx 和异常 JSON 结构都会返回错误，不会被当成连接成功。
- 新增 `src/api.test.ts`：覆盖成功响应、HTTP 503、响应结构错误三类情况。
- 修改 `vite.config.ts`：开发服务器把 `/api/*` 代理至 `http://127.0.0.1:8000`，并去掉 `/api` 前缀以匹配 FastAPI `/health`。
- 修改 `src/App.vue`：页面启动时请求 API，显示连接中/连接成功/服务不可用；失败时明确提示当前页面不会保存学习记录，不虚报后端已连接。
- 扩展 `e2e/mobile-home.spec.ts`：覆盖 API 成功状态和 HTTP 503 时的失败状态。E2E 通过 Playwright route mock 验证前端处理行为，不等于真实 FastAPI 进程已在浏览器端联通。
- 更新 `docs/MATH_TASK_REGISTER.json`、`docs/PROGRESS_DASHBOARD.md`、`docs/CHANGELOG.md` 记录变更及证据边界。

## 本轮提交与 CI
- 本轮代码/测试提交：`cdf22e31adc8daeddd149180f9eb5f4676fa9091`、`0bd0a788eeb5956b34fd289a75cfd1fd3d408a47`、`031574acd4a93be5bfd2b4879cb328b93ade86c3`、`ca81ebe3b712cedaa48a566ae184286cfd92010e`、`4a981292297ba3f50adadf7a7e2d2f8945fbbff5`。
- 任务登记与进度/变更文档提交：`7093661d53d5db1e345d8f4c65f8eec62ae283c6`、`793de86168008a2925bde75f65e740417fd6db3c`、`c22d24b478a271e3cca9cabfe2919141c37a56eb`。
- 本轮最后一次状态查询时，Push CI run `39323657522`（SHA `c22d24b478a271e3cca9cabfe2919141c37a56eb`）为 queued；PR CI run `39323655532`（SHA `793de86168008a2925bde75f65e740417fd6db3c`）为 queued；前面若干提交的 CI 处于 in_progress。故本轮新增代码和测试尚不能记为 CI 通过。接手必须查询最终 HEAD 和对应 run/job 结果。
- 由于本轮通过 GitHub 文件接口直接修改源码，没有在本地克隆工作区执行 npm/pytest；只记录 CI 为待验证，不声称本轮测试已通过。
- 之前已通过的 CI 仅对各自历史 SHA 生效，不可移作本轮新代码的验证证据。

## 当前进度与下一步
- 固定任务 32 项、总权重 100%；已验收 0/32、加权完成率 0%；状态分布仍为 NOT_STARTED 31、IN_PROGRESS 1。
- MATH-002 仍 IN_PROGRESS；本轮 API 接线不等于任务验收，也不增加软件完成率。
- 下一步：先查本轮最新 HEAD 的 Push/PR CI 和具体失败/成功 job。若通过，再做真正运行的前后端联调：启动 FastAPI 服务和 Vite dev server，验证浏览器发出的 `/api/health` 经代理到实际 FastAPI，而不是只靠 E2E mock。随后才处理学习数据 schema/业务持久化和真实设备验收。
- PR #33 继续 Open/Draft/未合并；未经用户明确许可不得合并。不得修改 `apps/ad-studio-desktop/`。
