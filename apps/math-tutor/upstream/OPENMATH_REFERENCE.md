# OpenMath 上游参考记录

- 上游：Galliard7/OpenMath
- 仓库：https://github.com/Galliard7/OpenMath
- 本次初步读取的 main commit：8b7ebaa86b886df2e7631f5760128507f65571b0（后续执行选型门禁时需重新核对当前 commit）
- 初步参考价值：结构化 YAML 课程、分层提示、常见误解映射、答案校验、SQLite 学习进度、本地 Ollama 推理。
- 初步读取路径：`backend/app/curriculum.py`、`tests/test_curriculum.py`。
- 当前状态：仅做过初步源码/仓库结构查看；没有在本分支运行上游代码或测试，不能把 README 描述当作验收证据。

## 许可核查阻塞
上游 README 显示 Apache 2.0 徽章，但此前检查的 main 分支递归 Git tree 未找到 `LICENSE` 文件；仓库元数据也未显示已识别许可证。因此不能仅凭徽章认定可以复制、修改和再分发源代码。

选型门禁执行时必须重新检查：
1. 当前默认分支和 commit SHA；
2. 仓库 LICENSE 文件、GitHub license metadata、源文件头和 README 许可说明；
3. 如仍不一致，查找作者正式许可或上游明确的授权说明；
4. 保存 URL/commit/文件路径/检查日期与结论。
许可不清楚时不复制源代码。可以继续维护本项目自编需求、规范和课程内容。

## 选型规则
按照 `docs/TECHNICAL_ARCHITECTURE.md` 与 `docs/IMPLEMENTATION_PLAN.md` 执行：OpenMath 是首个候选；若许可证或关键架构不合格，最多再评估两个候选，总候选最多三个。比较课程可编辑性、分步教学、错误诊断、掌握追踪、云端 API、手机界面、持久化、测试、维护状态与许可清晰度。不能无限搜索，也不能因为已建项目目录就强行复用。

## 不把功能介绍当作验收结果
在实际启动、测试、API 适配和手机流程完成前，所有相关能力都标记为待验证。选定课程 schema 后，再验证现有 YAML；当前 YAML 是自编草稿，不保证与 OpenMath loader 兼容。
