(function () {
  'use strict';

  var app = document.getElementById('app');
  var nav = document.querySelectorAll('.nav');
  var VERSION = '20260929-18';
  var SUPABASE_URL = 'https://skuoxmrzlxhebzhfgbyn.supabase.co';
  var ANON_KEY = 'sb_publishable_u46tZ4GMUgwqSYhMJNFG8Q_IzYwl95T';
  var CLIENT_KEY = 'ecommerce-agent-sandbox-v1';
  var state = { view: location.hash.slice(1) || 'overview', run: null, game: [], market: [] };

  function esc(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function page(title, subtitle, body) {
    if (!app) return;
    app.innerHTML =
      '<h1 class="page-title">' + esc(title) + '</h1>' +
      '<div class="subtitle">' + esc(subtitle) + '</div>' + body;
  }

  function card(message) {
    return '<div class="card"><div class="notice">' + esc(message) + '</div></div>';
  }

  function table(headers, rows) {
    if (!rows.length) return card('该模块当前没有数据库记录。');
    return '<div class="card"><table class="table"><thead><tr>' +
      headers.map(function (x) { return '<th>' + esc(x) + '</th>'; }).join('') +
      '</tr></thead><tbody>' +
      rows.map(function (row) {
        return '<tr>' + row.map(function (x) { return '<td>' + esc(x) + '</td>'; }).join('') + '</tr>';
      }).join('') +
      '</tbody></table></div>';
  }

  function getJSON(url) {
    return fetch(url, {
      method: 'GET',
      headers: {
        apikey: ANON_KEY,
        Authorization: 'Bearer ' + ANON_KEY,
        Accept: 'application/json'
      },
      cache: 'no-store'
    }).then(function (response) {
      return response.text().then(function (body) {
        var data;
        try {
          data = JSON.parse(body);
        } catch (error) {
          throw new Error('HTTP ' + response.status + ' 返回非 JSON');
        }
        if (!response.ok) {
          throw new Error('HTTP ' + response.status);
        }
        return data;
      });
    });
  }

  function runURL(tableName) {
    return SUPABASE_URL + '/rest/v1/' + tableName +
      '?run_id=eq.' + encodeURIComponent(state.run.id) +
      '&order=created_at.desc';
  }

  function loadRun() {
    var url = SUPABASE_URL +
      '/rest/v1/sandbox_runs?select=id,status,updated_at,client_key' +
      '&client_key=eq.' + encodeURIComponent(CLIENT_KEY) +
      '&order=updated_at.desc&limit=1';
    return getJSON(url).then(function (rows) {
      if (!Array.isArray(rows) || !rows.length) {
        throw new Error('没有找到 sandbox_runs');
      }
      state.run = rows[0];
    });
  }

  function loadBusinessData() {
    return Promise.all([
      getJSON(runURL('sandbox_game_states')),
      getJSON(runURL('sandbox_market_signals'))
    ]).then(function (values) {
      state.game = values[0];
      state.market = values[1];
    });
  }

  function overview() {
    return page(
      '商业博弈总览',
      'BOOT-DEBUG-' + VERSION + ' · 第一批数据库业务数据',
      '<div class="grid">' +
      '<div class="card"><div class="label">Sandbox Run</div><div class="metric">' + esc(state.run.status) + '</div></div>' +
      '<div class="card"><div class="label">商业博弈记录</div><div class="metric">' + state.game.length + '</div></div>' +
      '<div class="card"><div class="label">市场信号</div><div class="metric">' + state.market.length + '</div></div>' +
      '</div>' +
      card('数据库连接、sandbox_runs、商业博弈和市场情报四层已完成读取。')
    );
  }

  function game() {
    return page(
      '商业博弈',
      '直接读取 sandbox_game_states · Sandbox 模拟数据',
      table(
        ['产品', '竞品', '场景', '竞品价格', '我方价格', 'CPC', 'CVR'],
        state.game.map(function (x) {
          return [
            x.product,
            x.competitor,
            x.scenario,
            x.competitor_price,
            x.our_price,
            x.cpc,
            x.cvr
          ];
        })
      )
    );
  }

  function market() {
    return page(
      'Web 市场情报',
      '直接读取 sandbox_market_signals · Sandbox 模拟数据',
      table(
        ['名称', '类型', '强度', '说明'],
        state.market.map(function (x) {
          return [x.name, x.signal_type, x.strength, x.detail];
        })
      )
    );
  }

  function placeholder(title) {
    return page(title, 'BOOT-DEBUG-' + VERSION, card('这一页暂时没有恢复。当前阶段只验证核心业务数据读取。'));
  }

  var views = {
    overview: overview,
    game: game,
    market: market,
    ads: function () { return placeholder('广告 / 流量'); },
    experiments: function () { return placeholder('实验与回测'); },
    risk: function () { return placeholder('风险控制器'); },
    jobs: function () { return placeholder('任务监控'); },
    memory: function () { return placeholder('学习记忆'); }
  };

  function render() {
    for (var i = 0; i < nav.length; i++) {
      nav[i].classList.toggle('active', nav[i].dataset.view === state.view);
    }
    (views[state.view] || overview)();
  }

  function load() {
    page('数据库业务数据测试', 'BOOT-DEBUG-' + VERSION, card('正在读取 sandbox_runs、商业博弈、市场情报……'));

    loadRun()
      .then(loadBusinessData)
      .then(render)
      .catch(function (error) {
        console.error('BUSINESS_DATA_ERROR', error);
        page('数据库业务数据读取失败', 'BOOT-DEBUG-' + VERSION, card(error.message));
      });
  }

  for (var i = 0; i < nav.length; i++) {
    nav[i].addEventListener('click', function () {
      state.view = this.dataset.view;
      location.hash = state.view;
      render();
    });
  }

  window.__EA_APPDB_LOADED__ = true;
  window.__EA_APPDB_VERSION__ = VERSION;
  load();
}());
