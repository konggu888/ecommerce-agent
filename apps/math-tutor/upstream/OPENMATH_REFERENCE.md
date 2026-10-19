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
