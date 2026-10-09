# AI 商品广告工厂：独立 AI 接手入口

> 本文件是“完全不知道本项目历史的新 AI”使用的最短接手入口。它不依赖聊天记录、个人记忆或上一位 AI 的口头结论。

## 1. 项目目标

这是一个 Windows 本地的“AI 商品广告工厂”桌面项目。目标是让用户从商品资料/实拍素材开始，经 AI 分析与决策、本地程序编排执行、必要时调用云端生成能力，完成视频生产、事实/视觉/安全检查、成片交付与失败恢复。

产品目标和完整工作流以 apps/ad-studio-desktop/HELP.md 为用户侧说明，以 apps/ad-studio-desktop/PROJECT_LOGIC.md 为内部逻辑地图。

## 2. 架构与强制规则

先读根目录 AGENTS.md。核心原则：
- LLM 负责思考和决策。
- Python 桌面程序负责编排、执行、存储、版本、成本和硬件能力调度。
- 本地设备负责适合本地完成的加工；云端负责本地能力不足或不适合本地执行的高质量生成。
- 任何具体显卡型号都不是系统最低配置或架构边界。
- 修改桌面端代码必须同步更新 HELP.md 和 PROJECT_LOGIC.md，并通过文档同步检查。

## 3. 当前验收进度

以 docs/AD_STUDIO_ACCEPTANCE_PLAN.md 的正式顺序为准：

**已完成：A0–A33。B1–B3 真实投放相关阶段按用户要求暂缓。当前未来功能开发入口：docs/AI_AD_STUDIO_FUTURE_FEATURE_MEMO.md。三种 AI 工作模式已完成第一轮 UI/关键动作接入：主界面提供中文模式选择，项目可保存/恢复模式；半自动模式确认初始创意方案，用户控制模式要求用户选择初始方案，云端 AI 补镜头、批量生成版本和最终交付已接入相应确认入口。全生产链统一接入与完整暂停/确认/继续状态机仍未完成；Windows 真实机器测试暂缓。**

不要把历史文档中的旧“下一阶段”文字当成当前状态；以本文件的当前验收进度和 docs/AD_STUDIO_ACCEPTANCE_PLAN.md 的最新记录为准。

## 4. 验收计划

唯一阶段顺序入口：docs/AD_STUDIO_ACCEPTANCE_PLAN.md

A32 已完成验收。其验收重点是一个没有任何本项目聊天历史的新 AI，能否独立找到：
1. 项目目标
2. 架构
3. 当前进度
4. 验收计划
5. 测试方式
6. 安全边界
7. 下一步工作

## 5. 测试入口

桌面核心测试：python3 -m unittest discover -s apps/ad-studio-desktop -p 'test_*.py'

A32 专项自动化验收：apps/ad-studio-desktop/test_ai_handoff.py

文档同步检查：python tools/check_ad_studio_docs.py --base <base-ref> --head <head-ref>

CI 还会运行前端语法、Python 语法、Typecheck、Engine 和 Risk Controller 测试。

## 6. 安全边界

- 不把 TODO、stub、placeholder 或未适配 Provider 写成已接通。
- 不把模拟数据写成真实投放结果。
- 不凭空生成 CTR、CVR、CPA、ROAS 等真实平台指标。
- 商品事实、禁用词、高风险表达、视觉风险和待复核 AI 镜头必须遵守确定性安全闸门。
- AI 生成镜头默认待复核，未经人工审核不得进入最终成片。
- 真实 Provider/API 的具体接通状态以代码、测试和 HELP 中“当前已知限制”为准。

## 7. 新 AI 的固定接手顺序

**本文件 → AGENTS.md → PROJECT_LOGIC.md → HELP.md → AD_STUDIO_ACCEPTANCE_PLAN.md → 目标代码/测试 → 安全边界**

读完后，先检查当前最新 CI/失败日志和工作区状态，再决定是否继续修改。不得凭聊天记录或上一轮结论直接推进。

## 8. 接手结论

如果上述入口均可访问，且 A32 专项测试能从这些长期文件中独立验证七项信息，则项目具备“无聊天历史接手”的可验证基础。该能力属于项目可维护性/交接能力，不代表真实 AI Provider 或真实投放已经接通。

## 9. 未来路线开发状态

未来功能总表：`docs/AI_AD_STUDIO_FUTURE_FEATURE_MEMO.md`。2026-10-09 已完成三种模式的第一轮 UI/关键动作接入，测试入口为 `apps/ad-studio-desktop/test_workflow_modes.py`。目前覆盖模式选择与项目持久化、半自动创意方案确认、用户控制模式下初始方案选择、云端补镜头授权、批量生成确认和最终交付确认。其余生产动作的统一策略与完整暂停/确认/继续状态机仍未完成；Windows 真机验证暂缓，不能将其描述为三种模式已完整可用。


### 工作模式状态保留修复（2026-10-09）

- `_activate_plan()` 重建创意方案数据时，必须调用 `preserve_workflow_state()` 保留项目级 `workflow_mode` 与 `workflow_approvals`。
- 专项测试 `test_workflow_mode_and_storyboard_approvals_survive_variant_activation` 覆盖跨方案切换时的模式/分镜审批持久性，并检查桌面代码确实接入该 helper。
- 当前提交 `51894e4f575fa62f4cca0117aa8424f94cbba1df` 的 CI #869 和 doc-sync #482 均已成功。此修复不等于完整工作模式状态机已完成。


### 云端视频生成授权修复（2026-10-09）

- 单镜头生成和一键生成全部版本现在都会在第一次云端视频 Provider 调用前走 `cloud_generation` 授权策略；用户拒绝时不调用云端服务。
- 本地生成和实拍素材裁剪不应触发云端授权框。
- 测试增加了两条 UI 接入契约：单镜头云端授权和批量云端授权。Windows 真实机器和真实 Provider 仍未测试。


### 超预算确认修复（2026-10-09）

一键生成全部版本和 AI 补镜头在预计成本超过剩余预算时，现改为展示金额并请求用户明确确认，不再直接用警告框拦截。拒绝时不会开始生成；同意只适用于本次操作，仍需单独通过云端生成授权。测试已添加对应接入契约。


### 批量预审取消恢复（2026-10-09）

检查发现批量生成的预算预审会逐方案切换当前活动方案；用户拒绝超预算或云端授权时，原实现直接返回，界面会停留在最后一次预审的方案。现增加 `_restore_variant_selection()`，取消时恢复原方案并保存，且不启动生成。新增专项测试。真实 Windows 机器验证仍暂缓。


### 批量操作异常恢复（2026-10-09）

- 新增批量生成、批量输出异常时恢复原选中方案的处理；恢复前缓存当前方案运行态，避免丢失部分成功的镜头/输出状态。
- `test_workflow_modes.py` 增加对应源代码契约检查。提交后的 CI 仍需单独核验；这不是 Windows 真机测试，也不是完整工作模式状态机验收。

- 新增行为级离线测试 `VariantRecoveryBehaviorTests.test_restore_caches_current_partial_variant_before_switching_back`，通过 fake app/store 执行真实恢复方法，验证缓存、切换、刷新和保存顺序；最新提交必须重新跑 CI 后才可视为验证通过。

- 测试不直接导入 `ad_studio.app`（CI/Linux 环境未安装 tkinter）；改为 AST 提取真实恢复方法，在 fake app/store 上执行，确保行为覆盖仍可在无 GUI 环境运行。

- 行为测试从 AST 提取方法时移除 Tk 专用 `@ui_action` 装饰器，避免依赖桌面窗口初始化；最新 CI 会验证该测试是否可运行。

### 本轮继续推进：批量预审失败恢复

- 发现批量生成的逐方案预审循环位于主生成 `try` 之外：方案激活/解析异常可能导致 UI 留在预审中的其他方案。已为预审循环增加异常处理，失败后恢复原选中方案并终止生成。
- `test_workflow_modes.py` 增加针对预审失败恢复路径的回归契约检查。以本次新 head 的 CI/doc-sync 为准，未进行真机/剪映/真实 Provider 测试。

### 本地后处理 UI 入口复核

- 检查发现 `postprocess_selected()` 与 `finish_selected()` 未显式执行 `_ui_execution_gate()`，且没有先检查项目是否存在。已补充闸门和项目检查，并增加 AST 回归验证。
- 这只验证入口契约，不等同于真实视频/字幕/BGM 编码的机器实测。

### 工作模式审批状态复核与修复

- 发现 AI 补镜头通过人工复核并插入当前分镜后，没有清除该方案旧的 `workflow_approvals`，可能让半自动/用户控制模式跳过对更新分镜的再次确认。
- 已添加 `invalidate_storyboard_approval()` 公用逻辑，并同时接入镜头编辑保存、AI 补镜头插入路径；新增单元测试验证只清除当前方案审批，并用 AST 确认两个真实调用路径接入。
- 需以最新提交 CI/doc-sync 为准。该修复未替代 Windows 真机或真实 Provider 测试。
