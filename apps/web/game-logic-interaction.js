(function(){
'use strict';
function esc(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}
var currentId=null;
function render(){
  var app=document.getElementById('app');
  if(!app)return;
  var title=app.querySelector('.page-title');
  if(!title||title.textContent.indexOf('博弈逻辑')<0)return;
  var list=window.EA_GAME_LOGICS||[];
  if(!list.length)return;
  var old=app.querySelector('#ea-game-logic-ui');
  if(old)return;
  var box=document.createElement('div');box.id='ea-game-logic-ui';box.className='card';
  box.innerHTML='<div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap"><div><div class="label">博弈逻辑库</div><div class="metric">'+list.length+' 套 · 可展开棋谱</div></div><div class="muted">点击任意策略查看完整行动链</div></div><div id="ea-game-list" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px;margin-top:14px"></div><div id="ea-game-detail" style="margin-top:14px"></div>';
  var cards=box.querySelector('#ea-game-list');
  list.forEach(function(x){var d=document.createElement('button');d.type='button';d.className='notice';d.dataset.gameId=x.id;d.style.cssText='text-align:left;cursor:pointer;width:100%;border:1px solid var(--line);background:var(--panel);color:inherit;padding:12px;border-radius:10px';d.innerHTML='<b>'+esc(x.id)+' · '+esc(x.name)+'</b><br><span class="muted">'+esc(x.type||'')+'</span><div style="margin-top:6px">'+esc(x.trigger||'')+'</div>';cards.appendChild(d);});
  var detail=box.querySelector('#ea-game-detail');
  function show(id){var x=list.find(function(a){return a.id===id;});if(!x)return;currentId=id;detail.innerHTML='<div class="card" style="border-left:4px solid var(--accent)"><div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap"><div><div class="label">'+esc(x.type||'博弈')+'</div><h2 style="margin:4px 0">'+esc(x.id)+' · '+esc(x.name)+'</h2></div><button type="button" id="ea-game-close" class="action">收起</button></div><div class="notice" style="margin:10px 0"><b>触发条件</b><br>'+esc(x.trigger||'未定义')+'</div><div class="label">行动棋谱</div><ol style="line-height:1.8">'+(x.steps||[]).map(function(s){return'<li>'+esc(s)+'</li>';}).join('')+'</ol><div class="label" style="margin-top:12px">分支响应</div><div style="display:flex;gap:8px;flex-wrap:wrap">'+(x.branches||[]).map(function(b){return'<span class="tag">'+esc(b)+'</span>';}).join('')+'</div><div class="notice" style="margin-top:12px"><b>策略目标</b><br>'+esc(x.goal||'未定义')+'</div></div>';
    var close=document.getElementById('ea-game-close');if(close)close.onclick=function(){detail.innerHTML='';currentId=null;};
  }
  cards.addEventListener('click',function(e){var b=e.target.closest('[data-game-id]');if(b){e.preventDefault();show(b.dataset.gameId);}});
  app.appendChild(box);
}
var obs=new MutationObserver(function(){render();});
obs.observe(document.body,{childList:true,subtree:true});
setTimeout(render,0);
})();
