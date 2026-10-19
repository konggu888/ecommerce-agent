# 数学辅导项目进度看板

最后更新：2026-10-20
计划版本：2.2（自研实现、中国儿童体验、既定功能全部保留）
分支：feat/beishi-grade2-math-tutor
PR：#33（Draft，未合并）

## 项目目标
建立能诊断知识缺口、依据证据调整教学、逐步培养独立答题能力，并通过可比的单元/期中/期末测评验证学习变化的数学学习系统。产品交付进度与孩子学习效果分别统计。

## 本次计划重构
- 核心闭环为发现问题—验证原因—选择教学策略—无提示变式—延迟复测—策略调整。
- AI 诊断是可检验假设；证据不足标 unknown。
- 验证教学策略是否有效，连续失败时换策略或检查前置知识。
- 逐步培养独立性，但不机械拒绝合理求助。
- 掌握度需要独立、迁移、延迟和错误复现等多种证据。
- 保留原有 32 项任务和总权重 100%，不增加分母。

## 真实进度
- 任务总数：32。
- 已验收：1/32。
- 加权完成率：4%。
- 应用产品代码：早期 Vue 首页 UI 已通过真实 FastAPI 健康接口连接验证；完整学习流程、学生学习记录业务 API 与学习数据 schema/持久化尚未实现。
- 自研技术基线：IN_PROGRESS；FastAPI/SQLite smoke test、Vue/Vite build、前端 helper tests，以及浏览器经 Vite 代理访问真实 FastAPI 的集成 E2E 已在 CI 对 SHA `178c50a2a23345bf3ae4123fa153bdfe555014f2` 验证通过；真实物理手机验收和学习记录业务持久化仍未验证。
- 自动化验证：最新已核验代码 SHA `178c50a2a23345bf3ae4123fa153bdfe555014f2` 的 Push CI run `39324288870` 与 PR CI run `39324295556` 均成功；其中真实 FastAPI + Vite 浏览器联调、前端构建/测试、Python 基线和进度一致性检查通过。文档更新后会产生新 SHA，仍须重查最终 HEAD。
- DeepSeek 实际调用：未运行。
- 手机端实测：未运行。
- 教材目录映射：未验收，需核对孩子实际教材。
- 学习效果测量：未运行；目前没有真实提分证据。

## 指标必须分开
软件交付：仅按已验收任务权重统计；代码提交、文档完善和 CI 成功均不自动增加百分比。
学习效果：分别记录基线、单元结束平行测验、延迟复测、迁移题、无提示独立率、提示依赖、错误类型变化和学校考试结果。无数据时显示未测量，不能填 0 分或推断没有进步。
教学闭环：记录诊断假设、证据、所选策略、后续无提示表现、延迟结果和是否调整。连续失败但没有调整，视为闭环未通过。

## 最新 GitHub 状态（本轮文档修改前的核验快照，2026-10-19）
- PR #33：Open、Draft、未合并。
- 修改前 HEAD：`c8519a557bb4dabefad9ab74118c3fb05d929941`。
- 该 SHA 的 GitHub Actions `CI` run `39217632873`：completed / success。
- 该 SHA 的 combined status 返回 Netlify deploy-preview：success。
- 上述成功状态对应本轮文档修改前的 SHA；本轮提交会产生新 HEAD，必须重新查询新 SHA 的 CI/status，不能沿用旧结果。
- CI 与预览成功只证明对应自动化/部署检查结果，不代表应用功能、照片识别或教学效果已经验收。

## 下一步（2026-10-19 决策已更新）
- 当前唯一任务：MATH-002 自研技术栈与开发环境基线验证（Vue 3 + TypeScript + Vite、FastAPI、SQLite、自动化测试、手机端路径）。必须以实际 build/test 或明确可复查的环境验证结果为证据。
- OpenMath 缺少许可证全文，因此不复制其源码；该问题不再阻塞自研。
- MATH-003 为中国儿童视觉/交互系统；MATH-004 为独立应用骨架与前后端 build/test/API/持久化 smoke test。
- 已将孩子自主选择单元、任意已学单元组合、累计复习、混合比例、老师作业与自主练习分离、暂停/跳过/返回和数学正确性保障纳入产品规格与验收；仍需后续代码和测试，不能计为已交付。
- 当前任务验收 0/32、加权完成率 0%。
## v2.1 用户强制目标及状态
以下能力已纳入首期必须实现范围，当前全部为**未实现/未验收**，不能因文档已写入提高进度：
- 每日时间上限、按证据排序、稳定掌握后减少练习。
- 试卷照片上传与空白/已作答未批改/老师已批改三种状态分流。
- 识别置信度与人工确认、评分来源隔离、图片题共用教学闭环。
- 无效教学策略的真实切换或前置知识回查。
- 学习时间、独立作答、迁移、延迟复测与学校成绩分别报告。
本轮更新的是规格、范围映射和验收门槛，不是应用实现。已验收仍为 0/32，加权完成率仍为 0%。必须由后续代码、自动化测试、手机端端到端步骤和学习数据分别验证。

## AI 连续性与执行控制文件
- 接手摘要：apps/math-tutor/SESSION_HANDOFF.md
- 执行协议：docs/AD_MATH_EXECUTION_CONTROL.md
- 固定路线图：docs/IMPLEMENTATION_PLAN.md
- 机器可读任务登记：docs/MATH_TASK_REGISTER.json
- 验收标准：docs/ACCEPTANCE.md
- 变更历史：docs/CHANGELOG.md

## 连续性文件补齐状态
- 已新增执行控制协议和机器可读任务登记表。
- 任务登记表包含 MATH-001–MATH-032 共 32 项，权重总计 100%，当前全部 NOT_STARTED。
- 当前验收仍为 0/32、加权完成率 0%；新增文档不计入产品进度。
- 本轮文档提交会改变 HEAD；因此本节不把旧 SHA 冒充最新状态。下一个窗口必须重新查询最新 PR #33 的 head SHA、CI/status、workflow runs 和部署检查。若查询没有状态项，标记 NO_DATA/未确认。



## 2026-10-19 候选评估补充
- 已按固定上限评估两个替代候选：`onemorepereira/math-tutor` 与 `AyushDixit-21/MathTalk`，合计候选（含 OpenMath）不超过 3。
- 两个候选均发现根目录 MIT 许可证全文；候选 A 的儿童数学练习界面更接近目标，但 AWS Bedrock/Cognito/排行榜与私人 DeepSeek 使用目标不匹配；候选 B 更适合参考确定性数学验证/教学状态机，但定位和课程不匹配。
- 尚未 clone、安装、运行或测试候选；这轮只做仓库文件级初筛。选型仍未完成，任务验收仍 0/32、加权完成率 0%。


## 2026-10-19 最新提交后复查（元数据更新前快照）
- 五份候选评估/交接文档已提交后，PR #33 HEAD 为 `59226c26e1997361a73dad0051308a1703ba1cc2`，PR 仍 Open/Draft/未合并。
- 该 SHA 的 GitHub Actions CI run `39218680024` 为 queued/running；combined status 尚无状态项。当前提交的 CI 不能标为成功。
- 该 SHA 的 JSON 任务登记已重新解析通过：32 项、权重总计 100%、已验收 0 项，MATH-001 仍 BLOCKED。候选评估不计入软件完成率。
- 这是元数据更新前的复查快照；本次记录本身会产生新 HEAD，接手时仍须重新查询最新 SHA 和 CI。


## 候选 A 静态代码审查结果
- 已读取候选 A 的 `GameView.vue`、`router/index.ts`、`createGameSession.ts`、`submitAnswer.ts`、`requestHint.ts` 和两个测试文件。
- 已确认其采用游戏积分/单次答题、Cognito 登录、AWS Bedrock 与 DynamoDB；与私人 DeepSeek、长期重做队列和首期试卷照片闭环存在实质差距。
- 发现部分单元测试文件，但未执行；执行环境浅克隆失败，原因是无法解析 github.com。因此基线运行/测试状态是 BLOCKED/NOT_RUN，不是失败也不是成功。
- 选型未完成，已验收 0/32、加权完成率 0%。下一步只做候选 A 可运行基线验证，未验证前不开始大规模改编。


## 2026-10-19 自研方向调整
- 已按用户决定改为从头自研；不再以 OpenMath 或其他上游项目的许可证/运行作为开发门禁。
- 参考项目用于全网设计与技术借鉴，不复制未经核实许可的源码。
- MATH-001–MATH-004 调整为参考调研、技术栈基线、儿童设计系统、自研骨架；仍保持 32 项/100%。
- 首期所有既定能力保持强制范围，不得因框架限制删除或降级。
- 软件验收仍为 0/32、加权完成率 0%；本轮仅调整方向与计划，没有新增已验收软件功能。


## MATH-002 实测补充（2026-10-19）
- 新增 `tests/test_environment_baseline.py`，当前执行容器 `pytest -q`：2 passed；覆盖 FastAPI TestClient HTTP 往返和 SQLite 最小读写。
- 环境版本：Node v22.16.0、npm 10.9.2、TypeScript 5.8.3、Python 3.13.5、FastAPI 0.128.2、Starlette 0.50.0、pytest 9.0.2、SQLite 3.46.1。
- Vite 未安装，Vue/Vite 项目级 build/test 未运行；GitHub clone 因当前容器 DNS 无法解析 github.com 而受阻；手机端 E2E 未运行。
- MATH-002 状态为 IN_PROGRESS，不是 ACCEPTED。软件验收仍 0/32、加权完成率 0%。详情见 `docs/STACK_BASELINE.md`。


## 2026-10-19 用户体验范围补充：AI 老师声音、黑板与积分奖励
- 产品规格和验收新增普通话讲解音频、同步字幕、暂停/重播/音量/静音、温和鼓励、AI 老师讲解状态和可操作数学黑板。
- 新增家长自定义奖励目录/积分门槛、可用余额、兑换确认与扣分、完整积分流水及历史兑换快照；兑换后扣余额但不删除历史。
- 这些需求映射到 MATH-003/MATH-009/MATH-021/MATH-023/MATH-025/MATH-028，不增加 32 项任务分母或 100% 权重。
- 当前仍为需求/验收更新，未实现语音、老师动画、黑板、积分账户或兑换功能；不能计入软件完成率。已验收仍 0/32、加权完成率 0%。


## 2026-10-19 — 学而思/作业帮方向参考后的覆盖审计
参考范围来自两家产品公开介绍中可见的个性化学习、AI 老师伴学、学情诊断和交互答疑方向；不把厂商宣传当作效果证明，也不复制其专有资产。
- 已由现有任务覆盖：知识点/课程映射（MATH-006/007/013/014）、有证据的诊断与策略切换（MATH-018/019）、掌握/迁移/延迟复测（MATH-020/029/030/031）、AI 老师与语音黑板（MATH-003/021）、家长报告（MATH-022）、题目校验（MATH-015/016/025）、失败恢复（MATH-024）。
- 本轮补齐此前验收表达不足的行为：当前题目内连续追问与上下文保持；测验模式下防止语音/黑板/追问泄题；家长报告展示样本数、题组版本和不确定性；正式题目的质量发布门禁；原图、OCR 候选、用户确认内容、AI 诊断分别留痕；失败恢复的幂等性。
- 已把细项写入 PRODUCT_SPEC.md、ACCEPTANCE.md、AI_TUTORING_PROTOCOL.md，并映射回现有 MATH-010/014/015/016/019/021/022/024/025/028/030/031。任务总数仍 32，权重总和仍 100%；不新增任务 ID，不把文档审计算作软件完成。
- 本轮未实现应用功能。MATH-002 仍 IN_PROGRESS：FastAPI/SQLite smoke tests 2 passed；Vue/Vite 项目级 build/test 与手机端 E2E 尚未运行。


## 2026-10-19 — MATH-002 基线测试接入 CI
- 已将 FastAPI/SQLite 基线 smoke test 接入 GitHub Actions：Python 3.13 + requirements-dev.txt + pytest。
- 最新提交后的 CI 尚待重新查询，不能提前记为通过。
- Vue/Vite 项目级 build/test 和手机端 E2E 仍未运行；MATH-002 继续 IN_PROGRESS，软件验收仍 0/32、加权完成率 0%。


## 2026-10-19 — 自动进度一致性检查接入（状态快照）
- 最新已核对的代码 SHA `666cc6cf7c63eb60ee67feae209476eea1079e05` 对应 CI run `39223512454` 当时处于 queued；Netlify deploy-preview 为 pending。该状态不代表后续文档提交的 CI 已通过。
- 新增 `tests/test_progress_integrity.py`，在 CI 中校验固定任务 ID 为 MATH-001–MATH-032、权重合计 100%、仅 ACCEPTED 计入加权完成率、已验收证据非空，以及看板数字与机器登记一致。
- CI 现在运行 `apps/math-tutor/tests` 全部测试，而非只运行环境 smoke test。若任务分母、权重、验收证据或看板统计漂移，CI 应失败并要求先修复。
- 当前登记仍为 32 项、权重 100%、已验收 0/32、加权完成率 0%；MATH-002 为 IN_PROGRESS。Vue/Vite 构建与前端测试已纳入 CI 命令，但本轮最新 CI 结果须重新查询。
- 该机制会自动发现登记表/看板不一致，但不会替代人工验收或自行修改任务状态。


## 2026-10-19 — 进度守卫 CI 验证结果
- 对 SHA `dfc152a725dabb13b531ab4dd949921d170c5ae1` 的 GitHub Actions PR CI run `39223691429` 已 completed/success；Netlify deploy-preview status 为 success。
- 该 CI 实际通过了 Vue 前端 build、前端测试、`apps/math-tutor/tests` 全部 Python 测试（包含新进度一致性守卫）及工作流中的其他检查。
- 此证据只对应上述 SHA；后续文档提交产生的新 SHA 仍需重新查询 CI。
- 软件任务仍为 32 项、100% 权重、已验收 0/32、加权完成率 0%；MATH-002 继续 IN_PROGRESS。CI 通过不等于 MATH-002 已验收，也不代表产品功能完成。


## 进度计算器（2026-10-19）
- 计算脚本：`apps/math-tutor/scripts/update_progress.py`。
- 更新任务状态或验收证据后运行 `python apps/math-tutor/scripts/update_progress.py --write`，脚本按固定任务表重新计算验收数、加权完成率和状态分布，并同步本看板及 JSON 快照。
- CI 运行 `python apps/math-tutor/scripts/update_progress.py --check`；若 JSON 快照或看板数字过期，检查失败。
- 该脚本不自动将任务标为 ACCEPTED；只有先核验代码/测试/人工证据并更新任务状态，才会重新计算。进度计算时间与 GitHub CI/HEAD 快照是不同字段，CI 状态仍须按最新提交查询。
- 当前计算结果：32 项、权重 100%、已验收 0/32、加权完成率 0%；状态分布 NOT_STARTED 31、IN_PROGRESS 1。


## 2026-10-19 MATH-002 继续推进
- 新增确定性进度计算器：`python apps/math-tutor/scripts/update_progress.py --write` 重新计算任务状态、已验收数、权重完成率并同步 JSON 快照与本看板；CI 使用 `--check` 检查是否漂移。
- 新增计算器单元测试：验证固定任务数/权重、状态变更后的加权计算、无验收证据禁止标记 ACCEPTED，以及快照状态分布。
- 新增 Playwright mobile Chromium E2E：首页入口、390px 手机视口无水平溢出、键盘触发和“不伪造学习记录”检查。新 CI 结果未完成前，不记录为通过。
- 当前真实进度仍为 32 项/100%，验收 0/32、加权完成率 0%；MATH-002 IN_PROGRESS。CI/文档提交不会增加软件完成率。


## 最新已验证工程检查（2026-10-19；非当前 HEAD 保证）
- SHA `79560df651e35d7148eecc30ff5109a6a2dcc75d` 的 PR CI run `39224952190` 为 completed/success；Netlify deploy preview 查询结果为 success。
- 已通过：Vue/Vite build、前端 helper tests、Playwright mobile Chromium E2E、FastAPI/SQLite smoke tests、进度计算器一致性检查及工作流其他检查。
- 该 SHA 之后又提交了验收证据和文档更新，故以上成功状态不代表最新 HEAD 已通过 CI。接手时必须重新查询最新 SHA 对应的 Push/PR CI 与部署状态。
- 软件验收仍 0/32、加权完成率 0%；MATH-002 仍 IN_PROGRESS，因为业务 API、持久化学习数据和真实设备验收未完成。


## 2026-10-19 MATH-002 实际技术实现补充
- 已新增 `backend/app.py` 的 FastAPI `/health` 入口，以及 `backend/storage.py` 文件型 SQLite schema 元数据读写。
- 新增 `tests/test_backend_api.py`，验证真实 FastAPI TestClient HTTP 请求、数据库文件创建和重新初始化后的持久化。
- SHA `c622e4c67097bcecd5557e8dd3bd068bd788bf14` 的 PR CI run `39225650580` 已 completed/success；Vue/Vite build、前端 helper tests、Playwright mobile E2E、Python 全部测试、进度计算器检查均通过，Netlify preview 当时为 success。
- 以上仅为技术基线，不代表学习数据 schema、前后端业务 API、DeepSeek、OCR 或教学闭环已实现。最新文档提交后的 SHA 必须重新检查 CI。


## 2026-10-20 最新工程状态补充（前端 API 链路实现后）
- 已在 Vue 首页接入真实 `GET /api/health` 请求；开发服务器配置 `/api` → FastAPI `127.0.0.1:8000` 代理。
- UI 会分别呈现连接中、连接成功和服务不可用；失败时明确说明当前页面不会保存学习记录。
- 新增 API 客户端测试（成功、HTTP 失败、格式异常）和移动端 E2E 的 API 成功/失败 UI 检查。
- 此次代码刚提交，当前 SHA 对应的 CI 必须重新查询；新增测试尚不能标为通过。
- 软件进度保持 32 项、已验收 0/32、加权完成率 0%；MATH-002 仍 IN_PROGRESS。剩余缺口：真实前后端联调（浏览器请求经代理访问实际 FastAPI 服务）、学习数据业务 schema/持久化，以及物理手机/人工验收。

## 2026-10-20 最新联调实现（CI 待验证）
- Playwright 现会启动真实 FastAPI/Uvicorn 与 Vite 服务；首页测试通过浏览器真实请求 `/api/health` 检查 Vite 代理与 FastAPI 响应契约。
- CI 已调整为先安装 Python 后端依赖，再运行 mobile Chromium E2E；Uvicorn 为固定测试依赖。
- 这一变更仍未改变任务状态：MATH-002 IN_PROGRESS，固定 32 项/100%，已验收 0/32、加权完成率 0%。必须等最新 SHA 的 Push/PR CI 成功后，才可将真实联调自动化视为已验证；仍未覆盖学习记录业务 schema/持久化和物理设备验收。


## 2026-10-20 最新实测补充
- 已把真实前后端联调纳入 Playwright：CI 启动 FastAPI/Uvicorn 与 Vite 两个实际服务进程；首页 E2E 不 mock 成功响应，而是浏览器真实执行 `fetch('/api/health')`，通过 Vite proxy 访问 FastAPI 并检查 HTTP 200 和 SQLite/schema 元数据。
- 已验证 SHA：`178c50a2a23345bf3ae4123fa153bdfe555014f2`；Push CI `39324288870` 和 PR CI `39324295556` 均 completed/success。该 SHA 的真实服务 E2E、Python 基线、进度 `--check`、前端 build/helper tests 与仓库既有检查均通过。
- 最新验收边界：这证明健康接口链路在 CI 环境真实可用，不代表学习记录业务 API/schema 已实现，也不代表真实物理手机验收通过。
- 固定计划 32 项/100%；已验收 0/32、加权完成率 0%；MATH-002 仍 IN_PROGRESS。CI 通过不直接增加软件完成百分比。


## 2026-10-20 最新实现：SQLite 版本化迁移基线（已由 CI 验证）
- `backend/storage.py` 已加入 `schema_migrations` 迁移历史表与版本注册表，初始化时应用尚未记录的基础设施迁移。
- 测试覆盖重复初始化、历史版本记录、现有元数据保留，以及旧版 `app_meta` 数据库在无迁移历史时的兼容接管。
- SHA `99d5405007dfac6eae86ff90be8b17e36931a3d2` 的 Push CI `39325112034`、PR CI `39325121132` 均 completed/success；真实 FastAPI/Vite E2E、Python tests、前端 build/helper tests、进度 `--check` 和现有仓库检查通过。
- 此项属于技术迁移底座；没有提前实现或宣称 MATH-007 课程/题目数据契约、MATH-023 学习记录业务持久化。
- 固定任务 32 项/100%；已验收 0/32、加权完成率 0%；MATH-002 仍 IN_PROGRESS，物理手机/人工验收仍未执行。

## 2026-10-20 — SQLite migration future-version guard (verification pending)
- Migration runner now rejects unknown recorded migration versions rather than proceeding against a potentially newer schema.
- Regression test added for a database carrying unsupported migration version 99.
- This is MATH-002 technical-baseline hardening only; CI for the latest HEAD must be checked before claiming the test passed.
- Progress remains: fixed 32 tasks, total weight 100%, accepted 0/32, weighted completion 0%; MATH-002 IN_PROGRESS. No task denominator or weight changed.

## 2026-10-20 最新状态复核与 MATH-001 验收
- 最新核验 HEAD（文档更新前）：`3eda480f8061b0547c146c96007b9222ff8bd672`；PR #33 Open/Draft/未合并。
- 该 SHA 的 Push CI `39326945702` 与 PR CI `39326955062` 均 completed / success。新增 SQLite 未知未来迁移版本拒绝机制及 version 99 回归测试已包含在该 SHA 的 CI。
- MATH-001「全网参考调研与第三方许可风险登记」已验收：限额比较三个候选并记录当前上游 SHA、许可证状态和差异；OpenMath 缺少 LICENSE 正文，明确排除源码复用；另外两个候选根 LICENSE 为 MIT，但仅作为静态参考，未复制代码。
- MATH-002 仍 IN_PROGRESS：技术基线、真实 FastAPI/Vite 联调和迁移保护测试已由 CI 验证；真实物理手机/人工验收仍未执行。不得把模拟视口当作实体手机验收。
- 当前固定任务 32 项、总权重 100%；已验收 1/32；加权完成率 4%；状态分布 ACCEPTED 1、IN_PROGRESS 1、NOT_STARTED 30。
- 下一步唯一任务：完成 MATH-002 的实体手机/人工验收。自动化代码检查已通过，不重复已通过的测试；这一步需要真实手机浏览器实际打开当前部署/本地可访问页面并留存结果。若暂时无法接入实体手机，任务保持 IN_PROGRESS，不虚报验收。


## 2026-10-20 自托管部署准备进展（不增加验收百分比）
- 新增 Docker Compose 自托管骨架：Nginx 前端、内部 FastAPI 服务、SQLite 持久化命名卷；默认仅监听宿主机 127.0.0.1。
- CI 已加入 backend/frontend Docker image build 步骤，等待最新 SHA 实际结果。
- 这属于部署准备，不等于真实服务器部署或生产验收；公网发布被认证/授权、HTTPS、备份恢复与安全测试门槛阻止。
- 固定路线图仍为 32 项；除非任务登记与验收证据同步通过进度守卫，不手动增加完成百分比。


## 2026-10-20：部署地址与实体手机验收阻塞
- 当前没有已确认的、用户无需受邀登录即可访问的测试 URL。Netlify deploy-preview 虽曾返回 success，但用户遇到受邀账号登录墙，因此不可作为交付地址。
- 已新增 `docs/DEPLOYMENT_AND_MOBILE_ACCEPTANCE.md`，审计旧文档中的 Netlify 记录并定义真实手机验收证据。
- 当前仓库内未发现要求必须在 Netlify 开发的活动指令；`pages.yml` 面向独立 `apps/web/` 仪表板。旧 SHA 的 Netlify 状态是历史记录。
- MATH-002 保持 IN_PROGRESS；缺少可访问 URL 与实体手机人工验收证据。不得因 CI 成功提高验收进度。