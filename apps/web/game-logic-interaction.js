(function(){
'use strict';
function esc(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}
function enhance(){
  var app=document.getElementById('app');
  if(!app)return;
  var title=app.querySelector('.page-title');
  if(!title||title.textContent.indexOf('博弈逻辑')<0)return;
  var list=window.EA_GAME_LOGICS||[];
  if(!list.length)return;
  if(app.dataset.gameOnly==='1')return;
  app.dataset.gameOnly='1';
  var subtitle=app.querySelector('.subtitle');
  app.innerHTML='';
  var h=document.createElement('h1');h.className='page-title';h.textContent='博弈逻辑';app.appendChild(h);
  var sub=document.createElement('div');sub.className='subtitle';sub.textContent='50套可点击博弈棋谱 · 我变 → 对手学 → 我再变';app.appendChild(sub);
  var card=document.createElement('div');card.className='card';
  var head=document.createElement('div');head.className='label';head.textContent='博弈逻辑库 · '+list.length+'套';card.appendChild(head);
  var listBox=document.createElement('div');listBox.style.display='grid';listBox.style.gap='8px';listBox.style.marginTop='10px';
  var detail=document.createElement('div');detail.id='ea-game-detail';detail.style.marginTop='14px';
  list.forEach(function(x){
    var item=document.createElement('button');item.type='button';item.className='notice';item.style.cssText='display:block;width:100%;text-align:left;cursor:pointer;border:1px solid var(--border);';
    item.innerHTML='<b>'+esc(x.id)+' · '+esc(x.name)+'</b><div class="muted">'+esc(x.type||'博弈')+' · 点击展开完整棋谱</div>';
    item.onclick=function(){show(x);};
    listBox.appendChild(item);
  });
  card.appendChild(listBox);card.appendChild(detail);app.appendChild(card);
  function show(x){
    detail.innerHTML='<div class="card" style="margin-top:12px"><div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap"><div><div class="label">'+esc(x.type||'博弈')+'</div><h2 style="margin:4px 0">'+esc(x.id)+' · '+esc(x.name)+'</h2></div><button type="button" id="ea-game-close" class="action">收起</button></div><div class="notice" style="margin:10px 0"><b>触发条件</b><br>'+esc(x.trigger||'未定义')+'</div><div class="label">行动棋谱</div><ol style="line-height:1.8">'+(x.steps||[]).map(function(s){return'<li>'+esc(s)+'</li>';}).join('')+'</ol><div class="label" style="margin-top:12px">分支响应</div><div style="display:flex;gap:8px;flex-wrap:wrap">'+(x.branches||[]).map(function(b){return'<span class="tag">'+esc(b)+'</span>';}).join('')+'</div><div class="notice" style="margin-top:12px"><b>策略目标</b><br>'+esc(x.goal||'未定义')+'</div></div>';
    document.getElementById('ea-game-close').onclick=function(){detail.innerHTML='';};
  }
}
var obs=new MutationObserver(function(){enhance();});
obs.observe(document.body,{childList:true,subtree:true});
setTimeout(enhance,0);
})();
