(function () {
  'use strict';

  var app = document.getElementById('app');
  var nav = document.querySelectorAll('.nav');
  var VERSION = '20260929-45';
  var BASE = 'https://skuoxmrzlxhebzhfgbyn.supabase.co';
  var KEY = 'sb_publishable_u46tZ4GMUgwqSYhMJNFG8Q_IzYwl95T';
  var CLIENT = 'ecommerce-agent-sandbox-v1';
  var state = {
    view: location.hash.slice(1) || 'overview',
    run: null,
    error: null,
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
      '<h1 class="page-title">' + esc(title) + ' <span style="font-size:16px;font-weight:500;color:var(--accent);margin-left:10px">我变 → 对手学 → 我再变</span></h1>' +
      '<div class="subtitle">' + esc(sub) + '</div>' +
      '<div class="card" style="margin:10px 0 16px;border-left:4px solid var(--accent);background:rgba(255,180,0,.06)"><b>连续博弈座右铭</b><div style="font-size:18px;margin-top:6px">我变 → 对手学 → 我再变</div><div class="muted" style="margin-top:4px">不要重复暴露同一种打法；让每一轮对手的学习，成为下一轮改变的输入。</div></div>' +
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
      '/rest/v1/sandbox_runs?select=id,status,updated_at,client_key,agent_progress,backtest_progress,risk_progress,memory_count,run_count,state' +
      '&client_key=eq.' + encodeURIComponent(CLIENT) +
      '&order=updated_at.desc&limit=1';

    return getJSON(url).then(function (rows) {
      if (!Array.isArray(rows) || rows.length === 0) {
        throw new Error('没有找到 sandbox_runs');
      }
      state.run = rows[0];
      state.error = state.run.status === 'failed' && state.run.state && state.run.state.error ? state.run.state.error : null;
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

  function chainPanel(latest) {
    var steps = [
      ['01','输入','我方 + 对手 + 市场 Sandbox 数据'],
      ['02','突破口','识别可利用的竞争结构'],
      ['03','策略','选择本轮动作与后续动作'],
      ['04','Risk Controller','资金 / 单位经济 / 市场 / 对手风险拦截'],
      ['05','执行','模拟投入、出价、价格、关键词/定向'],
      ['06','对手','多个参与者分别响应并更新压力/适应'],
      ['07','市场','收入、ROI、边际ROI、拥挤、库存/现金'],
      ['08','反馈','真实响应写回下一轮决策状态'],
      ['09','继续/停止','扩张、降级、等待或 STOP'],
      ['10','学习','把本轮结果作为下一轮输入']
    ];
    var html='<div class="card"><div class="label">完整闭环链路 · 每一轮都从左向右经过</div><div style="display:flex;gap:8px;overflow:auto;padding:12px 0">';
    for(var i=0;i<steps.length;i++){
      html+='<div style="min-width:150px;border:1px solid var(--line);border-radius:10px;padding:10px;background:'+(latest&&i===6?'rgba(255,180,0,.08)':'transparent')+'"><span class="tag">'+steps[i][0]+'</span><br><b>'+esc(steps[i][1])+'</b><div class="muted">'+esc(steps[i][2])+'</div></div>';
      if(i<steps.length-1) html+='<div style="font-size:20px;align-self:center">→</div>';
    }
    html+='</div>'+(latest?'<div class="notice">当前执行位置：R'+esc(latest.round)+' · '+esc(latest.action)+' → '+esc(latest.actual_opponent_response||'-')+' → '+esc(latest.next_action_hint||'-')+' · '+(latest.stop_signal?'已停止':'继续')+'</div>':'<div class="notice">等待第一轮模拟。</div>')+'</div>';
    return html;
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
      chainPanel((state.agentRounds||[]).length ? state.agentRounds[state.agentRounds.length-1] : null) +
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

  function strategyStepsPanel(round, allRounds) {
    function parseSteps(v) { try { return v ? (typeof v === 'string' ? JSON.parse(v) : v) : []; } catch(e) { return []; } }
    var steps = parseSteps(round.strategy_steps || (round.decision_tree && round.decision_tree.strategySteps));
    var html = '<div style="margin-top:14px"><div class="label">本轮博弈：每一个参与者采用了什么策略</div>';
    if (!steps.length) return html + '<div class="muted">本轮暂无策略拆解数据。</div></div>';
    html += '<div style="display:grid;gap:8px;margin-top:8px">';
    for (var i=0;i<steps.length;i++) {
      var s=steps[i], mine=s.actor==='OUR_AGENT', hit=s.actor!=='OUR_AGENT' && s.responseToUs===round.actual_opponent_response;
      html += '<div style="border:1px solid var(--line);border-radius:10px;padding:10px;background:'+(mine?'rgba(80,160,255,.06)':(hit?'rgba(255,180,0,.08)':'transparent'))+'">' +
        '<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap"><span class="tag '+(mine?'positive':(hit?'warning':''))+'">'+esc(s.actorName||s.participant||s.actor)+'</span><b>策略：'+esc(s.strategy||s.strategyCode||'-')+'</b><span>→</span><b>动作：'+esc(s.action||'-')+'</b>'+(hit?'<span class="tag warning">实际响应</span>':'')+'</div>' +
        '<div class="muted" style="margin-top:5px">触发：'+esc(s.trigger||'-')+'；原因：'+esc(s.rationale||'-')+'</div><div style="margin-top:5px">对我方：'+esc(s.responseToUs||s.result||'-')+' · 下一策略：'+esc(s.nextStrategy||'-')+'</div></div>';
    }
    html += '</div></div>';
    if (allRounds && allRounds.length) {
      html += '<div style="margin-top:14px"><div class="label">全程策略轨迹（每一轮都记录）</div><div style="overflow:auto"><table class="table"><thead><tr><th>轮次</th><th>我方策略</th><th>我方动作</th><th>价格竞品</th><th>流量竞品</th><th>内容竞品</th><th>实际主响应</th><th>下一策略</th></tr></thead><tbody>';
      for (var j=0;j<allRounds.length;j++) {
        var rr=allRounds[j], ss=parseSteps(rr.strategy_steps || (rr.decision_tree && rr.decision_tree.strategySteps)), map={};
        for(var z=0;z<ss.length;z++) map[ss[z].actor]=ss[z];
        html += '<tr><td>R'+esc(rr.round)+'</td><td>'+esc(map.OUR_AGENT&&map.OUR_AGENT.strategy||'-')+'</td><td>'+esc(rr.action||'-')+'</td><td>'+esc(map['OPP-01']&&map['OPP-01'].strategy||'-')+' / '+esc(map['OPP-01']&&map['OPP-01'].action||'-')+'</td><td>'+esc(map['OPP-02']&&map['OPP-02'].strategy||'-')+' / '+esc(map['OPP-02']&&map['OPP-02'].action||'-')+'</td><td>'+esc(map['OPP-03']&&map['OPP-03'].strategy||'-')+' / '+esc(map['OPP-03']&&map['OPP-03'].action||'-')+'</td><td><b>'+esc(rr.actual_opponent_response||'-')+'</b></td><td>'+esc(rr.next_action_hint||'-')+'</td></tr>';
      }
      html += '</tbody></table></div></div>';
    }
    return html;
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
      strategyStepsPanel(r, d.rounds) +
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
    state.error = null;
    show('Agent 正在启动', 'Sandbox 新模拟', chainPanel(null) + notice('正在创建新的 Agent 模拟任务……'));
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
      state.error = e.message;
      show('Agent 模拟启动失败', 'Sandbox', chainPanel(null) + '<div class="card"><div class="notice"><b>错误已进入网页事件链：</b> ' + esc(e.message) + '</div></div>' + eventTable());
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
      if (state.view !== 'game' && state.view !== 'overview') {
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

  function gameLogic() {
    var list = window.EA_GAME_LOGICS || [];
    var selectedId = list.length ? list[0].id : '';

    function renderDetail(x) {
      if (!x) return notice('没有预设博弈逻辑。');
      var h = '<div class="card"><span class="tag">' + esc(x.id) + '</span><span class="tag">' + esc(x.type) + '</span>' +
        '<h2>' + esc(x.name) + '</h2><div class="muted">触发条件：' + esc(x.trigger) + '</div>' +
        '<h3>完整博弈过程</h3><div style="display:grid;gap:8px">';
      for (var i=0;i<x.steps.length;i++) {
        h += '<div style="padding:10px;border:1px solid var(--line);border-radius:8px"><span class="tag">第' + (i+1) + '步</span> ' + esc(x.steps[i]) + '</div>';
      }
      h += '</div><h3>对手可能分支</h3><div class="notice">' + x.branches.map(esc).join('　|　') + '</div>' +
        '<div class="notice"><b>终局目标：</b>' + esc(x.goal) + '</div></div>';
      return h;
    }

    var buttons='<div class="card"><div class="label">30套预设博弈逻辑</div><div class="muted" style="margin:6px 0 12px">点击 G01、G02、G03……查看对应的完整博弈过程。</div><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px">';
    for(var j=0;j<list.length;j++){
      var x=list[j];
      buttons+='<button type="button" class="game-logic-choice" data-id="'+esc(x.id)+'" style="text-align:left;padding:10px;border:1px solid '+(x.id===selectedId?'var(--accent)':'var(--line)')+';border-radius:8px;background:transparent;color:inherit;cursor:pointer"><span class="tag">'+esc(x.id)+'</span> <b>'+esc(x.name)+'</b><div class="muted">'+esc(x.type)+'</div></button>';
    }
    buttons+='</div></div><div id="game-logic-detail">'+renderDetail(list[0])+'</div>';

    show('博弈逻辑','30套预设商业博弈逻辑 · 点击编号查看完整博弈过程',buttons);

    var choices=document.querySelectorAll('.game-logic-choice');
    for(var k=0;k<choices.length;k++){
      choices[k].addEventListener('click',function(){
        var id=this.dataset.id, found=null;
        for(var z=0;z<list.length;z++) if(list[z].id===id){found=list[z];break;}
        if(!found) return;
        selectedId=id;
        document.getElementById('game-logic-detail').innerHTML=renderDetail(found);
        var all=document.querySelectorAll('.game-logic-choice');
        for(var q=0;q<all.length;q++){
          all[q].style.borderColor=all[q].dataset.id===id?'var(--accent)':'var(--line)';
        }
      });
    }
  }

  function threats() {
    var list=window.EA_THREAT_LIBRARY||[];
    var selected=list.length?list[0]:null;
    function detail(x){
      if(!x)return notice('暂无对手攻击面数据。');
      var playbooks=(window.EA_THREAT_PLAYBOOKS||{})[x.id]||[];
      var inf=window.EA_THREAT_INFERENCE||{};
      var signals=(inf.threatSignals&&inf.threatSignals[x.id])||[];
      var vis=(inf.visibility&&inf.visibility[x.id])||{level:'未知',data:[],missing:[],alternatives:[]};
      var h='<div class="card"><span class="tag warning">'+esc(x.id)+'</span> <span class="tag">'+esc(x.category)+'</span><h2>'+esc(x.name)+'</h2>'+
        '<div class="label">实际能看到的信号</div><div class="notice">'+esc(x.signal)+'</div>'+
        '<div class="label">数据可见性</div><div class="notice"><b>'+esc(vis.level)+'</b><br>可用：'+esc((vis.data||[]).join('、'))+'<br>缺失：'+esc((vis.missing||[]).join('、'))+'<br>替代解释：'+esc((vis.alternatives||[]).join('、'))+'</div>'+
        '<div class="label">理论攻击链</div><div style="display:grid;gap:6px">';
      for(var i=0;i<playbooks.length;i++)h+='<div class="notice"><span class="tag warning">STEP '+(i+1)+'</span> '+esc(playbooks[i])+'</div>';
      h+='</div><div class="label">推断流程</div><div class="notice">先观察结果性信号 → 建立多个假设 → 寻找旁证 → 更新置信度 → 决定下一观察项。没有旁证时不把理论攻击链当成事实。</div>'+
        '<div class="label">防范重点</div><div class="notice">'+esc(x.defense||'建立基线、留存证据、降低单点依赖并使用平台正常申诉/举证渠道。')+'</div></div>';
      return h;
    }
    var b='<div class="card"><div class="label">潜在攻击机制 · '+list.length+'项</div><div class="muted">旧版攻击面分析保留：只展示可观测信号、数据可见性、理论攻击链与防范重点。</div><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:8px;margin-top:12px">';
    for(var i=0;i<list.length;i++){var x=list[i];b+='<button type="button" class="threat-choice" data-id="'+esc(x.id)+'" style="text-align:left;padding:10px;border:1px solid '+(selected&&x.id===selected.id?'var(--accent)':'var(--line)')+';border-radius:8px;background:transparent;color:inherit;cursor:pointer"><span class="tag warning">'+esc(x.id)+'</span> <b>'+esc(x.name)+'</b><div class="muted">'+esc(x.category)+'</div></button>';}
    b+='</div></div><div id="threat-detail">'+detail(selected)+'</div>';
    show('对手攻击面','现实数据推断：可观测信号 → 多假设 → 理论攻击链 → 防范重点',b);
    var cs=document.querySelectorAll('.threat-choice');
    for(var j=0;j<cs.length;j++)cs[j].addEventListener('click',function(){var id=this.dataset.id,found=null;for(var k=0;k<list.length;k++)if(list[k].id===id){found=list[k];break;}if(!found)return;document.getElementById('threat-detail').innerHTML=detail(found);var all=document.querySelectorAll('.threat-choice');for(var q=0;q<all.length;q++)all[q].style.borderColor=all[q].dataset.id===id?'var(--accent)':'var(--line)';});
  }

  function positiveAttacks() {
    var list = window.EA_POSITIVE_ATTACK_LIBRARY || [];
    var selected = list.length ? list[0] : null;

    function detail(x) {
      if (!x) return notice('暂无正向增长策略。');
      var p = null, ps = window.EA_POSITIVE_ATTACK_PLAYBOOKS || [];
      for (var pi=0;pi<ps.length;pi++) if(ps[pi].id===x.id){p=ps[pi];break;}
      var stages = p && p.stages ? p.stages : [];
      var resp = p && p.opponentResponses ? p.opponentResponses.join(' / ') : '无数据';
      var ends = p && p.endStates ? p.endStates.join(' / ') : '扩大 / 保持 / 降级 / 等待 / 停止';

      var defense = [
        '先设保护线：预算、毛利、库存、履约和现金流不能因为实验失控',
        '监测搜索、流量、CTR、CVR、退款、评价、投诉等关键指标，区分市场自然波动与竞争响应',
        '如果实验效果不确定，缩小规模继续采样，不把低样本结果当成结论'
      ];
      var offense = [
        x.action || '围绕当前增长变量做小规模实验',
        '把成功动作拆成多个可验证变量，逐项测试，避免一次性重投入',
        '优先建设真实、可持续、难以被单点复制的产品/内容/服务/供应链能力'
      ];
      var mirror = [
        '观察对手是否复制该增长动作，再决定是否迁移到下一条路线',
        '如果对手跟随，改变变量组合、场景、人群或渠道，而不是长期重复同一种打法',
        '镜像的是竞争机制，不复制虚假评价、恶意举报、骚扰、造谣、刷量等违规手段'
      ];

      function bullets(items){var h='<div style="display:grid;gap:7px">';for(var bi=0;bi<items.length;bi++)h+='<div class="notice">• '+esc(items[bi])+'</div>';return h+'</div>';}
      var stageHtml = stages.length ? '<div class="label">多轮博弈链</div><div style="display:grid;gap:8px">' +
        '<div class="notice"><b>R1 触发</b>：'+esc(stages[0])+'</div>' +
        '<div class="notice"><b>R2 我方动作</b>：'+esc(stages[1])+'</div>' +
        '<div class="notice"><b>R3 观察反馈</b>：'+esc(stages[2])+'</div>' +
        '<div class="notice"><b>R4 市场/对手响应假设</b>：'+esc(stages[3])+'</div>' +
        '<div class="notice"><b>R5 终局决策</b>：'+esc(stages[4])+'</div></div>' : '';

      return '<div class="card" style="border:2px solid var(--accent);padding:16px">' +
        '<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap"><span class="tag positive">'+esc(x.id)+'</span><span class="tag">'+esc(x.category)+'</span><span class="tag positive">主动增长</span></div>' +
        '<h2>'+esc(x.name)+'</h2>' +
        '<div class="label">发现条件</div><div class="notice">'+esc(x.signal)+'</div>' +
        '<div class="label">建议动作</div><div class="notice">'+esc(x.action)+'</div>' +
        '<div class="label">战略目标</div><div class="notice"><b>'+esc(x.goal)+'</b></div>' +
        '<div class="label">① 防守方案 · 防止增长实验反噬</div>'+bullets(defense) +
        '<div class="label" style="margin-top:14px">② 正向进攻方案 · 主增长路线</div>'+bullets(offense) +
        '<div class="label" style="margin-top:14px">③ 镜像应对 · 对手跟随后的换路方案</div>'+bullets(mirror) +
        stageHtml +
        '<div class="label">可能响应（假设，不是已观测事实）</div><div class="notice">'+esc(resp)+'</div>' +
        '<div class="label">终局状态</div><div class="notice">'+esc(ends)+'</div>' +
        '<div class="card" style="margin-top:14px;border-left:4px solid var(--accent)"><b>连续博弈</b><div style="font-size:17px;margin-top:5px">我变 → 对手学 → 我再变</div><div class="muted" style="margin-top:5px">正向攻势不是找到一个“永久有效”的打法，而是建立一条能够持续实验、反馈、换路的增长路径。</div></div>' +
        '<div class="muted" style="margin-top:12px">所有方案先进入 Sandbox，并经过 Risk Controller；不把竞品隐藏动作当成已知事实。</div>' +
        '</div>';
    }

    var groups = {};
    for (var i=0;i<list.length;i++) {
      var c=list[i].category;
      if(!groups[c]) groups[c]=[];
      groups[c].push(list[i]);
    }
    var buttons='<div class="card"><div class="label">正向增长攻势 · '+list.length+'项 · 每项包含防守 / 正攻 / 镜像应对</div>' +
      '<div class="muted" style="margin:6px 0 12px">这里不是“防守对手”，而是寻找我方可以主动改变市场结果的变量：搜索、主图、详情、视频、真实评价、品牌合作、认证、产品、服务、供应链、渠道等。</div>' +
      '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:8px">';
    for(var j=0;j<list.length;j++){
      var x=list[j];
      buttons+='<button type="button" class="positive-attack-choice" data-id="'+esc(x.id)+'" style="text-align:left;padding:10px;border:1px solid '+(selected&&x.id===selected.id?'var(--accent)':'var(--line)')+';border-radius:8px;background:transparent;color:inherit;cursor:pointer"><span class="tag positive">'+esc(x.id)+'</span> <b>'+esc(x.name)+'</b><div class="muted">'+esc(x.category)+'</div></button>';
    }
    buttons+='</div></div>' +
      '<div class="card"><div class="label">正向攻势的六大变量</div><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px;margin-top:8px">' +
      '<div class="notice"><b>流量</b><br>关键词、搜索内容、达人、渠道</div>' +
      '<div class="notice"><b>点击</b><br>主图、标题、素材、视频</div>' +
      '<div class="notice"><b>转化</b><br>详情页、评价、信任、服务</div>' +
      '<div class="notice"><b>商品</b><br>SKU、规格、套餐、新品</div>' +
      '<div class="notice"><b>品牌</b><br>合作、授权、认证、心智</div>' +
      '<div class="notice"><b>供给</b><br>成本、库存、履约、独家合作</div>' +
      '</div></div>' +
      '<div id="positive-attack-detail">'+detail(selected)+'</div>';

    show('正向攻势','主动增长模型 · '+list.length+'种可观察、可实验的竞争动作',buttons);
    var cs=document.querySelectorAll('.positive-attack-choice');
    for(var k=0;k<cs.length;k++) cs[k].addEventListener('click',function(){
      var id=this.dataset.id, found=null;
      for(var z=0;z<list.length;z++) if(list[z].id===id){found=list[z];break;}
      if(!found)return;
      document.getElementById('positive-attack-detail').innerHTML=detail(found);
      var all=document.querySelectorAll('.positive-attack-choice');
      for(var q=0;q<all.length;q++) all[q].style.borderColor=all[q].dataset.id===id?'var(--accent)':'var(--line)';
      document.getElementById('positive-attack-detail').scrollIntoView({behavior:'smooth',block:'start'});
    });
  }

  function humanBehavior() {
    var list = window.EA_HUMAN_BEHAVIOR_LIBRARY || [];
    var selected = list.length ? list[list.length - 1] : null;

    function tone(x) {
      if (x === '低') return 'positive';
      if (x === '高' || x === '中高') return 'warn';
      return '';
    }

    function hasNegative(x) {
      var seq = x.sequence || [];
      for (var i=0;i<seq.length;i++) {
        if (String(seq[i]).indexOf('负') >= 0 || String(seq[i]).indexOf('强负') >= 0) return true;
      }
      return x.risk === '高' || x.risk === '中高';
    }

    function hasPositive(x) {
      var seq = x.sequence || [];
      for (var i=0;i<seq.length;i++) if (String(seq[i]).indexOf('正') >= 0) return true;
      return false;
    }

    function hasSwitch(x) {
      var seq = x.sequence || [];
      var last = '';
      for (var i=0;i<seq.length;i++) {
        var cur = String(seq[i]);
        if (last && cur !== last) return true;
        last = cur;
      }
      return seq.length >= 3;
    }

    function planFor(x) {
      var negative = hasNegative(x);
      var positive = hasPositive(x);
      var switching = hasSwitch(x);
      var defense = [];
      var offense = [];
      var mirror = [];

      defense.push('把该行为当作“可观测模式”而不是人格结论；至少连续观察多个窗口');
      defense.push('建立价格、流量、转化、评价、退款、投诉、广告和排名的异常基线，发现异常先记录事实再归因');
      if (negative) {
        defense.push('对负向压力做隔离：降低单一渠道/单一关键词/单一爆款依赖，并设置预算、库存和利润保护线');
        defense.push('保存可验证证据与时间线；遇到平台规则相关问题走正式申诉/举证渠道，不用情绪化响应');
      } else {
        defense.push('保持低成本监测，不因正常竞争动作过度反应');
      }

      if (positive) {
        offense.push('正向竞争：把产品、内容、服务、评价、供应链和品牌资产做成对手难以快速复制的长期变量');
        offense.push('优先做小规模实验，用真实反馈验证增量，再逐步扩大，不把一次成功当成永久优势');
      }
      if (negative) {
        offense.push('针对其施压所在的变量建立替代路线：价格压力→价值/套餐/成本结构；流量压力→关键词/内容/渠道分散；转化压力→商品与信任资产强化');
        offense.push('只在有证据支持时做“精准反制”，目标是恢复我方经营空间，而不是无差别升级冲突');
      } else {
        offense.push('以正向增长为主：抢占真实需求、内容入口、服务体验和供应链效率等可持续变量');
      }

      mirror.push('镜像反制：可以复制“竞争机制”，但必须使用真实商品、真实数据、正常投放和平台允许的方式');
      if (negative) {
        mirror.push('如果对方持续价格施压，可做有边界的价格/套餐实验；如果对方强化内容覆盖，可增加内容覆盖；如果对方争夺流量，可测试替代入口');
        mirror.push('不要复制虚假评价、恶意举报、骚扰、造谣、刷量或其他违规手段；这些不进入策略库');
      } else {
        mirror.push('如果对方以建设性方式竞争，优先用更好的产品、内容、服务和效率回应，而不是把正向竞争转成负向对抗');
      }
      if (switching) {
        mirror.push('对手一旦切换路径，我方同步切换观察维度；不要在同一位置长期重复暴露');
      }

      return {defense:defense, offense:offense, mirror:mirror};
    }

    function detail(x) {
      if (!x) return notice('暂无行为模型。');
      var seq = x.sequence || [];
      var flow = '';
      for (var i=0;i<seq.length;i++) {
        flow += '<span class="tag '+tone(x.risk)+'">'+esc(seq[i])+'</span>';
        if(i<seq.length-1) flow += ' <span class="muted">→</span> ';
      }
      var plan = planFor(x);
      function bullets(items, cls) {
        var h='<div style="display:grid;gap:7px">';
        for(var bi=0;bi<items.length;bi++) h+='<div class="notice '+(cls||'')+'">• '+esc(items[bi])+'</div>';
        return h+'</div>';
      }
      return '<div class="card" style="border:2px solid var(--accent);padding:16px">' +
        '<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap"><span class="tag">'+esc(x.id)+'</span><span class="tag">'+esc(x.style)+'</span><span class="tag '+tone(x.risk)+'">风险：'+esc(x.risk)+'</span></div>' +
        '<h2>'+esc(x.name)+'</h2>' +
        '<div class="label">行为演变链</div><div class="notice">'+flow+'</div>' +
        '<div class="label">可观测特征</div><div class="notice">'+esc(x.signal)+'</div>' +
        '<div class="label">可能目标</div><div class="notice"><b>'+esc(x.goal)+'</b></div>' +
        '<div class="label">① 防守方案 · 先保护自己</div>'+bullets(plan.defense) +
        '<div class="label" style="margin-top:14px">② 正向进攻方案 · 建设自己的优势</div>'+bullets(plan.offense,'positive') +
        '<div class="label" style="margin-top:14px">③ 镜像反制 · 以其竞争机制还之，但不复制违规手段</div>'+bullets(plan.mirror,'warning') +
        '<div class="card" style="margin-top:14px;border-left:4px solid var(--accent)"><b>连续博弈规则</b><div style="font-size:17px;margin-top:5px">我变 → 对手学 → 我再变</div><div class="muted" style="margin-top:5px">每次反制都要记录：对手实际行为 → 我方响应 → 市场反馈 → 对手下一次是否改变。未知就是未知，不把推测写成事实。</div></div>' +
        '<div class="muted" style="margin-top:12px">这是行为模式假设，不是心理诊断。所有“进攻/反制”仅进入商业竞争范围，并受平台规则、法律和 Risk Controller 约束。</div>' +
        '</div>';
    }

    var buttons='<div class="card"><div class="label">人性行为演变 · '+list.length+'种行为模式</div>' +
      '<div class="muted" style="margin:6px 0 12px">这里不只回答“他是什么行为模式”，而是把识别结果直接转换成三套可执行方案：防守、正向进攻、镜像反制。每套方案都要根据新的观测持续更新。</div>' +
      '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:8px">';
    for(var j=0;j<list.length;j++){
      var x=list[j];
      buttons+='<button type="button" class="human-behavior-choice" data-id="'+esc(x.id)+'" style="text-align:left;padding:10px;border:1px solid '+(selected&&x.id===selected.id?'var(--accent)':'var(--line)')+';border-radius:8px;background:transparent;color:inherit;cursor:pointer"><span class="tag">'+esc(x.id)+'</span> <b>'+esc(x.name)+'</b><div class="muted">'+esc(x.style)+' · 风险 '+esc(x.risk)+'</div></button>';
    }
    buttons+='</div></div>' +
      '<div class="card"><div class="label">四层输出</div><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px;margin-top:8px">' +
      '<div class="notice"><b>① 识别</b><br>行为模式、证据、置信度、下一观察项</div>' +
      '<div class="notice"><b>② 防守</b><br>隔离风险、降低暴露、保护利润和数据</div>' +
      '<div class="notice"><b>③ 正攻</b><br>产品、内容、服务、流量、供应链等建设性竞争</div>' +
      '<div class="notice"><b>④ 镜像反制</b><br>在合规边界内回应对方的竞争机制，不复制违规行为</div>' +
      '</div></div>' +
      '<div class="card"><div class="label">系统判断原则</div><div class="notice">' +
      '不要因为一次差评、一次降价、一次流量变化就给对手贴上“负向型”标签。至少观察多个窗口，比较持续性、集中度、跨指标同步变化和行为转折点。最终输出“行为模式假设 + 置信度 + 防守方案 + 正向进攻方案 + 镜像反制方案 + 下一观察项”。' +
      '</div></div>' +
      '<div id="human-behavior-detail">'+detail(selected)+'</div>';

    show('人性行为演变','连续博弈中的行为识别 → 防守 → 正向进攻 → 镜像反制',buttons);
    var cs=document.querySelectorAll('.human-behavior-choice');
    for(var k=0;k<cs.length;k++) cs[k].addEventListener('click',function(){
      var id=this.dataset.id, found=null;
      for(var z=0;z<list.length;z++) if(list[z].id===id){found=list[z];break;}
      if(!found)return;
      document.getElementById('human-behavior-detail').innerHTML=detail(found);
      var all=document.querySelectorAll('.human-behavior-choice');
      for(var q=0;q<all.length;q++) all[q].style.borderColor=all[q].dataset.id===id?'var(--accent)':'var(--line)';
      document.getElementById('human-behavior-detail').scrollIntoView({behavior:'smooth',block:'start'});
    });
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
    var latestTask = state.tasks.length ? state.tasks.slice().sort(function(a,b){ return String(b.created_at||'').localeCompare(String(a.created_at||'')); })[0] : null;
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
      chainPanel(latest) +
      (state.error ? '<div class="card"><div class="notice"><b>当前 Run 错误：</b> ' + esc(state.error) + '</div></div>' : '') +
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

    if (state.view === 'threats') { threats(); } else if (state.view === 'positive-attacks') { positiveAttacks(); } else if (state.view === 'human-behavior') { humanBehavior(); } else if (state.view === 'game-logic') {
      gameLogic();
    } else if (state.view === 'game') {
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
    if (state.view === 'game' || state.view === 'overview') bindPlayback();
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
