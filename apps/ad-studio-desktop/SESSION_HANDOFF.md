## 【最新接手状态｜2026-10-17｜路线阶段标签归一化 v1】

- 最新进度台账新增标准化字段：`normalized_roadmap_phase`、`phase_normalization_original`、`phase_mapping_confidence`。原始映射字段保留；18 项 provisional 映射仍需核验，没有被自动判定为已确认。
- 标准化阶段槽位数：阶段0=7、阶段1=52、阶段2=14（其中 9 项待核验）、阶段3=3、阶段4=32（其中 9 项待核验）、阶段5=5，总计 113。标签分类归一化 6/6=100%，不代表阶段完成率。
- 阶段完成率仍暂不发布；下一步核验 18 项 provisional 映射，再做 A0–A112 跨来源状态/证据 reconciliation。总体产品完成率仍关闭。
- 不新增 A113+，不改 A0–A112 正式验收状态，不合并 PR #32。代码/文档提交后必须核查最新 HEAD 的 PR CI/docs-sync；Push 触发项如果连接器无法核实，应如实注明。

---

## 【最新接手状态｜2026-10-17｜阶段百分比统计 v1 已发布】

- 分支 `feat/product-drama-visual-review`；PR #32 保持 Open/unmerged；本段是阶段统计口径，不是验收状态变更。
- 台账 `docs/AD_STUDIO_TASK_REGISTER.json` 已加入 `stage_progress_metrics`。以基线 HEAD `08af9d8d5c46fc6b1c03df76046a3a2170e39b12` 计算：编号槽位盘点 113/113=100%；需求文本级复核 113/113=100%；路线阶段映射 113/113=100%；任意证据指针 113/113=100%；直接源码/测试指针 112/113=99.1%；绑定历史源码/测试快照 56/113=49.6%；精确绑定当前 HEAD 的证据 0/113=0%；完整代码/测试审计 0/113=0%；正式验收通过 0/113=0%。
- **不要把以上覆盖指标称为产品完成率。** 总体产品完成率仍关闭，权重仍未审定；路线阶段名称存在重复变体，阶段完成率也暂不发布。台账保留 `progress_percentages_enabled=false` 作为总体完成率关闭标志，并新增 `stage_progress_percentages_enabled=true`。
- 统计写入台账的提交为 `055e5590cc7a066047e56d7e5da03868d2e12bc2`；本次 dashboard/handoff 更新后必须再次检查最新 HEAD 的 CI PR、docs-sync PR；Push 触发项若连接器无法确认必须标为未核实。
- 下一步：完成阶段名称归一化与 A0–A112 跨来源语义去重/状态冲突核验，审查每个任务的证据边界与当前 HEAD 绑定，再制定可解释的阶段权重，之后才开放总体完成率。不得新增 A113+，不改 A0–A112 正式状态，不合并 PR #32。真实 Provider/账单、Windows 真机、剪映现场和真实投放继续暂缓。

---

## 【实时接手状态｜2026-10-17｜未知视频单价记账修正】

- 已验证代码/测试基线 `fc34d1ec901e3d9fb783ea9da694cf3ad21bf257`：PR CI `39014144867` success，docs-sync PR `39014144870` success；Push 触发项未独立核实。
- 生产层在视频 Provider 缺少配置单价时，不再把占位 `0.72` 写成已知费用：成功账本行记录 `estimated_cost_rmb=0`、`cost_status=price_missing`；失败尝试的占位报价也置零/未知。未知费用计数仍保留。这里的 0 不是“供应商免费”，只是“没有可计入的已知金额”。
- 中间一次 CI 因把账本全局/项目汇总语义改得过宽而使 A57/A59/A61/A63/A65/A99 历史成本合同测试失败；已撤回宽泛改动，只保留定向缺价修复，并在上述 SHA 通过。保留失败历史。
- 文档更新后须核查最新 HEAD 的 CI/docs-sync，不得沿用上述 SHA 结果。
- **下一步唯一主线：**审计 `app.py` 的创建预算预估（约 1722 行）、混合补镜头（约 968/1036 行）、一键批量生成（约 2155 行）和短剧项目预算预估（约 2754 行）。这些路径可能读取默认占位价而把缺失价格显示成确定金额；按现有合同修正未知提示/预算决策，再审计其余 Provider 入口与 endpoint provenance。不得新增 A113+，不改 A0–A112 正式验收状态，不合并 PR #32。真实 Provider、真实扣费/账单、Windows 真机、剪映现场和真实投放继续暂缓。

---

## 【实时接手状态｜2026-10-17｜端点绑定授权已验证】

- 已验证代码/测试基线 `fff8f59916cac0864d6bd69ce02a75028993c5f1`：PR CI `39013621163` success，docs-sync PR `39013621460` success；Push 触发项未独立核实。
- 云端视频入口已从布尔授权收紧为 `authorized_endpoint`：用户确认时传递 endpoint 快照；生产层将其与实际加载 Provider endpoint 精确比较。未授权或端点变化时拒绝分发，要求重新确认。
- 新增测试覆盖无授权零加载/零分发、端点变更后零分发和镜头状态/版本不变。中间一次 CI 失败来自测试 mock 未区分 `UnconfiguredProvider` 哨兵，fixture 已修复并在上述 SHA 通过；保留失败历史。
- 以上是代码/测试基线；本段更新本身会产生新文档 HEAD，必须重新检查新 HEAD 的 CI/docs-sync。
- **下一步唯一主线：**继续对照 A13、A29、A51–A65 合同审查授权、数据外发和费用记录；审计剩余 Provider 入口、未知费用语义和 endpoint provenance。不得新增 A113+，不得修改 A0–A112 正式验收状态，不合并 PR #32。真实 Provider、实际扣费/账单、Windows 真机、剪映现场和真实投放继续暂缓。

---

## 【实时接手状态｜2026-10-17｜云端视频授权闸门已验证】

- 仓库 `konggu888/ecommerce-agent`；分支 `feat/product-drama-visual-review`；PR #32 保持 Open、未合并。
- 已验证代码/测试基线 `ecce52c904044db4b2618a1faefa5692fa727a40`：PR CI `39013274826` success，docs-sync PR `39013274821` success；Push 触发项未由当前连接器独立核实。
- 中间 HEAD `1b5c5aedb4233f65ab4d5b227cb6ef512621123f` 的 CI 曾因正向路由测试未传 `video_authorized=True` 失败；测试夹具已修正，最终基线 CI 重跑成功。保留该失败记录。
- 已修复后端视频入口：`render_shot()` / `render_cloud_shot()` 的云端路径默认拒绝无授权请求；UI 只在用户确认本次端点/费用后传入授权标记及同一 `ExecutionDecision` 快照。新增测试证明无授权时 Provider loader/dispatch 调用为 0，镜头状态/版本不变。
- 文档已更新 HELP、PROJECT_LOGIC、进度看板和 UXS-2 审计；本次 handoff 更新提交后还要重新核查最终 HEAD 的 CI/docs-sync，不能把基线绿灯沿用到新文档 SHA。
- **下一步唯一主线：**继续对照 A13、A29、A51–A65 合同审查授权、数据外发与费用记录；审计剩余 Provider 入口、未知费用语义和 endpoint provenance。只依据证据修复/补测，不新增 A113+，不改 A0–A112 正式状态，不合并 PR #32。真实 Provider、实际扣费/账单、Windows 真机、剪映现场和真实投放继续暂缓。

---

## 【实时接手状态｜2026-10-17｜云端视频入口授权闸门】

- 仓库 `konggu888/ecommerce-agent`；分支 `feat/product-drama-visual-review`；PR #32 Open/unmerged。
- 本轮开始时 HEAD `76d6c6e9735c72615a45271ad4163783bd4a43a5`；该 SHA 的 PR CI #39012326559 与 docs-sync PR #39012326577 success。Push 触发项未由当前连接器独立核实。
- 已发现并修复后端入口缺口：`ProductionStore.render_shot()` / `render_cloud_shot()` 云端路径原先可在未显式传入本次视频授权的情况下进入 Provider 分发。现增加 `video_authorized=False` 默认拒绝；UI 在用户确认当前端点/费用后传入确认时路由快照的授权标记；未授权时在 Provider 加载/分发前拒绝。
- 新增测试 `test_cloud_video_entrypoints_fail_closed_without_explicit_authorization`，覆盖两种入口无授权时 loader/dispatch 调用为 0、镜头状态与版本不变。生产层、UI、测试分别提交：`c055c18e052a3a6d89336c7a948610c0724f2d45`、`77badfd012082a1ed3ebd0ff0afcbf07724a2088`、`786f8b5b3aebb82b7b49a88bbb2355b284427ad7`。
- 当前仍待同步 HELP、PROJECT_LOGIC、本看板与 UXS-2 审计记录，并检查这些新提交最终 HEAD 的 CI/docs-sync；在结果出来前不能称新测试已通过。
- 下一步按既有计划继续 A13、A29、A51–A65 合同和 Provider 入口审计；不新增 A113+，不改 A0–A112 正式状态，不合并 PR #32。真实 Provider、真实扣费/账单、Windows 真机、剪映现场、真实投放继续暂缓。

---

## 【实时接手状态｜2026-10-17｜以此段优先】

- 仓库：`konggu888/ecommerce-agent`；分支：`feat/product-drama-visual-review`；PR #32 当前 Open、未合并。
- 本窗口开始时的上一窗口基线为 `3f8c78c6199b79ed2413e53efc34efb8653c8388`：当时用户报告 CI Push #39011857814、CI PR #39011860648、docs-sync Push #39011857829、docs-sync PR #39011861064 四项全绿。此为上一窗口提供的历史状态，不是当前 HEAD 的检查证明。
- 本窗口新增提交后，当前代码 HEAD 为 `2138a24af70ea41ec0eb40451f1f6c409de314df`。该 SHA 的 CI PR run #39012203130 与 docs-sync PR run #39012203128 已完成并 Success；CI 的 Python 语法、桌面核心测试、TypeScript、Engine、Risk Controller 均通过。当前连接器只返回这两个 PR 触发的工作流，未独立核实该 SHA 的 Push 两项。
- 本窗口代码改动：`App.create()` 第二道预算确认现在通过授权门控制项目、商品资料、商品库保存和 UI 刷新；新增首次拒绝外部操作计数、预算拒绝持久化计数，以及创建流程顺序测试。代码/测试提交见 `2138a24af70ea41ec0eb40451f1f6c409de314df`。
- 已更新 `HELP.md`、`PROJECT_LOGIC.md`、本文件和 `docs/AD_STUDIO_PROGRESS_DASHBOARD.md`。文档同步 PR run #39012203128 已通过。
- **下一步唯一任务：**按上一窗口明确的顺序，先对照既有 A13、A29、A51–A65 合同核对授权、外发数据与费用记录边界；再盘点剩余 Provider 入口，检查是否存在未经明确授权的外部调用。将 `CapabilityRouter.decide_asset/decide_video` 本地/云端回退、用户拒绝后的零调用、费用确认先于 Provider 调用、未知价格语义和 endpoint 历史追溯纳入该审计，不另起新验收编号。
- 完成合同/入口审计后，再根据证据决定是否补测试或修复；每次提交后重新核验新 HEAD 的 CI 与 docs-sync。Push 两项如无法独立查询，必须写明未核实，不能称四项全绿。
- 验收边界：A0–A112 状态不变，不新增 A113+；PR #32 不合并；真实 Provider、实际扣费/账单、Windows 真机、剪映现场和真实投放继续暂缓。

---



# 【历史快照｜交接一致性修复规则｜2026-10-16】

> **这是接手协议和最近核实的历史基线，不是替代实时 GitHub 查询的静态快照。** 每次新会话必须先查询分支 HEAD、PR #32 和该 HEAD 的四项工作流；无论本段 SHA 是什么，都不得直接假定它仍是 HEAD。若 HEAD 不同，先识别新增提交及状态，更新交接记录后再继续任务。严禁从历史快照推断当前状态。

- 仓库：`konggu888/ecommerce-agent`
- 工作分支：`feat/product-drama-visual-review`
- 最近一次确认的代码/测试基线：`55f0202da0db941c3b45ddaa55fc197c10c6d769`（DEDUP-013，A57/A60 成本恢复保存/重载断言）；该基线四项检查曾成功：CI Push #38788160714、CI PR #38788169343、docs-sync Push #38788160480、docs-sync PR #38788169267。它不是后续文档提交的 CI 证明。
- 此后只为修复交接连续性，已更新进度看板、AI handoff、SESSION_HANDOFF；上次查询看到的交接元数据提交为 `d92128a07b0b1e8e2439ce7fd06b27a313abca49`，其 CI #2225 与 docs-sync #1904 当时为 in_progress。由于本段更新本身会产生新的文档提交，**当前 HEAD 与检查状态必须重新实时查询**；不能把这些 in_progress 结果沿用到新 SHA。
- PR #32：最后核实为 Open、未合并；新会话必须重新查询。禁止合并，除非用户明确授权。
- DEDUP-013：A57「无账本旧项目恢复后保存/重载仍保留项目/镜头成本」与 A60「failed-only 账本恢复后保存/重载仍保留项目/镜头成本及成本分类汇总」断言已补强。曾发生一次 docs-sync Push 失败，后续补齐要求文档并修复；保留失败历史，不得抹去。A57、A60、A99 仍为 `not_audited`。A99「成功账本权威后清除未计费兄弟镜头陈旧成本」为独立合同，不与 A57/A60 合并。
- **当前唯一下一步：**审计并收紧 `CapabilityRouter.decide_asset/decide_video` 的本地/云端回退：明确用户如何允许/拒绝目的地变更；用 mock 覆盖本地服务不可用、云端候选可用/不可用、用户拒绝后调用计数为 0，并验证费用确认先于 Provider 调用。随后补未知费用语义和 endpoint 历史追溯。不新增 A113+，PR #32 不合并。
- **上一阶段记录：**A52/A55 已完成部分源码/测试证据映射，但仍为 `not_audited`；详细缺口见总进度看板。
- 不新增 A113+；不删除、合并或重编号 A0–A112；全局语义去重和完整代码/测试审计仍未完成；整体完成率关闭。
- Windows 真机、真实素材、真实 Provider/实际扣费与账单、剪映现场、真实投放/商业效果继续暂缓。自动化测试和 CI 绿灯不等于真实环境验收完成。
- **防止再次断档：**当前状态唯一权威入口是本文档顶部和 `docs/AD_STUDIO_PROGRESS_DASHBOARD.md` 顶部。AI handoff 与其他历史记录只作背景，不得维护互相冲突的“下一步”。新会话必须先读本文、查 HEAD、PR、四项工作流，再核对 dashboard；如果某项无法查询，明确写“未核实”。文档/代码每次提交后都必须重新验证其自身 SHA 的 CI Push、CI PR、docs-sync Push、docs-sync PR，分别记录成功/失败/运行中/未运行。

---

# 当前接手状态｜PLAN-003 DEDUP-013 已验证｜2026-10-16

- 分支 `feat/product-drama-visual-review`；已验证基线 `c8797e4b8d65580a7c124903d4a9c8f6e188f41a`；PR #32 Open/unmerged。
- 上一修复 SHA 的四项工作流均成功：CI Push 38787892022、CI PR 38787902592、docs-sync Push 38787891485、docs-sync PR 38787902562。
- DEDUP-013 增加 A57 无账本旧项目、A60 failed-only 账本恢复后的保存/重载断言；CI 已运行通过。初始 docs-sync Push 失败已通过补齐 AGENTS.md、HELP.md、PROJECT_LOGIC.md 修复。
- A99 成功账本清除陈旧兄弟镜头是独立合同；A57/A60/A99 均未正式验收，真实 Provider 账单、Windows 真机、真实素材继续暂缓。
- 下一步继续 PLAN-003 有界源码/测试审计。任何新提交都必须重新检查四项 CI/docs-sync。不新增 A113+，不改 A0–A112，不合并 PR #32；整体完成率关闭。

---


---


---


---


---


---


---

# 【历史快照｜PLAN-003 A110–A112 部分证据映射｜2026-10-15】

- 权威进度入口：`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`；PR #32 保持 Open/unmerged。
- 源码/测试审计基线 `c77704d86d6131d13501448af76ce24afc56ad7b`；A110–A112 文档更新前最后一次明确核验成功的工作流 HEAD `47479d41725cf726e1543524bda012fee8bdf890`（CI PR / docs-sync PR 38730727069 / 38730727058）；文档更新后的 HEAD `143d01f87c3161deee04cd2d3c821b1e915084d1` 的 CI PR / docs-sync PR 38731016045 / 38731016172 也 success；Push 未独立核实。
- A110–A112 全部重新标记 partial_evidence_mapping/not_audited。A110 缺 CTA 专测与生产集成；A111 缺 build_final 整链回归；A112 缺字幕记录 applied/fallback 整链回归。真实 Windows/素材/Provider/商业视听继续暂缓。
- A0–A112 已无新编号任务；下一步进行全量语义去重、证据冲突与未审计范围复核。不得新增 A113+，不合并 PR #32。

---

# 【历史快照｜PLAN-003 A100–A104 证据映射补充｜2026-10-15】

- 权威进度入口：`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`；PR #32 保持 Open/unmerged。
- 本轮源码/测试基线 `c77704d86d6131d13501448af76ce24afc56ad7b`；关键 blobs：`postprocess.py` `36ce0e4a17d635e3ed381c3b0bada1428e0290c4`、`ffmpeg.py` `d13870a12eae682133995bac7305900e0a4ff767`、`production.py` `e53968f47a6b8fd23df773dbd3a4ad553753e1e0`；测试 `test_postprocess.py` `29141bb61ee3ec6ae5960395e81c7dc64ef79feb`、`test_ffmpeg.py` `e409cbded7db0c01a1962f722d54c615429f5e37`、`test_desktop.py` `357c54dad99f61b99891bcc365dd2f9efc1a1009`。
- A100–A104 均只完成部分证据映射，正式验收仍 not_audited。基线 CI PR 与 docs-sync PR 成功；Push 未独立核实。真实 FFmpeg/Windows 视听验收仍暂缓。
- 下一批 A105–A109；文档提交后先核验最新 SHA 四项 CI/docs-sync。不新增 A113+，不更改真实机器测试暂停安排，不合并 PR #32。

---

# 【历史快照｜PLAN-003 A95–A99 部分证据映射｜2026-10-15】

- 权威进度入口：`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`；PR #32 保持 Open/unmerged。
- 本轮源码/测试审计基线 `c77704d86d6131d13501448af76ce24afc56ad7b`；`production.py` / `test_desktop.py` blobs：`e53968f47a6b8fd23df773dbd3a4ad553753e1e0` / `357c54dad99f61b99891bcc365dd2f9efc1a1009`。基线 CI PR 与 docs-sync PR success；Push 结果未独立核实。
- A95–A99 均只完成部分证据映射，正式验收仍 not_audited；细项与缺口见进度看板和任务台账。下一批 A100–A104；文档提交后先核验最新 SHA 四项 CI/docs-sync。
- 不新增 A113+，不更改真实机器测试暂停安排，不合并 PR #32。

---

# 【历史快照｜PLAN-003 A90–A94 部分证据映射｜2026-10-15】

- 权威进度入口：`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`；PR #32 保持 Open/unmerged。
- 源码/测试审计基线 HEAD `a6e052fa7edefa7e2fb794166684547436ff90f6`；本轮文档更新后的最新 HEAD `64857c4f93a4b648c207328299e690f1ef932dca`；源码/测试 blobs：`e53968f47a6b8fd23df773dbd3a4ad553753e1e0`、`2506410d9621840ec34464fce1fa2746c7d798f4`、`357c54dad99f61b99891bcc365dd2f9efc1a1009`、`2995b5764f7a86ee8c274b6359ff2f09cdf7a288`。CI PR 和 docs-sync PR success；Push 对应工作流本轮尚未独立核实。
- A90–A94 完成部分源码/测试映射，正式验收仍 not_audited。详细证据边界见总进度台账。下一批 A95–A99；文档提交后先核验最新 SHA 四项 CI/docs-sync。
- 不新增 A113+，不修改真实机器测试暂停安排，不合并 PR #32。

---

# 【历史快照｜PLAN-003 A85–A89 部分证据映射｜2026-10-15】

- 唯一权威进度：`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`；PR #32 保持 Open / unmerged。
- 本轮开始 HEAD `2b92072a1dd5335fe803955ffca11881ebf2dec3`；源码/测试审计快照 `4063ba5a452c0c883ff39c8ea1ce33499a80eaf4`，`short_drama.py` / `test_short_drama.py` blobs 为 `2506410d9621840ec34464fce1fa2746c7d798f4` / `2995b5764f7a86ee8c274b6359ff2f09cdf7a288`。该快照 CI Push/PR、docs-sync Push/PR 四项均 success；本轮文档提交后须核验最终 SHA 的四项工作流。
- A85–A89 仅完成部分证据映射，正式验收未完成：A85 人物长期状态；A86 状态变化因果闭环；A87 可观察表演；A88 多人物状态依赖；A89 跨集演员/场景锁定。具体缺口见总进度台账。
- 台账指标：需求文本复核 113；source/test/CI/workflow 指针 90；任意 evidence 102；路线图映射 113/113；源码/测试快照绑定 32；最终文档 HEAD 精确绑定 0；完整代码/测试审计 0；完整审计 0；语义去重未完成。权重与总体完成率关闭。
- 不开发新产品功能，不新增 A113+，不删/合并/重编号 A0–A112。真实 Windows、素材、Provider/扣费、剪映现场和真实商业效果继续暂缓。
- 下一批 A90–A94。先核验本轮文档提交后最新 HEAD 的 CI Push、CI PR、docs-sync Push、docs-sync PR，再继续。

---

# 【历史快照｜PLAN-003 A80–A84 部分证据映射｜2026-10-15】

- 唯一权威进度：`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`；PR #32 保持 Open / unmerged。
- 源码/测试快照 `4063ba5a452c0c883ff39c8ea1ce33499a80eaf4` 的 `short_drama.py` / `test_short_drama.py` blob 分别为 `2506410d9621840ec34464fce1fa2746c7d798f4` / `2995b5764f7a86ee8c274b6359ff2f09cdf7a288`；该 SHA 四项 CI/docs-sync 均 success。文档提交后必须重查最新 HEAD 四项。
- A80–A84 已完成部分映射，正式验收未完成：关系变化/后果、人物状态连续性、信息时间线、承诺/误解/行动结果、跨集承接事项。主要剩余风险是正向路径不足、语义字符串匹配局限，以及最终集/保存重载等边界。
- 台账覆盖数：需求复核 113；source/test/CI/workflow 指针 85；任意 evidence 97；路线图阶段映射 113/113；源码/测试快照绑定 27；最终文档 HEAD 精确绑定 0；完整代码/测试审计 0；完整审计 0；语义去重未完成。权重和总体完成率关闭。
- 不开发新产品功能，不新增 A113+，不删/合并/重编号 A0–A112。真实素材、Windows、Provider/扣费、剪映现场与商业效果验收继续暂缓。
- 文档同步清单：`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`、`docs/AD_STUDIO_TASK_REGISTER.json`、`docs/AD_STUDIO_ACCEPTANCE_PLAN.md`、`docs/AD_STUDIO_ACCEPTANCE_SOP.md`、`docs/AD_STUDIO_PRODUCT_ROADMAP.md`、`docs/AD_STUDIO_AI_HANDOFF.md` 与 `docs/AI_AD_STUDIO_FUTURE_FEATURE_MEMO.md` 已同步 A80–A84 部分映射和已知缺口。
- 下一批 A85–A89。先核验最终文档 HEAD 的 CI Push、CI PR、docs-sync Push、docs-sync PR 全部完成且 success。

---



---

---



---



---



---

# 桌面项目接手状态｜PLAN-003 A50–A53 部分证据映射｜2026-10-15

- 唯一权威进度与下一项：`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`。PR #32 保持 Open/unmerged。
- 本轮 A50–A53 已做部分映射，均保持 `acceptance_status=not_audited`，路线图阶段均为阶段1「可靠的生产底座」。
- 关联候选：A50↔A56；A51↔A52/A43；A52↔A51/A55/A57/A60/A61/A63/A64/A99；A53↔A43/A45/A54/A57。保留所有原始编号，不合并。
- 证据 SHA 指向源代码/测试快照 `5fe7fe19b9827aad26787eb05ba93dc18e48b6be`，不等于当前文档 HEAD；因此当前 HEAD 精确证据数为 0。
- 指标：需求文本级复核 113；source/test/ci/workflow 指针记录 54；任意 evidence 66；路线图映射 97；待映射 16；当前 HEAD 精确证据 0；完整代码/测试审计 0；完整审计 0；语义去重未完成。evidence SHA 未逐文件绑定。
- 审计快照 `c14b9bf10ae80379c45e80b42224722aab8c31d7` 的 CI Push/PR 与 docs-sync Push/PR 均 success；新文档提交后重查四项。下一批 A54–A57。只做 PLAN-003 审计，不开发产品功能；真实 Windows/素材/Provider/扣费/剪映/投放继续暂缓。
- 下方既有内容均为历史接手快照；如与上述状态冲突，以总进度台账顶部为准。
---


## 最新接手状态｜PLAN-003 凭据异常文本与预算授权顺序｜2026-10-15

- 文档审计基线：`c0eb959e1b281d22a6905b155904ef131d0267e8`。本轮只做静态证据核验与文档同步，不改产品代码、不运行本地测试、不连接真实 Provider/代理、不产生真实扣费。
- 新确认：`ModelRouter.complete_json()` 将请求失败的 `str(exc)` 写入 `usage-ledger.json`；实拍转写异常可持久化到项目 `creative_plan.footage_transcripts`；成本结算恢复记录也会保存异常文本。视频 Provider HTTP 错误正文前 1000 字符、转写 HTTP 错误正文前 800 字符会进入异常文本。
- 没有证据证明 API Key 实际被错误正文回显或泄露；结论只能是“异常文本可能持久化，脱敏行为尚未验收”。本轮检查的核心模块未发现常规 logger 调用，桌面 UI 未发现显式导出/备份入口，但全仓库、打包脚本与手工备份盘点未完成。
- 已直接确认 `App.create()` 在预算确认前调用创意模型；实拍模式还会先执行视觉分析、可选转写和剪辑规划。因此取消预算弹窗不能撤销之前可能已发出的模型请求，属于既有授权合同的 P0 候选阻断。
- 静态检查 `test_model_router.py` 与 `test_desktop.py` 的相关用例，未找到直接证明异常正文脱敏、假 API Key 不进入账本/项目恢复数据、或预算确认前外部调用计数为零的专项测试。
- 下一步唯一主线：将以上证据逐条对照 A0–A112 原始合同，重点 A13、A29、A30、A51–A65；核对合同、直接测试和状态冲突。保持 `fully_audited=0`、`semantic_dedup_completed=false`、`code_test_evidence_audit_completed_ids=0`；不新增 A113+、不发布总体完成率、不开发产品功能。PR #32 保持 Open / unmerged；真实环境验收继续暂缓。


- 仓库：`konggu888/ecommerce-agent`；项目：`apps/ad-studio-desktop`；分支：`feat/product-drama-visual-review`；PR #32 必须保持 Open / unmerged。
- **唯一权威进度与下一项**：`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`。当前进入 PLAN-003 全量跨来源语义去重、状态冲突裁决与依赖/证据边界复核；A0–A112 台账及分批静态映射已存在，不能重建或重复从 A50 开始。
- 最近一次已完整核验通过的基线：`8e2a714abfc77e6ce9f7e136a0ba41195f2c8fae`；该 SHA 的 PR-triggered CI 与 docs-sync 均 success，Netlify deploy-preview success。之后又提交了审计/帮助/逻辑文档更新，因此该状态**不是当前 HEAD 的通过证明**；接手时必须实时查最新 HEAD、CI、docs-sync、部署预览，Push-triggered CI/docs-sync 未独立核实前必须注明。
- 当前继续 PLAN-003 跨来源语义/状态冲突与证据边界审计，当前子问题是预算授权时点、Provider 自动回退、密钥保存、未知费用与外发数据。仅做审计和台账裁决，不开发产品功能、不删/重编号 A0–A112、不赋权、不计算总体完成率。真实 Windows、真实素材、Provider/扣费、剪映现场、真实投放与商业效果验证继续暂缓。
- **七层结果证明标准已纳入全项目证据规则**：软件运行、功能行为、端到端流程、普通用户可用、商品表达真实安全、商业成片质量、真实商业效果；详细定义和禁止替代关系见总进度台账及执行控制协议。台账规范化时逐项映射，不新增正式验收 ID。
- **用户自由度已纳入 PLAN-003**：规范化 A0–A112 台账时必须映射选择/控制/知情/撤回纠正四个维度，核对模型与 Provider 选择、自动回退授权、数据外发告知、费用不确定性、密钥保存、缓存/历史隔离及取消后外部调用为零的证据。详见 UXS-2 与执行控制协议；不新增正式验收 ID，不启动产品功能开发。
- 下方历史快照仅供追溯；其中的旧 SHA 和“下一项”不得作为当前执行指令。冲突以总进度台账为准。

---

# 【历史接手快照｜UXS-2 用户旅程证据映射｜2026-10-15｜不可覆盖总进度台账】

- 审查入口：`docs/AD_STUDIO_USER_EXPERIENCE_SAFETY_AUDIT.md`；本轮已完成“创建入口、商品输入、费用授权顺序、项目持久化”的首轮静态证据映射（第 3A 节）。这是审计，不是新产品功能开发。
- 首个重要合同/证据冲突候选：`App.create()` 在显示 `AI创意与项目预算确认` 前调用 `create_plan/create_plans`；`ModelRouter.create_plan()` 对九个阶段调用 `complete_json()`。HELP/PROJECT_LOGIC 当前允许确认前进行 AI 分析，但用户费用授权范围是否覆盖收费规划模型调用尚待裁决。若所有收费云端模型调用都必须先确认，则是 P0 候选阻断；若只限制视频/资产生成 Provider，则需核实规划调用费用是否披露/计入预算。实际收费影响依赖模型路由，当前未修复、未新增验收编号、未改产品代码。
- 已查测试证据：`test_setup_form_grid_rows_do_not_overlap` 为 AST 布局检查；`test_product_parser.py` 覆盖解析器异常/回退；`test_budget_policy` 与 `test_cost_breakdown_is_auditable_and_configurable` 覆盖费用计算；`test_project_save_load`、`test_project_lifecycle_isolated_between_projects` 覆盖持久化/隔离。未发现 `test_desktop.py` 直接调用 `App.create()` 的测试；`test_a33_full_flow.py` 仅测试模拟最终交付，不证明创建前确认顺序。
- 本文件已与 UXS-2 首轮映射、进度台账和 AI handoff 同步；最新审查文档 SHA 需以 GitHub 分支实时 HEAD 为准。开始基线 `3bd083e73ea51aec26b2ab66c755aa6c83a929cf` 的 PR CI `38695479000` 与 PR docs-sync `38695478983` success；Push-triggered 两项未独立核实。每次新提交后重查可用的当前 SHA 工作流。
- 上述 UXS-2 任务文字属于历史接手快照，不能覆盖总进度台账。当前唯一任务以 `docs/AD_STUDIO_PROGRESS_DASHBOARD.md` 顶部为准：PLAN-003 全量跨来源关系/状态冲突裁决。只审计和记录；不得删/重编号 A0–A112，不计算总体完成率。
- 状态口径保持：`code_test_evidence_reviewed_ids=113` 仅表示已开始映射；`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false`。Windows 真机、真实素材、Provider/实际扣费、剪映现场和真实投放/商业效果验证继续暂缓；PR #32 不合并。

---

# 【PLAN-003 最新接手状态｜A100–A112 部分证据映射｜2026-10-15】

- 本轮开始基线 `14ac6d153cf2f9027d02ff71a82ff8facc643768`：CI Push、CI PR、docs-sync Push、docs-sync PR 四项均 success；PR #32 Open / unmerged。新提交后必须重查最新 SHA 的四项工作流。
- 本轮完成 A100–A112 静态代码/测试证据映射；全部仅部分映射，不代表每项正式验收完成。台账 `code_test_evidence_reviewed_ids=113`（A0–A112 均已开始映射），`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false`。
- 重点裁决：A100/A101/A103 单镜头淡化与音画同步分开；A104 是跨镜头 xfade/acrossfade；A105/A106/A107 分别是 pacing、角色决策、运行时字段执行；A108 字幕生成与 A112 实际 cue 保护分开；A109/A110/A111/A112 的音乐卡点链路仍保留独立合同。1080P 输出尺寸不等于真实细节增强。
- 已找到专项测试线索：A100–A103 在 test_postprocess.py；A104 在 test_ffmpeg.py；A105–A107 在 test_creative_engine.py；A108 在 test_subtitles.py；A109–A112 在 test_music_sync.py；最终 1080P/媒体 QC 在 test_desktop.py。所有这些仍是静态证据映射，真实素材、Windows、真实口播/听感和商业质量暂缓。
- 下一步唯一主任务：全量跨来源去重与状态裁决，对照 A0–A112 正式验收计划、路线图、未来功能备忘、验收 SOP、任务登记表和执行控制文档；核对重复段落、转义换行和历史状态冲突。不得删 ID、补造编号、计算总体完成率或开发新产品功能。

---

# 【PLAN-003 最新接手状态｜A83–A99 部分证据映射｜2026-10-15】

- 本轮开始基线：`a2dd27fa6df1fb17cdaf2914b7633649809bd901`；CI Push、CI PR、docs-sync Push、docs-sync PR 四项均 success。新提交之后必须按最新 SHA 重查四项检查。PR #32 保持 Open / unmerged。
- 本轮完成 A83–A99 静态代码/测试/文档证据映射；全部仅部分映射，不宣称正式验收完成。台账 `code_test_evidence_reviewed_ids=100`、`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false`。
- 重要裁决：A83/A84 单集与跨集承诺承接分开；A85/A86/A87 状态持久化、因果闭环、可观察表演分开；A88 多人物依赖独立于可选状态台账；A89–A96 文本锁定/物理 ID/失效保护/恢复重试分层；A97/A98 恢复摘要稳定性分开；A99 成功账本下清除未计费兄弟镜头陈旧成本，和 A57/A59 相关但不合并。
- A84–A87 计划仍有未勾选项；A89–A96 的通过记录来自历史 SHA，当前 HEAD 需重新验证；A97/A98/A99 的直接测试名已找到，但要确认所有断言及当前 SHA 运行结果。A88 计划/逻辑文档中的重复段落与字面量转义换行已在本轮统一清理；仍需按最新 SHA 检查文档同步和 CI。
- 下一步：完成新 SHA 四项 CI/doc-sync 检查；全绿后继续 A100–A112 并检查商业剪辑专项/A102 1080P 条款。若失败先读日志修复。不得开发新产品功能、不得计算总体完成率；真实 Provider/扣费、Windows 真机、真实素材、剪映与真实投放继续暂缓。

---

# 【PLAN-003 最新接手状态｜A68–A82 部分证据映射｜2026-10-15】

- 本轮开始基线：`c6c6294f0d1626cf6a8f65ccd364ae476a2e5520`；CI Push、CI PR、docs-sync Push、docs-sync PR 四项均 success。提交新 SHA 后必须重新查询四项检查。PR #32 保持 Open / unmerged。
- 本轮已对 A68–A82 完成静态代码/测试/文档证据映射，全部仅部分映射。台账 `code_test_evidence_reviewed_ids=83`、`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false`。
- 主要证据：A68 后续集影响报告；A69/A70 故事引擎与结构审查；A71/A72 备选方向和人物动机；A73/A74 因果链与文本证据；A75/A76 商品事实/卖点覆盖；A77–A82 镜头事件、行动依据、人物绑定、关系变化、状态连续性和知识时间线。
- 重要缺口：A77–A80 在正式验收计划中仍有未勾选/开发中状态。不得因逻辑文档写有实现说明、测试文件里有相关用例或旧 SHA CI 曾绿，就改写为当前验收完成；需逐项核验专门正反例、调用链和最新 SHA 证据。A81/A82 的历史 SHA 记录不自动替代当前 HEAD 证据。
- 下一项：完成新 SHA 四项 CI/doc-sync 核验；全绿后继续 PLAN-003 A83–A99。若失败先查日志修复。不得开发新产品功能、不得计算总体完成率；真实 Provider/账单、Windows 真机、真实素材、剪映和真实投放继续暂缓。

---

# 【PLAN-003 最新接手状态｜A50–A67 部分证据映射｜2026-10-15】

- 本轮开始基线：`707758608e105840f21d4945aa40b3eb89b00522`；该 SHA 的 CI Push、CI PR、docs-sync Push、docs-sync PR 均 success。新提交 `707758608e105840f21d4945aa40b3eb89b00522` 之后，四项新 SHA 工作流尚待核验；不要沿用旧 SHA 的绿灯结论。PR #32 保持 Open / unmerged。
- 本轮对 A50–A67 完成静态证据映射，全部只是部分映射，不宣称正式验收通过。台账 `code_test_evidence_reviewed_ids=68`、`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false`。
- 关键证据：A50/A56 提示词真实换行行为合同与后续回归修复；A51 费用预估输入校验；A52 失败尝试成本去重；A53/A54 旧视频有效性与恢复；A55/A57/A59/A60/A61/A63/A64/A65 成本账本/恢复/迁移保护；A66/A67 人工视觉证据有效性与失效复查。
- 保留裁决：A50/A56 不合并；A57 在正式计划中有两个独立场景（成本待核对 UI、项目恢复与成本对账）；A61/A62 不合并。A66 文件校验不能代替商品真实性判断，A67 历史 passed 状态不能覆盖证据失效。
- 下一项：完成新 SHA 的四项 CI/doc-sync 检查；全部成功后继续 PLAN-003 A68–A82。若失败先读取日志并修复。不得开发新产品功能、不得计算整体完成率；真实 Provider/账单、Windows 真机、真实素材、剪映与真实投放继续暂缓。

---

# 【PLAN-003 最新接手状态｜A34–A49 部分证据映射｜2026-10-15】

- 当前最新提交：`b48f7a9859476ed639bc9220035c986cd5e77c37`；该 SHA 的 CI Push、CI PR、docs-sync Push、docs-sync PR 四项均成功；PR #32 Open / unmerged。
- 本轮已对 A34–A49 做静态代码/测试/文档证据映射，全部仅部分映射，不宣称正式验收通过。台账 `code_test_evidence_reviewed_ids=50`、`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false`。
- 重点证据：A34 AI 视觉对比的差异拦截/不自动批准/输入校验测试；A35/A36 单镜头修复、可编辑草稿与费用/版本防护；A43–A49 旧视频恢复、稳定短剧镜头映射、失败状态 UI、素材解析失败、裁剪安全输出与多段临时文件清理测试。
- 仍需逐项确认实际调用链、失败边界、UI 状态、跨项目/跨镜头隔离和每项直接断言；相关任务不因链路相连而合并。A37 草稿换行不等同于 A50/A56 视频提示词换行回归。
- 注意：接手文档下方有历史 SHA、PR 状态与旧任务指令，均为历史记录；新会话以本段、实时 GitHub HEAD/PR/四项 CI 和进度台账为准。PR #32 不合并。
- 唯一下一项：PLAN-003 继续 A50–A67 代码/测试证据审计，特别保留既定的 A50/A56、A57 内两个独立场景、A61/A62 不合并裁决。暂不开发产品功能、不计算整体完成率；Windows 真机、真实素材、真实 Provider/扣费、剪映和真实投放继续暂缓。

---

# 【PLAN-003 当前进度｜2026-10-15｜本段优先于下方历史记录】

- 最新完整核验基线（本次接手前）：`1fd6d08dac970cb7886c59239b05c4f6e2128cf9`；CI Push `38691577983`、CI PR `38691582839`、docs-sync Push `38691577999`、docs-sync PR `38691582806` 均 success。PR #32 当前 Open / unmerged；任何新提交后必须重新核验四项结果。
- A0–A5 本轮证据映射（未正式验收）：A0 `App.create()` 入口存在，缺专门启动/创建 UI 操作覆盖；A1 缺任务级稳定性矩阵；A2 有项目隔离与 save/load 测试，缺直接 `App.create()` 编排测试；A3 有布局 AST、三类任务策略和 task_type 持久化测试，完整 UI 流程未验收；A4 有扫描、不可解析素材记录、重复素材评分、废片归档及保护引用源文件测试，覆盖矩阵仍不完整；A5 已实现关键帧提取/视觉清单，但已检查的 desktop `test*.py` 未发现 `extract_keyframes()` / `build_visual_manifest()` 专项测试，视觉分析失败回退也待核验。

---

---

# 【最新接手指令｜规划体系优先｜2026-10-14】

- 规划体系实施前 HEAD：`7cfabb23e9ab0c05c6189d31dcf6b7410f7934c7`；该 SHA 的 CI Push 38571014259、CI PR 38571022693、docs-sync Push 38571014277、docs-sync PR 38571022758 均 success。规划体系新提交后必须重新查询 HEAD 与四项工作流。
- PR #32 保持 Open / unmerged。Windows 真机、真实素材、真实 Provider/扣费、剪映现场、真实投放数据继续暂缓。
- 用户已批准先建立完整计划与 AI 执行控制体系。执行协议：`docs/AD_STUDIO_EXECUTION_CONTROL.md`；总进度：`docs/AD_STUDIO_PROGRESS_DASHBOARD.md`；战略路线图：`docs/AD_STUDIO_PRODUCT_ROADMAP.md`。
- A112 已完成自动化阶段；下方“下一项 A112”等旧文字均为历史记录，不得用作当前指令。
- 当前唯一任务：PLAN-003，全量盘点 A0–A112、路线图任务、未来功能备忘和 SOP 检查点；去重映射、核验代码/测试/当前 SHA 证据。完成前不计算整体完成百分比。
- 每轮开始前重新检查当前 HEAD、PR #32 和 CI Push、CI PR、docs-sync Push、docs-sync PR；一次只执行一个有明确停止条件的任务。
- 桌面代码变更同一提交同步八份强制文档；规划变更同步所有受影响入口，避免无意义重复提交。

---

# 【最新接手状态｜A112 自动化 CI 已通过｜2026-10-14】

- 仓库：konggu888/ecommerce-agent；分支：feat/product-drama-visual-review；PR #32 保持 open/unmerged。
- 当前已完成 A112：SRT 实际 cue 时间窗在证据有效时进入音乐卡点内容保护；缺失/损坏/越界/版本不匹配时安全回退。经修正后代码基线 SHA e8deb1ec4ef9edf7d999c79539762ea2627affab 的 CI Push、CI PR、docs-sync Push、docs-sync PR 四项均 success。任何后续提交必须重新检查新 SHA。
- A112 代码基线 SHA e8deb1ec4ef9edf7d999c79539762ea2627affab 四项检查均 success：CI Push 38570453607、CI PR 38570460103、docs-sync Push 38570453565、docs-sync PR 38570460195。后续提交必须重新核验。
- 首轮 A111 CI 曾失败 3 个旧断言，根因是断言仍要求整组回退，与 A111 局部回退设计冲突；修复测试预期与审计原因后，最终 SHA 四项检查全部成功。没有隐瞒中间失败。
- 代码、测试与八份强制文档/路线图已同步。A112 自动化阶段完成；下一步先复核阶段 2 剩余退出条件与路线图，不将自动化绿灯误当作商业成片验收。
- Windows 真机、真实素材、真实 Provider/扣费、剪映现场、真实听感和商业效果仍暂缓。PR #32 不合并。

---

---

---

---

---

---

# 【历史接手状态｜2026-10-14｜已由文件顶部 PLAN-003 当前状态取代】

> 本段优先级高于下方旧历史记录；如果下方内容提到旧 PR、旧 SHA 或旧任务，请以本段和 GitHub 实时状态为准。

## 历史路线图执行指令（2026-10-14；当前执行以文件顶部 PLAN-003 为准）
- 唯一战略路线图：`docs/AD_STUDIO_PRODUCT_ROADMAP.md`。所有 AI 接手后必须按该路线图执行，不可直接沿用旧备忘录里的开发顺序。
- 历史基线为 `83549d4ca428adc233d61da292e2f245d498da0d`；该记录仅供历史追溯，不是当前 HEAD。当前最新完整核验基线为 `464977a54e9784fff375ffe081985624688261e9`，四项 CI/doc-sync 均 success。
- 历史主攻记录：阶段 2“商业级剪辑决策层”；A109“音乐节拍与画面切点真实联动”已提交自动化实现。该记录不覆盖当前 PLAN-003；接手者先检查最新 HEAD、完整 CI 与 docs-sync，再修复任何失败。实现涉及项目级统一 BGM、节拍分析、实际镜头时长计划、同步变速、拼接后统一混音和 1080P 输出；真实音乐/口播/Windows 质量验收仍暂缓。
- A108 是字幕基础时间轴与密度风险提示，不代表语义口播对齐、真实画面可读性或商业成片质量已验收。
- PR #32 保持 open/unmerged。Windows 真机、真实素材、真实 Provider/扣费、剪映现场与真实投放数据验证继续暂缓。

- 仓库：`konggu888/ecommerce-agent`
- 项目：`apps/ad-studio-desktop`
- 分支：`feat/product-drama-visual-review`
- 商业剪辑焦点定位功能提交：`fe3dcfde8e78f7d5d079fcbc1ed99d6265a79dbb`
- 该功能提交对应的 CI push、CI PR、docs-sync push、docs-sync PR 均已 success；此后若 HEAD 有变化，必须重新检查最新 SHA 的四项结果。
- PR #32 保持 open/unmerged，未经用户明确许可不得合并。
- 用户最新优先级：暂停费用对账/单镜头重试保护检查线，继续推进未来路线图第 5 项“商业级剪辑决策层升级”。
- 用户新增硬性画质要求：最终导出最低为 1080P 级。A102 已实现最终拼接后统一归一化转码：9:16 1080×1920、16:9 1920×1080、1:1 1080×1080，并由 ffprobe 拒绝低于该尺寸的交付结果。注意这保证像素尺寸，不代表已实现 AI 超分/细节恢复；A102 当前 SHA 的 CI/doc-sync 需检查。
- 已完成的小步：修正 `focus_x/focus_y` 语义，让它们表示缩放后源画面中的主体/视觉焦点归一化位置；裁切窗口在合法边界内尽量将焦点放到输出画面中心。新增 `test_postprocess.py` 检查实际 FFmpeg 参数、边界夹紧及非法/非有限输入回退。
- 商业剪辑决策层 A106 已新增：`resolve_editing_intent()` 根据分镜文本角色补齐缺省时长/节奏/转场，并将理由与参数来源存入 `editing_intent`；显式参数优先。A106 基线 `884c45dd8524abf4c4ebf7ee7fc8daa67987f686` 的 CI Push/PR 与 docs-sync Push/PR 均 success；A107 本轮修改提交后必须重新核验四项。
- 本轮目标不是宣称商业剪辑整体完成。文本关键词规则不等于画面理解；画面驱动节奏、音乐卡点、字幕密度、商品展示节奏和剪后反馈仍待开发/验收。
- 这只是“焦点参数真正影响裁切”的单项修复，**不是商业剪辑整体完成**。下一步应建立/完善可追溯的商业剪辑决策层：解释镜头商业角色、选择理由、节奏/时长理由、转场理由，并保证决策确实影响实际执行；后续再做字幕信息密度、音乐卡点、镜头衔接与剪后反馈。
- 先读本段，再读 `docs/AD_STUDIO_AI_HANDOFF.md`、`PROJECT_LOGIC.md`、`HELP.md`。每次代码修改必须同步 HELP、PROJECT_LOGIC、本文件、验收计划、验收 SOP、AI handoff 和未来功能备忘。
- Windows 真机、真实 Provider/实际扣费、剪映现场验收继续按用户要求暂缓；不得把 CI 绿灯或命令字符串测试等同于真实商业成片质量验收。

---

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


## A88｜多人物状态依赖一致性
- 新增每集可选 `continuity_state.cross_character_dependencies`，声明人物间知识、关系或承诺依赖。
- 检查双方人物、规则、证据和镜头引用；`same_understanding` 陈述不一致时警告，`asymmetric_knowledge` 缺少原因时警告。
- `different_beliefs_allowed` 允许不同信念，不将合理误解自动判成矛盾。
- 新增直接冲突、不同信念、知识不对称、未知人物和无效镜头引用测试。提交后以最终 SHA 核验 CI/docs-sync。
- PR #32 保持 open/unmerged；真实 Provider、Windows 真机、扣款/账单及剪映现场验收仍暂缓。


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


## 当前接手状态覆盖（2026-10-14；以本节为准）
- 当前分支：`feat/product-drama-visual-review`；PR #32 保持 open/unmerged，不得自动合并。
- A90 SHA：`8baa4339618f6a40fac4cdf0191eecf4eb0208cf`。以下 A91 提交的完整 CI 与 docs-sync 必须以最新 SHA 重新核验。
- A91：项目重新打开、任务恢复、单镜头生成/重生成前复核跨集锁定素材；失效时 fail-closed，保留原 asset_id 并记录恢复原因。
- Windows 真机、真实 Provider、实际扣款/账单核对、剪映现场验收继续暂缓。
- A91 补充保护：镜头素材解析先预检锁定 ID；一旦锁定失效，在任何其他缺失素材生成之前 fail-closed。

## A92 接手状态
- A91 最新 SHA `9e0dc1c89539444af7203fdcf88882fabfcd750f` 的 PR CI 与 PR docs-sync 已通过；push CI 曾出现长时间 in_progress，后续接手需再次核对是否结束。
- A92 新增端到端回归：两集目标镜头必须落到相同锁定 actor/scene ID，忽略相似标签替代素材，并在保存/重新打开后保留绑定。
- PR #32 继续 open/unmerged；Windows 真机、真实 Provider、实际扣款和剪映现场验收仍暂缓。

## A92 CI 修正待验证（2026-10-14）
- 首次 A92 CI 在保存/重载断言失败：测试调用 `resolve_assets()` 后直接 `load()`，遗漏 `store.save(project)`。
- 已识别为测试步骤遗漏；后续提交会在 reload 前保存已解析的项目，修复后的 SHA 需要重新确认 CI/docs-sync。
- 当前分支 head 为 A92 SHA `0758bfe5604ae31f604988bd3a320ede7f1b7ece`，该 SHA 的 PR CI 失败，不能标记 A92 通过；PR #32 继续 open/unmerged。


## A92 CI 根因与修复（2026-10-14）
- SHA `e01003444a268a2b8fa70a031d0bd2155ac062e7` 的 CI 失败位置为重载后 `restored.shots[1].actor_id` 为 `None`。
- 根因：`new_project()` 创建的默认镜头数不止一个；测试追加的第二集镜头并不一定处于列表位置 1，导致按位置断言检查错了镜头。
- 已修正夹具为仅包含 `first` 和 `second` 两个镜头；解析后明确断言两镜头绑定的 actor/scene ID 均为指定锁定值；重载后按稳定 `shot.id` 检查。
- 新 SHA 的完整 CI/docs-sync 未通过前，A92 仍不得验收完成。PR #32 保持 open/unmerged；真机、真实 Provider、账单与剪映验收继续暂缓。


## A93｜Provider 边界回归（新增，待最新 SHA 验证）
- 目标：直接调用单镜头 Provider 渲染入口，在锁定演员素材已停用时验证 fail-closed，而不只测试 resolve_assets() 的返回值。
- 验收点：Provider 调用次数为 0；抛出 SERIES_LOCKED_ASSET_INVALID；原锁定 ID 保留；不绑定相似素材；其他镜头状态/已有输出路径不变。
- 同镜头其他缺失素材不得在锁定失败前触发自动生成。
- 必须以新 SHA 的 CI push/PR 和 docs-sync push/PR 验证；PR #32 保持 open/unmerged。Windows 真机、真实 Provider、账单和剪映现场验收继续暂缓。


### A92/A93 自动化验收结果（2026-10-14；以本节为准）
- 最终代码与测试 SHA：`db8c2a4e80bdbd6a5d308848e84905c1c2a348d0`。
- CI push run `38470175403`、CI PR run `38470184669`、docs-sync push run `38470175408`、docs-sync PR run `38470184505` 均 success。
- A92 跨集锁定 actor/scene 精确 ID 已验证解析绑定、相似标签不覆盖、保存/重开后绑定持久化。
- A93 从 `_render_with_provider()` 入口验证失效锁定素材在 Provider 调用前拦截，Provider 调用次数为 0；保留原锁定 ID，不绑定替代演员，不影响其他镜头已有状态/路径。
- PR #32 保持 open/unmerged。以上仅为自动化测试；Windows 真机、真实 Provider、真实账单/扣款、剪映现场及生成画面视觉一致性继续暂缓。


## A94｜原锁定素材恢复后的重试（待最新 SHA 验证）
- 先停用原锁定演员，确认返回 SERIES_LOCKED_ASSET_INVALID 且不自动生成。
- 恢复同一 ID 的 active/reusable 状态，并保留一个标签相同的相似演员作为干扰项。
- 再次解析后必须绑定原 actor-fixed ID，source 为“跨集锁定素材复用”，generation_if_missing 为 false。
- 不允许因之前有失效恢复记录而永久阻断，也不允许改绑相似资产。
- 最新 SHA 的完整 CI push/PR 与 docs-sync push/PR 通过后才能标记完成。PR #32 保持 open/unmerged。


### A94 自动化验收结果（2026-10-14；以本节为准）
- 代码与测试 SHA：`289cc0954cb93ce1a218436d2a6137317a7c6130`。
- CI push run `38470748908`、CI PR run `38470757428`、docs-sync push run `38470748944`、docs-sync PR run `38470757442` 均 success。
- 失效阶段确认锁定素材错误并关闭生成；恢复同一 asset_id 后可重试并精确绑定原 ID，即使存在同标签相似资产也不替换；锁定 ID 仍禁止 fallback/自动生成。
- PR #32 保持 open/unmerged；真实 Provider、Windows 真机、账单/扣款、剪映现场与画面视觉一致性仍暂缓。


## A95｜损坏素材索引保护（待最新 SHA 验证）
- 使用无效/截断 JSON 模拟本地 `library.json` 损坏。
- 预期错误码为 `SERIES_LOCKED_ASSET_LIBRARY_UNAVAILABLE`，不得误报为单个资产不存在。
- `resolve_assets()` 必须 fail-closed，不处理同镜头其他素材，不触发补素材。
- `_render_with_provider()` 必须在 Provider 调用前拦截，计数型 Provider 调用次数为 0。
- 原锁定 ID 与其他镜头已有状态/输出路径必须保持不变。
- 最新 SHA 的 CI push/PR、docs-sync push/PR 全部通过后方可标记通过；PR #32 保持 open/unmerged。


### A95 自动化验收结果（2026-10-14；测试代码 SHA `6b225e09adac63265d53b27eae3ed6a54a51f49e`）
- CI push run `38471501401`、CI PR run `38471510428`、docs-sync push run `38471501250`、docs-sync PR run `38471510506` 全部 success。
- 无效/截断 `library.json` 返回 `SERIES_LOCKED_ASSET_LIBRARY_UNAVAILABLE`；素材解析提前停止，不继续处理其他素材；Provider 调用次数为 0。
- 原锁定 ID 保留，非目标镜头状态及已有输出路径保持不变。
- PR #32 保持 open/unmerged。真实 Provider、Windows 真机、实际账单/扣款、剪映现场和生成画面视觉一致性继续暂缓。


## A96｜索引修复后重试（待最新 SHA 验证）
- 先把 `library.json` 截断，确认返回 `SERIES_LOCKED_ASSET_LIBRARY_UNAVAILABLE` 且不自动生成。
- 修复索引，重新写入原锁定 ID，并保留同标签相似资产作为干扰项。
- 再次解析应成功绑定原 ID，来源为跨集锁定素材复用，`generation_if_missing` 仍为 false。
- CI push/PR 与 docs-sync push/PR 必须以最新 SHA 全部通过；PR #32 不合并。


### A96 自动化验收结果（2026-10-14；测试代码 SHA `fc01ace4eeb90ccb2f2df10b44a57f8b3c69f134`）
- CI push run `38471876626`、CI PR run `38471884325`、docs-sync push run `38471876601`、docs-sync PR run `38471884345` 全部 success。
- 索引损坏时返回 `SERIES_LOCKED_ASSET_LIBRARY_UNAVAILABLE` 并禁止 fallback；索引恢复后，重新解析精确绑定原锁定资产 ID，标签相似资产不能替换，且不触发自动生成。
- PR #32 继续保持 open/unmerged。真实 Provider、Windows 真机、账单/扣款、剪映现场与生成画面视觉一致性继续暂缓。


## A97｜单镜头恢复隔离（2026-10-14，待最新 SHA CI 验证）
新增回归覆盖项目恢复时仅重置缺失成片的目标镜头；有效兄弟镜头的输出路径、状态、版本和费用必须保持，保存/重开后仍一致。完成后需检查最新 SHA 的 push/PR CI 与 docs-sync 四项结果；PR #32 保持 open/unmerged。真实 Provider、Windows 真机、账单和剪映验收继续暂缓。


## A98｜恢复摘要幂等性（2026-10-14，等待最新 SHA 验证）
新增修复：项目第一次恢复发现缺失成片后，即使后续再次打开并恢复，尚未处理的镜头仍出现在 `missing_media` 中；普通未生成镜头不误报；有效兄弟镜头路径/状态/版本保持不变。修改后需检查最新 SHA 的 push/PR CI 与 docs-sync 四项结果。PR #32 保持 open/unmerged；真实 Provider、Windows 真机、账单与剪映现场验收继续暂缓。


## 2026-10-14：A99 已提交，CI 待验证
最新提交：`c8252dc58995289d8ca38dfd15dc8e66f8001eeb`。A99 修复恢复阶段的逐镜头费用快照残留：只要存在成功的实际费用账本记录，就以账本逐镜头对账；没有成功费用记录的镜头归零，防止单镜头显示旧金额而项目总额已更新。新增 `test_a99_successful_ledger_clears_stale_cost_on_unbilled_sibling_shot`，覆盖账本金额、未计费兄弟镜头归零及保存/重载。已同步 HELP.md 与 PROJECT_LOGIC.md。当前该 SHA 的 CI 与 docs-sync push workflow 已排队，不能提前宣称通过；下一步先确认该 SHA 的 CI、docs-sync push/PR 全部结束，再继续检查单镜头重试的版本与计费联动。PR #32 保持 open/unmerged；Windows 真机和真实 Provider/账单验收仍暂缓。


---

# 2026-10-14 接手状态更新：转向商业剪辑能力主线

> **下一位 AI 必须先读本段，再读本文件其余内容。** 旧段落中出现的历史 SHA、PR 编号和“本轮必须继续做的事”可能过期；以下面的当前状态和 GitHub 实际检查为准。

## 当前工作现场
- 仓库：`konggu888/ecommerce-agent`
- 分支：`feat/product-drama-visual-review`
- 本轮起始基线：`4713c6b024b2a4f407b3b9b4ac8fc4f2b6077597`
- 当前优先级已由用户明确调整：**暂停费用对账/单镜头重试保护检查线，优先推进未来路线图第 5 项“商业级剪辑决策层升级”。**
- Windows 真机测试、真实视频 Provider/真实扣款、剪映现场验收继续暂缓；PR 不得擅自合并。
- 已发现并修复：`postprocess.process_shot()` 原先接收 `focus_x/focus_y`，但 FFmpeg crop 仍固定居中，导致 AI 焦点参数没有影响实际输出构图。
- 代码变更：新增 `_normalized_focus()` 与 `_focus_crop_filter()`，把归一化焦点坐标实际写入 FFmpeg crop 的 x/y；越界坐标夹紧，NaN/Infinity/非法值回退中心。
- 新增回归测试：`apps/ad-studio-desktop/test_postprocess.py`，验证生成的 FFmpeg 命令包含焦点坐标，并覆盖边界/异常值。
- 本轮代码提交：`6beb0786b2cf94dedfc146bd7672e2be3bdeac76`；测试提交：`3c47efafb317b42157c7a4054ff4b9d479250b63`；帮助文档提交：`c5b0634b88e1e2df2333d358ddacf4942aa44704`。后续文档提交和 CI 状态必须按最新 SHA 重新确认。
- 下一步严格顺序：检查最新 HEAD/PR 与 CI/docs-sync；运行新增焦点裁切回归测试及桌面全量单测/语法检查（若无法运行必须如实说明）；再继续商业剪辑决策链审计。
- 后续重点：目标驱动的镜头节奏、真实动态裁切/焦点执行、镜头衔接与转场判断、字幕信息密度、音画节奏/音乐卡点、商品展示节奏、剪后质量反馈。
- 每次代码修改必须同步 HELP、PROJECT_LOGIC、SESSION_HANDOFF、验收计划、验收 SOP、`docs/AD_STUDIO_AI_HANDOFF.md` 和根目录未来功能备忘。
- 不得把基础 FFmpeg 拼接、结构化参数或 CI 通过描述为“商业级剪辑已完成”。路线图第 5 项继续保留，直到各能力实现并正式验收。


## 2026-10-14 最新接手更新：商业剪辑焦点语义校正
- 接手时必须重新查询分支 `feat/product-drama-visual-review` 的最新 HEAD、PR #32 和该 SHA 的 CI/docs-sync；当前修正基于起始 HEAD `728e786a7adcbdab1e110c86e4dd99fbf08d9033`，不能沿用起始 SHA 的 CI 作为新提交验收。
- 继续暂停费用对账/单镜头重试保护线；当前主线是商业剪辑决策层。
- 焦点坐标语义明确为“缩放后源画面中的主体/视觉焦点归一化位置”，不是裁切窗口偏移量。裁切窗口尽可能把该焦点放在目标画面中心，并用 FFmpeg 的 max/min 表达式限制在画面边界内；没有多余画面可裁的轴保持边界位置。
- `adapt_aspect()` 是独立的中心裁切工具，不声称执行 AI 焦点；需要焦点驱动的单镜头处理应走 `process_shot()`。
- `test_postprocess.py` 验证实际传给 FFmpeg 的 `-vf` 字符串、焦点定位表达式、边界夹紧及非法/非有限输入回退。它不等于真实视频画面已视觉验收。
- 下一步：检查最新提交四项 CI/docs-sync；在可用的本地仓库环境运行桌面全量单测与语法检查；随后继续审查目标驱动的节奏、镜头衔接、字幕密度、音画卡点和剪后反馈。
- 必须同步维护 HELP、PROJECT_LOGIC、本文件、验收计划、验收 SOP、`docs/AD_STUDIO_AI_HANDOFF.md` 和根目录未来功能备忘。PR #32 保持 open/unmerged；Windows 真机、真实 Provider/扣费和剪映现场验收继续暂缓。

## 2026-10-14 最新接手补充：文档同步 CI 扩围（本次变更后需重新查 CI）
- 已发现旧的 `tools/check_ad_studio_docs.py` 只强制检查 HELP.md 与 PROJECT_LOGIC.md，覆盖范围小于项目既定接手规则。
- 本次将其扩展为要求同一桌面代码/测试变更同时修改八个规则/文档文件，并增加自动化契约测试。
- 变更后必须重新查询本分支最新 HEAD 对应的 CI push、CI PR、docs-sync push、docs-sync PR；不能把本次变更前 SHA 的绿色结果当作本次结果。
- 文档检查只验证规定文件是否出现在同一差异中，不证明文档内容语义完全正确；仍需审阅差异，并将 docs-sync 与完整 CI 分开报告。
- PR #32 继续保持 open/unmerged；不执行合并。


## 2026-10-14｜A100 商业剪辑淡出修正（本轮待 CI）
- 起始 SHA：`7358148776e10775edff98b69273c5d29fab7ec5`；该 SHA 的 CI push/PR 与 docs-sync push/PR 已全部 success。
- 本轮修正 `postprocess.process_shot()`：旧“淡出”滤镜从 0 秒开始，实际会在镜头开头淡出。现在先读取输入时长，再按速度计算输出时长，将淡出放到处理后镜头尾部；极短镜头会缩短淡出时长。
- 新增 `test_postprocess.py` 两个回归：变速后的末尾淡出、短片段边界。
- 本次新 SHA 的完整 CI 与 docs-sync push/PR 必须重新核验，未通过前不标记 A100 自动化验收完成。
- 后续继续商业剪辑决策层：镜头节奏、真实镜头间转场、字幕信息密度、音画节奏/卡点、商品展示节奏、剪后质量反馈。不能把本次局部滤镜修正说成商业级剪辑已完成。
- PR #32 保持 open/unmerged；Windows 真机、真实 Provider/扣费和剪映现场验收继续暂缓。


## 2026-10-14｜A101 变速音画同步修正（本轮待 CI）
- 前置提交 `523dd66bd09b6892aa3c5ac862d531493d115a01` 的完整 CI push/PR 与 docs-sync push/PR 均已通过，A100 自动化验收完成；Windows 真实画面/听感仍暂缓。
- 本轮在 `postprocess.process_shot()` 为非 1.0 倍速增加 `atempo`，使原音轨与 `setpts` 调整后的画面时长保持一致；正常速度不加音频变速滤镜。
- 新增两个回归测试，分别覆盖 1.25 倍速和 1.0 倍速。
- 新 SHA 的完整 CI 与 docs-sync push/PR 需要重新核验后，才能确认 A101 自动化验收。
- 商业剪辑路线图仍未完成：真实镜头间衔接、字幕信息密度、音乐卡点、商品展示节奏、剪后质量反馈；不要把基础变速修复描述为商业剪辑整体完成。
- PR #32 保持 open/unmerged；Windows 真机、真实 Provider/扣费和剪映现场验收继续暂缓。


## A102：最终成片最低 1080P 级输出（待 CI）
- 最终拼接结果先进入临时文件，再经 `normalize_output_resolution()` 归一化转码后成为交付输出。
- 最低输出：9:16 1080×1920；16:9 1920×1080；1:1 1080×1080。ffprobe 质检拒绝尺寸不足的输出。
- 新增测试：后处理命令覆盖竖屏/横屏/方形配置；最终媒体质检覆盖 720×1280 竖屏拒绝。
- 这只是最低像素尺寸保障，不等于 AI 超分、去噪或细节恢复。Windows 实机画质检查仍暂缓。
- 当前提交 SHA 的完整 CI 与 docs-sync push/PR 结果待确认；PR #32 必须保持 open/unmerged。

A102 后续修正：首轮 CI 暴露测试夹具没有模拟归一化阶段输出文件、以及一条 FFmpeg 参数断言检查错位置；已修复夹具并调整断言。当前最新 SHA `cf21060274bf1eb3dc0b1b37e19ae81aec3d1b05` 的 CI/doc-sync 需重新确认。


## A103：镜头淡入/淡出音画同步（待 CI）
- 修改 `ad_studio/postprocess.py`：淡入/淡出时同时处理视频和原音轨，按变速后的输出时长计算窗口，短镜头自动缩短淡化时长。
- 新增测试覆盖变速淡出音频滤镜、短片段淡入及常速淡出。
- 这项是单镜头淡化；相邻镜头交叉溶解、节奏分析和音乐卡点仍未完成。
- 当前提交的完整 CI 与 docs-sync push/PR 结果待确认；PR #32 保持 open/unmerged。

## A104：相邻镜头真实交叉溶解（当前提交待 CI）
- 最新改动在 ffmpeg.concat_with_transitions() 中使用真实 xfade 画面交叠和 acrossfade 音频交叠，按镜头实际时长计算 offset；无音轨输入生成等长静音。
- ProductionStore.build_final() 仅在非首镜头的 transition == “交叉溶解”时启用；其他项目保留原 concat。
- 新增 test_ffmpeg.py 覆盖滤镜图、无音轨补静音与配置数量校验。
- 当前提交的 CI push/PR 与 docs-sync push/PR 尚待核验。PR #32 必须保持 open/unmerged；Windows 真机、真实 Provider/扣费和剪映现场验收继续暂缓。


## A105：分镜节奏默认值接入实际播放速度（当前提交待 CI 核验）
- `creative_engine.validate_plan()` 现在将 pacing 标签映射为可执行速度默认值：慢 0.85x、标准 1.0x、快 1.15x、极快 1.3x。
- schema 中 `speed` 可省略；显式 `speed` 优先，未知 pacing 回退“标准”。新增 `test_creative_engine.py` 覆盖四档映射、显式速度覆盖和未知标签回退。
- 下一步先核验当前最新 SHA 的 CI Push/PR 与 docs-sync Push/PR。不要把此基础映射描述为画面理解、情绪节奏或音乐卡点已完成。PR #32 保持 open/unmerged；Windows 真机验收继续暂缓。


## A106 接手记录：商业镜头角色驱动默认剪辑决策（待最新 SHA CI）
新增 `resolve_editing_intent()`，将分镜文本归类为 hook、product_detail、demonstration、proof、pain_point、reaction、cta 或 story_beat；仅在字段缺失时补齐默认时长、节奏/速度与转场，显式参数优先。决策理由、规则依据和参数来源写入 `CreativeShot.editing_intent`。新增测试覆盖主要角色、末镜 CTA 淡出和显式参数覆盖。首轮 CI 暴露未知 pacing 标签回退规则需兼容 A105，已修正为“标准”，并补充最终生效参数审计字段。修复提交后必须重新查询当前 SHA 的 CI Push/PR 与 docs-sync Push/PR；PR #32 保持 open/unmerged。文本规则不代表视觉理解，商业剪辑整体与真实素材验收仍未完成。

## A107 接手记录：商业角色时长进入运行时生成请求
A106 的角色默认时长没有从 `CreativeShot` 复制到运行时 `Shot`，导致视频 Provider 请求可能继续使用默认 3 秒。A107 新增 `runtime_shot_editing_fields()` 并由 `app._activate_plan()` 消费，映射 duration_seconds/pacing/speed/transition；测试覆盖商品细节镜头默认 4 秒。提交后核对当前 SHA 的 CI Push/PR、docs-sync Push/PR 四项。PR #32 保持 open/unmerged；Windows 真机、真实 Provider/实际扣费、剪映现场验收继续暂缓。商业剪辑整体仍未完成，下一步继续推进音乐卡点、字幕信息密度和真实内容驱动的剪后优化。


## A108 接手记录：字幕按实际镜头时长与信息密度自适应（修复提交后待重新核验）
`subtitles.py` 新增时间轴规划和密度分析；字幕加工 UI 使用 FFprobe 实际时长，不再固定 `duration=3`，按时长/文本长度切分 SRT，尽量在标点处断句，并在短镜头减少快速切换、提示高字/秒风险。请检查当前 SHA 的 CI Push/PR、docs-sync Push/PR 四项。PR #32 保持 open/unmerged；真实素材、Windows 真机和字幕可读性验收继续暂缓。下一项商业剪辑可继续推进音乐节拍与画面卡点，但不得宣称字幕高级优化已完成。

## A109｜音乐节拍与画面切点真实联动（本轮实现，须按最新 HEAD 复核 CI）
- BGM 由逐镜头混音改为项目级统一音轨：字幕加工时保存选择，最终拼接后一次性混入，避免同一歌曲在每个镜头重启。
- 新增 `ad_studio/music_sync.py`：本地 PCM 节拍候选分析、置信度、保守切点规划、音画同步变速和最终统一 BGM 混音。
- `ProductionStore.build_final()` 消费切点计划并渲染临时变速镜头；超出安全边界时保持原切点；最终归一化到既有 1080P 级配置。
- 新增 `test_music_sync.py` 覆盖合成节拍、静音、低置信度、调整边界、音画同步命令和全局 BGM 命令。
- 必须查询最新 SHA 的 CI/doc-sync Push/PR；本轮自动化实现不等于真实音乐/口播/字幕视觉质量验收。PR #32 仍不得合并，真实环境验收继续暂缓。

### A109 旧项目音轨兼容边界
A109 兼容边界：旧项目中已把 BGM 烧录进镜头音轨的成片，无法仅凭现有文件可靠分离旧音乐。重新使用全局 BGM 前，应从未混入 BGM 的镜头源重新执行字幕处理；否则可能叠加旧音乐。

### A109 转场安全补充
A109 转场安全补充：当前切点变速遇到显式“交叉溶解”时保守回退原镜头时长，仍保留既有交叉溶解与全局连续 BGM；待单独建模转场重叠时长后再开放这类边界的卡点调整。
\n\n## A112｜字幕实际时间窗接入（本轮代码提交后必须重新核验）\n已实现候选代码：字幕烧录后保存当前视频版本与 SRT 的绑定；严格解析 cue 时间窗并校验镜头时长；有效证据才进入音乐卡点保护，异常/缺失/不匹配写入逐镜头回退审计。新增 parser 和最短 cue 保护测试。代码基线 SHA e8deb1ec4ef9edf7d999c79539762ea2627affab 的 CI Push/PR、docs-sync Push/PR 已全部 success；仅自动化阶段通过，真实 Windows/素材/听感验收仍暂缓。真实 Windows/素材/听感验收仍暂缓。\n\n## A112 CI 中间结果与修复记录\n首个 A112 提交的 docs-sync Push 曾失败，原因是随后修正 SRT 转义的代码提交未同时触及强制文档；该提交的 PR docs-sync 通过不能替代 Push 结果。现重建为包含 SRT 解析修正和全部强制文档更新的单个提交链，必须检查新 SHA 的 CI Push、CI PR、docs-sync Push、docs-sync PR 四项。此记录保留失败事实，不得删除。



## 历史接手状态｜2026-10-15｜已由文件顶部 PLAN-003 状态取代
- 本段旧基线：3801204559bb05cb617a13ef249fe35db0030a50；它不是当前 HEAD，不能用来证明最新提交 CI。当前状态以文件顶部 PLAN-003 段和 GitHub 实时 Actions 为准。PR #32 仍须 Open / unmerged。
- A3 设置区布局修复与 AST 回归测试已提交，自动化 CI 全绿；仍未完成 Windows 真机验收，也未宣称完整 A3 验收完成。
- A68–A74 已从历史实现提交和 HELP/PROJECT_LOGIC/SESSION_HANDOFF 找回，正式验收计划/SOP及未来备忘已补回；A99 也已找回。113 个编号均有任务标题，编号缺口为 0。
- 需求文本级复核已记录 113 个编号，但最终跨来源重复/状态段合并审计尚未完成；代码/测试证据审计仅 A0–A5 部分映射，fully_audited=0、权重为空、总体完成率关闭。
- 下一项：继续 PLAN-003 最终跨来源去重和 A0–A5 逐项证据审计；不要顺手扩展产品功能。此 handoff-only 状态提交完成后仍需重新核验新 SHA 的四项 CI/doc-sync。


## PLAN-003 最新接手状态｜A12–A17 部分证据映射｜2026-10-15

- 最新提交基线：`177088ee6a743253d61dfe3ecb74842babe8e2a9`；上一基线四项 CI/doc-sync 已全部通过，PR #32 仍 Open / unmerged。新提交后仍必须重新核验四项工作流。
- A12：已定位 `hybrid_router.py` 的缺口分类、证据保护与预算路由；需补分类误报/漏报及 UI 提示映射。
- A13：已定位生成桥接、Provider 不可用与商品证据拦截测试、失败和人工复核闭环；真实 Provider/实际扣费暂缓。
- A14：已定位混合来源、待复核、最终渲染排除与 A23 闭环测试；最终逐镜头来源可追溯性仍需补证。
- A15：共享生产组件、音频、字幕、输出质检和 1080P 尺寸测试存在，但尚未证明全链业务目标一次性通过。
- A16：商品事实保护有相关测试；主体清晰、遮挡、细节、顺序与参数一致性没有在本轮证明已完成专项验收。
- A17：创意版本隔离和创意分析有测试；Hook/卖点/证明/CTA 的最终产物断言及真实投放效果未验收。
- 所有 A12–A17 只标记“证据已部分映射”，不代表正式验收通过。台账 `code_test_evidence_reviewed_ids=18`，`code_test_evidence_audit_completed_ids=0`；总体完成率关闭。
- 唯一下一项：继续 PLAN-003，审计 A18–A33 的计划、代码、专项测试、依赖/重复关系与当前 SHA；不开发新产品功能。Windows 真机、真实素材、真实 Provider/扣费、剪映现场及真实投放继续暂缓。


## PLAN-003 最新接手状态｜A18–A33 部分证据映射｜2026-10-15

- 本轮开始时基线：`53800b7845a9db49c329242506d80f6a1747281c`；该 SHA 的 CI Push、CI PR、docs-sync Push、docs-sync PR 均 success；PR #32 Open / unmerged。
- A18–A19：已映射版本状态隔离、物理输出路径、创意机制差异和禁止虚构投放指标的测试；原始版本追溯、实验设计字段需继续核验。
- A20–A25：已有事实边界、安全闸门、媒体质量、1080P 尺寸和无效输出拦截测试线索；逐条覆盖和当前基线独立复核仍未完成。
- A26–A30：已有历史修订独立性、交付复查、项目持久化、数据来源边界及失败恢复专项测试；不能推定正式清单全部子项都已覆盖。
- A31–A32：接手文档测试存在，但文本存在性/关键字段测试不能证明全部说明始终与最新实现一致。
- A33：三类用户流程离线回归存在，但媒体拼接、归一化和探针使用夹具/mock；不等于真实端到端或 Windows 实机验收。
- 本轮共覆盖 A18–A33 的部分映射；台账 `code_test_evidence_reviewed_ids=34`，`code_test_evidence_audit_completed_ids=0`，总体完成率关闭。
- 唯一下一项：PLAN-003 继续审计 A34–A49；不开发新产品功能。PR #32 保持 Open / unmerged。真实素材、Provider/扣费、Windows、剪映现场和真实投放继续暂缓。



## 2026-10-15 接手更新｜用户自由度 / 模型与 Provider 接入审计
- 当前审计分支 HEAD 基线：`aa825eaa106810e6a56b463b894053145f719864`。开始本轮时 PR #32 仍为 Open / unmerged；本轮提交后必须重新核对 PR head 与分支 ref 是否一致，不能沿用旧 SHA 状态。
- 已对 `model_router.py`、`providers.py`、`capability.py`、`app.py::model_settings` 与 `test_model_router.py` 做静态首轮审查，并将发现写入 `docs/AD_STUDIO_USER_EXPERIENCE_SAFETY_AUDIT.md` 的 UXS-2 专项节。
- 当前可证实：多模型池、按功能路由、自定义 Base URL / 模型 ID / API Key、OpenAI-compatible 本地服务通道、部分通用 REST 视频/资产 Provider；不能把它描述为任意模型/任意 API 无条件即插即用。
- 重点风险：规划模型可能在预算确认前调用；路由可能自动切换本地/云端；模型配置 JSON 保存完整 API Key；usage/价格缺失时成本估算可能为 0；外发数据告知、端点安全、换 Provider 后缓存/历史隔离证据不足。
- 证据限制：本轮为静态审查，没有运行测试，没有连接真实模型/Token 代理，没有核对实际账单。不得声称这些风险已修复或完成正式验收。
- 正式 ID 规则：不新增 A113+，不删/改号 A0–A112；先做语义去重和跨来源映射。完成率继续关闭，`code_test_evidence_audit_completed_ids=0`、`fully_audited=0`、`semantic_dedup_completed=false` 保持不变。
- 唯一下一步：继续 UXS-2 / PLAN-003，检查路由回退授权、密钥存储/导出、预算授权时点、外发数据提示、缓存键/历史项目可迁移性，并逐项映射 A0–A112。暂不开发产品功能；PR #32 必须保持 Open / unmerged；Windows 真机、真实 Provider/代理、真实账单、剪映和投放验证继续暂缓。


## 本轮审计提交链说明（2026-10-15）
- 模型/Provider 用户自由度首轮审计的完整证据与风险矩阵以 `docs/AD_STUDIO_USER_EXPERIENCE_SAFETY_AUDIT.md` 的 UXS-2 专项节为准；本接手文件仅保留执行摘要与下一步，避免复制整份审计导致版本漂移。
- 该审计当前只证明静态代码中存在相关配置/路由路径，不证明真实模型、代理、费用或 UI 已通过现场验收。下一步必须继续映射现有 A0–A112，不新增正式 ID。


## PLAN-003 接手更新｜路由回退与外发边界｜2026-10-15

- 最新已知审计提交：96b48068b069629ebf1c50caa4606c2635e0966b（dashboard 增补路由回退、未知费用、端点/数据外发边界）。此 SHA 是提交快照；新接手必须重新读取 GitHub 当前 PR #32 HEAD 和该 SHA 的 CI/doc-sync/部署状态，不能直接沿用历史状态。
- 本轮确认源码存在跨模型、以及本地资产/视频服务转云端的自动回退分支；尚无证据证明每次切换前都征得用户同意。
- 文本/视觉请求向配置 Base URL 发送提示词和可能的图像 data URI；视频/资产请求向配置 endpoint 发送请求。逐次外发告知与端点安全边界仍缺证据。
- 单价/usage 缺失可能使成本估算为 0；不能将该值解释为免费。模型、视频和资产配置存在普通 JSON 凭据写入路径；完整日志/导出/备份/迁移盘点尚未完成。
- 唯一任务仍是 PLAN-003：映射现有 A0–A112、消除语义重复与状态冲突、审计依赖和证据边界。不得新增 A113+、开发产品功能、分配权重或发布总体完成率。真实 Windows、真实素材、Provider/代理/账单、剪映和投放验收继续暂缓。


## 最新本轮验证快照更新｜2026-10-15

- 本轮文档更新前的已验证提交：c8d4d6463d07a1662e2d12917c5ec02dac4aa043；其 PR CI 与 ad-studio-doc-sync 均成功，Netlify 部署预览成功。更新本 handoff 会产生新提交，因此接手者必须再次读取 GitHub 最新 PR #32 HEAD，并核对该新 SHA 的 CI、doc-sync 与部署状态。
- 本轮已将路由自动回退、费用未知不能等于免费、自定义端点与图像数据外发边界，补充到 dashboard、UX safety audit、HELP、PROJECT_LOGIC、验收 SOP 和 AI handoff。
- 未修改产品代码；没有声称授权时点、自动回退授权、密钥加密、端点安全或实际账单问题已解决。PLAN-003 仍为唯一主线。


## 最新合同语义校准｜A29 不是端点/凭据安全合同｜2026-10-15

- 已重新读取正式验收计划与 SOP：A29 只管模拟/真实数据、AI推演/真实事实、用户输入/系统推断和平台数据来源，不等于 API Key 存储、外发告知、endpoint/redirect 安全或异常脱敏。
- A13 的范围是 AI 生成路由/预算/失败状态/商品事实/人工复核；A30 的范围是失败恢复。两者现有测试不能代替逐次回退授权、预算确认前零外部调用、异常正文脱敏的直接断言。
- A51–A65 是多个独立验收合同，不可整体合并。A57 的两个场景独立保留；A61/A62 不合并。详情见 `docs/PLAN003_UXS2_CREDENTIAL_AND_COST_EVIDENCE_2026-10-15.md` 和唯一权威台账 `docs/AD_STUDIO_PROGRESS_DASHBOARD.md`。
- 下一步继续映射 A0–A112 其余正式合同，确认是否存在直接覆盖端点/外发告知、凭据存储与异常脱敏的条款；若没有，登记为既有计划的合同缺口，不新增 A113+。不开发产品功能，不发布总体完成率。PR #32 必须 Open / unmerged；真实 Provider/扣费、Windows 真机、真实素材、剪映和投放验证继续暂缓。


## 接手提醒｜PLAN-003 发现台账指标口径冲突｜2026-10-15

- 当前权威 dashboard 声称 A0–A112 的跨文档部分证据映射已开始（计数 113）；但规范 JSON 台账仅有 18 个任务含 evidence、其中 6 个编号含 source/test/CI/workflow 证据，且没有证据 SHA 绑定当前 HEAD。
- JSON 台账仍有 70 个任务的 `roadmap_phase=待路线图映射`，与 dashboard 中“阶段 2–6 分批依赖映射已写入”的概括存在逐项落库/统计口径冲突。
- 这是台账/指标一致性问题，不是产品功能验收。下一步逐项把已存在的映射和可定位证据同步到规范 JSON，区分跨文档已审阅数、台账结构化证据数和当前 HEAD 证据数；不要猜填阶段、不要把旧 CI 当当前证据。
- 继续保持 `fully_audited=0`、`semantic_dedup_completed=false`、`code_test_evidence_audit_completed_ids=0`；不新增 A113+、不赋权、不发布总体完成率。PR #32 Open / unmerged，真实环境验收继续暂缓。


## PLAN-003 最近一次实质落库｜A0–A6 主阶段映射、A0–A4 当前 SHA 证据｜2026-10-15

- 最新审计基线为 `c5497fd29ab2aafd071dfc6acc80fcef4558b5a1`。本轮核对产品路线图、验收计划及当前源文件/测试文件。
- 规范 JSON 台账已把 A0–A6 的主路线图阶段写为“阶段1｜可靠的生产底座”；A5 的 A4 输入依赖已落库。只记录明确前置依赖，不把关联任务随意变成依赖。
- A0–A4 的 source/test/workflow 证据已刷新到当前 HEAD，并关联当前 CI Push/PR 与 docs-sync Push/PR 成功记录。此证据刷新不等于这些任务正式验收通过。
- 当前仍有 63 个任务待路线图阶段映射；全量代码/测试证据审计完成数仍为 0；语义去重与总体审计均未完成。不新增 A113+，不赋权、不发布总体完成率。
- 下一步继续对照路线图阶段退出条件，按任务逐条映射依赖和证据边界；真实 Windows、真实素材、Provider/扣费、剪映现场和真实投放继续暂缓。PR #32 保持 Open / unmerged。


## PLAN-003 最新推进｜A0–A8 阶段/依赖与证据增量落库｜2026-10-15

- 当前审计基线：`b11ab5306e4b4992b982fe2f2393fac43861d93e`。A0–A8 的主路线图阶段与对应源码/测试证据已逐项写入规范台账；A0–A6 归阶段1，A7–A8 归阶段3。
- 已明确登记 A5→A4、A7→A6、A8→A7 的直接输入依赖。其他“相关/共享组件”关系不自动升级为依赖。
- 九个任务的源码/测试证据绑定到当前分支树；CI Push/PR 与 docs-sync PR 当前 SHA 已通过。当前 SHA 的 docs-sync Push 记录未找到，不能宣称四项均通过。
- 仍有 61 个任务待主阶段映射；全量代码/测试审计完成数为 0，语义去重未完成；不新增 A113+、不赋权、不发布总体完成率。
- 下一步继续 A9–A17 的阶段退出条件、依赖与证据映射；真实 Windows、真实素材、Provider/扣费、剪映现场和真实投放仍暂缓。PR #32 Open / unmerged。


## PLAN-003 最新推进｜A8 阶段纠正、A9–A17 证据增量落库｜2026-10-15

- A8「剪辑策略」已纠正为阶段2「商业级剪辑决策层」；A7 仍属阶段3。
- A9–A17 已归入阶段1，源码/专项测试路径、部分自动化证据和剩余缺口已写入规范 JSON 台账。
- 依赖记录：A12→A5/A8，A13→A12，A14→A13，A15→A8/A9/A10/A11，A16→A8/A10/A11，A17→A7/A8/A9/A10/A11。依赖不代表验收通过。
- 重点未证实项：ASR准确率、免费商用音乐/字体授权、字幕与口播及商品事实一致、AI画面商品一致、混合素材来源追溯、三类成片完整端到端质量。
- 本轮修改前基线 `5138685b3489fd249be5469fe86821b6374edde0` 的 CI Push/PR 与 docs-sync Push/PR 均成功；本轮新提交工作流需重新检查。
- 不新增 A113+；全量代码/测试审计仍为 0，语义去重未完成，不赋权、不发布总体完成率。真实 Windows、素材、Provider/扣费、剪映现场和真实投放继续暂缓。PR #32 保持 Open / unmerged。


## PLAN-003 文档同步补记｜2026-10-15
- 本轮 A66–A69 部分证据映射已同步到总进度台账、任务登记表、正式验收计划、验收 SOP、产品路线图、根级 AI handoff 与未来功能备忘。
- 源码/测试审计快照仍为 `fe298b3ae6005b118d8b7b1adf775a261d228ffe`，仅作源证据快照；当前文档 HEAD 已继续变化，当前 HEAD 精确绑定任务数保持 0。
- A67 的“通过后证据删除/清空再复核”、A68 的全部非法引用/不改写/持久化断言、A69 的旧方案兼容与调用方拒绝保存均仍是明确缺口；A66–A69 全部保持 `not_audited`。
- 下一位 AI 必须先查询 PR #32 最新 HEAD，并分别核对 CI Push、CI PR、docs-sync Push、docs-sync PR 是否都绑定该 SHA 且完成成功。任何一项缺失或仍运行，不得开始下一批。下一批是 A70–A74：短剧故事结构检查、备选故事方向差异化、人物动机与关系动力、剧情事件因果链、因果链与剧本/分镜证据对齐。


## PLAN-003 增量审计记录｜A105–A109｜2026-10-15

- **源码/测试审计基线**：`c77704d86d6131d13501448af76ce24afc56ad7b`；文档更新前最近检查的分支 HEAD 为 `57ed689911025f2e31241ddf487e70143ffedbe0`。该 HEAD 的 CI PR [38730155209](https://github.com/konggu888/ecommerce-agent/actions/runs/38730155209) 与 docs-sync PR [38730155147](https://github.com/konggu888/ecommerce-agent/actions/runs/38730155147) 均 success；Push 触发工作流未被当前查询接口独立返回，不能宣称四项均已核实。PR #32 Open/unmerged。
- **A105｜分镜节奏映射**：慢/标准/快/极快默认速度、显式速度优先、未知标签回退有单测；后处理命令同步 setpts/atempo。真实渲染和完整 UI 到成片链未集成测试。
- **A106｜商业角色默认剪辑**：源码按分镜文本关键词推断角色、时长/节奏/速度/转场，并记录 rationale/basis/参数来源；测试覆盖 hook、商品细节、演示、证据和末镜 CTA，以及显式参数优先。pain_point/reaction/story_beat 等角色与歧义关键词未全面测试；不是视觉语义识别。UI 仅发现展示转场值，未找到明确的可编辑转场选择器。
- **A107｜推断时长进入生成请求**：CreativeShot → runtime Shot 的字段映射存在，生产入口将 runtime `duration_seconds` 传入 GenerationRequest；目前测试止于 runtime mapping，没有直接断言 Provider 请求最终收到推断时长。真实 Provider 仍不调用。
- **A108｜字幕自适应**：按 FFprobe 实际时长生成 SRT，拆分长文案、限制短镜头字幕切换并显示密度警告；桌面路径可见 probe → analyze → write_srt → burn_subtitles。单测覆盖规划器/SRT，但没有 app 级整链集成测试；真实阅读舒适度和 Windows 烧录效果未验证。
- **A109｜音乐节拍与实际切点**：生产源码把节拍分析、切点规划、内容/字幕保护、镜头变速、拼接后一次性混入全局 BGM 接入最终导出链；专项测试覆盖合成节拍、静音/低置信度回退、时长变化、内容保护、变速命令和 BGM 混音命令。但没有直接测试最终 build_final 的完整调度链，实际 FFmpeg 渲染/视听仍未验证。台账中历史 `automation_passed` 已降为 `partial_evidence_mapping` / `not_audited`，因为验收计划四项 workflow gate 尚未完整核实，且生产集成证据仍有缺口。
- A105–A109 均为 `partial_evidence_mapping` / `not_audited`。映射覆盖：113 个编号任务；source/test/CI/workflow 指针任务 110；任意 evidence 任务 112；路线图映射 113/113；源码/测试快照绑定任务 52；最终文档 HEAD 精确绑定 0；完整代码/测试审计 0；完整审计 0；语义去重未完成；权重与总体完成率关闭。
- 本轮不改产品代码。Windows 真机、真实素材、Provider/扣费、剪映现场与商业效果继续暂缓。PR #32 不合并；不新增 A113+，不删除/合并/重编号 A0–A112。
- 下一批按既有编号进入 **A110–A112**。文档提交后先核验最新 SHA 的 CI Push、CI PR、docs-sync Push、docs-sync PR；Push 若无法独立查询须明确记录未核实。


## PLAN-003 增量审计记录｜A110–A112｜2026-10-15

- **源码/测试审计基线**：`c77704d86d6131d13501448af76ce24afc56ad7b`；文档更新前最近检查 HEAD `a9fe2d93d186bac79dafee294e518209d963f420` 的 CI PR [38730727069](https://github.com/konggu888/ecommerce-agent/actions/runs/38730727069) 与 docs-sync PR [38730727058](https://github.com/konggu888/ecommerce-agent/actions/runs/38730727058) 均 success。Push 触发工作流未独立核实，PR #32 Open/unmerged。
- **A110｜商业剪辑内容保护**：源码把口播/屏幕文字/商品角色/CTA 停留时间作为音乐卡点下限，低置信度和不安全计划回退；测试覆盖对话、屏幕文字、商品停留与安全回退。CTA 专门下限尚无独立断言，生产链整合测试缺失。
- **A111｜逐边界局部音乐卡点规划**：算法逐镜头验证最短时长、最大变化、变速约束，仅回退冲突边界并记录 adjusted/reverted 边界；专项测试覆盖单/多相邻保护、无关安全边界仍可调整、总时长保持、低置信度和交叉溶解回退。尚无 build_final 整链测试或实际 FFmpeg 渲染。
- **A112｜字幕实际时间窗参与内容保护**：SRT 解析校验 cue 顺序/范围/结束时间，最短 cue 时长进入卡点保护；生产代码检查字幕记录是否绑定当前源视频路径和时长，异常时回退。单测覆盖解析和 helper 边界，但没有生产级 applied/fallback 整链回归。
- A110–A112 历史 `automation_passed` 不直接继承；本轮全部改为 `partial_evidence_mapping` / `not_audited`，因为本轮源码/测试复核发现专项集成证据缺口，且当前查询未独立核实 Push 工作流。真实素材、Windows 真机、真实音画/字幕可读性与商业成片质量仍暂缓。
- 映射覆盖：编号任务 113；任意 evidence 任务 113；source/test evidence 任务 112；源码/测试快照绑定任务 55；完整代码/测试审计 0；完整审计 0；语义去重未完成；权重与总体完成率关闭。
- 本轮未改产品代码。PR #32 不合并；不新增 A113+，不删除/合并/重编号 A0–A112。下一步不再有新的编号任务；应回到 PLAN-003 对 A0–A112 做语义去重、证据冲突与未审计范围的统一核对，不得凭空扩展编号。

## PLAN-003 增量审计｜A52 / A55 源码与测试证据边界｜2026-10-16

- 审计源码/测试快照：分支当前已核实的 HEAD `e4fa3365b4a44aa7ddb62a492826afc66a2a191b`；产品代码未修改。PR #32 仍 Open / unmerged。
- **当前 SHA 的 PR 触发工作流**：CI #2230 success，docs-sync #1907 success；部署预览 status success。当前可用 connector 的 commit-workflow 查询只返回 PR 触发项，Push 触发的 CI 与 docs-sync 未独立核实，因此不得宣称四项都已核实通过。
- **A52｜Provider 失败尝试与成本去重：部分证据映射，not_audited。** `production.py::_render_with_provider` 在 Provider 调用开始后捕获生成异常，尝试写 failed video ledger row；失败报价进入 `unit_cost_rmb`、`estimated_cost_rmb=0`，成功行才进入实际成本汇总。专项测试 `test_a52_failed_video_attempt_is_auditable_without_double_counting_actual_cost` 覆盖一次失败+一次成功重试、失败行类别/报价字段、失败成本为零及成功成本仅计一次。**未直接断言**失败行的 project_id/shot_id/provider/error 全字段，失败后旧视频仍可用，以及重新创建 Store/重新加载后失败行仍存在；不能把“账本文件写入实现”代替这些行为断言。
- **A55｜视频成功但成本记账失败：部分证据映射，not_audited。** 源码把 Provider 生成/替换和成功记账分成两个异常边界；账本异常时保留输出路径，设置“已生成（成本待核对）”，记录 recovery history 并尝试保存项目。专项测试 `test_a55_ledger_failure_does_not_turn_successful_video_into_provider_failure` 覆盖新视频文件、活动路径、待核对状态、恢复记录和项目重载后的视频路径/状态。**尚未直接断言**该场景不会新增 failed Provider 记录、不会产生重复 success ledger 行，以及账本恢复后对账动作是否安全幂等；真实账单核对仍暂缓。
- 本轮没有发现足以证明生产实现必须立即修改的缺陷；发现的是正式验收断言缺口。因此不改产品代码、不把 A52/A55 标为正式通过，也不继承验收计划中历史 SHA 的自动化通过标签作为当前 HEAD 的完整证据。
- **后续主线**：回到 PLAN-003 对 A0–A112 的跨来源语义重复、状态冲突、依赖和证据边界做统一裁决；A52/A55 的上述缺口作为待补证据保留。不得新增 A113+、删/合并/重编号既有任务、赋权或发布总体完成率。Windows 真机、真实 Provider/扣费账单、剪映和真实投放仍暂缓。

## PLAN-003 当前进度｜A52/A55 映射完成，转入 UXS-2 合同核对｜2026-10-16

- 源码/测试基线 `e4fa3365b4a44aa7ddb62a492826afc66a2a191b`；最新文档 HEAD `fd7b25b86aa3f3bc5f68f474afb1aa92389612be`。CI #2235 运行中、docs-sync #1910 success；Push 触发项未独立核实。每次接手仍必须实时查询当前 HEAD 和四项工作流。
- A52/A55 仅完成部分证据映射，保持 `not_audited`；不继承历史验收勾选。
- **唯一下一步：**按 UXS-2 / PLAN-003 核对 A13、A29、A30、A51–A65 正式验收合同与测试，先裁决费用授权、路由静默回退、API Key 明文存储、未知费用和数据目的地告知的映射关系。先审计，不改产品代码，不新增 A113+。
- P0 候选：`App.create()` 的创意规划调用先于预算确认；P1 风险：模型回退、密钥存储、费用未知状态、请求前数据目的地告知。实际扣费/泄漏未被本轮证明。
- PR #32 保持 Open/unmerged；真实 Provider/代理、账单、Windows 真机、剪映和投放验收继续暂缓；整体完成率关闭。

## PLAN-003 最新状态｜A13/A29/A30/A51–A65 合同对照｜2026-10-16

- 审计基线 `b678560d0f0c97ff7e632ace2be9c39e848edefa`。该 SHA 的 CI PR #2251 与 docs-sync PR #1920 已成功；Push 工作流未独立核实。当前新文档提交的工作流必须重新查询，禁止沿用旧 SHA 绿灯。
- A13/A29/A30/A51–A65 的合同范围、测试证据和状态冲突见 `docs/AD_STUDIO_USER_EXPERIENCE_SAFETY_AUDIT.md`。A13 路由测试只证明九个 create_plan 阶段；A29 数据来源测试不等于外发授权；A30 恢复测试不等于拒绝后零调用；A51 数值校验不等于费用未知语义；账本持久化不等于密钥加密。
- P0 候选：`App.create()` 在预算确认前调用创意规划模型；P1 风险：自动路由回退、API Key JSON 明文保存、未知费用、请求前数据目的地告知。
- **唯一下一步：**核对资产/视频 CapabilityRouter、视觉与转写入口、模型设置 UI，以及缓存/历史模型标识的调用链与测试，继续映射现有 A0–A112；先审计，不改产品代码、不新增 A113+。
- PR #32 不合并；真实 Provider/代理/账单、Windows 真机、剪映和投放继续暂缓；整体完成率关闭。

## PLAN-003 路由与 Provider 入口审计｜2026-10-16

- 审计基线：d48a3af0f68f357c1b32abeb92503a17be7f09aa。该 SHA 的 PR CI #2267 与 docs-sync #1930 曾成功；Push 工作流未独立核实。最新文档提交必须重新检查其 SHA。
- 详见 `docs/AD_STUDIO_USER_EXPERIENCE_SAFETY_AUDIT.md`：`resolve_route()` 可能静默切换模型；视觉分析把关键帧作为 data URI 发往自定义 Base URL；语音转写使用单独 endpoint，且 helper 无条件要求 API Key，与本地无 Key 路由不一致；模型/视频/资产配置以 JSON 保存密钥；缺失 usage/价格按 0 估算但 UI 有非免费提示；自定义资产库路径可能与资产配置文件路径分离，视频/资产历史记录不足以复原实际 endpoint/model。
- **唯一下一步：**把 UXS-2 静态发现转成不联网的 mock 测试矩阵，逐项映射现有 A0–A112：路由回退授权/零调用、预算确认前调用计数、本地转写无 Key、自定义资产库配置路径、各 Provider payload/目的地、未知费用语义、项目重载后的路由可追溯性。合同裁决前不改产品代码、不新增 A113+。
- PR #32 不合并；A0–A112 不删除/合并/重编号，不计算整体完成率。真实 Provider、账单和 Windows 真机继续暂缓。


## UXS-2 首批 mock 修复与当前唯一下一步｜2026-10-16

- 已修复：本地 `local_openai` 转写可无 Key 请求且不添加 Authorization；远程无 Key 在请求前拒绝。自动资产解析改为从应用配置根目录读取 `asset-generation.json`，不随用户自定义 `library_root` 改变。
- 新增测试：本地无 Key 转写成功（mock URL），远程无 Key 零请求，自定义资产库目录下资产配置路径稳定。源码/测试提交 `d6d78cec8368065975aa64cfdd913ec1e152a4c2` 的 CI #2305 与 docs-sync #1958 均通过；其后的文档同步提交必须重新查最新 HEAD 的检查结果。
- 这两项最小修复不代表 UXS-2 完成，不改变 A0–A112 正式状态；没有真实 Provider 请求、账单验证或 Windows 真机测试。
- **唯一下一步：**优先修复 P0 费用授权时序。当前 `App.create()` 在预算确认弹窗前调用 `create_plan/create_plans`，可能先向云端发出规划请求。应先在任何外部模型/Provider 调用前取得明确授权，再在计划生成后显示视频、演员、场景、商品素材的详细费用并取得生成授权。用编排级 mock 计数断言：每个拒绝/取消分支之后文本、视觉、转写、资产、视频调用计数为 0，且没有未确认的新项目落盘。
- 不新增 A113+；不合并 PR #32；A0–A112 不删除/合并/重编号；Windows 真机、真实 Provider/扣费继续暂缓。


## UXS-2 最新状态与下一步｜2026-10-16

- 本地转写：仅 `local_openai` 允许无 API Key，空 Key 请求不附加 Authorization；远程无 Key 在请求前拒绝。
- 资产配置：`ProductionStore.resolve_assets()` 从应用配置根目录读取 `asset-generation.json`，不再随用户自定义资产库目录改变路径。
- 创建前授权：`App.create()` 在商品解析/创意规划前显示当前路由、endpoint、配置单价和潜在回退目标；URL 显示去除 query/userinfo；拒绝后不执行被门控的商品解析操作。计划后详细费用确认仍保留。
- 测试包括：本地转写无 Key、远程无 Key 零请求、自定义资产库路径、拒绝授权零操作、授权信息不暴露 URL query/API Key、源码顺序检查。中间测试夹具失败已经修正，失败历史保留；请从实时最新 HEAD 查询 CI/docs-sync。
- **尚未正式验收：**完整 GUI/各 Provider 运行时调用计数、逐个回退目标的拒绝路径、未知费用语义、实际 endpoint 历史追溯、密钥静态存储保护。
- **唯一下一步：**收紧模型与资产/视频 Provider 自动回退，定义用户逐次允许/拒绝规则；为云→云、云→本地、无可用模型增加 mock 测试，拒绝后外部调用必须为 0，并记录实际目标。之后处理未知费用和端点历史追溯。
- PR #32 Open/unmerged；A0–A112 不删除/合并/重编号；不新增 A113+；真实 Provider/扣费、Windows 真机继续暂缓。

## UXS-2 路由状态更新｜2026-10-16

- 文本/视觉模型：`ModelRouter.resolve_route()` 已改为 fail-closed；所选模型不可用时不再自动切换到另一云端/本地模型。三类离线回归覆盖云→云、云→本地、无可用替代模型。
- 创建授权：已加入前置目的地/配置单价告知与拒绝零操作 helper；计划完成后保留详细费用确认。完整 GUI/各 Provider 运行时调用计数尚未正式验收。
- 资产库路径：自动素材解析读取应用配置根目录的 `asset-generation.json`；本地转写无 Key 仅对 `local_openai` 放行且不发送 Authorization；远程无 Key 仍在请求前拒绝。
- **唯一下一步：**审计 `CapabilityRouter.decide_asset/decide_video` 的本地/云端回退并增加拒绝后零调用 mock；之后处理未知费用语义、endpoint 历史追溯与密钥存储合同。
- PR #32 Open/unmerged；A0–A112 不删除/合并/重编号；不新增 A113+；真实 Provider/扣费、Windows 真机继续暂缓。

## UXS-2 最新接手状态｜2026-10-16

- 单镜头视频生成按钮已增加逐次目的地/费用确认；拒绝时在镜头状态变更前返回，同意后将确认时的 ExecutionDecision 快照传给生产层，避免再次路由。
- 测试覆盖脱敏 endpoint、云端数据边界、取消不改状态的顺序与路由快照传递。
- 当前 SHA bb337ce7be236ad5148a9dd59120defd0efd67e5 尚待 CI/docs-sync。不要把此前 d1f7e54db2f511ba2dde900a14d848657adbbc3d 的绿灯用于当前代码。
- 下一步：资产 Provider 逐次授权。重点检查 ProductionStore.resolve_assets()→AssetGenerator.generate() 和 generate_missing_asset()；授权前不发外部请求，拒绝后 Provider 调用计数为 0、无素材落盘/镜头绑定。随后覆盖批量成片与短剧商品镜头重生成。
- PR #32 保持 Open/unmerged；A0–A112 不新增/删除/合并/重编号；真实 Provider/扣费与 Windows 真机继续暂缓。

## UXS-2 资产授权闸门接手说明｜2026-10-16

- 资产云端生成层已要求 authorize_cloud 回调；无回调/拒绝时不调用云端 Provider、不创建生成文件、不绑定资产/改镜头状态。
- 该回调尚未接入正式 UI，因此云端资产自动生成目前 fail-closed；本地服务路径仍可使用。
- 单镜头视频已有端点/费用确认与确认时路由快照传递。
- 当前 SHA 77ccc7a6e978fc8c6144a18b8f2958bf981ad2d6 的 CI/docs-sync 待最终结果；此前首轮 CI 失败是旧测试夹具不兼容与目录创建假设错误，已修正。
- **下一步：**接入资产 Provider 授权 UI；展示脱敏 endpoint、数据类别、配置价格与未知费用提醒；拒绝时 Provider 调用为 0，且没有素材文件、资产库记录、镜头 ID/状态变化。之后覆盖批量视频与短剧商品镜头重生成。

## UXS-2 最新接手状态｜2026-10-16

单镜头生成已接入两层逐次授权：视频 Provider 的端点/费用确认，以及缺失资产需要云端生成时的资产端点/费用确认。素材授权拒绝会在镜头状态变更前返回，并阻止视频 Provider 调用；生产层将资产解析前置到状态写入之前。当前 SHA 5f4b0c1656158313e193c8adf3c051c62fd7beea 的 CI/docs-sync 正在运行，不能沿用此前 SHA 的状态。

**下一步：**审计并接入 AI补镜头、批量创意方案生成和短剧商品镜头重生成入口的逐次视频/资产授权；每个取消分支都要证明 Provider 调用计数为 0、镜头/项目版本与资产绑定没有意外变化。PR #32 保持 Open/unmerged；A0–A112 不新增/删除/合并/重编号；真实 Provider/账单和 Windows 真机继续暂缓。

## UXS-2 最新接手状态｜2026-10-16

单镜头、AI补镜头和批量创意方案生成已接入统一的视频目的地/费用确认；云端资产生成也逐次确认。拒绝分支不先修改镜头状态、不发起本次视频请求，确认时路由快照传入生产层。短剧商品镜头重生成的准备步骤不调用 Provider，真正生成走单镜头入口。

**下一步：**审计未知费用语义和 endpoint provenance：将真实零成本、缺失价格、缺失 usage、不可估算区分开；记录实际 provider/model/endpoint 来源并在项目重载后可追溯，绝不把 API Key 写入历史。当前最新代码/测试 SHA 37e8d3f4a63d98d6a4f98459de8dbeb0970f0a28 的 CI 通过，文档同步后重查最新 HEAD。PR #32 保持 Open/unmerged；A0–A112 不新增/删除/合并/重编号。

## UXS-2 最新接手状态｜成本可信度与端点溯源｜2026-10-16

- 已增加账本字段 cost_status、usage_status、脱敏 endpoint；文本模型调用区分 usage 缺失、价格缺失、两者缺失与按配置价格估算。
- 视频/资产成本记录开始写入脱敏 endpoint 与价格可信状态；AI调用记录界面展示已知估算成本、未知费用记录数、脱敏 endpoint 和费用可信状态。
- 离线测试覆盖 endpoint 凭据脱敏、重载保留状态、usage 缺失与价格缺失。最新 CI 必须以当前 HEAD 为准；之前失败的测试夹具/上下文错误已修正后重跑。
- 覆盖边界：这是本地估算账本，不是供应商账单；转写、视觉分析及未接入账本的调用仍需独立审计。旧历史端点不能从新字段推断。
- **下一步：**检查最新 CI 与 docs-sync；若通过，继续审计转写/视觉等未入账入口及 endpoint provenance 的项目级追溯，之后处理密钥本地存储保护。PR #32 Open/unmerged；不新增 A113+，A0–A112 状态不变；真实 Provider/账单与 Windows 真机继续暂缓。

## UXS-2 授权报价未知语义｜2026-10-16

- 生成前授权弹窗现区分“显式配置价格”和“未配置/无法估算”：视频 Provider 通过 cost_price_configured 标记，资产按类型配置或通用配置读取 price_rmb。
- 未配置时显示“暂无法可靠估算（未知）”，不再显示伪造的 ¥0.00 或默认报价；显式 ¥0 仍提示不代表供应商免费。
- 当前最新提交后需重新检查 CI/docs-sync；若通过，下一步继续覆盖转写/视觉账本与密钥本地存储保护。

## UXS-2 转写账本与项目上下文｜2026-10-16

- 修正 ModelRouter 项目上下文：初始化 current_project_id，提供 set_project_context()；新建项目与打开项目时绑定项目 ID。
- 口播转写成功/失败会记录脱敏 endpoint、模型/Provider、耗时与未知费用状态。当前转写响应不提供可用 usage，因此不把 0 视为免费。
- 下一步检查最新 CI/docs-sync；若通过，继续核对视觉分析调用、其他未入账 Provider 与本地 API Key 存储。

## UXS-2 最新接手状态｜API Key 本地存储保护｜2026-10-16

- 最新已验证基线：`cd2c034fc4feb26a10de1c07e7107c06907109be`，typecheck-and-test 与 docs-sync 均 success；PR #32 仍 Open/unmerged。
- 静态审计确认 `ModelRouter.save()` 可能将模型配置中的原始 API Key 写入 JSON；视频 Provider 设置写 `video-provider.json`，资产 Provider 设置写 `asset-generation.json`，两者都可能包含明文 Key。UI 密码框仅遮挡显示。
- 没有密钥泄漏事件证据；账本 endpoint 已脱敏，当前问题是本地静态存储保护不足。
- **下一步：**先实现/评估 Windows DPAPI 或系统凭据库方案，覆盖模型、视频和资产三类 Key；设计旧明文配置迁移、无明文回写、项目重载与错误日志脱敏测试。真实 Windows 机器测试暂缓；不新增 A113+，A0–A112 正式状态不变。
