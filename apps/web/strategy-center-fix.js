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

  function findMove(arr,id){
    for(var j=0;j<arr.length;j++) if(arr[j] && arr[j].id===id) return arr[j];
    return null;
  }

  // 连续博弈不是“随机抽牌”：后一手必须能解释为对前一手的回应。
  // 这里把三类招式放进同一个状态机：
  // 我方动作 -> 对手根据动作强度/领域回应 -> 我方根据回应调整 -> ...
  // 对手越界升级只在压力、风险和前序信号累积后才允许出现。

  function intensity(m){
    if(!m)return 0;
    var s=(m.name||'')+' '+(m.category||'')+' '+(m.signal||'');
    if(/组合式|强|报复|集中|持续|大幅|抢|恶意组合/.test(s))return 3;
    if(/升级|扩大|压制|竞争|挤压|套利|异常|投诉|举报|低星|价格战/.test(s))return 2;
    if(/观察|跟随|小试|内容|长尾|优化|服务|测试|检测|验证/.test(s))return 0;
    return 1;
  }

  function domain(m){
    if(!m)return'通用';
    var s=(m.name||'')+' '+(m.category||'');
    if(/关键词|搜索|SEO|流量|点击/.test(s))return'流量';
    if(/评价|口碑|UGC|内容|视频|直播|达人|舆情/.test(s))return'内容口碑';
    if(/价格|优惠|套餐|SKU|成本/.test(s))return'价格商品';
    if(/供应|物流|履约|库存/.test(s))return'供应链履约';
    if(/品牌|商标|版权|专利|授权/.test(s))return'品牌知识产权';
    if(/客服|售后|退款|退货|支付|订单/.test(s))return'交易服务';
    if(/机制|账号|平台|规则|API|状态/.test(s))return'机制';
    return'通用';
  }

  function initialState(i,x){
    return {
      turn:0,
      momentum:0,
      pressure:0,
      risk:0,
      information:0,
      resource:0,
      lastSide:'',
      lastMove:null,
      lastDomain:'通用',
      lastIntensity:0,
      lastOutcome:'',
      personality:x,
      history:[],
      usedOur:{},usedThreat:{},usedBug:{}
    };
  }

  function phaseFromState(s){
    if(s.risk>=7 || s.pressure>=8)return'防守/校验阶段';
    if(s.pressure>=5)return'对抗升级阶段';
    if(s.information<2 && s.turn<=4)return'观察试探阶段';
    if(s.momentum>=5)return'增长推进阶段';
    return'自适应调整阶段';
  }

  function updateState(s,m,side){
    var d=domain(m), k=intensity(m);
    if(side==='我方'){
      s.momentum += k>=2?1:0.6;
      s.information += /观察|测试|内容|评价|检测|搜索/.test((m&&m.name)||'')?1:0.2;
      s.resource += k;
      s.pressure = Math.max(0,s.pressure-0.3);
      if(k>=3)s.risk+=1;
    }else{
      s.pressure += k*1.2;
      s.risk += k>=2?0.8:0.2;
      s.momentum = Math.max(0,s.momentum-0.5);
      s.information += 0.3;
      s.resource += k;
    }
    s.lastSide=side;
    s.lastMove=m;
    s.lastDomain=d;
    s.lastIntensity=k;
    s.turn++;
    s.history.push({side:side,id:m&&m.id,name:m&&m.name,domain:d,intensity:k});
    if(m&&m.id){if(m.kind==='正向攻击')s.usedOur[m.id]=1;else if(m.kind==='负向攻击面')s.usedThreat[m.id]=1;else s.usedBug[m.id]=1;}
  }

  function unused(pool,used){
    return pool.filter(function(m){return m && !used[m.id];});
  }

  function pickByScore(pool,used,preferredDomains,preferredIds,state){
    var candidates=unused(pool,used);
    if(!candidates.length)return null;
    var best=null,bestScore=-9999;
    candidates.forEach(function(m,idx){
      var score=0,d=domain(m),k=intensity(m);
      if(preferredIds&&preferredIds.indexOf(m.id)>=0)score+=8;
      if(preferredDomains&&preferredDomains.indexOf(d)>=0)score+=5;
      // 不允许连续重复领域，否则棋谱会变成“同一问题来回打”。
      if(state.lastDomain===d)score-=3;
      // 随着博弈推进，逐渐转向新的变量；不是永远盯着第一张牌。
      score += Math.min(state.information,6)*((d!==state.lastDomain)?0.8:0);
      score -= Math.abs(k-Math.min(3,Math.floor(state.turn/6)))*0.7;
      score += ((idx+state.turn)%7)*0.01;
      if(score>bestScore){bestScore=score;best=m;}
    });
    return best;
  }

  function getPositivePool(i,step,state){
    var a=lib('EA_POSITIVE_ATTACK_LIBRARY');
    if(!a.length)return null;
    var prev=state.lastMove, pd=state.lastDomain;
    var domains=[], ids=[];
    if(state.turn===0){
      // 首手只能从低成本、可验证路线开始。
      ids=['P02','P03','P12','P15','P25','P43','P49'];
    }else if(prev && state.lastSide==='对手'){
      // 我方读取对手刚刚打击的变量，但不能原地重复。
      if(pd==='流量') {domains=['流量','内容口碑','渠道增长'];ids=['P02','P22','P25','P31','P45'];}
      else if(pd==='价格商品') {domains=['商品策略','经营效率','产品策略'];ids=['P14','P15','P37','P38','P43'];}
      else if(pd==='内容口碑') {domains=['内容增长','信任增长','品牌增长'];ids=['P06','P07','P10','P39','P46'];}
      else if(pd==='供应链履约') {domains=['供应链','服务竞争','经营效率'];ids=['P19','P35','P36','P47'];}
      else if(pd==='品牌知识产权') {domains=['品牌增长','信任增长','产品策略'];ids=['P09','P10','P11','P26'];}
      else if(pd==='交易服务') {domains=['服务竞争','用户增长','经营效率'];ids=['P20','P21','P27','P28'];}
      else if(pd==='机制') {domains=['信任增长','经营效率','博弈增长'];ids=['P39','P43','P44','P49'];}
    }
    var z=pickByScore(a,state.usedOur,domains,ids,state);
    if(z)return z;
    return pickByScore(a,state.usedOur,['流量','内容增长','商品策略','产品策略'],[],state);
  }

  function chooseOur(i,step,state){
    var p=getPositivePool(i,step,state), b=lib('EA_BUG_ATTACK_LIBRARY');
    var phase=phaseFromState(state);
    // 机制型不是“补步数”的普通牌：只有异常持续/风险累积才进入棋谱。
    if(b.length && !state.usedBug && (state.risk>=7 || state.pressure>=8)){
      var bm=pickByScore(b,state.usedBug,['机制'],[],state);
      if(bm)return {id:bm.id,name:bm.name,kind:'机制型攻防',role:'我方',source:bm,
        reason:'压力/风险已累积到阈值，本手先处理异常与可验证性，而不是继续无条件扩张。'};
    }
    return p?{id:p.id,name:p.name,kind:'正向攻击',role:'我方',source:p,
      reason:state.turn===0?'首手只建立一个可验证变量，先观察真实反馈。':
      '读取对手上一手后切换到新的相关变量；已经使用过的招式不会再次拿来凑步数。'}:null;
  }

  function chooseOpponent(i,step,state){
    var t=lib('EA_THREAT_LIBRARY'), b=lib('EA_BUG_ATTACK_LIBRARY');
    if(!t.length&&!b.length)return null;
    var our=state.lastMove, d=domain(our), ourI=intensity(our);
    var map={
      '流量':{domains:['广告竞争','流量攻击','内容竞争'],ids:['T19','T18','T17','T26']},
      '内容口碑':{domains:['口碑与评价','舆情风险','内容竞争'],ids:['T01','T09','T25','T29','T08']},
      '价格商品':{domains:['价格竞争','交易风险'],ids:['T20','T21','T16']},
      '供应链履约':{domains:['供应链竞争','运营竞争'],ids:['T23','T24','T22']},
      '品牌知识产权':{domains:['知识产权','品牌安全','渠道风险'],ids:['T03','T04','T05','T31','T32']},
      '交易服务':{domains:['交易风险','平台治理','客户关系'],ids:['T13','T14','T12','T15','T10']},
      '机制':{domains:['平台治理','流量攻击','交易风险'],ids:['T39','T17','T16']},
      '通用':{domains:['价格竞争','内容竞争','平台治理'],ids:['T21','T19','T25']}
    };
    var m=map[d]||map['通用'];

    // 强度随博弈阶段上升，但每一手仍必须换牌、换变量。
    var ceiling=1;
    if(ourI>=2 || state.momentum>=4)ceiling=2;
    if(state.pressure>=6 || state.risk>=6)ceiling=3;

    var candidates=unused(t,state.usedThreat).filter(function(z){return intensity(z)<=ceiling;});
    var chosen=pickByScore(candidates,{},m.domains,m.ids,state);
    if(chosen)return {id:chosen.id,name:chosen.name,kind:'负向攻击面',role:'对手（模拟）',source:chosen,
      reason:'对手读取我方上一手的“'+d+'”变量后改变攻击面；同一招不会反复使用，强度也受当前累计压力限制。'};

    // 只有在风险已经明显累积时，机制型响应才允许进入。
    if(b.length && state.risk>=7){
      var bm=pickByScore(b,state.usedBug,['机制'],[],state);
      if(bm)return {id:bm.id,name:bm.name,kind:'机制型攻防',role:'对手（模拟）',source:bm,
        reason:'累计异常已经达到高风险区，模拟对手转向机制层响应；这是防御性假设，不是漏洞操作。'};
    }

    // 当前领域没有合适牌时，明确“换战场”，而不是重复上一张。
    var fallback=unused(t,state.usedThreat).filter(function(z){return intensity(z)<=ceiling;});
    if(fallback.length){
      var f=pickByScore(fallback,state.usedThreat,['价格竞争','内容竞争','平台治理','交易风险'],[],state);
      if(f)return {id:f.id,name:f.name,kind:'负向攻击面',role:'对手（模拟）',source:f,
        reason:'当前领域没有可升级的未使用招式，对手因此转向另一个竞争变量；不重复旧牌。'};
    }
    return null;
  }

  function build(i,x){
    var seq=Array.isArray(x.sequence)&&x.sequence.length?x.sequence:['正向'];
    var steps=[], state=initialState(i,x);
    for(var n=1;n<=40;n++){
      // 人格序列现在只作为“偏好权重”，不再直接决定抽哪张牌。
      // 真正决定下一手的是上一手、累积压力、风险、信息和资源状态。
      var phase=phaseFromState(state), m;
      if(n%2===1)m=chooseOur(i,n,state);
      else m=chooseOpponent(i,n,state);
      if(!m)break;

      var before={pressure:state.pressure,risk:state.risk,momentum:state.momentum,information:state.information};
      updateState(state,m,n%2?'我方':'对手');
      var after={pressure:state.pressure,risk:state.risk,momentum:state.momentum,information:state.information};

      steps.push({
        no:n,side:n%2?'我方':'对手',role:m.role,
        token:seq[mod(n-1,seq.length)],
        phase:phase,move:m,
        stateBefore:before,stateAfter:after,
        response:n===40?'本局结束：进入复盘。':
          (n%2===1?'我方出牌后，对手只能根据这张牌及当前累积状态作出下一手模拟响应。':
          '对手刚刚出牌，我方下一手必须读取这次压力变化后再调整。')
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
    if(s.stateBefore&&s.stateAfter){h+='<div class="muted" style="margin-top:5px">状态：压力 '+s.stateBefore.pressure.toFixed(1)+' → '+s.stateAfter.pressure.toFixed(1)+' · 风险 '+s.stateBefore.risk.toFixed(1)+' → '+s.stateAfter.risk.toFixed(1)+' · 动能 '+s.stateBefore.momentum.toFixed(1)+' → '+s.stateAfter.momentum.toFixed(1)+'</div>';}
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
      h+='人格序列只负责定义长期行为倾向；真正的棋谱由连续状态驱动。奇数步是我方，偶数步是对手。三类招式不是三条互相独立的棋谱，而是同一条链里的不同类型：正向攻击用于建设优势，负向攻击面必须针对我方上一手作出渐进式回应，机制型攻防只在异常、压力或风险累积后介入。';
      h+='</div><div class="notice" style="margin-top:10px"><b>关键：</b>不是“我方随便打一张牌、对手随机出大招”。下一手必须读取上一手的领域、强度和累计状态；对手强度有上限，只有压力累积后才允许升级。实际系统运行时，再把真实市场反馈替换“模拟假设”。</div>';
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