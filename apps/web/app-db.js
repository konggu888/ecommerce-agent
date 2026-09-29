(function () {
  'use strict';

  var app = document.getElementById('app');
  var nav = document.querySelectorAll('.nav');
  var VERSION = '20260929-19';
  var SUPABASE_URL = 'https://skuoxmrzlxhebzhfgbyn.supabase.co';
  var ANON_KEY = 'sb_publishable_u46tZ4GMUgwqSYhMJNFG8Q_IzYwl95T';
  var CLIENT_KEY = 'ecommerce-agent-sandbox-v1';
  var state = { view: location.hash.slice(1) || 'overview', run: null, game: [], market: [], ads: {} };

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

  var adTables = ['sandbox_ad_plans','sandbox_ad_units','sandbox_ad_keywords','sandbox_ad_keyword_moves','sandbox_ad_audiences','sandbox_ad_audience_combos','sandbox_ad_creatives','sandbox_ad_placements','sandbox_ad_regions','sandbox_ad_timeslots','sandbox_ad_negative_keywords','sandbox_ad_agent_actions'];

  function loadBusinessData() {
    return Promise.all([
      getJSON(runURL('sandbox_game_states')),
      getJSON(runURL('sandbox_market_signals'))
    ]).then(function (values) {
      state.game = values[0];
      state.market = values[1];
    });
  }

  function loadAdData() {
    return Promise.all(adTables.map(function (name) {
      return getJSON(runURL(name)).then(function (rows) { return { name: name, rows: rows }; });
    })).then(function (values) {
      state.ads = {};
      values.forEach(function (item) { state.ads[item.name] = item.rows; });
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

  function ads() {
    var a = state.ads;
    var plans = a.sandbox_ad_plans || [];
    var keywords = a.sandbox_ad_keywords || [];
    var moves = a.sandbox_ad_keyword_moves || [];
    var audiences = a.sandbox_ad_audiences || [];
    var combos = a.sandbox_ad_audience_combos || [];
    var creatives = a.sandbox_ad_creatives || [];
    var placements = a.sandbox_ad_placements || [];
    var regions = a.sandbox_ad_regions || [];
    var timeslots = a.sandbox_ad_timeslots || [];
    var negative = a.sandbox_ad_negative_keywords || [];
    var actions = a.sandbox_ad_agent_actions || [];

    var summary = '<div class="grid">' +
      '<div class="card"><div class="label">投放计划</div><div class="metric">' + plans.length + '</div></div>' +
      '<div class="card"><div class="label">关键词</div><div class="metric">' + keywords.length + '</div></div>' +
      '<div class="card"><div class="label">人群</div><div class="metric">' + audiences.length + '</div></div>' +
      '<div class="card"><div class="label">创意</div><div class="metric">' + creatives.length + '</div></div>' +
      '<div class="card"><div class="label">资源位</div><div class="metric">' + placements.length + '</div></div>' +
      '<div class="card"><div class="label">Agent动作</div><div class="metric">' + actions.length + '</div></div>' +
      '</div>';

    return page(
      '广告 / 流量',
      'BOOT-DEBUG-' + VERSION + ' · 直接读取广告模块数据库 · Sandbox 模拟数据',
      summary +
      table(['投放计划','状态','商品','场景','日预算','出价策略'], plans.map(function (x) {
        return [x.name, x.status, x.product, x.scene, x.daily_budget, x.bid_strategy];
      })) +
      table(['关键词','类型','匹配','出价','展现','点击','CTR','成交','CVR','消耗','GMV','ROI'], keywords.map(function (x) {
        return [x.keyword, x.keyword_type, x.match_type, x.bid, x.impressions, x.clicks, x.ctr, x.conversions, x.cvr, x.spend, x.gmv, x.roi];
      })) +
      table(['关键词迁移','原关键词','新关键词','点击','成交','CVR','ROI','Agent结论','状态'], moves.map(function (x) {
        return [x.move_type, x.source_keyword, x.related_keyword, x.clicks, x.conversions, x.cvr, x.roi, x.agent_conclusion, x.status];
      })) +
      table(['人群','类型','行为','窗口','规模','覆盖','CVR','ROI'], audiences.map(function (x) {
        return [x.name, x.audience_type, x.behavior, x.window_days, x.size, x.coverage, x.cvr, x.roi];
      })) +
      table(['人群组合','规模','重合','CVR','ROI','Agent结论'], combos.map(function (x) {
        return [x.name, x.size, x.overlap, x.cvr, x.roi, x.agent_conclusion];
      })) +
      table(['创意','类型','标题','审核','展现','点击','CTR','成交','ROI','状态'], creatives.map(function (x) {
        return [x.name, x.creative_type, x.title, x.audit_status, x.impressions, x.clicks, x.ctr, x.conversions, x.roi, x.status];
      })) +
      table(['渠道','资源位','展现','点击','CTR','消耗','成交','CVR','GMV','ROI'], placements.map(function (x) {
        return [x.channel, x.placement, x.impressions, x.clicks, x.ctr, x.spend, x.conversions, x.cvr, x.gmv, x.roi];
      })) +
      table(['地域','展现','点击','CTR','消耗','成交','CVR','ROI'], regions.map(function (x) {
        return [x.region, x.impressions, x.clicks, x.ctr, x.spend, x.conversions, x.cvr, x.roi];
      })) +
      table(['时段','星期','展现','点击','CTR','CPC','成交','CVR','ROI'], timeslots.map(function (x) {
        return [x.slot, x.weekday, x.impressions, x.clicks, x.ctr, x.cpc, x.conversions, x.cvr, x.roi];
      })) +
      table(['否定词','点击','消耗','成交','Agent结论','状态'], negative.map(function (x) {
        return [x.keyword, x.clicks, x.spend, x.conversions, x.agent_conclusion, x.status];
      })) +
      table(['Agent动作','目标','原因','结果','状态'], actions.map(function (x) {
        return [x.action_type, x.target, x.reason, x.result, x.status];
      }))
    );
  }

  function placeholder(title) {
    return page(title, 'BOOT-DEBUG-' + VERSION, card('这一页暂时没有恢复。当前阶段只验证核心业务数据读取。'));
  }

  var views = {
    overview: overview,
    game: game,
    market: market,
    ads: ads,
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
      .then(loadAdData)
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
