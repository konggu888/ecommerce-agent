(function(){
  'use strict';

  // 连续博弈策略中心：40种人格 × 12轮 × 每轮3步。
  // 这里是“模拟棋谱”，不是实际平台操作。对手动作均标记为“模拟假设”；
  // 机制库只用于异常识别、校验、隔离和防守，不用于真实平台漏洞利用。

  function esc(v){
    return String(v==null?'':v)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;')
      .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
  function lib(k){ return Array.isArray(window[k]) ? window[k] : []; }
  function byId(k,id){
    var a=lib(k);
    for(var i=0;i<a.length;i++) if(a[i] && a[i].id===id) return a[i];
    return null;
  }
  function mod(n,m){ return m ? ((n%m)+m)%m : 0; }

  function tokenToPhase(token){
    token=String(token||'');
    if(/负向|负|强负|竞争|施压|响应/.test(token)) return '防守反制';
    if(/防守|异常|失败|收缩|降低|退出/.test(token)) return '防守校验';
    if(/观察|测算|跟随|小试|再试|行动|反馈|更新|正常|被挑战/.test(token)) return '低成本试探';
    if(/扩大|扩张|快速|继续|正向|机会|重新进入|合作|联合/.test(token)) return '增长推进';
    return '自适应';
  }

  function positiveIndex(personIndex, round, slot){
    var P=lib('EA_POSITIVE_ATTACK_LIBRARY');
    if(!P.length) return -1;
    // 人格、轮次、位置共同决定招式，不再固定 P01。
    return mod(personIndex*7 + round*11 + slot*13, P.length);
  }

  function threatIndex(personIndex, round){
    var T=lib('EA_THREAT_LIBRARY');
    if(!T.length) return -1;
    return mod(personIndex*5 + round*9 + 3, T.length);
  }

  function bugIndex(personIndex, round, slot){
    var B=lib('EA_BUG_ATTACK_LIBRARY');
    if(!B.length) return -1;
    return mod(personIndex*3 + round*7 + slot*5, B.length);
  }

  function pickPositive(personIndex,round,slot){
    var P=lib('EA_POSITIVE_ATTACK_LIBRARY');
    var i=positiveIndex(personIndex,round,slot);
    return i<0?null:P[i];
  }
  function pickThreat(personIndex,round){
    var T=lib('EA_THREAT_LIBRARY');
    var i=threatIndex(personIndex,round);
    return i<0?null:T[i];
  }
  function pickBug(personIndex,round,slot){
    var B=lib('EA_BUG_ATTACK_LIBRARY');
    var i=bugIndex(personIndex,round,slot);
    return i<0?null:B[i];
  }

  function actionForPhase(personIndex,round,phase){
    var P=pickPositive(personIndex,round,0);
    var B=pickBug(personIndex,round,0);
    if(phase==='防守反制' || phase==='防守校验'){
      return {
        id:B?B.id:(P?P.id:''),
        name:B?B.name:(P?P.name:''),
        type:B?'机制型攻防':'正向攻击',
        role:'我方防守/校验',
        source:B||P,
        why:B?'人格进入防守或受压阶段，先确认异常来源、保护关键指标，再决定是否继续。':'人格需要在压力下维持经营基本盘，优先选择可验证的经营动作。'
      };
    }
    if(phase==='低成本试探'){
      return {
        id:P?P.id:'',
        name:P?P.name:'',
        type:'正向攻击',
        role:'我方试探',
        source:P,
        why:'该人格处于观察/试探阶段，先用低成本、可回测的经营动作获得信息，而不是一次性重仓。'
      };
    }
    return {
      id:P?P.id:'',
      name:P?P.name:'',
      type:'正向攻击',
      role:'我方推进',
      source:P,
      why:'该人格进入建设、扩张或机会阶段，用正向经营动作扩大已验证的优势。'
    };
  }

  function responseFor(personIndex,round,phase){
    var B=pickBug(personIndex,round,1);
    var P=pickPositive(personIndex,round,1);
    if(phase==='防守反制' || phase==='防守校验'){
      return {
        id:B?B.id:(P?P.id:''),
        name:B?B.name:(P?P.name:''),
        type:B?'机制型攻防':'正向攻击',
        role:'我方应对',
        source:B||P,
        why:B?'对手信号出现后，先做异常识别、交叉验证、隔离和复测，避免把噪声当成真实趋势。':'防守完成后用经营动作修复核心指标，并以真实结果验证。'
      };
    }
    return {
      id:P?P.id:'',
      name:P?P.name:'',
      type:'正向攻击',
      role:'我方应对',
      source:P,
      why:'先验证对手动作是否真正改变核心经营指标；若影响有限，则把资源继续投入自身可积累的优势。'
    };
  }

  function build(i,x){
    var seq=Array.isArray(x.sequence)&&x.sequence.length?x.sequence:['正向'];
    var rounds=[];
    var used={};
    for(var r=1;r<=12;r++){
      var token=seq[mod(r-1,seq.length)];
      var phase=tokenToPhase(token);
      var ours=actionForPhase(i,r,phase);
      var threat=pickThreat(i,r);
      var defend=responseFor(i,r,phase);

      // 同一套棋谱内尽量避免短期重复；如库耗尽再允许循环。
      var key1=ours.type+':'+ours.id;
      var key2='T:'+ (threat?threat.id:'');
      var key3=defend.type+':'+defend.id;
      if(used[key1] && lib('EA_POSITIVE_ATTACK_LIBRARY').length>12){
        ours.source=pickPositive(i+r,r,0)||ours.source;
        ours.id=ours.source?ours.source.id:ours.id;
        ours.name=ours.source?ours.source.name:ours.name;
      }
      if(used[key2] && lib('EA_THREAT_LIBRARY').length>12){
        threat=pickThreat(i+r,r);
      }
      if(used[key3] && lib('EA_BUG_ATTACK_LIBRARY').length>12){
        defend.source=pickBug(i+r,r,1)||defend.source;
        defend.id=defend.source?defend.source.id:defend.id;
        defend.name=defend.source?defend.source.name:defend.name;
      }
      used[ours.type+':'+ours.id]=1;
      if(threat) used['T:'+threat.id]=1;
      used[defend.type+':'+defend.id]=1;

      rounds.push({
        round:r,token:token,phase:phase,
        ours:ours,threat:threat,defend:defend,
        next:'根据本轮真实反馈更新对手模型；下一轮招式不预设为上一轮重复动作。'
      });
    }
    return {
      id:x.id,name:x.name,style:x.style||'',risk:x.risk||'中',
      signal:x.signal||'',goal:x.goal||'',sequence:seq,rounds:rounds
    };
  }

  function moveLink(type,id){
    if(!id)return '#';
    var v=type==='正向攻击'?'positive-attacks':type==='对手攻击'?'threats':'bug-attacks';
    return 'javascript:void(0)';
  }

  function renderLibraryCoverage(){
    var P=lib('EA_POSITIVE_ATTACK_LIBRARY'),T=lib('EA_THREAT_LIBRARY'),B=lib('EA_BUG_ATTACK_LIBRARY');
    var h='<details class="card" style="margin-top:14px"><summary style="cursor:pointer;font-weight:700;font-size:16px">📚 完整招式库：正向 '+P.length+' · 对手 '+T.length+' · 机制型 '+B.length+'</summary>';
    h+='<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;margin-top:12px">';
    function col(title,a,cls){
      var s='<div class="card" style="margin:0"><b>'+esc(title)+'（'+a.length+'）</b><div style="margin-top:8px;line-height:1.7">';
      a.forEach(function(m){s+='<div><span class="tag '+cls+'">'+esc(m.id)+'</span> '+esc(m.name)+'</div>';});
      return s+'</div></div>';
    }
    h+=col('正向经营招式',P,'');
    h+=col('对手/负向招式（模拟）',T,'');
    h+=col('机制型攻防招式',B,'');
    h+='</div></details>';
    return h;
  }

  function render(){
    if(location.hash!=='#strategy-center')return;
    var app=document.getElementById('app');if(!app)return;
    var H=lib('EA_HUMAN_BEHAVIOR_LIBRARY').slice(0,40);
    var html='<h1 class="page-title">连续博弈策略中心 <span style="font-size:16px;font-weight:500;color:var(--accent);margin-left:10px">我变 → 对手学 → 我再变</span></h1>';
    html+='<div class="subtitle">40种行为人格 · 每套12轮 · 每轮3步 · 共36步：我方招式 → 对手响应 → 我方应对</div>';
    html+='<div class="card" style="margin:10px 0 16px;border-left:4px solid var(--accent);background:rgba(255,180,0,.06)">';
    html+='<b>棋谱规则</b><div style="font-size:16px;line-height:1.7;margin-top:6px">';
    html+='人格决定阶段与选招逻辑；上一轮的对手响应进入下一轮状态。每轮固定展示“我方怎么打 → 对手怎么回应 → 我方怎么应对”，而不是把三个固定招式重复12次。';
    html+='对手动作全部是模拟假设，必须用真实市场数据验证；机制型招式只用于异常识别、校验、隔离和防守。';
    html+='</div></div>';
    html+='<div class="card"><div class="label">40套连续博弈棋谱</div><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:10px;margin-top:12px">';
    H.forEach(function(x,i){
      var b=build(i,x);
      html+='<div class="game-wrap" data-game="'+esc(b.id)+'"><div class="card">';
      html+='<span class="tag">'+esc(b.id)+'</span><b style="display:block;margin-top:7px">'+esc(b.name)+'</b>';
      html+='<div class="muted" style="margin-top:5px">模式：'+esc(b.style)+' · '+esc(b.risk)+'风险</div>';
      html+='<div style="margin-top:5px">信号：'+esc(b.signal)+'</div>';
      html+='<div style="margin-top:5px"><b>行为序列：</b>'+esc(b.sequence.join(' → '))+'</div>';
      html+='<div style="margin-top:7px"><b>棋谱长度：</b>36步（12轮 × 3步）</div>';
      html+='<div style="display:flex;gap:8px;margin-top:10px"><button type="button" class="game-card" data-mode="playbook">♟ 36步棋谱</button><button type="button" class="game-card" data-mode="reasoning">🧠 为什么这样走</button></div>';
      html+='</div><div class="game-detail" style="display:none;margin-top:8px"></div></div>';
    });
    html+='</div></div>';
    html+=renderLibraryCoverage();
    app.innerHTML=html;
  }

  function rowHtml(x,r){
    var o=r.ours,t=r.threat,d=r.defend;
    var h='<div class="card" style="margin:0 0 10px;border-left:3px solid var(--accent)">';
    h+='<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap"><span class="tag">第'+r.round+'轮</span><b>'+esc(r.token)+'</b><span class="muted">阶段：'+esc(r.phase)+'</span></div>';
    h+='<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:10px">';
    h+='<div style="border:1px solid var(--border);padding:10px;border-radius:8px"><b>① 我方怎么走</b><div style="margin-top:5px"><span class="tag">'+esc(o.id)+'</span> '+esc(o.name)+'</div><div class="muted" style="margin-top:5px">'+esc(o.why)+'</div>';
    h+='<button type="button" class="action" data-open-type="'+esc(o.type)+'" data-open-id="'+esc(o.id)+'">查看原招式 →</button></div>';
    h+='<div style="border:1px solid var(--border);padding:10px;border-radius:8px"><b>② 对手怎么回应</b><div style="margin-top:5px">'+(t?'<span class="tag">'+esc(t.id)+'</span> '+esc(t.name):'未找到对手招式')+'</div><div class="muted" style="margin-top:5px">'+(t?esc(t.signal):'本轮无可用对手招式')+'</div><div class="muted" style="margin-top:5px">⚠️ 模拟假设：不是事实认定。</div>';
    if(t) h+='<button type="button" class="action" data-open-type="对手攻击" data-open-id="'+esc(t.id)+'">查看对手招式 →</button>';
    h+='</div>';
    h+='<div style="border:1px solid var(--border);padding:10px;border-radius:8px"><b>③ 我方如何应对</b><div style="margin-top:5px"><span class="tag">'+esc(d.id)+'</span> '+esc(d.name)+'</div><div class="muted" style="margin-top:5px">'+esc(d.why)+'</div>';
    h+='<button type="button" class="action" data-open-type="'+esc(d.type)+'" data-open-id="'+esc(d.id)+'">查看应对招式 →</button></div>';
    h+='</div><div class="notice" style="margin-top:10px"><b>下一轮：</b>'+esc(r.next)+'</div></div>';
    return h;
  }

  document.addEventListener('click',function(e){
    var b=e.target&&e.target.closest?e.target.closest('.game-card'):null;
    if(b){
      var wrap=b.closest('.game-wrap'),detail=wrap&&wrap.querySelector('.game-detail');
      if(!wrap||!detail)return;
      var id=wrap.getAttribute('data-game'),mode=b.getAttribute('data-mode');
      var H=lib('EA_HUMAN_BEHAVIOR_LIBRARY'),x0=null,idx=0;
      for(;idx<H.length;idx++)if(H[idx].id===id){x0=H[idx];break;}
      if(!x0)return;
      var x=build(idx,x0);
      detail.style.display='block';
      var h='<div class="card" style="margin:0;border-left:3px solid var(--accent)">';
      h+='<div class="label">'+esc(x.id)+' · '+esc(x.name)+'</div>';
      h+='<div style="margin-top:7px"><b>人格：</b>'+esc(x.signal)+'　<b>目标：</b>'+esc(x.goal)+'</div>';
      if(mode==='playbook'){
        h+='<div style="margin-top:12px"><b>连续博弈棋谱 · 36步</b></div>';
        h+='<div class="muted" style="margin:6px 0 12px">每轮都重新选择招式；不是固定 P01。你可以从上到下看“人格 → 我方 → 对手 → 我方应对 → 下一轮”。</div>';
        x.rounds.forEach(function(r){h+=rowHtml(x,r);});
      }else{
        h+='<div style="margin-top:10px;line-height:1.8"><b>人格为什么用这些招式？</b><br>';
        h+='系统先读取人格的行为序列，再把每一轮映射成增长推进、低成本试探、防守校验或防守反制。随后从正向招式库选择我方动作，从对手库生成“模拟响应”，再从机制库或正向库选择应对。下一轮的招式索引同时受到人格、轮次和位置影响，因此不会出现“12轮全部P01”的假棋谱。';
        h+='</div>';
        h+='<div class="notice" style="margin-top:10px"><b>验证原则：</b>对手动作只是模拟假设；真正运行时应把市场、流量、转化、库存、现金流和实际竞品信号作为反馈，再更新下一轮。</div>';
        h+='<div style="margin-top:10px"><b>本套棋谱36步的招式概览：</b></div>';
        h+='<div style="max-height:360px;overflow:auto;margin-top:6px">';
        x.rounds.forEach(function(r){
          h+='<div style="padding:6px 0;border-bottom:1px solid var(--border)">第'+r.round+'轮：'+esc(r.ours.id)+' '+esc(r.ours.name)+' → '+(r.threat?esc(r.threat.id)+' '+esc(r.threat.name):'无')+' → '+esc(r.defend.id)+' '+esc(r.defend.name)+'</div>';
        });
        h+='</div>';
      }
      h+='</div>';
      detail.innerHTML=h;
      detail.querySelectorAll('[data-open-id]').forEach(function(btn){
        btn.onclick=function(ev){
          ev.stopPropagation();
          window.__EA_OPEN_MOVE__={type:btn.getAttribute('data-open-type'),id:btn.getAttribute('data-open-id')};
          var v=btn.getAttribute('data-open-type')==='正向攻击'?'positive-attacks':btn.getAttribute('data-open-type')==='对手攻击'?'threats':'bug-attacks';
          state.view=v;location.hash=v;
        };
      });
      detail.scrollIntoView({behavior:'smooth',block:'nearest'});
      return;
    }
  },false);

  window.__EA_STRATEGY_CENTER_RENDER__=render;
  window.addEventListener('hashchange',function(){setTimeout(render,30);});
  setTimeout(render,50);
})();