(function(){
  'use strict';
  function esc(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
  function lib(k){return Array.isArray(window[k])?window[k]:[];}
  function find(k,id){var a=lib(k);for(var i=0;i<a.length;i++)if(a[i]&&a[i].id===id)return a[i];return null;}
  function move(id,type,side){return{id:id,type:type,side:side};}
  function chooseMove(x,i,kind,step){
    var P=lib('EA_POSITIVE_ATTACK_LIBRARY'),T=lib('EA_THREAT_LIBRARY'),B=lib('EA_BUG_ATTACK_LIBRARY');
    if(kind==='正向'){var p=P[i%P.length];return p?move(p.id,'正向攻击','我方招式'):null;}
    if(kind==='负向'){var t=T[i%T.length];return t?move(t.id,'对手攻击','对手招式（待验证）'):null;}
    if(kind==='防守'){var b=B[(i*3)%B.length];return b?move(b.id,'机制型攻防','我方招式（机制防守）'):null;}
    if(kind==='观察'||kind==='小试'||kind==='正常'||kind==='失败'||kind==='机会'){
      var p2=P[(i+step)%P.length];return p2?move(p2.id,'正向攻击','我方招式（低成本试探）'):null;
    }
    if(kind==='复制对手'||kind==='跟随'||kind==='强防守'||kind==='异常'){
      var b2=B[(i+step*2)%B.length];return b2?move(b2.id,'机制型攻防','待验证招式'):null;
    }
    var p3=P[(i+step)%P.length];return p3?move(p3.id,'正向攻击','我方招式'):null;
  }
  function getMoves(x,i){
    var seq=Array.isArray(x.sequence)?x.sequence:[],out=[];
    for(var s=0;s<seq.length;s++){var m=chooseMove(x,i,seq[s],s+1);if(m)out.push(m);}
    return out;
  }
  function routeTo(type,id){
    window.__EA_OPEN_MOVE__={type:type,id:id};
    var v=type==='正向攻击'?'positive-attacks':type==='对手攻击'?'threats':'bug-attacks';
    state.view=v;location.hash=v;render();
  }
  function build(i,x){
    var moves=getMoves(x,i),steps=[];
    for(var j=0;j<moves.length;j++){
      var m=moves[j],source=m.type==='正向攻击'?find('EA_POSITIVE_ATTACK_LIBRARY',m.id):m.type==='对手攻击'?find('EA_THREAT_LIBRARY',m.id):find('EA_BUG_ATTACK_LIBRARY',m.id);
      if(source)steps.push({move:m,source:source});
    }
    return{id:x.id,name:x.name,style:x.style||'',sequence:x.sequence||[],risk:x.risk||'中',signal:x.signal||'',goal:x.goal||'',steps:steps};
  }
  function render(){
    if(location.hash!=='#strategy-center')return;
    var app=document.getElementById('app');if(!app)return;
    var H=lib('EA_HUMAN_BEHAVIOR_LIBRARY').slice(0,40);
    var html='<h1 class="page-title">连续博弈策略中心 <span style="font-size:16px;font-weight:500;color:var(--accent);margin-left:10px">我变 → 对手学 → 我再变</span></h1><div class="subtitle">40种行为人格 · 每套棋谱调用真实招式，并可溯源到原招式页面</div>';
    html+='<div class="card" style="margin:10px 0 16px;border-left:4px solid var(--accent);background:rgba(255,180,0,.06)"><b>棋谱规则</b><div style="font-size:17px;margin-top:6px">正向攻击、对手攻击、机制型攻防全部来自现有招式库。每一招显示真实编号与名称；点击“查看原招式”直接进入对应招式页面。机制型招式只属于我方防守/校验或对手待验证行为，不把平台本身当成主动攻击方。</div></div>';
    html+='<div class="card"><div class="label">40套连续博弈棋谱</div><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:10px;margin-top:12px">';
    H.forEach(function(x,i){
      var b=build(i,x);
      html+='<div class="game-wrap" data-game="'+esc(b.id)+'"><div class="card"><span class="tag">'+esc(b.id)+'</span><b style="display:block;margin-top:7px">'+esc(b.name)+'</b><div class="muted" style="margin-top:5px">模式：'+esc(b.style)+' · '+esc(b.risk)+'风险</div><div style="margin-top:5px">信号：'+esc(b.signal)+'</div><div style="margin-top:5px"><b>行为序列：</b>'+esc(b.sequence.join(' → '))+'</div><div style="display:flex;gap:8px;margin-top:10px"><button type="button" class="game-card" data-mode="playbook">♟ 棋谱</button><button type="button" class="game-card" data-mode="reasoning">🧠 推理</button></div></div><div class="game-detail" style="display:none;margin-top:8px"></div></div>';
    });
    html+='</div></div>';app.innerHTML=html;
  }
  document.addEventListener('click',function(e){
    var b=e.target&&e.target.closest?e.target.closest('.game-card'):null;if(!b)return;
    var wrap=b.closest('.game-wrap'),detail=wrap.querySelector('.game-detail'),id=wrap.getAttribute('data-game'),mode=b.getAttribute('data-mode'),H=lib('EA_HUMAN_BEHAVIOR_LIBRARY'),x0=null,idx=0;
    for(;idx<H.length;idx++)if(H[idx].id===id){x0=H[idx];break;}if(!x0)return;
    var x=build(idx,x0);detail.style.display='block';
    var h='<div class="card" style="margin:0;border-left:3px solid var(--accent)"><div class="label">'+esc(x.id)+' · '+esc(x.name)+'</div>';
    if(mode==='playbook'){
      h+='<div style="margin-top:8px"><b>连续博弈棋谱 · 招式链</b></div><ol style="line-height:1.9;margin:8px 0">';
      x.steps.forEach(function(s){h+='<li><span class="tag">'+esc(s.move.id)+'</span> <b>'+esc(s.source.name)+'</b> · '+esc(s.move.side)+' <button type="button" class="action" style="margin-left:6px;padding:4px 8px" data-open-type="'+esc(s.move.type)+'" data-open-id="'+esc(s.move.id)+'">查看原招式 →</button><div class="muted" style="margin-top:3px">'+esc(s.source.category||'')+' · '+esc(s.source.signal||'')+'</div></li>';});
      h+='</ol><div class="notice"><b>目标：</b>'+esc(x.goal)+'<br>下一轮根据实际响应决定继续、换招、防守或停止。</div>';
    }else{
      h+='<div style="margin-top:8px"><b>连续博弈推理</b></div><div style="line-height:1.8;margin-top:8px">先把可观测市场信号作为事实，再用“'+esc(x.name)+'”作为行为假设。每个具体动作都落到已有招式库：正向攻击、对手攻击、机制型攻防。对手招式只是待验证假设；机制型招式不是平台主动攻击。实际响应优先于预测。</div>';
      h+='<div style="margin-top:10px"><b>本套棋谱调用的真实招式：</b>'+x.steps.map(function(s){return'<button type="button" class="action" style="margin:4px" data-open-type="'+esc(s.move.type)+'" data-open-id="'+esc(s.move.id)+'">'+esc(s.move.id)+' · '+esc(s.source.name)+'</button>';}).join('')+'</div>';
      h+='<div class="notice" style="margin-top:8px"><b>目标：</b>'+esc(x.goal)+'</div>';
    }
    h+='</div>';detail.innerHTML=h;
    detail.querySelectorAll('[data-open-id]').forEach(function(btn){btn.onclick=function(ev){ev.stopPropagation();routeTo(btn.getAttribute('data-open-type'),btn.getAttribute('data-open-id'));};});
    detail.scrollIntoView({behavior:'smooth',block:'nearest'});
  },false);
  window.__EA_STRATEGY_CENTER_RENDER__=render;
  window.addEventListener('hashchange',function(){setTimeout(render,30);});
  setTimeout(render,50);
})();