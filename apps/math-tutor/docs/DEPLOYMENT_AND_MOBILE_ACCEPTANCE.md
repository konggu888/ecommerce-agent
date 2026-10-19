# 部署地址与真实手机验收状态

更新日期：2026-10-20

## 1. 当前结论

- 源码仓库：`konggu888/ecommerce-agent`，分支 `feat/beishi-grade2-math-tutor`，PR #33（Open、Draft、未合并）。
- 当前源码 HEAD（本次审计开始时）：`ee309416a31d2d0c6fb3d64bdc9913a19d59cc5e`。
- GitHub Actions CI 对该 SHA 为 completed/success；这只能证明 CI 中执行的自动化步骤通过，不能证明用户能打开网页或实体手机验收通过。
- Netlify 集成曾返回预览地址 `https://deploy-preview-33--gilded-pithivier-aee0ab.netlify.app`，但用户实际遇到要求登录受邀 Netlify 账号的访问限制。**因此它不是已交付给用户、可用来验收的地址。**
- 当前没有证据证明存在一个用户无需受邀登录即可访问的测试网址；实体手机验收尚未完成。不能把 Netlify 的 status=success 说成网站可访问。
- 不允许因等待测试网址而把 MATH-002 标为 ACCEPTED；当前固定任务进度仍以 `MATH_TASK_REGISTER.json` 为准。

## 2. 代码和配置审计结果

本轮检查了数学项目的接手文件、README、架构、路线图、验收、进度看板、变更日志、技术基线、产品规格、隐私与成本、教学协议、执行控制、课程计划、上游参考、任务登记，以及 Vite/Playwright 配置、Docker/Compose/Nginx、前后端入口和 GitHub Actions 工作流。

结果：

1. 在当前分支的仓库文件中，没有找到要求开发必须通过 Netlify 网站操作、要求用户登录 Netlify 才能开发、或把 Netlify 作为正式生产运行依赖的活动指令。
2. `.github/workflows/pages.yml` 部署的是仓库中独立的 `apps/web/` 仪表板，不是 `apps/math-tutor/` 数学学习项目；不应将其误认为数学项目的部署方式。
3. 旧版 `SESSION_HANDOFF.md`、`PROGRESS_DASHBOARD.md`、`CHANGELOG.md`、`STACK_BASELINE.md` 中保留了历史 SHA 的 Netlify deploy-preview 状态。它们是历史记录，不是要求继续使用 Netlify 的指令；历史状态不能代表当前可访问性。
4. 当前 GitHub PR 的 Netlify deploy-preview 状态来自仓库外部集成，未发现对应的 Netlify 部署配置文件或工作流在仓库内。代码本身不能让受限的 Netlify 预览自动变成公开可访问。
5. 项目已有 Playwright 的 390px Chromium 模拟视口测试和真实 FastAPI/Vite 的 CI 联调，但这不是实体手机验收，也不等于家长/学生完整数学学习流程已实现。
6. Docker Compose 自托管配置只是待验证的部署骨架。尚无用户服务器上的部署日志、外网访问地址或实体设备验收证据。

## 3. 实体手机验收必须先有可访问地址

验收地址状态：**BLOCKED — 尚无已确认的、用户可访问的测试 URL。**

当前预览链接仅供诊断，不作为验收地址：
`https://deploy-preview-33--gilded-pithivier-aee0ab.netlify.app`

获得可访问地址后，必须用真实手机（不是只用桌面浏览器缩窄窗口）记录：
- 实际 URL、部署 SHA、测试日期和是否需要登录；
- 手机型号、操作系统、浏览器版本；
- 首页是否能加载、字体/按钮是否可读、是否横向溢出；
- 前后端健康状态和断网/后端不可用提示；
- 页面刷新、返回/前进、键盘/触控交互；
- 当前产品功能边界：目前只是早期首页与健康接口基线，不能假装已实现完整练习、试卷 OCR、学习记录或家长报告。

没有真实手机测试记录之前，MATH-002 必须保持 IN_PROGRESS。

## 4. 下一步

1. 不再把 Netlify 预览成功当作用户可访问证明，也不要求用户去申请未知账号的邀请。
2. 先确定一个无需受邀登录、可供本轮测试的公开预览方案，或由用户提供可部署的测试/自有服务器环境。任何新托管服务仅可用于测试，不改变生产必须部署在用户自有服务器的要求。
3. 在真实手机打开可用 URL 并完成以上清单，保留证据。
4. 再根据证据更新 MATH-002 状态；不自动合并 PR，不改变固定 32 项任务分母或权重。
