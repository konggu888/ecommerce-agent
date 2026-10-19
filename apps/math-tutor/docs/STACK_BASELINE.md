# MATH-002 自研技术栈与环境基线记录

日期：2026-10-19  
状态：IN_PROGRESS，未验收  
适用范围：只验证开发环境基础能力，不代表数学辅导产品功能已实现。

## 已执行的环境检查

| 检查项 | 实测结果 | 结论 |
|---|---|---|
| Node.js | v22.16.0 | 可用 |
| npm | 10.9.2 | 可用 |
| TypeScript 编译器 | 5.8.3（全局安装） | 编译器可用；尚未验证项目内依赖安装 |
| Python | 3.13.5 | 可用 |
| pip | 25.1.1 | 可用 |
| FastAPI | 0.128.2 | 可导入 |
| Starlette | 0.50.0 | 可导入 |
| pytest | 9.0.2 | 可用 |
| SQLite | 3.46.1 | 可用 |
| FastAPI TestClient smoke test | HTTP 200，返回 `{"ok": true}` | 通过 |
| SQLite 写入/读取 smoke test | 成功读回 `ok` | 通过 |
| 可复现测试文件 | `tests/test_environment_baseline.py` | 2 passed（本地执行） |
| Vite | 未安装（`vite: command not found`） | 未验证 |
| Vue 3 + Vite 项目 build/test | 未执行 | 未验证 |
| GitHub 仓库本地 clone | DNS 无法解析 `github.com` | 环境受限，非项目失败 |
| 手机浏览器 / E2E | 未执行 | 未验证 |

## 测试命令与结果

在当前执行容器创建的临时基线测试中运行：

```text
pytest -q
2 passed in 0.24s
```

已检查版本：

```text
node v22.16.0
npm 10.9.2
tsc Version 5.8.3
Python 3.13.5
SQLite 3.46.1
FastAPI 0.128.2
Starlette 0.50.0
pytest 9.0.2
```

测试文件仅验证 FastAPI TestClient 的最小 HTTP 往返和 SQLite 的最小读写；它们不是产品 API、产品数据库 schema 或学习流程测试。

## 阻塞与下一步

- 当前执行容器无法解析 GitHub，且 Vite 不在环境中；因此没有把临时测试冒充成 Vue/Vite 项目 build。
- 仍需验证项目级 Vue 3 + TypeScript + Vite 依赖安装、build/test、FastAPI/SQLite 项目配置、手机视口及浏览器路径。
- 不得因为 Python smoke test 通过就把 MATH-002 标为 ACCEPTED；当前只能标记 IN_PROGRESS。
- MATH-002 未验收前，软件加权完成率不变；当前 0/32、0%。
