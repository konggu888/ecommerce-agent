# OpenMath 上游参考记录

- 上游：Galliard7/OpenMath
- 仓库：https://github.com/Galliard7/OpenMath
- 本次初步读取的 main commit：8b7ebaa86b886df2e7631f5760128507f65571b0（后续执行选型门禁时需重新核对当前 commit）
- 初步参考价值：结构化 YAML 课程、分层提示、常见误解映射、答案校验、SQLite 学习进度、本地 Ollama 推理。
- 初步读取路径：`backend/app/curriculum.py`、`tests/test_curriculum.py`。
- 当前状态：仅做过初步源码/仓库结构查看；没有在本分支运行上游代码或测试，不能把 README 描述当作验收证据。

## 许可证门禁核查记录（2026-10-19）

**结论：BLOCKED；目前没有足够清晰、可复查的正式许可证文本或作者授权证据，不得复制/改编/再分发上游代码。MATH-001 未验收。**

已检查的证据：
1. 上游仓库 `https://github.com/Galliard7/OpenMath` 的 README 在 `License` 章节声明 `Apache 2.0`，并有 Apache 2.0 徽章；这是上游作者的许可证声明，但不是许可证全文。
2. 通过 GitHub 内容接口检查 `main` 分支根目录的 `LICENSE`、`LICENSE.md`、`LICENSE.txt`、`COPYING`、`NOTICE`，均返回 404 / NOT_FOUND。
3. 本次上游 README 内容 blob SHA：`3590673738e755ae071c6ff2260a56387b79d6e6`。
4. 本次查询到的上游最新提交记录为 `e741351d09f6f7c96b14b7806600f2174836da6d`（2026-05-18）；后续接手仍需重新查询当前默认分支与 HEAD。
5. 上游 README 声明使用 Gemma 4/Ollama、本地推理；本项目计划使用服务端 DeepSeek。此差异属于适配评估，不是许可证结论。

因此，README 的 Apache 2.0 声明应保留为调查线索，但在没有许可证文本或作者明确确认之前，不将其视为本项目许可门禁已通过。下一步应在不复制上游代码的前提下，最多再评估两个候选并记录来源、许可文件、技术匹配度和维护/测试证据；不得无限扩展候选数量。

来源：
- 上游仓库/README：`https://github.com/Galliard7/OpenMath`
- 上游 README：`https://github.com/Galliard7/OpenMath/blob/main/README.md`
- 上游提交：`https://github.com/Galliard7/OpenMath/commit/e741351d09f6f7c96b14b7806600f2174836da6d`

许可不清楚时不复制源代码。可以继续维护本项目自编需求、规范和课程内容。

## 选型规则
按照 `docs/TECHNICAL_ARCHITECTURE.md` 与 `docs/IMPLEMENTATION_PLAN.md` 执行：OpenMath 是首个候选；若许可证或关键架构不合格，最多再评估两个候选，总候选最多三个。比较课程可编辑性、分步教学、错误诊断、掌握追踪、云端 API、手机界面、持久化、测试、维护状态与许可清晰度。不能无限搜索，也不能因为已建项目目录就强行复用。

## 不把功能介绍当作验收结果
在实际启动、测试、API 适配和手机流程完成前，所有相关能力都标记为待验证。选定课程 schema 后，再验证现有 YAML；当前 YAML 是自编草稿，不保证与 OpenMath loader 兼容。


## 2026-10-19 — 两个回退候选的第一轮证据评估

本轮按既定上限评估两个候选；OpenMath 仍计入总候选数，因此没有继续扩展搜索。

### 候选 A：onemorepereira/math-tutor（Number Ninja）
- 来源：`https://github.com/onemorepereira/math-tutor`
- 许可证据：根目录 `LICENSE` 存在，内容为 MIT License，版权行标注 Miguel Pereira 2025–2026；本次读取的 LICENSE blob SHA：`d4b77a37f58d8fe75ff571ff86319652355ece7a`。可作为明确许可候选继续评估，但仍需遵守 MIT 版权/许可声明要求，并逐项检查依赖和素材的独立许可。
- 技术证据：README 描述 Vue 3/TypeScript 手机适配、答题记录、分层提示和成绩回顾；`frontend/package.json` 是 Vue 3/Vite；`backend/package.json` 使用 AWS Lambda、DynamoDB、Bedrock；根 `package.json` 定义前后端工作区。
- 与本项目的差距：默认设计含 Cognito 注册、公共排行榜和 AWS Bedrock/DynamoDB，不符合“个人自用、首选 DeepSeek、避免多人/排行榜商业化复杂度”的目标；README 未显示首期试卷照片三状态、老师批改痕迹识别、三次提示上限、延迟复测和真实教学效果闭环已经实现。
- 初步判断：两个候选中更接近儿童数学练习网站的可参考脚手架，但不是可直接交付的完整底座。若后续选用，应删减注册/排行榜/多用户服务，改为私人访问、服务端 DeepSeek，并重新实现首期强制闭环。尚未 clone、启动或运行其测试，不能声称运行通过。

### 候选 B：AyushDixit-21/MathTalk
- 来源：`https://github.com/AyushDixit-21/MathTalk`
- 许可证据：根目录 `LICENSE` 存在，内容为 MIT License；本次读取的 LICENSE blob SHA：`4775913c2512cacb675c438e88adda8858cdf813`。依赖和第三方集成仍需分别核查。
- 技术证据：README 描述 React + TypeScript 前端、FastAPI 后端、SymPy 数学验证、学习者记忆和逐级辅助；README 明确将其定位为原型，并声明教育效果假设尚未通过正式用户研究验证。`frontend/package.json` 使用 React/Vite。
- 与本项目的差距：定位为语音优先/可访问性数学环境，不是北师大版二年级课程平台；没有已证实的目标年级课程、试卷照片三状态和家长所需的单元前后/延迟复测流程。当前已检查文件未找到根 `package.json` 或 `backend/package.json`，后端安装/测试命令还需进一步核实。
- 初步判断：可参考确定性数学校验与教学状态机思路，不建议作为本项目的主底座。尚未 clone、启动或运行其测试，不能声称运行通过。

### 当前结论与门禁
- 两个替代候选均有可复查的 MIT 根许可证文件；这解决了候选许可证文本的初步可见性，但不代表其所有依赖、模型或素材许可均已完成审查。
- 当前最有价值的下一步是对候选 A 做有边界的代码/测试/目录审查，确认它的实际可复用范围与改造成本；候选 B 不再扩展调查，除非候选 A 不可用。
- OpenMath 的 MATH-001 仍为 BLOCKED：README 虽声明 Apache 2.0，但未找到许可证全文/作者确认；不复制其代码。
- 本轮只完成候选桌面审查证据整理，未 clone/运行任何候选；不计产品任务完成，不增加软件进度。
