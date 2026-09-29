(function () {
  'use strict';

  var app = document.getElementById('app');
  var nav = document.querySelectorAll('.nav');
  var VERSION = '20260929-35';
  var BASE = 'https://skuoxmrzlxhebzhfgbyn.supabase.co';
  var KEY = 'sb_publishable_u46tZ4GMUgwqSYhMJNFG8Q_IzYwl95T';
  var CLIENT = 'ecommerce-agent-sandbox-v1';
  var state = {
    view: location.hash.slice(1) || 'overview',
    run: null,
    game: [],
    market: [],
    ads: {},
    backtests: [],
    events: [],
    memories: [],
    risk: [],
    tasks: [],
    agentRounds: [],
    playback: { playing: false, current: 0, timer: null, poll: null }
  };

  function esc(v) {
    return String(v == null ? '' : v)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function show(title, sub, body) {
    app.innerHTML =
      '<h1 class="page-title">' + esc(title) + '</h1>' +
      '<div class="subtitle">' + esc(sub) + '</div>' +
      body;
  }

  function notice(v) {
    return '<div class="card"><div class="notice">' + esc(v) + '</div></div>';
  }

  function table(headers, rows) {
    if (!rows.length) return notice('没有数据库记录。');
    var h = '<div class="card"><table class="table"><thead><tr>';
    for (var i = 0; i < headers.length; i++) {
      h += '<th>' + esc(headers[i]) + '</th>';
    }
    h += '</tr></thead><tbody>';
    for (var r = 0; r < rows.length; r++) {
      h += '<tr>';
      for (var c = 0; c < rows[r].length; c++) {
        h += '<td>' + esc(rows[r][c]) + '</td>';
      }
      h += '</tr>';
    }
    return h + '</tbody></table></div>';
  }

  function getJSON(url) {
    return fetch(url, {
      headers: {
        apikey: KEY,
        Authorization: 'Bearer ' + KEY,
        Accept: 'application/json'
      },
      cache: 'no-store'
    }).then(function (res) {
      return res.text().then(function (body) {
        var data;
        try {
          data = JSON.parse(body);
        } catch (e) {
          throw new Error('HTTP ' + res.status + ' 返回非 JSON');
        }
        if (!res.ok) {
          throw new Error('HTTP ' + res.status);
        }
        return data;
      });
    });
  }

  function runURL(name, runScoped) {
    var q = '?select=*&order=id.desc';
    if (runScoped && state.run && state.run.id) q += '&run_id=eq.' + encodeURIComponent(state.run.id);
    return BASE + '/rest/v1/' + name + q;
  }

  function loadRun() {
    var url = BASE +
      '/rest/v1/sandbox_runs?select=id,status,updated_at,client_key' +
      '&client_key=eq.' + encodeURIComponent(CLIENT) +
      '&order=updated_at.desc&limit=1';

    return getJSON(url).then(function (rows) {
      if (!Array.isArray(rows) || rows.length === 0) {
        throw new Error('没有找到 sandbox_runs');
      }
      state.run = rows[0];
    });
  }

  function loadCore() {
    return Promise.all([
      getJSON(runURL('sandbox_game_states', true)),
      getJSON(runURL('sandbox_market_signals', true)),
      getJSON(runURL('sandbox_backtests', true)),
      getJSON(runURL('sandbox_events', true)),
      getJSON(runURL('sandbox_memories', true)),
      getJSON(runURL('sandbox_risk_results', true)),
      getJSON(runURL('sandbox_task_results', true)),
      getJSON(runURL('sandbox_agent_rounds', true))
    ]).then(function (x) {
      state.game = x[0];
      state.market = x[1];
      state.backtests = x[2];
      state.events = x[3];
      state.memories = x[4];
      state.risk = x[5];
      state.tasks = x[6];
      state.agentRounds = x[7];
    });
  }

  var adTables = [
    'sandbox_ad_plans',
    'sandbox_ad_units',
    'sandbox_ad_keywords',
    'sandbox_ad_keyword_moves',
    'sandbox_ad_audiences',
    'sandbox_ad_audience_combos',
    'sandbox_ad_creatives',
    'sandbox_ad_placements',
    'sandbox_ad_regions',
    'sandbox_ad_timeslots',
    'sandbox_ad_negative_keywords',
    'sandbox_ad_agent_actions',
    'sandbox_ad_results',
    'sandbox_ad_reports'
  ];

  function loadAds() {
    var jobs = [];
    for (var i = 0; i < adTables.length; i++) {
      jobs.push(loadOneAd(adTables[i]));
    }
    return Promise.all(jobs).then(function (items) {
      state.ads = {};
      for (var j = 0; j < items.length; j++) {
        state.ads[items[j].name] = items[j].rows;
      }
    });
  }

  function loadOneAd(name) {
    return getJSON(runURL(name)).then(function (rows) {
      return { name: name, rows: rows };
    });
  }

  function agentSummary() {
    var rounds = state.agentRounds || [];
    if (!rounds.length) return notice('还没有 Agent 多轮闭环记录。');
    var last = rounds[rounds.length - 1];
    var stopped = 0;
    var blocked = 0;
    for (var i = 0; i < rounds.length; i++) {
      if (rounds[i].stop_signal) stopped++;
      if (!rounds[i].risk_approved) blocked++;
    }
    return '<div class="grid">' +
      '<div class="card"><div class="label">已模拟轮次</div><div class="metric">' + rounds.length + '</div></div>' +
      '<div class="card"><div class="label">风险拦截</div><div class="metric">' + blocked + '</div></div>' +
      '<div class="card"><div class="label">停止信号</div><div class="metric">' + stopped + '</div></div>' +
      '<div class="card"><div class="label">当前动作</div><div class="metric">' + esc(last.action) + '</div></div>' +
      '</div>' +
      '<div class="card"><div class="notice">最新一轮：' + esc(last.breakthrough || '') +
      ' · ROI ' + esc(last.roi) + ' · 边际ROI ' + esc(last.marginal_roi) +
      ' · 风险 ' + (last.risk_approved ? '通过' : '拦截') +
      (last.stop_signal ? ' · 已触发停止：' + esc(last.stop_reason) : '') + '</div></div>';
  }

  function overview() {
    show(
      '商业博弈总览',
      'BOOT-DEBUG-' + VERSION,
      '<div class="grid">' +
      '<div class="card"><div class="label">Sandbox Run</div><div class="metric">' + esc(state.run.status) + '</div></div>' +
      '<div class="card"><div class="label">商业博弈记录</div><div class="metric">' + state.game.length + '</div></div>' +
      '<div class="card"><div class="label">市场信号</div><div class="metric">' + state.market.length + '</div></div>' +
      '<div class="card"><div class="label">Agent闭环轮次</div><div class="metric">' + state.agentRounds.length + '</div></div>' +
      '</div>' +
      playbackPanel() +
      notice('上面的模拟器会按轮次播放当前 Sandbox Agent 的已生成结果；点击“开始”后每 1.8 秒推进一轮。当前仍不接真实店铺。')
    );
  }


  function sortedRounds() {
    return (state.agentRounds || []).slice().sort(function (a, b) {
      return Number(a.round || 0) - Number(b.round || 0);
    });
  }

  function playbackData() {
    var rounds = sortedRounds();
    if (!rounds.length) return null;
    var index = Math.max(0, Math.min(state.playback.current, rounds.length - 1));
    return { rounds: rounds, index: index, current: rounds[index] };
  }

  function playbackPanel() {
    var d = playbackData();
    if (!d) return notice('还没有可播放的 Agent 模拟轮次。');
    var r = d.current;
    var status = state.playback.playing ? '▶ 正在模拟' : (d.index >= d.rounds.length - 1 && state.run && state.run.status === 'completed' ? '■ 模拟完成' : 'Ⅱ 已暂停');
    var timeline = '<div style="display:flex;gap:6px;flex-wrap:wrap;margin:12px 0">';
    for (var i = 0; i < d.rounds.length; i++) {
      var cls = i === d.index ? 'tag warning' : (i < d.index ? 'tag positive' : 'tag');
      timeline += '<span class="' + cls + '">R' + esc(d.rounds[i].round) + '</span>';
    }
    timeline += '</div>';

    function parse(v, fallback) {
      try { return v ? (typeof v === 'string' ? JSON.parse(v) : v) : fallback; } catch (e) { return fallback; }
    }
    var branches = parse(r.response_branches, []);
    var opponents = parse(r.opponent_participants, []);
    var pathHtml = '';
    for (var p = 0; p <= d.index; p++) {
      var pr = d.rounds[p];
      var isCurrent = p === d.index;
      pathHtml += '<div style="display:flex;gap:8px;align-items:center;margin:6px 0">' +
        '<span class="tag ' + (isCurrent ? 'warning' : 'positive') + '">R' + esc(pr.round) + '</span>' +
        '<b>' + esc(pr.action) + '</b><span>→</span><span class="tag">' + esc(pr.actual_opponent_response || '-') + '</span><span>→</span><b>' + esc(pr.next_action_hint || '-') + '</b>' +
        (pr.stop_signal ? '<span class="tag warning">STOP</span>' : '') + '</div>';
    }

    var futureHtml = '';
    for (var q = d.index + 1; q < d.rounds.length; q++) {
      var fr = d.rounds[q];
      futureHtml += '<div style="display:flex;gap:8px;align-items:center;margin:6px 0;opacity:.7"><span class="tag">R' + esc(fr.round) + '</span><span>' + esc(fr.action) + '</span><span>→</span><span>' + esc(fr.actual_opponent_response || '-') + '</span></div>';
    }

    var opponentHtml = '';
    for (var o = 0; o < opponents.length; o++) {
      var op = opponents[o];
      var active = op.lastResponse === r.actual_opponent_response;
      opponentHtml += '<div style="flex:1;min-width:190px;border:1px solid var(--line);border-radius:10px;padding:10px;' + (active ? 'box-shadow:0 0 0 2px rgba(255,180,0,.25);' : '') + '">' +
        '<div class="label">' + esc(op.id) + '</div><b>' + esc(op.name) + '</b><br><span class="muted">' + esc(op.strategy) + '</span><br>' +
        '<span class="tag ' + (active ? 'warning' : '') + '">' + esc(op.lastResponse || '-') + '</span><br><span class="muted">压力 ' + esc(Number(op.pressure || 0).toFixed(2)) + ' · 适应 ' + esc(Number(op.adaptation || 0).toFixed(2)) + '</span>' +
        (active ? '<br><b>← 本轮实际进入主路径</b>' : '') + '</div>';
    }

    var branchHtml = '';
    for (var x = 0; x < branches.length; x++) {
      var chosen = branches[x].response === r.actual_opponent_response;
      branchHtml += '<div style="padding:8px 10px;margin:6px 0;border-left:3px solid ' + (chosen ? 'var(--accent)' : 'var(--line)') + ';background:' + (chosen ? 'rgba(255,180,0,.08)' : 'transparent') + '">' +
        '<b>' + (chosen ? '★ ' : '') + esc(branches[x].response) + '</b> · ' + esc(Math.round(Number(branches[x].probability || 0) * 100)) + '% → <b>' + esc(branches[x].nextActionHint) + '</b>' +
        '<div class="muted">停止：' + esc(branches[x].stopCondition) + '；扩张：' + esc(branches[x].expansionCondition) + '</div></div>';
    }

    var tree = '<div style="margin-top:14px;padding:12px;border:1px solid var(--line);border-radius:12px;overflow:auto">' +
      '<div class="label">完整动态博弈树 · 已走路径 + 当前分支 + 后续轮次</div>' +
      '<div style="min-width:900px;margin-top:10px">' +
      '<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">' +
      '<div style="border:2px solid var(--accent);border-radius:12px;padding:10px;min-width:150px"><div class="label">当前轮 R' + esc(r.round) + '</div><b>我们：' + esc(r.action) + '</b><br><span class="muted">突破：' + esc(r.breakthrough || '-') + '</span></div>' +
      '<div style="font-size:22px">→</div>' + (opponentHtml || '<span class="muted">暂无多方响应数据</span>') +
      '<div style="font-size:22px">→</div><div style="border:2px solid var(--line);border-radius:12px;padding:10px;min-width:150px"><div class="label">下一步</div><b>' + esc(r.next_action_hint || '-') + '</b></div>' +
      '</div>' +
      '<div style="margin-top:14px"><div class="label">已发生主路径</div>' + pathHtml + '</div>' +
      '<div style="margin-top:14px"><div class="label">未来模拟路径（尚未执行）</div>' + (futureHtml || '<span class="muted">当前已到最后一轮</span>') + '</div>' +
      '<div style="margin-top:14px"><div class="label">当前轮所有可能分支</div>' + (branchHtml || '<span class="muted">暂无分支</span>') + '</div>' +
      '</div></div>';

    return '<div class="card" id="agent-playback">' +
      '<div style="display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap">' +
      '<div><div class="label">Agent Sandbox 实时模拟器</div><div class="metric">' + status + ' · 第 ' + esc(r.round) + ' / ' + d.rounds.length + ' 轮</div></div>' +
      '<div><button class="action" id="sim-start">▶ 开始 / 新模拟</button><button class="action" id="sim-step">⏭ 单步</button><button class="action" id="sim-reset">↺ 重置</button></div></div>' +
      timeline +
      '<div class="grid"><div class="card"><div class="label">我方动作</div><div class="metric">' + esc(r.action) + '</div></div><div class="card"><div class="label">突破口</div><div class="metric">' + esc(r.breakthrough || '-') + '</div></div><div class="card"><div class="label">实际主响应</div><div class="metric">' + esc(r.actual_opponent_response || '-') + '</div></div><div class="card"><div class="label">下一动作</div><div class="metric">' + esc(r.next_action_hint || '-') + '</div></div></div>' +
      '<div class="notice">本轮结果：消耗 ' + esc(r.spend) + ' · 收入 ' + esc(r.revenue) + ' · ROI ' + esc(r.roi) + ' · 边际ROI ' + esc(r.marginal_roi) + ' · 拥挤 ' + esc(r.crowding) + (r.stop_signal ? ' · <b>触发停止：' + esc(r.stop_reason) + '</b>' : ' · 继续观察') + '</div>' +
      tree + '</div>';
  }

  function stopPlayback() {
    if (state.playback.timer) clearInterval(state.playback.timer);
    if (state.playback.poll) clearInterval(state.playback.poll);
    state.playback.timer = null;
    state.playback.poll = null;
    state.playback.playing = false;
  }

  function pollNewSimulation() {
    if (state.playback.poll) clearInterval(state.playback.poll);
    state.playback.poll = setInterval(function () {
      loadRun().then(loadCore).then(function () {
        state.playback.current = Math.max(0, state.agentRounds.length - 1);
        render();
        if (state.run && (state.run.status === 'completed' || state.run.status === 'failed')) {
          if (state.playback.poll) clearInterval(state.playback.poll);
          state.playback.poll = null;
          state.playback.playing = false;
          render();
        }
      }).catch(function (e) {
        console.error('SANDBOX_AGENT_POLL_ERROR', e);
      });
    }, 1200);
  }

  function advancePlayback() {
    if (!state.agentRounds.length) return;
    state.playback.current = Math.min(
      state.agentRounds.length - 1,
      state.playback.current + 1
    );
    if (state.playback.current >= state.agentRounds.length - 1 && state.run && state.run.status === 'completed') {
      state.playback.playing = false;
      if (state.playback.timer) clearInterval(state.playback.timer);
      state.playback.timer = null;
    }
    render();
  }

  function startNewSimulation() {
    stopPlayback();
    show('Agent 正在启动', 'Sandbox 新模拟', notice('正在创建新的 Agent 模拟任务……'));
    fetch(BASE + '/functions/v1/sandbox-agent-runner', {
      method: 'POST',
      headers: { apikey: KEY, Authorization: 'Bearer ' + KEY, 'Content-Type': 'application/json' },
      body: JSON.stringify({ client_key: CLIENT, rounds: 10 })
    }).then(function (res) {
      return res.text().then(function (body) {
        var data = {};
        try { data = JSON.parse(body); } catch (e) {}
        if (!res.ok) throw new Error(data.error || ('HTTP ' + res.status));
        return data;
      });
    }).then(function (data) {
      return loadRun().then(loadCore).then(function () {
        state.playback.current = 0;
        state.playback.playing = true;
        render();
        pollNewSimulation();
      });
    }).catch(function (e) {
      console.error('SANDBOX_AGENT_RUN_ERROR', e);
      show('Agent 模拟启动失败', 'Sandbox', notice(e.message));
    });
  }

  function startPlayback() {
    stopPlayback();
    if (!state.agentRounds.length) {
      startNewSimulation();
      return;
    }
    state.playback.playing = true;
    render();
    state.playback.timer = setInterval(function () {
      if (state.view !== 'game') {
        stopPlayback();
        return;
      }
      advancePlayback();
    }, 1800);
  }

  function bindPlayback() {
    var start = document.getElementById('sim-start');
    var step = document.getElementById('sim-step');
    var reset = document.getElementById('sim-reset');
    if (start) start.addEventListener('click', function () {
      if (state.playback.playing) stopPlayback(); else startPlayback();
      render();
    });
    if (step) step.addEventListener('click', function () {
      stopPlayback();
      advancePlayback();
    });
    if (reset) reset.addEventListener('click', function () {
      stopPlayback();
      state.playback.current = 0;
      render();
    });
  }

  function game() {
    var rows = [];
    for (var i = 0; i < state.game.length; i++) {
      var x = state.game[i];
      rows.push([x.product, x.competitor, x.scenario, x.competitor_price, x.our_price, x.cpc, x.cvr]);
    }
    var rounds = [];
    for (var j = 0; j < state.agentRounds.length; j++) {
      var r = state.agentRounds[j];
      rounds.push([r.round, r.action, r.recommended_action, r.breakthrough, r.risk_approved ? 'ALLOW' : 'BLOCK', r.decision_score, r.spend, r.revenue, r.conversions, r.roi, r.marginal_roi, r.crowding, r.actual_opponent_response || '', r.next_action_hint || '', (r.response_branches ? JSON.stringify(r.response_branches) : ''), r.stop_signal ? 'STOP' : '', r.stop_reason]);
    }
    show('商业博弈', 'BOOT-DEBUG-' + VERSION + ' · Sandbox 模拟数据 · 可视化模拟器',
      playbackPanel() +
      table(['产品','竞品','场景','竞品价格','我方价格','CPC','CVR'], rows) +
      '<h2>Agent 多轮闭环</h2>' +
      table(['轮次','实际动作','原推荐','突破口','风险','决策分','消耗','收入','成交','ROI','边际ROI','拥挤','对手响应','下一动作提示','响应分支','停止','停止原因'], rounds) +
      notice('这里展示 Agent 每一轮的：决策 → 风险 → 投入 → 市场结果 → 边际收益 → 停止信号 → 下一轮输入。'));
  }

  function market() {
    var rows = [];
    for (var i = 0; i < state.market.length; i++) {
      var x = state.market[i];
      rows.push([x.name, x.signal_type, x.strength, x.detail]);
    }
    show('Web 市场情报', 'BOOT-DEBUG-' + VERSION + ' · Sandbox 模拟数据',
      table(['名称','类型','强度','说明'], rows));
  }

  function ads() {
    var a = state.ads;
    var plans = a.sandbox_ad_plans || [];
    var units = a.sandbox_ad_units || [];
    var keywords = a.sandbox_ad_keywords || [];
    var moves = a.sandbox_ad_keyword_moves || [];
    var audiences = a.sandbox_ad_audiences || [];
    var combos = a.sandbox_ad_audience_combos || [];
    var creatives = a.sandbox_ad_creatives || [];
    var placements = a.sandbox_ad_placements || [];
    var regions = a.sandbox_ad_regions || [];
    var timeslots = a.sandbox_ad_timeslots || [];
    var negatives = a.sandbox_ad_negative_keywords || [];
    var actions = a.sandbox_ad_agent_actions || [];
    var results = a.sandbox_ad_results || [];
    var reports = a.sandbox_ad_reports || [];

    var planRows = [];
    for (var p = 0; p < plans.length; p++) {
      var q = plans[p];
      planRows.push([q.name, q.status, q.product, q.scene, q.daily_budget, q.bid_strategy]);
    }

    var unitRows = [];
    for (var u = 0; u < units.length; u++) {
      var un = units[u];
      unitRows.push([un.name, un.product, un.status, un.keyword_count, un.audience_count, un.creative_count]);
    }

    var keywordRows = [];
    for (var i = 0; i < keywords.length; i++) {
      var x = keywords[i];
      keywordRows.push([x.keyword, x.keyword_type, x.match_type, x.bid, x.impressions, x.clicks, x.ctr, x.conversions, x.cvr, x.spend, x.gmv, x.roi]);
    }

    var moveRows = [];
    for (var m = 0; m < moves.length; m++) {
      var mv = moves[m];
      moveRows.push([mv.source_keyword, mv.source_scene, mv.related_keyword, mv.related_scene, mv.move_type, mv.impressions, mv.clicks, mv.conversions, mv.cvr, mv.roi, mv.agent_conclusion, mv.status]);
    }

    var audienceRows = [];
    for (var j = 0; j < audiences.length; j++) {
      var au = audiences[j];
      audienceRows.push([au.name, au.audience_type, au.behavior, au.window_days, au.size, au.coverage, au.cvr, au.roi, au.bid, au.premium, au.overlap, au.status]);
    }

    var comboRows = [];
    for (var k = 0; k < combos.length; k++) {
      var co = combos[k];
      comboRows.push([co.name, JSON.stringify(co.components), co.size, co.overlap, co.cvr, co.roi, co.agent_conclusion]);
    }

    var creativeRows = [];
    for (var cr = 0; cr < creatives.length; cr++) {
      var cv = creatives[cr];
      creativeRows.push([cv.name, cv.creative_type, cv.title, cv.audit_status, cv.impressions, cv.clicks, cv.ctr, cv.conversions, cv.roi, cv.status]);
    }

    var placementRows = [];
    for (var pl = 0; pl < placements.length; pl++) {
      var pp = placements[pl];
      placementRows.push([pp.channel, pp.placement, pp.impressions, pp.clicks, pp.ctr, pp.spend, pp.conversions, pp.cvr, pp.gmv, pp.roi]);
    }

    var regionRows = [];
    for (var rg = 0; rg < regions.length; rg++) {
      var rr = regions[rg];
      regionRows.push([rr.region, rr.impressions, rr.clicks, rr.ctr, rr.spend, rr.conversions, rr.cvr, rr.roi]);
    }

    var timeRows = [];
    for (var ts = 0; ts < timeslots.length; ts++) {
      var tt = timeslots[ts];
      timeRows.push([tt.slot, tt.weekday, tt.impressions, tt.clicks, tt.ctr, tt.cpc, tt.conversions, tt.cvr, tt.roi]);
    }

    var negativeRows = [];
    for (var ng = 0; ng < negatives.length; ng++) {
      var nn = negatives[ng];
      negativeRows.push([nn.keyword, nn.clicks, nn.spend, nn.conversions, nn.agent_conclusion, nn.status]);
    }

    var actionRows = [];
    for (var ac = 0; ac < actions.length; ac++) {
      var aa = actions[ac];
      actionRows.push([aa.action_type, aa.target, aa.reason, JSON.stringify(aa.before_value), JSON.stringify(aa.after_value), aa.result, aa.status]);
    }

    var resultRows = [];
    for (var rs = 0; rs < results.length; rs++) {
      var re = results[rs];
      resultRows.push([re.kind, JSON.stringify(re.payload), re.created_at]);
    }

    var reportRows = [];
    for (var rp = 0; rp < reports.length; rp++) {
      var rd = reports[rp];
      reportRows.push([rd.dimension, rd.dimension_value, rd.impressions, rd.clicks, rd.ctr, rd.cpc, rd.spend, rd.conversions, rd.cvr, rd.gmv, rd.roi, rd.report_date]);
    }

    show(
      '广告 / 流量',
      'BOOT-DEBUG-' + VERSION + ' · Sandbox 模拟数据 · 广告数据链',
      '<div class="grid">' +
      '<div class="card"><div class="label">投放计划</div><div class="metric">' + plans.length + '</div></div>' +
      '<div class="card"><div class="label">投放单元</div><div class="metric">' + units.length + '</div></div>' +
      '<div class="card"><div class="label">关键词</div><div class="metric">' + keywords.length + '</div></div>' +
      '<div class="card"><div class="label">人群</div><div class="metric">' + audiences.length + '</div></div>' +
      '<div class="card"><div class="label">创意</div><div class="metric">' + creatives.length + '</div></div>' +
      '<div class="card"><div class="label">Agent动作</div><div class="metric">' + actions.length + '</div></div>' +
      '</div>' +
      '<h2>投放计划</h2>' + table(['投放计划','状态','商品','场景','日预算','出价策略'], planRows) +
      '<h2>投放单元</h2>' + table(['单元','商品','状态','关键词数','人群数','创意数'], unitRows) +
      '<h2>关键词</h2>' + table(['关键词','类型','匹配','出价','展现','点击','CTR','成交','CVR','消耗','GMV','ROI'], keywordRows) +
      '<h2>关键词迁移 / 扩词</h2>' + table(['源关键词','源场景','关联关键词','关联场景','动作类型','展现','点击','成交','CVR','ROI','Agent结论','状态'], moveRows) +
      '<h2>投放人群</h2>' + table(['人群','类型','行为','窗口天数','规模','覆盖率','CVR','ROI','出价','溢价','重叠','状态'], audienceRows) +
      '<h2>人群组合</h2>' + table(['组合','组成','规模','重叠','CVR','ROI','Agent结论'], comboRows) +
      '<h2>创意</h2>' + table(['名称','类型','标题','审核','展现','点击','CTR','成交','ROI','状态'], creativeRows) +
      '<h2>资源位</h2>' + table(['渠道','资源位','展现','点击','CTR','消耗','成交','CVR','GMV','ROI'], placementRows) +
      '<h2>地域</h2>' + table(['地域','展现','点击','CTR','消耗','成交','CVR','ROI'], regionRows) +
      '<h2>时段</h2>' + table(['时段','星期','展现','点击','CTR','CPC','成交','CVR','ROI'], timeRows) +
      '<h2>否定词</h2>' + table(['关键词','点击','消耗','成交','Agent结论','状态'], negativeRows) +
      '<h2>Agent动作</h2>' + table(['动作','目标','原因','动作前','动作后','结果','状态'], actionRows) +
      '<h2>投放结果</h2>' + table(['类型','Payload','时间'], resultRows) +
      '<h2>广告报告</h2>' + table(['维度','维度值','展现','点击','CTR','CPC','消耗','成交','CVR','GMV','ROI','日期'], reportRows) +
      notice('广告模块已恢复完整 Sandbox 数据链：计划 → 单元 → 关键词/扩词 → 人群 → 创意 → 资源位 → 地域 → 时段 → 否定词 → Agent动作 → 结果/报告。')
    );
  }

  function experiments() {
    var rows = [];
    for (var i = 0; i < state.backtests.length; i++) {
      var x = state.backtests[i];
      rows.push([x.scenario, x.rounds, x.roi, x.risk, x.action, x.created_at]);
    }
    show('实验与回测', 'BOOT-DEBUG-' + VERSION + ' · Sandbox 模拟回测',
      table(['场景','轮次','ROI','风险','动作','时间'], rows));
  }

  function risk() {
    var rows = [];
    for (var i = 0; i < state.risk.length; i++) {
      var x = state.risk[i];
      rows.push([x.metric, JSON.stringify(x.value), x.created_at]);
    }
    show('风险控制器', 'BOOT-DEBUG-' + VERSION + ' · Sandbox 风险结果',
      table(['指标','结果','时间'], rows) + '<h2>Agent 事后风险</h2>' + agentRiskTable());
  }

  function agentRiskTable() {
    var rounds = state.agentRounds || [];
    var rows = [];
    for (var i = 0; i < rounds.length; i++) {
      var x = rounds[i];
      rows.push([x.round, x.action, x.marginal_roi, x.crowding, x.stop_signal ? 'STOP' : 'CONTINUE', x.stop_reason]);
    }
    return table(['轮次','动作','边际ROI','拥挤','状态','原因'], rows);
  }

  function jobs() {
    var latest = state.agentRounds.length ? state.agentRounds[state.agentRounds.length - 1] : null;
    var progress = state.run ? (state.run.agent_progress || 0) : 0;
    var status = state.run ? state.run.status : 'unknown';
    var latestTask = state.tasks.length ? state.tasks[0] : null;
    var hero =
      '<div class="card">' +
      '<h2>Agent 实时任务</h2>' +
      '<div class="notice">' +
      'Run：' + esc(state.run ? state.run.id : '未启动') +
      '　状态：<b>' + esc(status) + '</b>' +
      '　进度：<b>' + esc(progress) + '%</b>' +
      '</div>' +
      (latest ? '<div class="grid">' +
        '<div><b>当前轮次</b><br>R' + esc(latest.round) + '</div>' +
        '<div><b>我方动作</b><br>' + esc(latest.action) + '</div>' +
        '<div><b>突破口</b><br>' + esc(latest.breakthrough) + '</div>' +
        '<div><b>对手响应</b><br>' + esc(latest.actual_opponent_response) + '</div>' +
        '<div><b>下一动作</b><br>' + esc(latest.next_action_hint) + '</div>' +
        '<div><b>边际ROI</b><br>' + esc(latest.marginal_roi) + '</div>' +
        '</div>' : '<p>尚未产生 Agent 轮次。</p>') +
      '</div>';
    var rows = [];
    for (var i = 0; i < state.tasks.length; i++) {
      var x = state.tasks[i];
      rows.push([x.task_id, x.task_type, x.status, x.progress + '%', x.created_at]);
    }
    var rounds = [];
    for (var j = 0; j < state.agentRounds.length; j++) {
      var r = state.agentRounds[j];
      rounds.push(['R' + r.round, r.action, r.actual_opponent_response, r.next_action_hint, r.stop_signal ? 'STOP' : 'CONTINUE', r.marginal_roi]);
    }
    show('任务监控', 'BOOT-DEBUG-' + VERSION + ' · Sandbox Agent 执行过程',
      hero +
      '<h2>任务队列</h2>' +
      (latestTask ? table(['任务ID','任务类型','状态','进度','创建时间'], rows) : notice('当前 Run 尚未创建任务。')) +
      '<h2>Agent 轮次</h2>' +
      (rounds.length ? table(['轮次','我方动作','对手响应','下一动作','风控信号','边际ROI'], rounds) : notice('等待 Agent 开始第一轮。')) +
      '<h2>事件流</h2>' + eventTable());
  }

  function eventTable() {
    var rows = [];
    for (var i = 0; i < state.events.length; i++) {
      var x = state.events[i];
      rows.push([x.event_type, x.title, x.detail, JSON.stringify(x.payload), x.created_at]);
    }
    return table(['事件类型','标题','详情','Payload','时间'], rows);
  }

  function memory() {
    var rows = [];
    for (var i = 0; i < state.memories.length; i++) {
      var x = state.memories[i];
      rows.push([x.memory_type, x.content, x.confidence, x.status, x.created_at]);
    }
    show('学习记忆', 'BOOT-DEBUG-' + VERSION + ' · Sandbox 学习结果',
      table(['记忆类型','内容','置信度','状态','时间'], rows));
  }

  function render() {
    for (var i = 0; i < nav.length; i++) {
      nav[i].classList.toggle('active', nav[i].dataset.view === state.view);
    }

    if (state.view === 'game') {
      game();
    } else if (state.view === 'market') {
      market();
    } else if (state.view === 'ads') {
      ads();
    } else if (state.view === 'overview') {
      overview();
    } else if (state.view === 'experiments') {
      experiments();
    } else if (state.view === 'risk') {
      risk();
    } else if (state.view === 'jobs') {
      jobs();
    } else if (state.view === 'memory') {
      memory();
    } else {
      overview();
    }
    if (state.view === 'game') bindPlayback();
  }

  function start() {
    show('数据库业务数据测试', 'BOOT-DEBUG-' + VERSION, notice('正在读取核心数据……'));

    loadRun()
      .then(loadCore)
      .then(loadAds)
      .then(function () {
        render();
      })
      .catch(function (e) {
        console.error('BUSINESS_DATA_ERROR', e);
        show('数据库业务数据读取失败', 'BOOT-DEBUG-' + VERSION, notice(e.message));
      });
  }

  for (var n = 0; n < nav.length; n++) {
    nav[n].addEventListener('click', function () {
      state.view = this.dataset.view;
      location.hash = state.view;
      render();
    });
  }

  window.__EA_APPDB_LOADED__ = true;
  window.__EA_APPDB_VERSION__ = VERSION;
  window.__EA_SIMULATOR__ = state.playback;
  start();
}());
