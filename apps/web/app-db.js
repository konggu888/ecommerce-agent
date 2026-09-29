(function () {
  'use strict';

  var app = document.getElementById('app');
  var nav = document.querySelectorAll('.nav');
  var VERSION = '20260929-16';

  function show(message) {
    if (!app) return;
    app.innerHTML =
      '<h1 class="page-title">前端 JavaScript 已启动</h1>' +
      '<div class="subtitle">BOOT-DEBUG-' + VERSION + '</div>' +
      '<div class="card"><div class="notice">' + String(message) + '</div></div>';
  }

  show('正在验证前端 JavaScript，不读取数据库。');

  for (var i = 0; i < nav.length; i++) {
    nav[i].addEventListener('click', function () {
      show('JavaScript 正常运行；页面导航测试成功。');
    });
  }

  window.__EA_APPDB_LOADED__ = true;
  window.__EA_APPDB_VERSION__ = VERSION;
}());
