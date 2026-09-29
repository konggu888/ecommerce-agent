(function(){
  function render(){
    if(location.hash!=='#external-links')return;
    var app=document.getElementById('app');if(!app)return;
    app.innerHTML='<h1 class="page-title">友情链接</h1><div class="subtitle">值得参考的外部项目与工具</div><div class="card" style="margin-top:12px"><div style="font-size:18px;font-weight:700">Easel · 社交媒体运营 AI Agent</div><div class="muted" style="margin-top:7px;line-height:1.7">社交媒体运营开源项目，覆盖热点发现、账号画像、内容策划、内容制作、多平台发布与数据复盘。</div><a href="https://github.com/ZJU-REAL/Easel" target="_blank" rel="noopener noreferrer" class="action" style="display:inline-block;margin-top:12px;text-decoration:none">打开 Easel 项目 →</a></div>';
  }
  document.addEventListener('click',function(e){var n=e.target&&e.target.closest?e.target.closest('.nav[data-view="external-links"]'):null;if(n){location.hash='#external-links';render();}});
  window.addEventListener('hashchange',render);render();
})();
