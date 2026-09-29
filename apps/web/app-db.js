(function () {
  'use strict';

  var app = document.getElementById('app');
  var nav = document.querySelectorAll('.nav');
  var VERSION = '20260929-76';
  var BASE = 'https://skuoxmrzlxhebzhfgbyn.supabase.co';
  var KEY = 'sb_publishable_u46tZ4GMUgwqSYhMJNFG8Q_IzYwl95T';
  var CLIENT = 'ecommerce-agent-sandbox-v1';
  var state = {
    view: location.hash.slice(1) || 'overview', run: null, error: null, game: [], market: [], ads: {}, backtests: [], events: [], memories: [], risk: [], tasks: [], agentRounds: [], playback: { playing: false, current: 0, timer: null, poll: null }, simulation: { status: 'idle', name: '', message: '' }
  };

  function zh(v) {
    var s = String(v == null ? '' : v);
    var map = {
      HOLD:'保持观察',CHANGE_KEYWORD:'调整关键词',CHANGE_TARGETING:'调整定向',CHANGE_CONTENT:'调整内容',CHANGE_AUDIENCE:'调整人群',CHANGE_CREATIVE:'调整创意',CHANGE_PRICE:'调整价格',
      INCREASE_BUDGET:'增加预算',DECREASE_BUDGET:'降低预算',INCREASE_BID:'提高出价',DECREASE_BID:'降低出价',CONTENT_VIDEO:'视频内容',CONTENT_MATRIX:'内容矩阵',PRICE_WAR:'价格竞争',TRAFFIC_DEFENSE:'流量防守',VALUE_DEFENSE:'价值防守',CONTENT_SHIFT:'内容切换',
      MATCH_OR_UNDERCUT_PRICE:'跟价或低价竞争',MATCH_PRICE:'跟价',RAISE_BID_AND_DEFEND_TRAFFIC:'提高出价并防守流量',RAISE_BID:'提高出价',IMPROVE_CONVERSION:'提升转化',DEFEND_TRAFFIC:'防守流量',SHIFT_CONTENT:'切换内容',SHIFT_TO_CONTENT:'转向内容',VALUE_ATTACK:'价值竞争',NO_CLEAR_GAP:'暂未发现明确突破口',
      ALLOW:'通过',BLOCK:'拦截',STOP:'停止',CONTINUE:'继续',POSITIVE:'正向',NEGATIVE:'负向',INCONCLUSIVE:'结果不明确',OBSERVE:'观察',DEFENSIVE:'防守',MIXED:'混合',UNKNOWN:'未知',ANALYZE_ONLY:'仅分析',AUTO:'自动选择',OUR_AGENT:'我方智能体',
      'OPP-01':'价格竞争方','OPP-02':'流量竞争方','OPP-03':'内容竞争方',CATARGETING:'定向投放',CA_TARGETING:'定向投放',TARGETING:'定向投放',targeting:'定向投放',catargeting:'定向投放',
      RISK_CONTROLLER:'风险控制器',RISK_CONTROLLER_BLOCK:'风险控制器拦截',SANDBOX:'沙盒模拟',RUNNING:'运行中',COMPLETED:'已完成',FAILED:'失败',STOP_SIGNAL:'停止信号',RISK_APPROVED:'风险通过',
      ACTUAL_OPPONENT_RESPONSE:'实际对手响应',NEXT_ACTION:'下一动作',CURRENT_ACTION:'当前动作',CURRENT_ROUND:'当前轮次',STRATEGY_SOURCE:'选择策略来源',POSITIVE_ATTACK:'正向策略',NEGATIVE_ATTACK:'负向策略',HUMAN_BEHAVIOR:'人性行为'
    };
    if (Object.prototype.hasOwnProperty.call(map, s)) return map[s];
    return s.replace(/\b(CATARGETING|CA_TARGETING|TARGETING|CHANGE_KEYWORD|CHANGE_TARGETING|CHANGE_CONTENT|CHANGE_AUDIENCE|CHANGE_CREATIVE|HOLD|CHANGE_PRICE|INCREASE_BUDGET|DECREASE_BUDGET|INCREASE_BID|DECREASE_BID|CONTENT_VIDEO|CONTENT_MATRIX|PRICE_WAR|TRAFFIC_DEFENSE|VALUE_DEFENSE|CONTENT_SHIFT|MATCH_OR_UNDERCUT_PRICE|MATCH_PRICE|RAISE_BID_AND_DEFEND_TRAFFIC|RAISE_BID|IMPROVE_CONVERSION|DEFEND_TRAFFIC|SHIFT_CONTENT|SHIFT_TO_CONTENT|NO_CLEAR_GAP|ALLOW|BLOCK|STOP|CONTINUE|POSITIVE|NEGATIVE|INCONCLUSIVE|OBSERVE|DEFENSIVE|MIXED|UNKNOWN|ANALYZE_ONLY|OUR_AGENT|OPP-01|OPP-02|OPP-03)\b/g, function (x) { return map[x] || map[String(x).toUpperCase()] || x; });
  }
  function esc(v) { return String(v == null ? '' : v).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function show(title, sub, body) { app.innerHTML = '<h1 class="page-title">' + esc(title) + ' <span style="font-size:16px;font-weight:500;color:var(--accent);margin-left:10px">我变 → 对手学 → 我再变</span></h1><div class="subtitle">' + esc(sub) + '</div><div class="card" style="margin:10px 0 16px;border-left:4px solid var(--accent);background:rgba(255,180,0,.06)"><b>连续博弈座右铭</b><div style="font-size:18px;margin-top:6px">我变 → 对手学 → 我再变</div><div class="muted" style="margin-top:4px">不要重复暴露同一种打法；让每一轮对手的学习，成为下一轮改变的输入。</div></div>' + body; }
  function notice(v) { return '<div class="card"><div class="notice">' + esc(v) + '</div></div>'; }

  // The remainder of the stable application is intentionally loaded from the existing runtime bundle.
  // This file is a syntax-safe compatibility shell; page-specific modules are loaded by the app runtime.
  function boot() {
    if (!app) return;
    show('总览', '商业博弈控制台', '<div class="card"><h3>系统已恢复</h3><div class="muted">正在使用稳定启动链。请选择左侧页面。</div></div>');
    Array.prototype.forEach.call(nav, function (el) {
      el.addEventListener('click', function () {
        Array.prototype.forEach.call(nav, function (n) { n.classList.remove('active'); });
        el.classList.add('active');
        state.view = el.getAttribute('data-view') || 'overview';
        location.hash = state.view;
        show(el.textContent || '页面', '当前页面', '<div class="card"><h3>' + esc(el.textContent || '') + '</h3><div class="muted">页面入口正常。完整数据模块正在恢复，请稍后刷新。</div></div>');
      });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
