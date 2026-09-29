(function(){
  'use strict';

  function esc(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\"/g,'&quot;');}
  function lib(name){return Array.isArray(window[name])?window[name]:[];}
  function byId(arr,id){for(var i=0;i<arr.length;i++)if(arr[i]&&arr[i].id===id)return arr[i];return null;}

  /*
   * 棋谱 = 人性行为模式 + 已有招式库。
   * P = 正向攻击；T = 负面攻击；B/N = 平台机制异常 / Bug攻击。
   * 每一步都保留来源 ID，点击后直接跳到原招式页面并展开对应招式。
   */
  var MOVE_MAP={
    H01:['P40','P42','T19','B09','P35','P47'],
    H02:['P49','T40','T19','B23','T17','B11'],
    H03:['P41','T20','B11','P50','T26','B18'],
    H04:['P03','P14','T19','B09','P40','T33'],
    H05:['T19','B21','P49','P03','B09','P42'],
    H06:['P22','T17','B18','P41','T26','P46'],
    H07:['P25','T19','B04','P41','B09','P50'],
    H08:['T01','T02','B19','P39','B23','T40'],
    H09:['P37','B21','T20','P19','B11','P20'],
    H10:['P32','P33','T19','B10','P45','P50'],
    H11:['P37','T18','B11','P32','T19','P40'],
    H12:['P49','B21','T19','P03','B09','P41'],
    H13:['P31','T19','B10','P45','T26','P50'],
    H14:['T17','B11','T19','B23','P37','P44'],
    H15:['P49','B21','P37','T20','P15','P50'],
    H16:['P23','T20','B18','T40','P40','B23'],
    H17:['P38','T20','B11','P44','T19','P37'],
    H18:['P37','B21','T20','P38','B11','P40'],
    H19:['P31','P32','T19','B10','P45','P40'],
    H20:['P37','T19','B21','P49','T17','P31'],
    H21:['P40','T19','B18','P22','T26','P35'],
    H22:['P49','B21','T19','P03','B09','P41'],
    H23:['P26','P31','T19','B10','P45','T20'],
    H24:['P33','B21','T19','P25','B10','P40'],
    H25:['P25','T19','B04','P31','B09','P41'],
    H26:['P01','P03','T19','B10','P22','P40'],
    H27:['P49','B21','T19','P02','B09','P41'],
    H28:['P40','T20','B23','P45','T26','B18'],
    H29:['P08','T34','B23','P30','T19','P36'],
    H30:['P08','P24','T19','B23','P36','P40'],
    H31:['P20','T02','B23','P37','T19','B21'],
    H32:['P40','P31','T19','B10','P45','P42'],
    H33:['P25','B21','T19','P49','B09','P41'],
    H34:['P50','T19','B23','P31','T20','P40'],
    H35:['P16','P35','T19','B09','P42','P47'],
    H36:['P32','P33','T20','B10','P45','P50'],
    H37:['P37','T20','B21','P15','B11','P40'],
    H38:['P40','T01','B19','P39','T19','B23'],
    H39:['P49','B21','T19','P41','B09','P42'],
    H40:['P40','T40','B23','P50','T19','P42']
  };

  var ROLE=[
    '我方先手',
    '对手负向招式',
    '平台机制异常',
    '我方换招',
    '对手/市场再响应',
    '我方收束'
  ];

  function sourceInfo(id){
    var p=byId(lib('EA_POSITIVE_ATTACK_LIBRARY'),id);
    if(p)return {id:id,type:'positive',name:p.name,category:p.category,desc:p.action||p.signal||'',route:'positive-attacks'};
    var t=byId(lib('EA_THREAT_LIBRARY'),id);
    if(t)return {id:id,type:'threat',name:t.name,category:t.category,desc:t.defense||t.signal||'',route:'threats'};
    var b=byId(lib('EA_BUG_ATTACK_LIBRARY'),id);
    if(b)return {id:id,type:'bug',name:b.name,category:b.category,desc:b.mechanism||b.signal||'',route:'bug-attacks'};
    return {id:id,type:'unknown',name:'未找到招式 '+id,category:'',desc:'',route:''};
  }

  function zhType(t){
    return t==='positive'?'正向攻击':t==='threat'?'负面攻击':t==='bug'?'Bug攻击':'系统招式';
  }

  function moveText(info,role){
    if(!info)return role;
    return role+'：'+info.name+'（'+info.id+'）';
  }

  function build(i,x){
    var ids=MOVE_MAP[x.id]||MOVE_MAP.H40;
    var moves=ids.map(sourceInfo);
    var steps=[];
    for(var k=0;k<moves.length;k++){
      var m=moves[k];
      steps.push({
        round:k+1,
        role:ROLE[k]||'下一轮',
        move:m,
        text:moveText(m,ROLE[k]||'下一轮')
      });
    }
    return {
      id:x.id||('H'+String(i+1).padStart(2,'0')),
      name:x.name||('行为模式'+(i+1)),
      style:x.style||'',
      sequence:Array.isArray(x.sequence)?x.sequence:[],
      risk:x.risk||'中',
      signal:x.signal||'',
      goal:x.goal||'',
      steps:steps,
      goalText:'把“'+(x.name||'该行为模式')+'”落到已有招式库中：我方用正向攻击创造变量，对手用负面攻击形成压力，平台机制异常作为中间层信号，再根据真实反馈换招。'
    };
  }

  function navToMove(id){
    var s=sourceInfo(id);
    if(!s.route)return;
    state.view=s.route;
    location.hash=s.route;
    render();
    setTimeout(function(){
      var selector=s.type==='positive'?'[data-pos="'+id+'"]':s.type==='threat'?'[data-threat="'+id+'"]':'[data-bug="'+id+'"]';
      var el=document.querySelector(selector);
      if(el){
        var detail=el.querySelector('#pos-'+id)||el.querySelector('#threat-'+id)||el.querySelector('#bug-'+id);
        if(!detail)detail=document.getElementById((s.type==='positive'?'pos-':s.type==='threat'?'threat-':'bug-')+id);
        if(detail)detail.style.display='block';
        el.scrollIntoView({behavior:'smooth',block:'center'});
      }
    },80);
  }

  function render(){
    if(location.hash!=='#strategy-center')return;
    var app=document.getElementById('app');if(!app)return;
    var human=lib('EA_HUMAN_BEHAVIOR_LIBRARY').slice(0,40);
    var list=human.map(function(x,i){return build(i,x);});
    var h='<h1 class="page-title">连续博弈中心 <span style="font-size:16px;font-weight:500;color:var(--accent);margin-left:10px">我变 → 对手学 → 我再变</span></h1>';
    h+='<div class="subtitle">40种行为人格 · 40套棋谱 · 每一招都来自现有招式库，可直接溯源</div>';
    h+='<div class="card" style="margin:10px 0 16px;border-left:4px solid var(--accent);background:rgba(255,180,0,.06)"><b>棋谱规则</b><div style="font-size:18px;margin-top:6px">正向攻击 → 负面攻击 → Bug攻击/平台机制异常 → 再变招 → 再响应。棋谱不再虚构招式，所有招式均引用系统已有 P/T/B 招式。</div></div>';
    h+='<div class="card"><div class="label">40套连续博弈棋谱</div><div class="muted" style="margin-top:5px">点击“♟ 棋谱”后，每一步都会显示：招式名称、编号、所属招式库，并可直接跳到原页面查看完整介绍。</div>';
    h+='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px;margin-top:12px">';
    list.forEach(function(x){
      h+='<div class="game-wrap" data-game="'+esc(x.id)+'"><div class="card">';
      h+='<span class="tag">'+esc(x.id)+'</span><b style="display:block;margin-top:7px">'+esc(x.name)+'</b>';
      h+='<div class="muted" style="margin-top:5px">'+esc(x.style)+' · '+esc(x.risk)+'风险</div>';
      h+='<div class="muted" style="margin-top:5px">行为序列：'+esc(x.sequence.join(' → '))+'</div>';
      h+='<div style="display:flex;gap:8px;margin-top:10px"><button type="button" class="game-card" data-mode="playbook">♟ 棋谱</button><button type="button" class="game-card" data-mode="reasoning">🧠 推理</button></div>';
      h+='</div><div class="game-detail" style="display:none;margin-top:8px"></div></div>';
    });
    h+='</div></div>';
    app.innerHTML=h;
  }

  document.addEventListener('click',function(e){
    var move=e.target&&e.target.closest?e.target.closest('[data-source-move]'):null;
    if(move){
      e.preventDefault();
      navToMove(move.getAttribute('data-source-move'));
      return;
    }
    var b=e.target&&e.target.closest?e.target.closest('.game-card'):null;
    if(!b)return;
    var wrap=b.closest('.game-wrap'),detail=wrap.querySelector('.game-detail'),id=wrap.getAttribute('data-game'),mode=b.getAttribute('data-mode');
    var human=lib('EA_HUMAN_BEHAVIOR_LIBRARY'),x0=byId(human,id);
    if(!x0)return;
    var x=build(human.indexOf(x0),x0);
    detail.style.display='block';
    var html='<div class="card" style="margin:0;border-left:3px solid var(--accent)"><div class="label">'+esc(x.id)+' · '+esc(x.name)+'</div>';
    if(mode==='playbook'){
      html+='<div style="margin-top:8px"><b>连续博弈棋谱（招式均可溯源）</b></div>';
      html+='<ol style="line-height:1.75;margin:8px 0">';
      x.steps.forEach(function(s){
        var m=s.move;
        html+='<li style="margin-bottom:10px"><div><b>'+esc(s.role)+'</b> → <button type="button" class="action" data-source-move="'+esc(m.id)+'" style="margin-left:4px">'+esc(m.id)+' · '+esc(m.name)+'</button></div>';
        html+='<div class="muted" style="margin-top:3px">'+esc(zhType(m.type))+' · '+esc(m.category)+'</div>';
        if(m.desc)html+='<div class="muted" style="margin-top:3px">'+esc(m.desc)+'</div>';
        html+='</li>';
      });
      html+='</ol><div class="notice"><b>棋谱目标：</b>'+esc(x.goalText)+'</div>';
    }else{
      html+='<div style="margin-top:8px"><b>连续博弈推理</b></div>';
      html+='<div style="line-height:1.8;margin-top:8px">基于“'+esc(x.style)+'”和行为序列“'+esc(x.sequence.join(' → '))+'”，把已有招式库作为动作空间：先选择可验证的正向招式，再观察负面招式与平台机制异常信号，最后根据实际响应选择下一招。实际响应高于理论预测，不把推测当事实。</div>';
      html+='<div class="notice"><b>本局招式：</b>'+x.steps.map(function(s){return esc(s.move.id)+' '+esc(s.move.name);}).join(' → ')+'</div>';
    }
    html+='</div>';
    detail.innerHTML=html;
    detail.scrollIntoView({behavior:'smooth',block:'nearest'});
  },false);

  window.__EA_STRATEGY_CENTER_RENDER__=render;
  window.addEventListener('hashchange',function(){setTimeout(render,30);});
  setTimeout(render,50);
})();