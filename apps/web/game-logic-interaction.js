(function(){
'use strict';
function esc(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\"/g,'&quot;').replace(/'/g,'&#39;');}
function enhance(){
  var app=document.getElementById('app');
  if(!app)return;
  var title=app.querySelector('.page-title');
  if(!title||title.textContent.indexOf('博弈逻辑')<0)return;
  var list=window.EA_GAME_LOGICS||[];
  if(!list.length)return;
  var box=app.querySelector('.card');
  if(!box)return;
  if(box.dataset.gameEnhanced==='1')return;
  var notices=box.querySelectorAll('.notice');
  var map={};
  list.forEach(function(x){map[x.id]=x;});
  for(var i=0;i<notices.length;i++){
    var n=notices[i];
    var text=(n.textContent||'').trim();
    var m=text.match(/^(G\d+)\s+/);
    if(!m||!map[m[1]])continue;
    var x=map[m[1]];
    n.dataset.gameId=x.id;
    n.setAttribute('role','button');
    n.setAttribute('tabindex','0');
    n.style.cursor='pointer';
    n.title='点击查看完整棋谱';
    n.onclick=function(){show(this.dataset.gameId);};
    n.onkeydown=function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();show(this.dataset.gameId);}};
  }
  var detail=document.createElement('div');
  detail.id='ea-game-detail';
  detail.style.marginTop='14px';
  box.appendChild(detail);
  box.dataset.gameEnhanced='1';
  function show(id){
    var x=map[id];if(!x)return;
    detail.innerHTML='<div class="card" style="border-left:4px solid var(--accent)"><div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap"><div><div class="label">'+esc(x.type||'博弈')+'</div><h2 style="margin:4px 0">'+esc(x.id)+' · '+esc(x.name)+'</h2></div><button type="button" id="ea-game-close" class="action">收起</button></div><div class="notice" style="margin:10px 0"><b>触发条件</b><br>'+esc(x.trigger||'未定义')+'</div><div class="label">行动棋谱</div><ol style="line-height:1.8">'+(x.steps||[]).map(function(s){return'<li>'+esc(s)+'</li>';}).join('')+'</ol><div class="label" style="margin-top:12px">分支响应</div><div style="display:flex;gap:8px;flex-wrap:wrap">'+(x.branches||[]).map(function(b){return'<span class="tag">'+esc(b)+'</span>';}).join('')+'</div><div class="notice" style="margin-top:12px"><b>策略目标</b><br>'+esc(x.goal||'未定义')+'</div></div>';
    var close=document.getElementById('ea-game-close');if(close)close.onclick=function(){detail.innerHTML='';};
  }
}
var obs=new MutationObserver(function(){enhance();});
obs.observe(document.body,{childList:true,subtree:true});
setTimeout(enhance,0);
})();
