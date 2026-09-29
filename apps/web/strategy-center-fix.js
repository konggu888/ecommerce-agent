(function(){
  'use strict';
  function esc(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
  function lib(name){return Array.isArray(window[name])?window[name]:[];}
  function byId(arr,id){for(var i=0;i<arr.length;i++){if(arr[i]&&arr[i].id===id)return arr[i];}return null;}

  var P_IDS=['P01','P03','P04','P05','P12','P13','P14','P16','P17','P19','P20','P22','P24','P25','P31','P32','P33','P35','P37','P38','P40','P41','P42','P43','P44','P45','P46','P47','P48','P49','P50'];
  var T_IDS=['T01','T02','T08','T09','T17','T18','T19','T20','T25','T26','T30','T31','T34','T35','T39','T40'];
  var B_IDS=['B01','B02','B03','B04','B05','B06','B07','B08','B09','B10','B11','B12','B13','B16','B17','B18','B19','B21','B22','B23'];

  function pickPositive(i){return P_IDS[i%P_IDS.length];}
  function pickThreat(i){return T_IDS[i%T_IDS.length];}
  function pickBug(i){return B_IDS[i%B_IDS.length];}

  function moveForToken(token,round,side){
    var t=String(token||'').toLowerCase();
    if(/负向|施压|报复|对抗|强负向|强响应|反扑|消耗|抢|竞争/.test(t))return {type:'T',id:pickThreat(round),side:side};
    if(/观察|小试|试探|信息|反馈|测算|正常|失败/.test(t))return {type:'B',id:pickBug(round+1),side:side};
    if(/防守|收缩|降低投入|克制|退出|等待/.test(t))return {type:'B',id:pickBug(round+4),side:side};
    return {type:'P',id:pickPositive(round),side:side};
  }

  function moveData(m){
    var P=lib('EA_POSITIVE_ATTACK_LIBRARY'),T=lib('EA_THREAT_LIBRARY'),B=lib('EA_BUG_ATTACK_LIBRARY');
    var x=m.type==='P'?byId(P,m.id):(m.type==='T'?byId(T,m.id):byId(B,m.id));
    if(!x)return {id:m.id,type:m.type,name:m.id,category:'',signal:'',detail:'',source:m.type==='P'?'正向攻击':(m.type==='T'?'对手攻击面':'机制型攻防')};
    return {id:x.id,type:m.type,name:x.name||x.id,category:x.category||'',signal:x.signal||'',detail:x.action||x.defense||x.mechanism||'',source:m.type==='P'?'正向攻击':(m.type==='T'?'对手攻击面':'机制型攻防')};
  }

  function sourceButton(m){
    var d=moveData(m);
    return '<button type="button" class="source-move" data-source-type="'+esc(m.type)+'" data-source-id="'+esc(m.id)+'" style="border:0;background:none;padding:0;color:var(--accent);cursor:pointer;text-decoration:underline;font-weight:700">['+esc(d.source)+' '+esc(d.id)+' · '+esc(d.name)+']</button>';
  }

  function makeRounds(x){
    var seq=Array.isArray(x.sequence)?x.sequence:[];
    var rounds=[];
    for(var r=0;r<5;r++){
      var token=seq.length?seq[r%seq.length]:'观察';
      var our=moveForToken(token,r,'我方');
      var opp;
      if(/正向|建设|合作|跟随|复制|扩大|继续|机会|扩张/.test(String(token)))opp={type:'P',id:pickPositive(r+2),side:'对手'};
      else if(/负向|施压|报复|对抗|反扑|强/.test(String(token)))opp={type:'T',id:pickThreat(r+1),side:'对手'};
      else opp={type:'B',id:pickBug(r+2),side:'对手'};
      rounds.push({n:r+1,token:token,our:our,opp:opp});
    }
    return rounds;
  }

  function sourceView(type){return type==='P'?'positive-attacks':(type==='T'?'threats':'bug-attacks');}

  function render(){
    if(location.hash!=='#strategy-center')return;
    var app=document.getElementById('app');if(!app)return;
    var H=lib('EA_HUMAN_BEHAVIOR_LIBRARY').slice(0,40);
    var h='<h1 class="page-title">连续博弈中心 <span style="font-size:16px;font-weight:500;color:var(--accent);margin-left:10px">我变 → 对手学 → 我再变</span></h1>';
    h+='<div class="subtitle">40种行为人格 · 每套棋谱直接调用系统已有的正向攻击、负面攻击、机制型攻防招式；每一招都有溯源名称，可直接点回原招式页面。</div>';
    h+='<div class="card" style="margin:10px 0 16px;border-left:4px solid var(--accent);background:rgba(255,180,0,.06)"><b>棋谱规则</b><div style="margin-top:6px;line-height:1.8">行为人格只决定对手的行为节奏假设；真正进入棋谱的招式全部来自现有招式库：<b>正向 P01-P50</b>、<b>负面 T01-T40</b>、<b>机制 B01-B23</b>。对手招式属于待验证假设，实际响应优先于预测。</div></div>';
    h+='<div class="card"><div class="label">40套连续博弈棋谱</div><div class="muted" style="margin-top:5px">点击“♟ 棋谱”查看5轮完整攻防；点击每一招的蓝色来源名称，直接进入对应招式页并展开该招。</div><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px;margin-top:12px">';
    H.forEach(function(x){h+='<div class="game-wrap" data-game="'+esc(x.id)+'"><div class="card"><span class="tag">'+esc(x.id)+'</span><b style="display:block;margin-top:7px">'+esc(x.name)+'</b><div class="muted" style="margin-top:5px">'+esc(x.style||'')+' · '+esc(x.risk||'中')+'风险</div><div class="muted" style="margin-top:5px">行为序列：'+esc((x.sequence||[]).join(' → '))+'</div><div style="display:flex;gap:8px;margin-top:10px"><button type="button" class="game-card" data-mode="playbook">♟ 棋谱</button><button type="button" class="game-card" data-mode="reasoning">🧠 推理</button></div></div><div class="game-detail" style="display:none;margin-top:8px"></div></div>';});
    h+='</div></div>';
    app.innerHTML=h;
  }

  function showPlaybook(wrap,x){
    var rounds=makeRounds(x);
    var html='<div class="card" style="margin:0;border-left:3px solid var(--accent)"><div class="label">'+esc(x.id)+' · '+esc(x.name)+' · 连续攻防棋谱</div><div class="muted" style="margin-top:5px">每一招均溯源到已有招式库，不重新发明招式。</div><ol style="line-height:1.8;margin:10px 0">';
    rounds.forEach(function(r){
      var od=moveData(r.our),pd=moveData(r.opp);
      html+='<li style="margin-bottom:12px"><b>第'+r.n+'轮 · 行为信号：'+esc(r.token)+'</b><div style="margin-top:5px">我方招式：'+sourceButton(r.our)+'<span class="muted"> · '+esc(od.detail)+'</span></div><div>对手招式：'+sourceButton(r.opp)+'<span class="muted"> · '+esc(pd.detail)+'</span></div><div class="muted" style="margin-top:3px">反馈：记录曝光、点击、转化、价格、排名、评价、退款、流量等实际变化；实际响应不一致时立即换招。</div></li>';
    });
    html+='</ol><div class="notice"><b>目标：</b>'+esc(x.goal||'持续根据实际响应调整策略')+'。每轮结束：实际响应 → 更新对手模型 → 下一轮换招/保持/防守/停止。</div></div>';
    wrap.querySelector('.game-detail').innerHTML=html;
    wrap.querySelector('.game-detail').style.display='block';
  }

  function showReasoning(wrap,x){
    var html='<div class="card" style="margin:0;border-left:3px solid var(--accent)"><div class="label">'+esc(x.id)+' · '+esc(x.name)+' · 连续博弈推理</div><div style="line-height:1.8;margin-top:8px">行为序列“'+esc((x.sequence||[]).join(' → '))+'”只用于生成对手行为假设。每一轮的实际招式必须从正向、负面或机制型招式库调用；如果实际反馈与假设不一致，停止沿用该人格模型，按真实响应重新选招。</div><div class="notice" style="margin-top:10px"><b>核心：</b>棋谱 = 已有招式库的组合，不是凭空生成新招。</div></div>';
    wrap.querySelector('.game-detail').innerHTML=html;
    wrap.querySelector('.game-detail').style.display='block';
  }

  function openSource(type,id){
    window.__EA_MOVE_TARGET__={type:type,id:id};
    location.hash=sourceView(type);
    setTimeout(function(){
      var sel=type==='P'?'[data-pos="'+id+'"]':(type==='T'?'[data-threat="'+id+'"]':'[data-bug="'+id+'"]');
      var card=document.querySelector(sel);
      if(card){card.click();card.scrollIntoView({behavior:'smooth',block:'center');}
    },180);
  }

  document.addEventListener('click',function(e){
    var b=e.target&&e.target.closest?e.target.closest('.game-card'):null;
    if(b){
      var wrap=b.closest('.game-wrap'),id=wrap.getAttribute('data-game'),x=byId(lib('EA_HUMAN_BEHAVIOR_LIBRARY'),id);
      if(!x)return;
      if(b.getAttribute('data-mode')==='playbook')showPlaybook(wrap,x);else showReasoning(wrap,x);
      return;
    }
    var s=e.target&&e.target.closest?e.target.closest('.source-move'):null;
    if(s){openSource(s.getAttribute('data-source-type'),s.getAttribute('data-source-id'));}
  },false);

  window.__EA_STRATEGY_CENTER_RENDER__=render;
  window.addEventListener('hashchange',function(){setTimeout(render,30);});
  setTimeout(render,50);
})();