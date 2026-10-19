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


## CI 可复现性补充（2026-10-19）
- 新增 `requirements-dev.txt`，固定 FastAPI、httpx 和 pytest 测试依赖版本。
- GitHub Actions CI 新增 Python 3.13 环境，安装上述依赖并执行 `python -m pytest -q apps/math-tutor/tests/test_environment_baseline.py`。
- 此改动让 FastAPI TestClient 和 SQLite smoke test 在仓库 CI 中可复现；提交后必须查看最新 CI 结果。它仍不验证 Vue/Vite 项目构建、完整后端应用、手机端 E2E 或产品功能。
- MATH-002 保持 IN_PROGRESS，除非前端构建/测试和手机端开发路径也有可复查证据，否则不得验收。


## 2026-10-19 后续更新：前端 build/test 已由 CI 验证
- 当前仓库已建立 `apps/math-tutor/package.json` 的 Vue 3 + TypeScript + Vite workspace。
- GitHub Actions PR CI run `39223691429`（SHA `dfc152a725dabb13b531ab4dd949921d170c5ae1`）中，`Build math-tutor Vue frontend` 与 `Test math-tutor frontend helpers` 均为 completed/success。
- 同一 CI 中数学项目 Python 测试（含进度一致性守卫）通过。
- 尚未完成：真实手机浏览器手工验收/移动端 E2E、完整前后端集成链路和产品功能验收。因此 MATH-002 仍为 IN_PROGRESS，不计入已验收任务。
- 本节证据只对应上述 SHA；新提交的 CI 状态必须重新查询。


## 2026-10-19 后续：手机视口浏览器自动化已加入（等待当前 CI）
- 新增 `@playwright/test` 与 `apps/math-tutor/playwright.config.ts`，固定使用 Chromium 的 iPhone 13 设备参数。
- 新增 `apps/math-tutor/e2e/mobile-home.spec.ts`，检查手机视口首页关键入口可见、页面无水平溢出、欢迎按钮可通过键盘触发，以及页面不伪造学习记录。
- GitHub Actions 已加入 Chromium 安装与 `test:e2e` 步骤。此为新增验证能力，不能在最新 SHA 的 CI 完成前写成“已通过”。
- 该 E2E 只验证当前前端基线的手机视口与基本交互，不代表真实手机硬件验收、前后端集成或数学辅导功能验收。MATH-002 继续 IN_PROGRESS。


## 2026-10-19 验证结果：手机视口 E2E 已通过
- GitHub Actions PR CI run `39224952190`，SHA `79560df651e35d7148eecc30ff5109a6a2dcc75d`：completed/success。
- `Build math-tutor Vue frontend`、`Test math-tutor frontend helpers`、`Install Chromium for math-tutor mobile E2E`、`Run math-tutor mobile browser E2E`、Python 基线测试与 `update_progress.py --check` 均通过。
- Playwright 检查了 390px 手机视口的首页内容、水平溢出、键盘交互及不伪造学习记录。
- 这证明自动化浏览器路径可运行，不等于真实手机硬件验收，也不验证前后端业务 API/学习数据持久化。MATH-002 继续 IN_PROGRESS。
- 此结果只对应 SHA `79560df651e35d7148eecc30ff5109a6a2dcc75d`；之后的文档提交会改变 HEAD，接手时必须重新查询最新 CI。


## 2026-10-19 验证结果：真实 FastAPI + 文件 SQLite 基线通过
- 新增 `backend/app.py`：可由 `create_app(database_path)` 创建 FastAPI 应用，`GET /health` 返回服务、SQLite 和 schema 版本信息。
- 新增 `backend/storage.py`：建立文件型 SQLite 数据库及 schema 元数据；支持重新连接后读取/写入验证。
- 新增 `tests/test_backend_api.py`：检查实际 FastAPI TestClient 请求与文件数据库跨初始化持久化。
- SHA `c622e4c67097bcecd5557e8dd3bd068bd788bf14` 的 GitHub Actions PR CI run `39225650580` completed/success；前端 build/helper tests、Playwright mobile Chromium E2E、Python 全部测试、进度快照检查及其他工作流检查均通过，Netlify deploy preview 当时为 success。
- 这只证明技术基线 API 与文件 SQLite 可运行；尚无学习者业务 schema、前端到后端的真实请求链路、学习记录功能或真实手机硬件验收。MATH-002 继续 IN_PROGRESS。
- 后续文档提交会产生新 SHA；接手时必须重新查询当前最新 HEAD 的 CI。
