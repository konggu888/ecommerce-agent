(function () {
  "use strict";

  var state = { view: "overview" };

  var signals = [
    ["竞争对手降价", "PRICE_PRESSURE", "高", "竞品可见价格较昨日下降约6%", "12分钟前"],
    ["流量成本上升", "TRAFFIC_COST_PRESSURE", "中高", "同类广告CPC连续3个窗口上升", "28分钟前"],
    ["需求变化", "DEMAND_CHANGE", "中", "搜索/内容热度上升，尚未完成归因", "41分钟前"],
    ["平台规则", "PLATFORM_SIGNAL", "待验证", "活动/流量规则信息等待官方来源确认", "1小时前"]
  ];

  var jobs = [
    ["WEB-20260929-001", "Web 市场扫描", "RUNNING", 72],
    ["BT-20260929-004", "30×8 回测", "COMPLETED", 100],
    ["SYNC-20260929-002", "店铺数据同步", "RUNNING", 37]
  ];

  function esc(value) {
    return String(value).replace(/[&<>"']/g, function (c) {
      return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];
    });
  }

  function page(title, sub, body) {
    return '<h1 class="page-title">' + esc(title) + '</h1>' +
      '<div class="subtitle">' + esc(sub) + '</div>' + body;
  }

  function cards(items) {
    return '<div class="grid">' + items.map(function (x) {
      return '<div class="card"><div class="label">' + esc(x[0]) +
        '</div><div class="metric">' + esc(x[1]) +
        '</div><div class="label">' + esc(x[2] || "") + '</div></div>';
    }).join("") + '</div>';
  }

  function renderOverview() {
    return page("商业博弈总览", "Sandbox 模拟数据已加载；后续将接入真实数据与 Agent。",
      cards([
        ["当前市场状态", "MIXED", "置信度 0.62"],
        ["今日广告消耗", "¥1,284", "预算 ¥2,000"],
        ["当前 ROI", "3.18", "目标 ≥ 2.60"],
        ["可执行策略", "7", "3 个需审批"]
      ]) +
      '<div class="grid2"><div class="card"><h3 class="section-title">完整决策链</h3>' +
      '<div class="timeline">' +
      ["平台/店铺数据","Web 市场情报","市场状态识别","竞争对手假设","利润/库存/现金流约束","候选策略与实验","Risk Controller","人工审批 / 自动执行","结果 → Memory"]
      .map(function (x, i) {
        return '<div class="event"><b>' + String(i + 1).padStart(2, "0") + " · " + esc(x) +
          '</b><small>' + ["已接入","已接入","运行中","有证据支持","已校验","已生成","已拦截风险动作","Read-only","持续学习"][i] +
          '</small></div>';
      }).join("") +
      '</div></div><div class="card"><h3 class="section-title">模拟店铺</h3>' +
      '<div class="notice"><b>淘宝模拟店</b><br><span class="tag">TAOBAO</span> GMV ¥12,860 · ROI 3.42</div>' +
      '<div class="notice"><b>拼多多模拟店</b><br><span class="tag">PINDUODUO</span> GMV ¥8,420 · ROI 2.91</div>' +
      '</div></div>');
  }

  function renderMarket() {
    return page("Web 市场情报", "当前展示 Sandbox 信号，不代表已经抓取真实平台。",
      '<div class="card"><h3 class="section-title">外部市场信号</h3><table class="table"><thead><tr><th>观察</th><th>状态</th><th>强度</th><th>证据</th><th>时间</th></tr></thead><tbody>' +
      signals.map(function (x) {
        return '<tr><td>' + esc(x[0]) + '</td><td><span class="tag">' + esc(x[1]) +
          '</span></td><td>' + esc(x[2]) + '</td><td>' + esc(x[3]) + '</td><td>' + esc(x[4]) + '</td></tr>';
      }).join("") + '</tbody></table></div>' +
      '<div class="grid2"><div class="card"><h3 class="section-title">Web → Game Agent</h3>' +
      '<div class="notice">事实 → 市场信号 → 竞争假设 → 证据 → 商业博弈</div>' +
      '<div class="notice">每条信号应保留 URL、标题、抓取时间、来源类型和可信度。</div></div>' +
      '<div class="card"><h3 class="section-title">扫描范围</h3><span class="tag">竞品价格</span><span class="tag">活动/促销</span><span class="tag">类目趋势</span><span class="tag">流量成本</span><span class="tag">平台规则</span><span class="tag">内容热点</span></div></div>');
  }

  function renderGame() {
    return page("商业博弈", "输入我、对手、市场三组数据，Sandbox Agent 先搜索突破口。",
      '<div class="grid2"><div class="card"><h3 class="section-title">对手与市场</h3>' +
      '<table class="table"><tr><th>变量</th><th>当前</th><th>变化</th></tr>' +
      '<tr><td>竞品价格</td><td>¥83.70</td><td class="danger">-6.1%</td></tr>' +
      '<tr><td>平均 CPC</td><td>¥2.14</td><td class="danger">+14.2%</td></tr>' +
      '<tr><td>类目 CVR</td><td>4.8%</td><td class="warning">-8.3%</td></tr>' +
      '<tr><td>库存覆盖</td><td>18 天</td><td class="positive">安全</td></tr>' +
      '<tr><td>现金可用</td><td>¥42,600</td><td class="positive">安全</td></tr></table></div>' +
      '<div class="card"><h3 class="section-title">策略候选</h3>' +
      '<button class="action" onclick="window.runSandboxAgent()"><b>运行 Sandbox Agent</b><br><span class="muted">多轮博弈 → 对手响应 → 突破口</span></button>' +
      '<button class="action"><b>提高核心词出价</b><br><span class="muted">+8% bid · APPROVAL_REQUIRED</span></button>' +
      '<button class="action"><b>降低低毛利计划预算</b><br><span class="muted">-12% budget · APPROVAL_REQUIRED</span></button>' +
      '</div></div><div class="card" style="margin-top:12px"><h3 class="section-title">Agent 输出</h3><div id="agentOutput" class="notice">等待运行。当前为 Sandbox 模拟推演。</div></div>');
  }

  function renderBreakthrough() {
    return page("突破口", "展示 Sandbox Agent 的多轮推演结果。",
      cards([["当前突破口","转化 / 内容","Sandbox 置信度 0.65"],["博弈鲁棒性","0.71","对手反击后仍可继续"],["对手威胁","3 类","价格 / 流量 / 声誉"]]) +
      '<div class="grid2"><div class="card"><h3 class="section-title">博弈路径</h3>' +
      '<div class="event"><b>01 · 我方：CONTENT_ANGLE</b><small>改善有效点击</small></div>' +
      '<div class="event"><b>02 · 对手：SHIFT_TO_CONTENT</b><small>可能复制内容打法</small></div>' +
      '<div class="event"><b>03 · 我方：DIFFERENTIATE_PRODUCT</b><small>提高复制成本</small></div>' +
      '<div class="event"><b>04 · 防御分支</b><small>异常评价/举报信号进入 Risk Controller</small></div></div>' +
      '<div class="card"><h3 class="section-title">结论状态</h3><div class="notice">这是 Sandbox 结果，不是真实市场结论。</div><div class="notice">真实数据接入后重新计算。</div></div></div>');
  }

  function renderInputs() {
    return page("博弈输入", "把“我、对手、市场”拆开输入，再交给 Agent。",
      '<div class="card"><h3 class="section-title">① 我方</h3><table class="table">' +
      '<tr><td>商品售价</td><td><input class="input" value="89"></td></tr><tr><td>毛利率</td><td><input class="input" value="32"></td></tr>' +
      '<tr><td>库存天数</td><td><input class="input" value="18"></td></tr><tr><td>可用现金</td><td><input class="input" value="42600"></td></tr>' +
      '<tr><td>CTR</td><td><input class="input" value="2.8"></td></tr><tr><td>CVR</td><td><input class="input" value="2.1"></td></tr></table>' +
      '<h3 class="section-title" style="margin-top:16px">② 对手</h3><table class="table">' +
      '<tr><td>竞品价格</td><td><input class="input" value="83.7"></td></tr><tr><td>竞品CPC</td><td><input class="input" value="2.31"></td></tr>' +
      '<tr><td>竞品评价量</td><td><input class="input" value="12800"></td></tr><tr><td>竞品CVR</td><td><input class="input" value="4.8"></td></tr></table>' +
      '<h3 class="section-title" style="margin-top:16px">③ 市场</h3><table class="table">' +
      '<tr><td>类目需求</td><td><input class="input" value="+11%"></td></tr><tr><td>平均CPC</td><td><input class="input" value="2.14"></td></tr>' +
      '<tr><td>类目CVR</td><td><input class="input" value="4.8%"></td></tr><tr><td>价格趋势</td><td><input class="input" value="-6%"></td></tr></table>' +
      '<button class="primary" onclick="window.runSandboxAgent()">运行 Sandbox Agent</button><div id="inputAgentOutput" class="notice">等待运行。</div></div>');
  }

  function renderGeneric(title, sub, body) { return page(title, sub, body); }

  function render() {
    var app = document.getElementById("app");
    if (!app) return;
    var body;
    if (state.view === "overview") body = renderOverview();
    else if (state.view === "market") body = renderMarket();
    else if (state.view === "game") body = renderGame();
    else if (state.view === "inputs") body = renderInputs();
    else if (state.view === "breakthrough") body = renderBreakthrough();
    else if (state.view === "ads") body = renderGeneric("广告 / 流量", "Sandbox 广告市场数据。", cards([["广告预算","¥2,000/日","上限"],["已消耗","¥1,284","64.2%"],["CPC","¥2.14","+14.2%"],["边际 ROAS","2.86","可继续测试"]]));
    else if (state.view === "experiments") body = renderGeneric("实验与回测", "Sandbox 实验记录。", '<div class="card"><table class="table"><tr><th>实验</th><th>状态</th><th>结果</th></tr><tr><td>出价 +8% vs hold</td><td>RUNNING</td><td>边际 ROI 2.86</td></tr><tr><td>低毛利降预算</td><td>COMPLETED</td><td>现金占用下降 9.4%</td></tr><tr><td>竞争降价情景</td><td>BACKTEST</td><td>待真实运行</td></tr></table></div>');
    else if (state.view === "risk") body = renderGeneric("Risk Controller", "写操作必须经过风险控制。", cards([["ANALYZE_ONLY","只分析","当前默认"],["APPROVAL_REQUIRED","需审批","高风险动作"],["AUTO_LIMITED","受限自动","小幅调整"],["AUTO_DISABLED","禁止","突破硬限制"]]) + '<div class="notice">当前真实平台保持 Read-only。</div>');
    else if (state.view === "jobs") body = renderGeneric("任务监控", "Sandbox 任务状态。", '<div class="card"><table class="table"><tr><th>任务</th><th>类型</th><th>状态</th><th>进度</th></tr>' + jobs.map(function(x){return '<tr><td>'+x[0]+'</td><td>'+x[1]+'</td><td>'+x[2]+'</td><td>'+x[3]+'%</td></tr>';}).join("") + '</table></div>');
    else body = renderGeneric("学习记忆", "Sandbox 学习记录。", '<div class="card"><table class="table"><tr><th>策略</th><th>预期 ROI</th><th>实际 ROI</th><th>信号</th></tr><tr><td>出价 +8%</td><td>3.10</td><td>2.86</td><td class="warning">低于预期</td></tr><tr><td>保持预算</td><td>2.70</td><td>2.74</td><td class="positive">符合</td></tr></table></div>');
    app.innerHTML = body;
  }

  window.runSandboxAgent = function () {
    var targets = [document.getElementById("agentOutput"), document.getElementById("inputAgentOutput")].filter(Boolean);
    targets.forEach(function (el) {
      el.innerHTML = "<b>Sandbox Agent 正在推演…</b><br>我方动作 → 对手响应 → 第二轮响应 → 风险约束 → 寻找突破口";
      setTimeout(function () {
        el.innerHTML = "<b>推演完成</b><br>" +
          "① 当前突破方向：内容 / 转化<br>" +
          "② 第一动作：CONTENT_ANGLE<br>" +
          "③ 预测对手：SHIFT_TO_CONTENT<br>" +
          "④ 第二动作：DIFFERENTIATE_PRODUCT<br>" +
          "⑤ 风险：不要进入无约束价格战；异常评价/举报进入防御分支<br>" +
          '<span class="tag">Sandbox · 待真实数据验证</span>';
      }, 500);
    });
  };

  document.querySelectorAll(".nav").forEach(function (button) {
    button.addEventListener("click", function () {
      document.querySelectorAll(".nav").forEach(function (b) { b.classList.remove("active"); });
      button.classList.add("active");
      state.view = button.getAttribute("data-view");
      render();
    });
  });

  render();
})();