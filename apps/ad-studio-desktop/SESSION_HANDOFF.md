# SESSION_HANDOFF.md — 桌面项目跨会话接手入口

> **新会话必须先读本文件，再读 `docs/AD_STUDIO_AI_HANDOFF.md`、`PROJECT_LOGIC.md` 和 `HELP.md`。** 本文件记录当前工作现场，不代表功能已验收。

## 当前仓库状态
- 仓库：`konggu888/ecommerce-agent`
- 项目：`apps/ad-studio-desktop`（本地 Python/Tkinter 桌面程序，不是 Web 应用）
- 工作分支：`feat/product-drama-visual-review`
- 最近一次完整 CI 验证通过的基准 SHA：`443f713cd3721eab528eb9bb17faf599d55ef3ce`（当前分支若有新提交，必须重新查询并验证最新 SHA）。
- PR：[#31](https://github.com/konggu888/ecommerce-agent/pull/31)，保持 open、未合并；没有用户明确许可不得合并。
- `443f713cd3721eab528eb9bb17faf599d55ef3ce` 的完整 CI 已成功：前端语法、桌面 Python 语法、桌面单测、TypeScript 检查、引擎测试和风险控制器测试均通过；同一 SHA 的 docs-sync 也成功。已将 `.github/workflows/ci.yml` 的 push 触发范围改为所有分支。任何后续提交都必须按最新 SHA 重新核实，不能把此基准结果直接套用到新 SHA。

## 最近完成
1. 商品短剧支持人工视觉核验，证据绑定具体生成图片/视频文件。
2. 支持视觉模型对照商品参考图与生成图片/视频抽帧；AI 未发现明确问题时也只进入待人工复核，不自动批准。
3. 商品短剧支持只修复所选镜头：用户写明修正要求、先确认费用；保留旧版本/旧视频/核验历史，新版本重置为 `not_checked`。
4. A36：从上次视觉比对摘要与问题列表预填可编辑修正草稿；费用必须是有限非负数，旧版本号必须有效。
5. A37：修正草稿使用真实换行；有回归断言。
6. 已同步 HELP、PROJECT_LOGIC、完整验收计划/SOP、AI handoff 和未来功能备忘；文档同步检查通过。

## 本轮必须继续做的事
1. 先重新读取 GitHub 当前 branch HEAD 和 PR #31，不要假设 HEAD 未变化。
2. 查看当前 HEAD 的 GitHub Checks/Actions；确认完整 CI 是否运行。若没有运行，查明触发原因并通过受支持方式让完整 CI 对当前提交执行；不能用旧 SHA 的 CI 冒充当前结果。
3. 审查并实际运行 `python3 -m unittest discover -s apps/ad-studio-desktop -p 'test_*.py'`、`python3 -m compileall -q apps/ad-studio-desktop/ad_studio`（若当前执行环境可访问仓库）；否则明确说明未运行，不要声称通过。
4. 继续核对 AI 视觉比对异常处理、单镜头重生成的版本映射/保存/成本记账，以及失败后恢复；只处理问题镜头，不重生成整部短剧。
5. 每次改代码，同一提交同步 HELP.md、PROJECT_LOGIC.md、验收计划、验收 SOP、接手文件和未来功能备忘，并增加回归测试。
6. PR 保持 open/unmerged。Windows 真机、真实视频 Provider/真实扣款、剪映现场验收仍按用户要求暂缓。

## 不得误报的边界
- 文档同步通过 ≠ 全量 CI 通过。
- 单元测试未执行 ≠ 测试通过。
- AI 视觉比对不是商品真实性认证；最终需人工核验。
- 当前实现不是已经验收的商业成片流程；真实机器/Provider 验收仍待后续。


## A39：CI 触发范围
CI 的 push 触发器现覆盖所有分支；每次提交后仍须查询当前 SHA 的 checks，等待完整 `typecheck-and-test` 工作流结束。此项改动本身的完整 CI 结果待当前提交的工作流返回。


## A40：已解决的 CI 路径失败
完整 CI 曾因 `test_ai_handoff.py` 的仓库根目录相对路径错误失败；现已修复为 `ROOT / "docs" / ...` 和 `ROOT / "apps" / "ad-studio-desktop" / ...`，并在 SHA `443f713cd3721eab528eb9bb17faf599d55ef3ce` 上完整 CI 成功。


## A41：已解决的文案断言
路径修复后曾剩下一个断言短语与文档不一致；已将测试改为匹配实际文案“不要把 docs-sync”，并在 SHA `443f713cd3721eab528eb9bb17faf599d55ef3ce` 上完整 CI 成功。


## A42：最新完整 CI 结果
完整 CI `38120824822` 在基准 SHA `443f713cd3721eab528eb9bb17faf599d55ef3ce` 结论为 success；docs-sync `38120824802` 也为 success。该结果覆盖：前端语法检查、桌面 Python 语法检查、桌面单元测试、TypeScript 类型检查、引擎测试和风险控制器测试。若当前 HEAD 与此 SHA 不同，必须重新查询当前 HEAD 的结果。

# SESSION_HANDOFF.md — 桌面项目跨会话接手入口

> **新会话必须先读本文件，再读 `docs/AD_STUDIO_AI_HANDOFF.md`、`PROJECT_LOGIC.md` 和 `HELP.md`。** 本文件记录当前工作现场，不代表功能已验收。

## 当前仓库状态
- 仓库：`konggu888/ecommerce-agent`
- 项目：`apps/ad-studio-desktop`（本地 Python/Tkinter 桌面程序，不是 Web 应用）
- 工作分支：`feat/product-drama-visual-review`
- 最近一次完整 CI 验证通过的基准 SHA：`443f713cd3721eab528eb9bb17faf599d55ef3ce`（当前分支若有新提交，必须重新查询并验证最新 SHA）。
- PR：[#31](https://github.com/konggu888/ecommerce-agent/pull/31)，保持 open、未合并；没有用户明确许可不得合并。
- `443f713cd3721eab528eb9bb17faf599d55ef3ce` 的完整 CI 已成功：前端语法、桌面 Python 语法、桌面单测、TypeScript 检查、引擎测试和风险控制器测试均通过；同一 SHA 的 docs-sync 也成功。已将 `.github/workflows/ci.yml` 的 push 触发范围改为所有分支。任何后续提交都必须按最新 SHA 重新核实，不能把此基准结果直接套用到新 SHA。

## 最近完成
1. 商品短剧支持人工视觉核验，证据绑定具体生成图片/视频文件。
2. 支持视觉模型对照商品参考图与生成图片/视频抽帧；AI 未发现明确问题时也只进入待人工复核，不自动批准。
3. 商品短剧支持只修复所选镜头：用户写明修正要求、先确认费用；保留旧版本/旧视频/核验历史，新版本重置为 `not_checked`。
4. A36：从上次视觉比对摘要与问题列表预填可编辑修正草稿；费用必须是有限非负数，旧版本号必须有效。
5. A37：修正草稿使用真实换行；有回归断言。
6. 已同步 HELP、PROJECT_LOGIC、完整验收计划/SOP、AI handoff 和未来功能备忘；文档同步检查通过。

## 本轮必须继续做的事
1. 先重新读取 GitHub 当前 branch HEAD 和 PR #31，不要假设 HEAD 未变化。
2. 查看当前 HEAD 的 GitHub Checks/Actions；确认完整 CI 是否运行。若没有运行，查明触发原因并通过受支持方式让完整 CI 对当前提交执行；不能用旧 SHA 的 CI 冒充当前结果。
3. 审查并实际运行 `python3 -m unittest discover -s apps/ad-studio-desktop -p 'test_*.py'`、`python3 -m compileall -q apps/ad-studio-desktop/ad_studio`（若当前执行环境可访问仓库）；否则明确说明未运行，不要声称通过。
4. 继续核对 AI 视觉比对异常处理、单镜头重生成的版本映射/保存/成本记账，以及失败后恢复；只处理问题镜头，不重生成整部短剧。
5. 每次改代码，同一提交同步 HELP.md、PROJECT_LOGIC.md、验收计划、验收 SOP、接手文件和未来功能备忘，并增加回归测试。
6. PR 保持 open/unmerged。Windows 真机、真实视频 Provider/真实扣款、剪映现场验收仍按用户要求暂缓。

## 不得误报的边界
- 文档同步通过 ≠ 全量 CI 通过。
- 单元测试未执行 ≠ 测试通过。
- AI 视觉比对不是商品真实性认证；最终需人工核验。
- 当前实现不是已经验收的商业成片流程；真实机器/Provider 验收仍待后续。


## A39：CI 触发范围
CI 的 push 触发器现覆盖所有分支；每次提交后仍须查询当前 SHA 的 checks，等待完整 `typecheck-and-test` 工作流结束。此项改动本身的完整 CI 结果待当前提交的工作流返回。


## A40：已解决的 CI 路径失败
完整 CI 曾因 `test_ai_handoff.py` 的仓库根目录相对路径错误失败；现已修复为 `ROOT / "docs" / ...` 和 `ROOT / "apps" / "ad-studio-desktop" / ...`，并在 SHA `443f713cd3721eab528eb9bb17faf599d55ef3ce` 上完整 CI 成功。


## A41：已解决的文案断言
路径修复后曾剩下一个断言短语与文档不一致；已将测试改为匹配实际文案“不要把 docs-sync”，并在 SHA `443f713cd3721eab528eb9bb17faf599d55ef3ce` 上完整 CI 成功。


## A42：最新完整 CI 结果
完整 CI `38120824822` 在基准 SHA `443f713cd3721eab528eb9bb17faf599d55ef3ce` 结论为 success；docs-sync `38120824802` 也为 success。该结果覆盖：前端语法检查、桌面 Python 语法检查、桌面单元测试、TypeScript 类型检查、引擎测试和风险控制器测试。若当前 HEAD 与此 SHA 不同，必须重新查询当前 HEAD 的结果。


## A44：短剧镜头映射防漂移（待本轮 CI）
新建短剧制作项目时保存 `short_drama_shot_number`；重生成/修正草稿不再盲用项目显示序号。旧项目仅在标题和集数唯一时回退定位，歧义则拒绝操作。本轮新 SHA 的完整 CI/doc-sync 尚待确认。
