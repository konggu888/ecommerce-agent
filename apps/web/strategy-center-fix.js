(function(){
  'use strict';

  function esc(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\"/g,'&quot;');}
  function getLibrary(){return Array.isArray(window.EA_HUMAN_BEHAVIOR_LIBRARY)?window.EA_HUMAN_BEHAVIOR_LIBRARY:[];}
  function findById(list,id){for(var i=0;i<list.length;i++){if(list[i]&&list[i].id===id)return list[i];}return null;}

  /*
   * 每个 H 行为模式都绑定一套“具体招法组合”：
   * P = 正向攻击（我方主动增长）
   * T = 负面攻击/威胁库（对手可能施压）
   * B = 平台机制异常/BUG攻击（对手可能利用机制）
   * 注意：T/B 只作为“对手可能路径/假设”，不是事实归因。
   */
  var ROUTES={
    H01:['P40','P42','P47','T19','T20','B11'],
    H02:['P37','P35','P40','T20','T26','B23'],
    H03:['P22','P31','P49','T19','T08','B18'],
    H04:['P03','P26','P40','T19','T33','B03'],
    H05:['P25','P29','P43','T17','T21','B21'],
    H06:['P12','P22','P44','T26','T34','B18'],
    H07:['P41','P25','P49','T19','T08','B04'],
    H08:['P20','P35','P40','T20','T34','B23'],
    H09:['P37','P19','P20','T24','T17','B11'],
    H10:['P02','P32','P33','T19','T22','B10'],
    H11:['P19','P37','P45','T24','T20','B11'],
    H12:['P49','P03','P25','T19','T26','B04'],
    H13:['P31','P45','P50','T20','T34','B10'],
    H14:['P37','P35','P47','T20','T23','B23'],
    H15:['P37','P38','P49','T20','T19','B11'],
    H16:['P23','P24','P40','T20','T25','B18'],
    H17:['P38','P17','P44','T20','T19','B15'],
    H18:['P37','P40','P49','T20','T19','B12'],
    H19:['P32','P33','P40','T19','T22','B06'],
    H20:['P20','P37','P45','T17','T24','B21'],
    H21:['P22','P31','P40','T19','T26','B23'],
    H22:['P49','P02','P43','T17','T21','B21'],
    H23:['P40','P35','P19','T19','T20','B06'],
    H24:['P33','P45','P25','T22','T19','B10'],
    H25:['P41','P25','P46','T08','T19','B04'],
    H26:['P01','P03','P40','T19','T20','B03'],
    H27:['P49','P02','P43','T17','T19','B21'],
    H28:['P40','P31','P50','T20','T25','B23'],
    H29:['P08','P30','P36','T34','T23','B20'],
    H30:['P08','P24','P36','T34','T23','B17'],
    H31:['P20','P37','P45','T02','T39','B15'],
    H32:['P33','P40','P47','T19','T20','B06'],
    H33:['P49','P25','P41','T26','T36','B04'],
    H34:['P42','P50','P40','T19','T20','B23'],
    H35:['P16','P42','P47','T08','T19','B18'],
    H36:['P33','P34','P40','T21','T20','B16'],
    H37:['P37','P45','P49','T17','T24','B11'],
    H38:['P20','P35','P40','T20','T34','B23'],
    H39:['P49','P43','P42','T17','T19','B21'],
    H40:['P40','P42','P50','T19','T26','B23']
  };

  function getMoveSet(){
    return {
      p:window.EA_POSITIVE_ATTACK_LIBRARY||[],
      t:window.EA_THREAT_LIBRARY||[],
      b:window.EA_BUG_ATTACK_LIBRARY||[]
    };
  }

  function move(id,sets){
    var type=id.charAt(0),list=type==='P'?sets.p:type==='T'?sets.t:sets.b;
    var x=findById(list,id);
    if(!x)return{id:id,name:'未加载招法',category:'',signal:'',action:'',mechanism:'',goal:'',defense:''};
    return {
      id:x.id,name:x.name,category:x.category||'',signal:x.signal||'',
      action:x.action||'',goal:x.goal||'',defense:x.defense||'',
      mechanism:x.mechanism||'',response:x.response||[]
    };
  }

  function build(i,x){
    var seq=Array.isArray(x.sequence)?x.sequence:[], ids=ROUTES[x.id]||['P40','P42','P50','T19','T20','B23'];
    var sets=getMoveSet();
    var m1=move(ids[0],sets),m2=move(ids[1],sets),m3=move(ids[2],sets);
    var o1=move(ids[3],sets),o2=move(ids[4],sets),o3=move(ids[5],sets);
    var a1=seq[0]||'观察',a2=seq[1]||'观察',a3=seq[2]||'观察',a4=seq[3]||'继续观察';
    return {
      id:x.id||('H'+String(i+1).padStart(2,'0')),name:x.name||('行为模式'+(i+1)),
      style:x.style||'',sequence:seq,risk:x.risk||'中',signal:x.signal||'',goal:x.goal||'',
      moves:[m1,m2,m3],opponents:[o1,o2,o3],
      steps:[
        {round:1,side:'我方',move:m1,behavior:a1,action:'先手招法'},
        {round:2,side:'对手',move:o1,behavior:a1,action:'可能响应'},
        {round:3,side:'我方',move:m2,behavior:a2,action:'根据实际反馈换招'},
        {round:4,side:'对手',move:o2,behavior:a3,action:'可能反制'},
        {round:5,side:'我方',move:m3,behavior:a4,action:'再变与风险控制'},
        {round:6,side:'对手',move:o3,behavior:'进入下一轮',action:'可能的机制/流量反馈'}
      ],
      goal:'把“'+(x.name||'该行为模式')+'”落到系统已有招法：P正向攻击 → T负面攻击/威胁假设 → B平台机制异常假设 → 我方再用P招法换路。实际响应优先于预测。'
    };
  }

  function moveHtml(m,side,behavior){
    var detail=side==='我方'
      ? ('动作：'+(m.action||'按该招法执行小成本、可撤回测试')+'；目标：'+(m.goal||'验证增量'))
      : ('信号：'+(m.signal||'观察异常变化')+'；机制：'+(m.mechanism||m.defense||'仅作为待验证假设'));
    return '<div style="margin-top:6px"><span class="tag">'+esc(side)+'</span> <b>'+esc(m.id)+' · '+esc(m.name)+'</b><div class="muted" style="margin-top:4px">行为路径：'+esc(behavior||'观察')+' · '+esc(m.category||'')+'</div><div style="margin-top:4px">'+esc(detail)+'</div></div>';
  }

  function render(){
    if(location.hash!=='#strategy-center')return;
    var app=document.getElementById('app');if(!app)return;
    var lib=getLibrary().slice(0,40),list=lib.map(function(x,i){return build(i,x);});
    var h='<h1 class="page-title">连续博弈中心 <span style="font-size:16px;font-weight:500;color:var(--accent);margin-left:10px">我变 → 对手学 → 我再变</span></h1>'+
      '<div class="subtitle">40种行为人格 · 40套连续棋谱 · 直接调用系统已有的正向攻击 / 负面攻击 / 平台机制异常招法</div>'+
      '<div class="card" style="margin:10px 0 16px;border-left:4px solid var(--accent);background:rgba(255,180,0,.06)"><b>棋谱规则</b><div style="font-size:18px;margin-top:6px">我方使用 P 正向攻击招法 → 对手响应使用 T 负面攻击或 B 平台机制异常招法（仅为待验证假设） → 我方根据真实反馈换招 → 风险控制 → 下一轮。</div></div>'+
      '<div class="card"><div class="label">40套连续博弈棋谱</div><div class="muted" style="margin-top:5px">棋谱不是泛泛的“观察/调整”，每一轮都落到已有策略库的具体编号。</div><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px;margin-top:12px">';
    list.forEach(function(x){
      h+='<div class="game-wrap" data-game="'+esc(x.id)+'"><div class="card"><span class="tag">'+esc(x.id)+'</span><b style="display:block;margin-top:7px">'+esc(x.name)+'</b><div class="muted" style="margin-top:5px">'+esc(x.style)+' · '+esc(x.risk)+'风险</div><div class="muted" style="margin-top:5px">行为序列：'+esc(x.sequence.join(' → '))+'</div><div class="muted" style="margin-top:5px">招法：'+esc(x.moves.map(function(m){return m.id;}).join(' → '))+' ↔ '+esc(x.opponents.map(function(m){return m.id;}).join(' → '))+'</div><div style="display:flex;gap:8px;margin-top:10px"><button type="button" class="game-card" data-mode="playbook" style="cursor:pointer">♟ 棋谱</button><button type="button" class="game-card" data-mode="reasoning" style="cursor:pointer">🧠 推理</button></div></div><div class="game-detail" style="display:none;margin-top:8px"></div></div>';
    });
    h+='</div></div>';
    app.innerHTML=h;
  }

  document.addEventListener('click',function(e){
    var b=e.target&&e.target.closest?e.target.closest('.game-card'):null;if(!b)return;
    var wrap=b.closest('.game-wrap'),detail=wrap.querySelector('.game-detail'),id=wrap.getAttribute('data-game'),mode=b.getAttribute('data-mode');
    var lib=getLibrary(),x0=findById(lib,id);if(!x0)return;
    var x=build(lib.indexOf(x0),x0);detail.style.display='block';
    var html='<div class="card" style="margin:0;border-left:3px solid var(--accent)"><div class="label">'+esc(x.id)+' · '+esc(x.name)+'</div>';
    if(mode==='playbook'){
      html+='<div style="margin-top:8px"><b>连续博弈棋谱 · 具体招法</b></div>';
      x.steps.forEach(function(s){
        html+='<div style="padding:9px 0;border-bottom:1px solid var(--line)"><b>第'+s.round+'轮 · '+esc(s.side)+'</b>'+moveHtml(s.move,s.side,s.behavior)+'</div>';
      });
      html+='<div class="notice" style="margin-top:10px"><b>棋谱目标：</b>'+esc(x.goal)+'</div>';
    }else{
      html+='<div style="margin-top:8px"><b>连续博弈推理</b></div>'+
        '<div style="line-height:1.8;margin-top:8px">先识别“'+esc(x.style)+'”与行为序列“'+esc(x.sequence.join(' → '))+'”。然后把已有 P/T/B 招法作为候选路径，而不是凭空创造动作。第1轮先用 '+esc(x.moves[0].id)+' 验证市场，第2轮检查是否出现 '+esc(x.opponents[0].id)+' 对应的可观测信号；第3轮切换 '+esc(x.moves[1].id)+'，第4轮继续检查 '+esc(x.opponents[1].id)+'；第5轮根据实际结果在 '+esc(x.moves[2].id)+' 与等待/防守之间选择。T/B 只能作为假设，不能仅凭异常直接归因给具体竞争者；实际响应写回下一轮。'+
        '</div>'+
        '<div class="card" style="margin-top:10px"><b>本局使用的系统招法</b><div style="margin-top:6px">我方正向攻击：'+esc(x.moves.map(function(m){return m.id+' '+m.name;}).join(' · '))+'</div><div style="margin-top:6px">对手负面攻击：'+esc(x.opponents.filter(function(m){return m.id.charAt(0)==='T';}).map(function(m){return m.id+' '+m.name;}).join(' · ')||'无')+'</div><div style="margin-top:6px">对手平台机制异常：'+esc(x.opponents.filter(function(m){return m.id.charAt(0)==='B';}).map(function(m){return m.id+' '+m.name;}).join(' · ')||'无')+'</div></div>'+
        '<div class="notice"><b>推理目标：</b>'+esc(x.goal)+'</div>';
    }
    html+='</div>';detail.innerHTML=html;detail.scrollIntoView({behavior:'smooth',block:'nearest'});
  },false);

  window.__EA_STRATEGY_CENTER_RENDER__=render;
  window.addEventListener('hashchange',function(){setTimeout(render,30);});
  setTimeout(render,50);
})();