# OpenMath 上游参考记录

- 上游：Galliard7/OpenMath
- 仓库：https://github.com/Galliard7/OpenMath
- 本次读取的 main commit：8b7ebaa86b886df2e7631f5760128507f65571b0
- 参考价值：结构化 YAML 课程、分层提示、常见误解映射、确定性答案校验、SQLite 学习进度、本地 Ollama 推理。
- 读取到的课程加载器路径：`backend/app/curriculum.py`
- 读取到的课程单元测试路径：`tests/test_curriculum.py`

## 许可核查阻塞
上游 README 显示 Apache 2.0 徽章，但在本次读取的 main 分支递归 Git tree 中未找到 `LICENSE` 文件；仓库元数据也未显示已识别的许可证。因此**不能仅凭徽章就断定可以复制、修改并再分发源码**。

在许可澄清之前：
1. 不把上游源码伪装成自己的代码。
2. 先开发自编中文课程内容、需求与验收规范。
3. 后续优先确认上游是否有可核实的正式许可证或作者许可；确认后再决定复制/fork 方案。
4. 保留上游归属和变更记录。

## 不把功能介绍当作验收结果
上游的公开 README 描述了离线教学、分层提示、题目验证和掌握度追踪，但本分支尚未运行其代码或测试。本文件仅记录源码审查起点。
