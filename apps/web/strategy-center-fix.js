(function(){
  'use strict';

  // 连贯式博弈棋谱：
  // 每个人格 = 一张连续棋谱；默认40步。
  // 不是“每轮三步后结束”，而是：我方一招 → 对手一招 → 我方一招 → 对手一招……
  // 正向攻击、负向/对手攻击、机制型攻防三类招式在同一条连续链中混合出现。
  // 所有对手动作均为模拟假设；机制型招式只用于模拟异常/校验/防守，不提供真实漏洞利用步骤。

  function esc(v){
    return String(v==null?'':v)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;')
      .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
  function lib(k){return Array.isArray(window[k])?window[k]:[];}
  function mod(n,m){return m?((n%m)+m)%m:0;}

  function phaseOf(token){
    token=String(token||'');
    if(/负向|强负|竞争|施压|报复|反击/.test(token))return'对抗阶段';
    if(/防守|异常|失败|收缩|退出|降低/.test(token))return'防守阶段';
    if(/观察|测算|跟随|小试|再试|反馈|行动|正常/.test(token))return'观察试探阶段';
    if(/扩大|扩张|机会|正向|合作|联合|重新进入|继续/.test(token))return'增长推进阶段';
    return'自适应阶段';
  }

  function positive(i,step){
    var a=lib('EA_POSITIVE_ATTACK_LIBRARY');
    return a.length?a[mod(i*7+step*11+3,a.length)]:null;
  }
  function threat(i,step){
    var a=lib('EA_THREAT_LIBRARY');
    return a.length?a[mod(i*5+step*13+1,a.length)]:null;
  }
  function bug(i,step){
    var a=lib('EA_BUG_ATTACK_LIBRARY');
    return a.length?a[mod(i*3+step*7+5,a.length)]:null;
  }

  function chooseOur(i,step,phase){
    var p=positive(i,step),b=bug(i,step);
    // 防守/异常阶段优先机制型招式；其他阶段以正向招式推进。
    if((phase==='防守阶段'||phase==='对抗阶段')&&b){
      return {id:b.id,name:b.name,kind:'机制型攻防',role:'我方',source:b,
        reason:'先识别、校验和隔离异常，再决定是否继续投入资源。'};
    }
    return p?{id:p.id,name:p.name,kind:'正向攻击',role:'我方',source:p,
      reason:'根据该人格当前阶段推进自身产品、内容、流量、服务、品牌或供应链优势。'}:
      {id:b?b.id:'',name:b?b.name:'',kind:'机制型攻防',role:'我方',source:b,
      reason:'正向招式不足时，用机制校验保持可验证性。'};
  }

  function chooseOpponent(i,step,phase){
    var t=threat(i,step),b=bug(i,step);
    // 对手主要来自负向攻击面；在机制异常信号明显时穿插机制型攻防作为“模拟机制响应”。
    if((step%7===0||phase==='防守阶段')&&b){
      return {id:b.id,name:b.name,kind:'机制型攻防',role:'对手（模拟）',source:b,
        reason:'模拟对手利用机制层信号制造异常反馈；这里只作为待验证假设。'};
    }
    return t?{id:t.id,name:t.name,kind:'负向攻击面',role:'对手（模拟）',source:t,
      reason:'模拟对手观察到我方动作后，选择相应的竞争、流量、口碑、价格、渠道或规则压力。'}:
      {id:b?b.id:'',name:b?b.name:'',kind:'机制型攻防',role:'对手（模拟）',source:b,
      reason:'暂无负向招式时，用机制异常作为模拟响应。'};
  }

  function build(i,x){
    var seq=Array.isArray(x.sequence)&&x.sequence.length?x.sequence:['正向'];
    var steps=[];
    var seen={};
    // 一张棋谱连续40步：1我方、2对手、3我方、4对手……
    for(var n=1;n<=40;n++){
      var token=seq[mod(Math.floor((n-1)/4),seq.length)];
      var phase=phaseOf(token);
      var m;
      if(n%2===1){
        m=chooseOur(i,n,phase);
      }else{
        m=chooseOpponent(i,n,phase);
      }
      // 避免连续重复同一招；库内还有其他招式时换一个索引。
      var key=m.kind+':'+m.id;
      if(seen[key]){
        if(m.kind==='正向攻击'){
          var p=positive(i,n+7); if(p){m.id=p.id;m.name=p.name;m.source=p;}
        }else if(m.kind==='负向攻击面'){
          var t=threat(i,n+9); if(t){m.id=t.id;m.name=t.name;m.source=t;}
        }else{
          var b=bug(i,n+11); if(b){m.id=b.id;m.name=b.name;m.source=b;}
        }
      }
      seen[m.kind+':'+m.id]=1;
      steps.push({
        no:n,side:n%2?'我方':'对手',role:m.role,
        token:token,phase:phase,move:m,
        response:n===40?'本局结束：进入复盘。':'这一招改变下一步可观察状态，下一步继续根据当前状态选招。'
      });
    }
    return {id:x.id,name:x.name,style:x.style||'',risk:x.risk||'中',signal:x.signal||'',goal:x.goal||'',sequence:seq,steps:steps};
  }

  function coverage(){
    var P=lib('EA_POSITIVE_ATTACK_LIBRARY'),T=lib('EA_THREAT_LIBRARY'),B=lib('EA_BUG_ATTACK_LIBRARY');
    var h='<details class="card" style="margin-top:14px"><summary style="cursor:pointer;font-weight:700;font-size:16px">📚 三大招式库完整内容：正向 '+P.length+' · 负向 '+T.length+' · 机制型 '+B.length+'</summary>';
    h+='<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;margin-top:12px">';
    function col(title,a){
      var s='<div class="card" style="margin:0"><b>'+esc(title)+'（'+a.length+'）</b><div style="margin-top:8px;line-height:1.7">';
      a.forEach(function(m){s+='<div><span class="tag">'+esc(m.id)+'</span> '+esc(m.name)+'</div>';});
      return s+'</div></div>';
    }
    h+=col('正向攻击面',P)+col('负向攻击面 / 对手招式',T)+col('机制型攻防招式',B);
    return h+'</div></details>';
  }

  function render(){
    if(location.hash!=='#strategy-center')return;
    var app=document.getElementById('app');if(!app)return;
    var H=lib('EA_HUMAN_BEHAVIOR_LIBRARY').slice(0,40);
    var html='<h1 class="page-title">连续博弈策略中心 <span style="font-size:16px;font-weight:500;color:var(--accent);margin-left:10px">我变 → 对手学 → 我再变</span></h1>';
    html+='<div class="subtitle">40种行为人格 · 每个人格一张连续棋谱 · 40步连续交锋 · 三大招式库混合使用</div>';
    html+='<div class="card" style="margin:10px 0 16px;border-left:4px solid var(--accent);background:rgba(255,180,0,.06)"><b>棋谱规则</b><div style="font-size:16px;line-height:1.7;margin-top:6px">';
    html+='不是“我方三步/一轮就结束”。每一套人格是一条完整连续链：<b>我方第1招 → 对手第2招 → 我方第3招 → 对手第4招 → …… → 第40招</b>。';
    html+='正向攻击面、负向攻击面、机制型攻防招式会在同一张棋谱中穿插；人格决定节奏和阶段，上一招改变下一招的状态。对手招式是模拟假设，机制型招式用于识别、校验、隔离和防守。';
    html+='</div></div>';
    html+='<div class="card"><div class="label">40套连续博弈棋谱</div><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:10px;margin-top:12px">';
    H.forEach(function(x,i){
      html+='<div class="game-wrap" data-game="'+esc(x.id)+'"><div class="card"><span class="tag">'+esc(x.id)+'</span><b style="display:block;margin-top:7px">'+esc(x.name)+'</b>';
      html+='<div class="muted" style="margin-top:5px">模式：'+esc(x.style)+' · '+esc(x.risk)+'风险</div><div style="margin-top:5px">信号：'+esc(x.signal)+'</div>';
      html+='<div style="margin-top:5px"><b>人格序列：</b>'+esc((x.sequence||[]).join(' → '))+'</div>';
      html+='<div style="margin-top:7px"><b>连续长度：</b>40步，不按“三步一局”截断</div>';
      html+='<div style="display:flex;gap:8px;margin-top:10px"><button type="button" class="game-card" data-mode="playbook">♟ 查看40步连续棋谱</button><button type="button" class="game-card" data-mode="reasoning">🧠 查看人格逻辑</button></div></div><div class="game-detail" style="display:none;margin-top:8px"></div></div>';
    });
    html+='</div></div>'+coverage();
    app.innerHTML=html;
  }

  function stepHtml(s){
    var m=s.move;
    var border=m.kind==='正向攻击'?'var(--accent)':m.kind==='负向攻击面'?'#b44':'#777';
    var h='<div class="card" style="margin:0 0 8px;border-left:4px solid '+border+'">';
    h+='<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap"><span class="tag">第'+s.no+'步</span><b>'+esc(s.side)+'</b><span class="tag">'+esc(m.kind)+'</span><span class="muted">'+esc(s.phase)+'</span></div>';
    h+='<div style="font-size:17px;margin-top:7px"><span class="tag">'+esc(m.id)+'</span> <b>'+esc(m.name)+'</b></div>';
    h+='<div class="muted" style="margin-top:5px">'+esc(m.reason)+'</div>';
    if(m.source){
      h+='<div class="muted" style="margin-top:4px">招式原定义：'+esc(m.source.action||m.source.defense||m.source.mechanism||m.source.signal||'')+'</div>';
      if(m.source.combo&&Array.isArray(m.source.combo.steps)){
        h+='<details style="margin-top:8px"><summary style="cursor:pointer;font-weight:700">🔗 查看具体组合方式</summary>';
        h+='<div class="notice" style="margin-top:6px"><b>'+esc(m.source.combo.name||'组合路径')+'</b><div style="margin-top:6px">';
        m.source.combo.steps.forEach(function(z){
          h+='<div style="margin:7px 0;padding:7px;border-left:3px solid var(--accent)"><b>'+esc(z.no)+' · '+esc(z.name)+'</b><div>'+esc((z.moves||[]).join(' → '))+'</div><div class="muted">目的：'+esc(z.purpose||'')+'</div></div>';
        });
        h+='</div><div class="muted" style="margin-top:6px"><b>组合规则：</b>'+esc(m.source.combo.rule||'按反馈逐段推进，不要求一次全部执行。')+'</div></div></details>';
      }
    }
    h+='<div class="notice" style="margin-top:6px">'+esc(s.response)+'</div>';
    h+='</div>';
    return h;
  }

  document.addEventListener('click',function(e){
    var b=e.target&&e.target.closest?e.target.closest('.game-card'):null;
    if(!b)return;
    var wrap=b.closest('.game-wrap'),detail=wrap&&wrap.querySelector('.game-detail');
    if(!wrap||!detail)return;
    var id=wrap.getAttribute('data-game'),mode=b.getAttribute('data-mode');
    var H=lib('EA_HUMAN_BEHAVIOR_LIBRARY'),x=null,idx=0;
    for(;idx<H.length;idx++)if(H[idx].id===id){x=H[idx];break;}
    if(!x)return;
    var data=build(idx,x);
    detail.style.display='block';
    var h='<div class="card" style="margin:0;border-left:3px solid var(--accent)"><div class="label">'+esc(data.id)+' · '+esc(data.name)+'</div>';
    h+='<div style="margin-top:8px"><b>人格：</b>'+esc(data.signal)+'<br><b>目标：</b>'+esc(data.goal)+'</div>';
    if(mode==='playbook'){
      h+='<div style="margin-top:12px"><b>一条连续40步棋谱</b></div>';
      h+='<div class="muted" style="margin:5px 0 12px">注意：这里是“连续交锋”，不是每三步重新开始。第1步结束后立即进入第2步，第2步又改变第3步，以此连续到第40步。</div>';
      data.steps.forEach(function(s){h+=stepHtml(s);});
    }else{
      h+='<div style="margin-top:10px;line-height:1.8"><b>这个人格为什么这样走？</b><br>';
      h+='人格序列只负责定义长期行为倾向；真正的棋谱由连续状态驱动。奇数步是我方，偶数步是对手。三类招式不是三条互相独立的棋谱，而是同一条链里的不同类型：正向攻击用于建设优势，负向攻击面用于模拟对手施压，机制型攻防用于处理异常信号和防守校验。';
      h+='</div><div class="notice" style="margin-top:10px"><b>关键：</b>不能看到某一招就认定对手一定会这样做；实际系统运行时，应把真实市场反馈替换“模拟假设”，再继续生成下一步。</div>';
      h+='<div style="margin-top:10px"><b>40步类型轨迹：</b><div style="line-height:2;margin-top:5px">';
      data.steps.forEach(function(s){h+='<span class="tag" style="margin:2px">'+s.no+' '+esc(s.move.kind)+'</span>';});
      h+='</div></div>';
    }
    h+='</div>';
    detail.innerHTML=h;
    detail.scrollIntoView({behavior:'smooth',block:'nearest'});
  },false);

  window.__EA_STRATEGY_CENTER_RENDER__=render;
  window.addEventListener('hashchange',function(){setTimeout(render,30);});
  setTimeout(render,50);
})();