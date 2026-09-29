(function () {
  'use strict';

  var app = document.getElementById('app');
  var nav = document.querySelectorAll('.nav');
  var VERSION = '20260929-20';
  var BASE = 'https://skuoxmrzlxhebzhfgbyn.supabase.co';
  var KEY = 'sb_publishable_u46tZ4GMUgwqSYhMJNFG8Q_IzYwl95T';
  var CLIENT = 'ecommerce-agent-sandbox-v1';
  var state = {
    view: location.hash.slice(1) || 'overview',
    run: null,
    game: [],
    market: [],
    ads: {}
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

  function runURL(name) {
    return BASE + '/rest/v1/' + name +
      '?run_id=eq.' + encodeURIComponent(state.run.id) +
      '&order=id.desc';
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
      getJSON(runURL('sandbox_game_states')),
      getJSON(runURL('sandbox_market_signals'))
    ]).then(function (x) {
      state.game = x[0];
      state.market = x[1];
    });
  }

  var adTables = [
    'sandbox_ad_plans',
    'sandbox_ad_keywords'
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

  function overview() {
    show(
      '商业博弈总览',
      'BOOT-DEBUG-' + VERSION,
      '<div class="grid">' +
      '<div class="card"><div class="label">Sandbox Run</div><div class="metric">' + esc(state.run.status) + '</div></div>' +
      '<div class="card"><div class="label">商业博弈记录</div><div class="metric">' + state.game.length + '</div></div>' +
      '<div class="card"><div class="label">市场信号</div><div class="metric">' + state.market.length + '</div></div>' +
      '</div>' +
      notice('核心数据库读取成功。广告模块也已进入读取阶段。')
    );
  }

  function game() {
    var rows = [];
    for (var i = 0; i < state.game.length; i++) {
      var x = state.game[i];
      rows.push([x.product, x.competitor, x.scenario, x.competitor_price, x.our_price, x.cpc, x.cvr]);
    }
    show('商业博弈', 'BOOT-DEBUG-' + VERSION + ' · Sandbox 模拟数据',
      table(['产品','竞品','场景','竞品价格','我方价格','CPC','CVR'], rows));
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
    var rows = [];
    var keywords = a.sandbox_ad_keywords || [];
    for (var i = 0; i < keywords.length; i++) {
      var x = keywords[i];
      rows.push([x.keyword, x.keyword_type, x.match_type, x.bid, x.impressions, x.clicks, x.ctr, x.conversions, x.cvr, x.spend, x.gmv, x.roi]);
    }

    var plans = a.sandbox_ad_plans || [];
    var planRows = [];
    for (var p = 0; p < plans.length; p++) {
      var q = plans[p];
      planRows.push([q.name, q.status, q.product, q.scene, q.daily_budget, q.bid_strategy]);
    }

    show(
      '广告 / 流量',
      'BOOT-DEBUG-' + VERSION + ' · Sandbox 模拟数据',
      '<div class="grid">' +
      '<div class="card"><div class="label">投放计划</div><div class="metric">' + plans.length + '</div></div>' +
      '<div class="card"><div class="label">关键词</div><div class="metric">' + keywords.length + '</div></div>' +
      '</div>' +
      table(['投放计划','状态','商品','场景','日预算','出价策略'], planRows) +
      table(['关键词','类型','匹配','出价','展现','点击','CTR','成交','CVR','消耗','GMV','ROI'], rows) +
      notice('广告模块第一阶段：先验证投放计划和关键词。其余广告表下一阶段恢复。')
    );
  }

  function placeholder(title) {
    show(title, 'BOOT-DEBUG-' + VERSION, notice('这一页暂时没有恢复。'));
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
      placeholder('实验与回测');
    } else if (state.view === 'risk') {
      placeholder('风险控制器');
    } else if (state.view === 'jobs') {
      placeholder('任务监控');
    } else if (state.view === 'memory') {
      placeholder('学习记忆');
    } else {
      overview();
    }
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
  start();
}());
