# SESSION_HANDOFF.md — 桌面项目跨会话接手入口

> **新会话必须先读本文件，再读 `docs/AD_STUDIO_AI_HANDOFF.md`、`PROJECT_LOGIC.md` 和 `HELP.md`。** 本文件记录当前工作现场，不代表功能已验收。

## 当前仓库状态
- 仓库：`konggu888/ecommerce-agent`
- 项目：`apps/ad-studio-desktop`（本地 Python/Tkinter 桌面程序，不是 Web 应用）
- 工作分支：`feat/product-drama-visual-review`
- 最近一次完整 CI 与 docs-sync 均验证通过的 SHA：`d976c34a48ff20af65648983be7855589ba2deca`（CI run `38162555687`、docs-sync run `38162555622` 均 success；后续提交必须重新验证最新 SHA）。
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


## A45：失败恢复状态显示
已修复桌面 UI 在 Provider/实拍裁剪失败后无条件覆盖状态、导致“已保留上一版本”提示丢失的问题。新 UI 状态判断同时检查恢复标记和旧版文件是否存在且非空；当前提交后的 CI/doc-sync 必须按新 SHA 查询。


## A46：编辑镜头也保留上一版（待当前 SHA CI）
发现编辑窗口保存镜头时仍直接清空 `video_path` 并递增版本，没有把旧路径保存到 `previous_video_path`，会绕过 A43 的失败恢复保护。现改为复用 `mark_regenerate()`，并添加 UI 集成路径回归断言。提交后必须重新查询完整 CI 与 docs-sync；PR #31 仍保持 open/unmerged。


## A46：CI 文案断言修复记录
SHA 2450e2d5b74bba26cd76ac3ef3ef5639499523f2 的完整 CI 暴露 1 个 handoff 测试断言：测试要求 AI 接手文档明确包含“旧版视频”，而原句只写“旧视频路径”。现已把接手文档改为“旧版视频文件路径”，保留测试断言与旧版保护语义。必须等待新 SHA 的完整 CI 和 docs-sync 结果后再确认 A46 自动化验收。


## A47：素材解析失败恢复（待当前 SHA CI）
已把视频生成前的素材解析步骤纳入旧版本恢复边界，防止素材自动生成/匹配阶段报错时留下空的活动视频路径。输出替换也不再先删除目标文件。新增测试覆盖素材解析失败、Provider 不被调用及旧视频重载仍存在。当前提交需重新检查完整 CI 与 docs-sync。


## A48：实拍裁剪旧文件保护（待当前 SHA CI）
实拍镜头现在先写同目录临时输出，确认文件非空后再替换正式成片；裁剪失败只清理临时片段并恢复旧版路径。新增失败模拟测试，验证旧文件内容和项目重载路径保持不变。提交后需查询当前 SHA 的完整 CI 与 docs-sync。


## A49：多段实拍中断清理（待当前 SHA CI）
项目恢复清理规则已扩展到多段裁剪产生的 `.partNN.mp4`；素材源缺失时也会清理遗留分段文件，并保留有效旧视频。新增中断恢复与素材缺失回归测试。当前提交后需按最新 SHA 查询完整 CI 和 docs-sync。


## A50：视频提示词换行回归（待本轮 CI）
检查 A47 的生成异常边界重构时发现 prompt 被改成字面量反斜杠+n，已修复并新增捕获 Provider 请求的测试。A49 在 SHA 953e40694aa2a28b2d164fc49800c639b45bebb8 的完整 CI 与 docs-sync 已通过；A50 的新 SHA 仍待完整 CI/doc-sync。


## 最新 CI 基准（A47–A50）
- 代码 SHA：`58de7ce984cf9df73bad2c99444d75a0624059c3`
- 完整 CI：success，覆盖桌面 Python 语法、桌面核心测试、TypeScript、Engine 和 Risk Controller：https://github.com/konggu888/ecommerce-agent/actions/runs/38121500267
- docs-sync：success：https://github.com/konggu888/ecommerce-agent/actions/runs/38121500259
- A47–A50 自动化阶段通过；Windows 真机、真实 Provider、真实素材和实际扣款仍暂缓。
- 以上是代码基准提交的结果。任何新的提交都必须重新查询最新 HEAD 和对应工作流。


## A51：费用预估前置校验
A47–A50 的自动化 CI 与 docs-sync 已在代码 SHA `58de7ce984cf9df73bad2c99444d75a0624059c3` 的完整工作流中通过。A51 新增局部重生成费用弹窗前报价校验；必须检查本次提交的新 SHA 和工作流，不能把之前的绿灯直接沿用。


## A52：失败尝试账本与成本去重（待本轮 CI）
A52 为视频 Provider 失败调用增加本地账本记录；失败报价不计入实际花费，成功重试独立记录且实际成本只计成功记录。新增失败+成功重试回归。新 SHA 的完整 CI/doc-sync 尚待确认；真实 Provider 的超时扣款/账单对账仍暂缓。

## A53：恢复时拒绝零字节旧视频（待验收）
发现恢复逻辑只将“文件不存在”视为旧版失效，没有处理“文件存在但大小为零”的情况。现已改为只恢复真实存在且非空的上一版视频；否则清除无效路径、加入 `missing_media` 并标记待重新生成，新增持久化回归测试。必须重新查询本次提交的完整 CI 与 docs-sync，不能沿用 A52 的结果。

## A54：活动视频零字节恢复保护（待验收）
进一步复查发现，A53 只覆盖上一版路径为零字节的情况，活动 `video_path` 自身若指向零字节文件也可能被当作存在的输出。现将活动文件检查改为“是文件且非空”；若旧版有效则恢复旧版，无旧版则清除无效路径并标记待重新生成。新增两项回归测试，本次提交必须重新跑完整 CI 与 docs-sync。


## A55：Provider 成功后账本故障保护
A51 费用预估校验、A52 失败尝试账本、A53 零字节旧版拒绝和 A54 活动视频零字节校验均已在验收计划记录的 SHA 上通过完整 CI/doc-sync。A55 将 Provider 有效输出安装与成本记账分离；账本异常时保留已生成视频、标记“成本待核对”并写恢复记录，不误报 Provider 失败。A55 当前 SHA 的 CI/doc-sync 需重新确认。


## A56：提示词换行回归修复（待本轮 CI）
SHA 18b958a269757781af4f062211d2a54485658e6e 的 CI 因 test_a50_video_prompt_uses_real_line_breaks 失败，确认 A55 重构把分隔符再次改成字面量反斜杠+n。已恢复真实换行；新 SHA 的完整 CI/doc-sync 尚待确认。

## A57：成本待核对 UI 对齐（待验收）
A55 已把有效新视频与成本记账异常分离，A56 修复了提示词换行回归。继续审查发现，桌面 `generate_shot()` 在返回后仍无条件展示“项目实际累计”，即使镜头状态是“已生成（成本待核对）”。现加入状态分支：待核对时显示明确提醒与账本路径提示，正常累计数字仅在成本状态正常时显示。新增 UI 回归测试，当前 SHA 的完整 CI/doc-sync 待确认。


## A57：打开项目自动恢复与成本对账（待本轮 CI）
此前 recover_project() 没有 UI 调用入口。A57 将它接入“打开已有项目”，显示恢复摘要，并按成功用量账本同步项目/镜头实际成本；没有账本记录的旧项目保留旧成本。当前 SHA 的完整 CI/doc-sync 尚待确认。

## A58：视觉核验输入格式保护（待验收）
A57 的项目打开恢复与成本对账已在 SHA `ba07c8d1a03440f1b4e40371011f1ea5c2234339` 的完整 CI 与 docs-sync 中通过。继续审查商品视觉核验时发现参考图/生成文件只检查存在性，空文件和不支持格式可能进入 FFmpeg/模型路由。现增加格式及非空校验，并加入短剧回归和 handoff 文档断言。本次提交仍须重新检查 CI/doc-sync。

## 最新自动化验收基准（2026-10-11）
- 当前代码与文档基准 SHA：`8773905c7293c76309938e633e761206ca3447ca`。
- 完整 CI：success，运行 `38122183446`：https://github.com/konggu888/ecommerce-agent/actions/runs/38122183446
- 商品视觉输入校验代码提交 `58e9b106a07151b0a9c1855f8d7599e8d9fc9a48` 的 docs-sync：success，运行 `38122132231`：https://github.com/konggu888/ecommerce-agent/actions/runs/38122132231
- A55–A58 自动化阶段通过；真实 Provider/账单、Windows 真机、真实素材与商业成片验收仍未完成。
- PR #31 保持 open/unmerged。后续任何代码变更仍需重新查询最新 SHA 的完整 CI 与 docs-sync。


## A60：失败-only 账本成本保护（待本轮 CI）
A60 修复失败-only 账本可能把旧项目实际成本清零的问题：至少存在成功记录才按账本重建；否则保留旧项目/镜头成本与分类摘要。当前 SHA 的完整 CI/doc-sync 尚待确认。


## A59：项目成本汇总去重
A56 提示词换行修复、A57 成本待核对 UI、A57 打开项目恢复/成本对账和 A58 视觉核验输入校验均已在验收计划所列 SHA 的完整 CI/doc-sync 中通过；最新基准 SHA `e2c1642fcc599bf6e7320460ff1216276e9f16e6` 的完整 CI 与 docs-sync 也均成功。A59 将本地 usage ledger 的成功记录汇总作为项目实际成本总额唯一来源，并同步 project cost_estimate；当前提交需重新查询完整 CI/doc-sync。


## 最新自动化验收基准（2026-10-11）
- 当前 HEAD：`cd6c853c5931af77d64b89bb0435cc31895034d7`。
- 完整 CI success：`38122328825`；docs-sync success：`38122328836`。
- A59 项目成本汇总去重与 A60 失败-only 账本兼容已通过自动化测试。
- PR #31 继续 open/unmerged。真实 Provider 账单对账、Windows 真机、真实素材和商业成片仍未验收。


## A61：旧项目成本迁移与镜头账本统一（待本轮 CI）
A61 为首次成功记账前的旧成本迁移增加原子批量账本写入，并把镜头实际成本统一为成功 ledger rows 汇总；移除资产/视频路径先增量再记账的差异。新增旧成本迁移和原子写入回归；当前 SHA 的完整 CI/doc-sync 尚待确认。


## A62：A61 handoff 断言修复（待本轮 CI）
A61 的 224 项桌面测试中 1 项失败：测试期望“历史成本迁移”，文档用“历史实际成本迁移”。现将断言对齐文档术语，成本迁移代码未改；A62 新 SHA 的完整 CI/doc-sync 尚待确认。


## A61：CI 文案断言失败处理
SHA `a760909be7927025a83a1f3fc5ae219acbd80ac0` 的完整 CI 因 `test_handoff_mentions_a61_legacy_cost_migration` 断言根级 AI 接手文档必须包含“历史成本迁移”而失败；224 项测试中仅该断言失败。已在根级接手文档明确写入旧项目历史成本迁移步骤，保留测试断言。修复后的新 SHA 必须重新查询完整 CI 与 docs-sync。


## A63：迁移基线持久化保护（待本轮 CI）
A63 在旧成本迁移批量写入成功后，立即同步项目与镜头实际成本快照。若后续新费用写入失败，历史成本仍可保存并重载。新增 A63 回归，当前 SHA 的完整 CI/doc-sync 尚待确认。


## A64：素材成本账本故障保护（待本轮 CI）
A61-A63 已在 SHA e6b4789d70cfa0abebfe2b20105b80049154dcbe 完整 CI 与 docs-sync 通过。A64 为 resolve_assets 和 generate_missing_asset 共用成本记账安全入口；账本失败时保留已生成素材，标记成本待核对并记录恢复动作。当前 SHA 的完整 CI/doc-sync 尚待确认。


## A65：用量账本原子写入与完整历史（待 CI）
发现 `record()` 直接覆盖正式 JSON，而批量写入虽原子替换却把账本限制为最后 2000 行。磁盘写入失败可能损坏现有账本；长期运行则会丢失早期成本，导致项目汇总被低估。A65 统一原子写入并保留完整历史，新增两项回归。当前 SHA 的完整 CI 与 docs-sync 需确认；不代表真实供应商账单已经对账。


## A66：人工商品画面核验证据防护（待最新 CI 确认）
- 人工核验现在拒绝缺失、零字节或扩展名不受支持的证据文件，并保存规范化绝对路径。
- 回归测试覆盖无效证据与有效临时图片文件。
- 最新分支 HEAD 和对应 CI 必须在本次文档提交后重新查询；不能用此前 SHA 的成功结果代替。
- PR #31 保持 open/unmerged；Windows 真机、真实视觉/视频 Provider 和真实扣款继续按用户要求暂缓。
- 下一步：确认本次 HEAD 的完整 CI 与 docs-sync；随后继续检查单镜头修复的成本账本、版本映射与视觉核验失败恢复边界。


## A67：短剧核验审查防止过期证据误通过
- 修复发现：人工核验入口会验证真实文件，但之后文件可能被移动/删除；审查函数此前只检查路径字符串、人工方式和备注，可能继续接受旧的 `passed` 状态。
- `audit_short_drama()` 现重新验证证据扩展名、文件存在及非零大小；证据失效会触发 `PRODUCT_VISUAL_NOT_VERIFIED`。
- 增加回归：伪造/失效路径必须触发提示；有效非空临时图片必须通过此项证据检查。
- 本轮代码/测试已提交，完整 CI 与 docs-sync 必须以最终最新 SHA 重新确认。
- PR #31 保持 open/unmerged；Windows 真机、真实视觉/视频 Provider、真实扣款与真实素材验收继续暂缓。


## A68：短剧后续剧情影响分析（功能推进）
- 在跨集连续性台账窗口增加“分析后续剧情影响”按钮，可指定一集分析其对后续集的影响。
- 调用 AI 短剧编导模型，输出受影响集、风险级别、具体依据、建议动作和暂未发现影响的理由；验证受影响集编号只能指向真实后续集。
- 报告保存到短剧方案的 `continuity_impact_reports`，不自动改写剧本；需要人工确认。
- 自动化回归已补充；当前提交的完整 CI/doc-sync 状态必须重新查询。真实模型质量、Windows 真机与真实素材验收仍按计划放到统一验收阶段。


## A69：AI 编导故事引擎与留存设计（功能推进）（CI 已发现并修正提示词回归断言；文档与代码将在同一提交同步。）
- 新增短剧生成质量契约：明确人物目标、阻力、失败代价、冲突升级、转折、伏笔兑现、情绪回报和开场留存设计。
- 新生成结果缺少 `story_engine` / `hook_design` 或升级/留存步骤不足时，会被拒绝保存；旧方案读取保持兼容。
- 新增提示词与负向回归测试；统一验收阶段还需验证真实模型能否持续产出好故事，结构字段本身不代表故事精彩。


## A70：短剧故事结构检查（功能推进）
- 确定性审核报告新增故事引擎和留存设计的结构性提醒：目标/阻力/代价/转折/伏笔兑现/情绪回报、冲突升级、开场疑问、结尾兑现、留存装置。
- 该检查为警告，不替代语义质量判断或真实观众反馈；回归测试与 HELP/PROJECT_LOGIC 同步更新。


## A71：备选故事方向差异化（功能推进）
- 新增备选方向字段：冲突来源、主角关键选择、反转机制、商品角色、受众吸引点与转化路径。
- 新生成方案必须提供至少两个方向并通过必填字段和核心机制重复检查；补充负向回归测试。
- 自然语言语义相似度仍需在统一验收阶段结合真实模型输出人工评估。


## A72：人物动机与关系动力（功能推进）
- 新增人物深层动机、恐惧/秘密、关系动态、决策压力字段，并要求主要人物的行动可追溯到目标/动机/压力。
- 新生成方案缺字段会被拒绝；旧方案仅提示 warning，保持向后兼容。
- 已补充负向测试；下一步继续推进事件因果链与分镜剧情一致性。真实模型写作质量尚未做人工/真机验收。


## A73：剧情事件因果链（功能推进）
- 已加入事件前因、人物选择、直接后果和状态变化的显式因果链要求。
- 新生成方案缺失/不完整会被拒绝；旧方案只告警，兼容历史项目。
- 下一步继续做因果链与剧本/分镜的一致性检查，防止只填结构而故事实际没有体现。


## A74：因果链与剧本/分镜证据对齐（功能推进）
- 新生成短剧的每个因果步骤必须引用完整剧本中的原文证据，并关联根级 storyboard 中至少一个真实分镜位置。
- 缺少证据、证据不在剧本、分镜引用越界会被拒绝；旧方案仅生成 warning，保持兼容。
- 下一步继续推进人物选择、反转和商品功能与镜头动作之间的语义一致性；当前规则不能宣称已经理解画面内容。


## A75：商品事实锁与剧情内容交叉审查（功能推进）
- 已确认商品事实缺少商品资料中的直接文本依据时产生警告。
- 未核实信息被写成肯定主张且附近没有明确不确定性标记时产生警告。
- 已增加回归测试；规则是文本风险筛查，不是事实认证。下一步继续推进人物选择、反转与商品真实功能的一致性检查。


## A76
- Added warning code `PRODUCT_SELLING_POINT_NOT_SHOWN` when confirmed selling points are absent from storyboard action, product integration, dialogue, and generation prompt text.
- This is a text coverage check, not visual verification. Recheck CI and docs-sync for the new SHA.


## 2026-10-11 接手进度：A77

- 基线：A76 文档同步提交 `95b57fcb32860c02c0deece035684b4004ba07f6`；当时 CI 与 docs-sync 均成功，PR #31 未合并。
- 本轮目标：短剧关键因果事件、故事转折与伏笔兑现是否真正落到可拍摄分镜；增加提示词字段 `narrative_function` / `story_event_reference` 与审查警告。
- 约束：文本匹配仅为遗漏筛查，不可宣称完成真实语义判断、生成画面核验或 Windows 真机验收。
- 继续步骤：运行短剧专项测试与完整 CI，检查 docs-sync；失败必须读日志修复后再确认最新 HEAD。


## 2026-10-11 接手进度：A78

- 基线：A77 提交 `60a76cb12bc11ba914dd4d3eeed43379f933a453`；CI 与 docs-sync 均通过，PR #31 未合并。
- 本轮目标：要求分镜逐人物说明行动依据，并检查人物所依赖的信息来源能否在完整剧本定位、关键选择是否落实到引用镜头。
- 新增检查代码：`CHARACTER_ACTION_BASIS_MISSING`、`CHARACTER_ACTION_BASIS_INCOMPLETE`、`CHARACTER_KNOWLEDGE_SOURCE_UNTRACEABLE`、`CHARACTER_CHOICE_NOT_SHOWN`。
- 限制：仅结构/文本审查；不能声称完成心理语义判定、真实生成画面核验或 Windows 真机验收。

- A78 首轮 CI 暴露审查代码执行顺序问题（`shot_texts` 未初始化）；已调整到文本索引构建后运行，并同步帮助/逻辑文档，需以修复后最新 CI 为准。

### A79：人物行动依据绑定检查
- 基线：A78 修复后的 HEAD 311686b8fe962a5276aa603422911f45d612c52e，CI 与 docs-sync 均成功。
- 本轮新增检查：行动依据不能绑定到当前镜头未出现的人物，也不能引用角色设定表中不存在的人物。
- 回归测试覆盖两类错误绑定；仍需以本次提交对应的完整 CI 与 docs-sync 结果为准。

### A80：人物关系变化审查
- 基线：A79 SHA 787447a849457ecb65540edb48d3f2fb9fcde720，CI 与 docs-sync 通过。
- 新增 relationship_change 字段及两项 warning，回归覆盖缺少关系变化说明、关系变化未落实到引用镜头。
- 该字段在审查阶段保持兼容；旧方案缺少字段时仅在多人物方案给出警告。
- 必须以本轮最终 HEAD 的 CI 与 docs-sync 结果为准。

- A80 首轮 CI 失败原因：关系审查执行时引用了尚未构建的 character_names；修复为读取 checked["characters"]，并同步文档。必须继续确认修复 SHA 的 CI。


## 最近推进｜A80 与 A81
- A80：因果链人物关系变化说明及其分镜落地审查；修复初始化顺序后，SHA `ecd7259205cd77b99516e958d89d7022a9f2ab3b` 的完整 CI 与 docs-sync 通过。
- A81（本轮）：新增 `state_continuity`，将因果事件造成的人物状态/信息/承诺/误解/关系后果追踪到后续分镜；覆盖未说明、未知人物、未展示、引用镜头顺序/位置等 warning。
- CI 首轮发现角色名集合初始化顺序错误，已修复；第二轮发现“无后续影响”测试夹具只覆盖单一步骤，已改为逐步声明状态连续性。
- 最终验证 SHA `d976c34a48ff20af65648983be7855589ba2deca`：完整 CI run `38162555687` success；docs-sync run `38162555622` success。PR #31 保持 open、未合并。


## A82｜人物信息掌握与时间线一致性（已提交并验证）
- 代码提交：`8756b773c3b2ee3bf08b80bf3b31992b7081a606`。
- 完整 CI：run `38306392896` success；docs-sync：run `38306392892` success。
- 规则区分剧情内获得的信息（来源镜头必须有效且早于行动镜头）与故事开始前已知的信息；旧方案缺少字段时只产生 warning。
- PR #31 已于 2026-10-11 合并，不要重复合并；A82 后续提交位于 `feat/product-drama-visual-review` 分支。

## A83｜人物承诺、误解与行动结果一致性（自动化阶段通过）
- 最终代码提交：`f57c0eb02249439ea42cc3d46dd2d94e87bab1c1`。
- 完整 CI push run `38307672489` success；PR CI run `38307795562` success。
- docs-sync push run `38307672505` success；PR docs-sync run `38307795710` success。
- A83 已加入 `narrative_obligations`，并覆盖承诺兑现/未兑现、误解与行动后果的来源证据、人物引用、镜头先后和后续文本覆盖回归。
- PR #32 已创建，状态 open/unmerged；不要自动合并。
- 仍需统一验收真实剧情语义、人物心理、画面表演、Windows 真机、真实 Provider 和真实扣款。


## 当前接手状态覆盖（2026-10-13；以本节为准）
- 当前工作分支：`feat/product-drama-visual-review`。
- PR #32 继续保持 open/unmerged；未获用户明确许可不得合并。PR 链接：https://github.com/konggu888/ecommerce-agent/pull/32
- A83 已完成并在最终 SHA `dc24957d5d773bd87bce648b00ea40c412a15da8` 上通过完整 CI 与 docs-sync（CI push `38307988335`、CI PR `38307994797`、docs-sync push `38307988310`、docs-sync PR `38307994904` 均 success）。
- A84 已增加跨集承诺/误解/行动后果的显式承接检查与 3 项回归测试；当前代码提交为 `00ad0d00a9747ca9ef666981b4e592bef6bde543`。此提交及后续文档提交的完整 CI 与 docs-sync 必须重新核验，不能沿用 A83 的绿灯。
- A84 专项：`cross_episode_required=true` 时要求事项引用来源集之后的镜头；仍为 open 的事项必须进入来源集承接状态，并在下一集开场状态/未解线索中延续。未声明该字段的旧方案兼容。
- 仍暂缓：Windows 真机、真实 Provider、真实扣款/账单核对、剪映现场验收。不得将自动化文本审查称为商业成片或语义验收。


## A84 当前验证状态（2026-10-13；本节为最新记录）
- A84 代码、测试及 HELP/PROJECT_LOGIC 同提交 SHA：`00ad0d00a9747ca9ef666981b4e592bef6bde543`。
- 完整 CI push `38308777852` success；完整 CI PR `38308783208` success。
- docs-sync push `38308777939` success；docs-sync PR `38308783195` success。
- PR #32 保持 open/unmerged；不得未经用户明确许可合并。
- A84 仅做跨集结构与文本承接审查；Windows 真机、真实 Provider、真实扣款/账单核对、剪映现场验收仍暂缓。


## A85｜人物长期状态与关系跨集一致性（待最新 CI）
- 新增可选每集字段 `continuity_state.character_state_ledger`，追踪人物认知、秘密、承诺、心理与人物关系等必须延续的状态。
- 对 `must_persist=true` 且未解决的状态，检查下一集是否继续记录；状态描述变化必须声明 changed/resolved，changed 必须提供在剧本/分镜中可定位的 transition_evidence。
- 增加状态缺失、关系无解释重置、转变证据缺失、非布尔持久标记、证据不可定位等回归测试。
- 本轮代码 SHA 与其后文档同步提交的 CI/doc-sync 必须重新确认，不能复用 A84 绿灯。
- 旧方案不提供此可选台账时兼容；Windows 真机、真实 Provider、真实账单与画面验收仍暂缓。


## A85 验证结果更新
- 代码与测试提交：`6128fabc3c530c6072dfe72e05a956fe7733065f`。
- 完整 CI push `38309397555`、PR `38309402963` 均 success；docs-sync push `38309397567`、PR `38309403129` 均 success。
- 本节记录只覆盖代码/测试 SHA；此后的文档提交仍需以最终最新 SHA 重新核验。


## A86｜人物状态变化因果闭环（接续事项）
- 新增 changed 状态的触发事件→变化→人物反应→后续影响字段和时序校验。
- 已添加有效闭环、缺少触发、触发晚于变化、反应/后果缺失或顺序错误等回归测试；需以最新 SHA 的 CI/docs-sync 结果确认。
- PR #32 仍保持 open/unmerged；Windows 真机、真实 Provider、真实扣款/账单与剪映现场验收继续暂缓。


## A87｜人物状态到分镜表演（接手记录）
- 对 `status=changed` 增加 `observable_manifestation` 与 `observable_storyboard_indices`，检查状态变化是否被具体动作、台词、表情或互动体现，而不只是心理标签。
- 新增测试：有效可观察表演、仅有抽象情绪标签、表演描述无法在引用镜头中定位。
- 本节记录的是实现目标；提交后必须以最终 SHA 的 CI 和 docs-sync 结果更新验证状态。
- PR #32 保持 open/unmerged；Windows 真机、真实 Provider、真实扣款/账单和剪映现场验收仍暂缓。
\n\n## A88｜多人物状态依赖一致性\n- 新增每集可选 `continuity_state.cross_character_dependencies`，声明人物间知识、关系或承诺依赖。\n- 检查双方人物、规则、证据和镜头引用；`same_understanding` 陈述不一致时警告，`asymmetric_knowledge` 缺少原因时警告。\n- `different_beliefs_allowed` 允许不同信念，不将合理误解自动判成矛盾。\n- 新增直接冲突、不同信念、知识不对称、未知人物和无效镜头引用测试。提交后以最终 SHA 核验 CI/docs-sync。\n- PR #32 保持 open/unmerged；真实 Provider、Windows 真机、扣款/账单及剪映现场验收仍暂缓。\n

## A89｜跨集演员/场景资产锁定（自动化阶段）
- 新增根级可选 `series_asset_locks`，可为重复人物/场景定义稳定 key、规范外观/布景描述和适用集数。
- 锁定描述进入对应分镜的演员/场景需求，供既有资产调度链使用；下一集续写上下文保留该锁定列表。
- 新增锁定注入、集数范围、非法 schema、无目标命中警告测试。
- 限制：这是需求文本锁定，不宣称已复用同一物理素材文件或保证生成画面身份一致。PR #32 保持 open/unmerged。


### A89 CI 修复追踪
- 首轮 CI 发现锁定注入调用位置不正确、集号范围测试夹具与单集方案集数不一致，已根据日志修复。
- 当前修复提交必须重新等待 push/PR CI 与 docs-sync push/PR；不得沿用之前 SHA 的失败或通过状态。


## A89｜跨集演员/场景资产文本锁定（2026-10-14 自动化验证通过）
- 当前工作分支：`feat/product-drama-visual-review`；PR #32 保持 open/unmerged。
- 最终代码 SHA：`9bcb19ac950f0addcc5a0bfab599dd060c11ec1e`。
- `series_asset_locks` 已加入短剧输出 schema；`validate_short_drama()` 将锁定描述注入匹配分镜的 actor/scene requirements；续写上下文携带锁定列表；未匹配目标产生 warning。
- A89 回归覆盖演员/场景锁定注入、生产行传递、适用集数、非法集号与目标未命中；299 项 Desktop Core 测试全部通过。
- CI push `38465502064`、CI PR `38465509232`、docs-sync push `38465502037`、docs-sync PR `38465509210` 均 success。
- 限制：仅文本/资产需求层约束，不等于同一物理素材文件复用，不保证生成画面身份绝对一致。Windows 真机、真实 Provider、真实扣款/账单、剪映现场验收仍暂缓。


## A90：跨集物理素材 ID 绑定（待最新 SHA 自动化验收）
跨集演员/场景锁定可选指定本地素材库 asset_id，并将精确 ID 传入制作行。生产解析按 ID 验证资产存在、启用、可复用且类型匹配；无效时明确返回 SERIES_LOCKED_ASSET_INVALID，禁止静默替换或自动生成。未提供 ID 的 A89 旧方案保持标签匹配兼容。此约束只保证素材调度选择，不保证生成画面像素级一致。最新 SHA 的完整 CI/docs-sync 必须重新核验；PR #32 保持 open/unmerged，Windows 真机与真实 Provider 验收继续暂缓。
