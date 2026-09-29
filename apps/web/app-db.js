(function () {
  'use strict';

  var app = document.getElementById('app');
  var nav = document.querySelectorAll('.nav');
  var VERSION = '20260929-17';
  var SUPABASE_URL = 'https://skuoxmrzlxhebzhfgbyn.supabase.co';
  var ANON_KEY = 'sb_publishable_u46tZ4GMUgwqSYhMJNFG8Q_IzYwl95T';
  var CLIENT_KEY = 'ecommerce-agent-sandbox-v1';
  var state = { view: location.hash.slice(1) || 'overview', run: null };

  function text(value) {
    return String(value == null ? '' : value);
  }

  function render(title, subtitle, message) {
    if (!app) return;
    app.innerHTML =
      '<h1 class="page-title">' + text(title) + '</h1>' +
      '<div class="subtitle">' + text(subtitle) + '</div>' +
      '<div class="card"><div class="notice">' + text(message) + '</div></div>';
  }

  function requestSandboxRun() {
    var url = SUPABASE_URL +
      '/rest/v1/sandbox_runs?select=id,status,updated_at,client_key' +
      '&client_key=eq.' + encodeURIComponent(CLIENT_KEY) +
      '&order=updated_at.desc&limit=1';

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
          throw new Error('Supabase 返回的不是 JSON，HTTP ' + response.status);
        }
        if (!response.ok) {
          throw new Error('Supabase HTTP ' + response.status);
        }
        return data;
      });
    });
  }

  function load() {
    render('Supabase 连接测试', 'BOOT-DEBUG-' + VERSION, '正在直接读取 sandbox_runs……');

    requestSandboxRun().then(function (rows) {
      if (!Array.isArray(rows)) {
        throw new Error('sandbox_runs 返回格式不是数组');
      }

      if (!rows.length) {
        render(
          'Supabase 连接成功',
          'BOOT-DEBUG-' + VERSION,
          '数据库可以访问，但 sandbox_runs 中没有找到模拟运行记录。'
        );
        return;
      }

      state.run = rows[0];
      render(
        'Supabase 连接成功',
        'BOOT-DEBUG-' + VERSION,
        '已读取 sandbox_runs：run=' + text(state.run.id) +
        '，状态=' + text(state.run.status) +
        '，更新时间=' + text(state.run.updated_at)
      );
    }).catch(function (error) {
      console.error('SUPABASE_BOOT_ERROR', error);
      render(
        'Supabase 连接失败',
        'BOOT-DEBUG-' + VERSION,
        text(error && error.message ? error.message : error)
      );
    });
  }

  for (var i = 0; i < nav.length; i++) {
    nav[i].addEventListener('click', function () {
      render(
        'Supabase 连接测试',
        'BOOT-DEBUG-' + VERSION,
        '当前正在进行第一阶段：只测试 Supabase → sandbox_runs。'
      );
    });
  }

  window.__EA_APPDB_LOADED__ = true;
  window.__EA_APPDB_VERSION__ = VERSION;
  load();
}());
