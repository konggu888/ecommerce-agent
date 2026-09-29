(function(){
  'use strict';

  // 连贯式博弈棋谱：
  // 每个人格 = 一张连续棋谱；没有固定步数，最多40步。
  // 不是“凑40步”，而是：我方一招 → 对手一招 → 我方一招 → 对手一招……
  // 只有局面仍发生有意义的变化才继续；优势形成、僵持、路线失效或风险封顶时自然收束。
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
      turn:0,momentum:0,opponentMomentum:0,pressure:0,risk:0,information:0,resource:0,
      lastSide:'',lastMove:null,lastMode:'',lastDomain:'通用',lastIntensity:0,lastOutcome:'',
      personality:x,history:[],usedMoves:{},domainCooldown:{},domainChanges:0,staleMoves:0,
      meaningfulMoves:0,lastStateSignature:'',endReason:'',maxTurns:40
    };
  }

  function phaseFromState(s){
    if(s.risk>=7 || s.pressure>=8)return'防守/校验阶段';
    if(s.pressure>=5)return'对抗升级阶段';
    if(s.information<2 && s.turn<=4)return'观察试探阶段';
    if(s.momentum>=5 || s.opponentMomentum>=5)return'增长推进阶段';
    return'自适应调整阶段';
  }

  var MODES=['建设','防守','试探','竞争','诱导','转移','反制','机制校验','负向施压'];

  function modeOf(m){
    if(!m)return'试探';
    var s=((m.name||'')+' '+(m.category||'')+' '+(m.action||'')+' '+(m.defense||'')+' '+(m.mechanism||'')+' '+(m.signal||'')).toLowerCase();
    if(/机制|规则|状态机|api|权限|频控|同步|窗口|漏洞|异常检测|校验/.test(s))return'机制校验';
    if(/防守|防御|保护|止损|收缩|退出|降低暴露|隔离/.test(s))return'防守';
    if(/观察|测试|试探|反馈|测算|检测|搜索|小试|跟随|再试/.test(s))return'试探';
    if(/诱导|信号|逼迫回应|引导/.test(s))return'诱导';
    if(/转移|换战场|重新进入|渠道|迁移/.test(s))return'转移';
    if(/反制|报复|回应|反击|对冲|逆转/.test(s))return'反制';
    if(/竞争|扩大|扩张|抢占|压制|挤压|价格战|套利|份额|高强度/.test(s))return'竞争';
    if(/恶意|举报|投诉|低星|抄袭|造谣|点击|刷量|退款|扰动|污染|攻击|施压/.test(s))return'负向施压';
    return'建设';
  }

  function personalityWeights(x,state,side){
    var w={建设:1.15,防守:1,试探:1.05,竞争:1,诱导:1,转移:.95,反制:1,机制校验:.85,负向施压:.75};
    var raw=((x&&x.name)||'')+' '+((x&&x.style)||'')+' '+((x&&x.signal)||'')+' '+((x&&x.goal)||'')+' '+((x&&x.sequence)||[]).join(' ');
    function add(keys,vals){keys.forEach(function(k){if(raw.indexOf(k)>=0){for(var j=0;j<vals.length;j++)w[vals[j][0]]+=vals[j][1];}});}
    add(['正向','建设','长期','复利','份额','扩张'],[['建设',.9],['竞争',.35]]);
    add(['负向','施压','报复','强势','过度扩张','反扑'],[['负向施压',.9],['竞争',.45],['反制',.35]]);
    add(['观察','试探','信息','耐心','跟随','小动作'],[['试探',.8],['防守',.25],['诱导',.3]]);
    add(['防守','止损','收缩','保护'],[['防守',.9],['转移',.25]]);
    add(['机会','窗口','套利','先手'],[['转移',.35],['竞争',.4],['建设',.35]]);
    add(['诱导','信号','隐藏意图'],[['诱导',1],['试探',.4]]);
    add(['切换','混合','自适应','动态','多路径','策略更新'],[['转移',.55],['试探',.35],['反制',.35]]);
    add(['异常','机制','规则'],[['机制校验',.45],['防守',.25]]);
    if(side==='对手' && state.lastSide==='我方'){
      if(state.lastMode==='建设') { w.试探+=.35;w.竞争+=.25;w.防守+=.2;w.负向施压+=state.momentum>=4?.3:0; }
      if(state.lastMode==='负向施压') { w.防守+=.55;w.反制+=.65;w.负向施压+=.25; }
      if(state.lastMode==='防守') { w.建设+=.35;w.转移+=.3;w.试探+=.25; }
      if(state.lastMode==='试探') { w.试探+=.35;w.诱导+=.3; }
      if(state.lastMode==='竞争') { w.防守+=.3;w.竞争+=.35;w.反制+=.4; }
      if(state.lastMode==='机制校验') { w.机制校验+=.35;w.转移+=.3; }
    }
    if(side==='我方' && state.lastSide==='对手'){
      if(state.lastMode==='建设') { w.竞争+=.35;w.转移+=.3;w.试探+=.2; }
      if(state.lastMode==='负向施压') { w.防守+=.45;w.反制+=.6;w.机制校验+=.3; }
      if(state.lastMode==='防守') { w.建设+=.4;w.竞争+=.25;w.转移+=.25; }
      if(state.lastMode==='试探') { w.试探+=.35;w.建设+=.25; }
      if(state.lastMode==='竞争') { w.反制+=.45;w.防守+=.25;w.竞争+=.25; }
      if(state.lastMode==='机制校验') { w.机制校验+=.35;w.转移+=.3; }
    }
    if(state.pressure>=6){w.防守+=.5;w.反制+=.45;w.机制校验+=.35;}
    if(state.information<2){w.试探+=.5;w.诱导+=.2;}
    if(state.momentum>=5){w.建设+=.35;w.竞争+=.25;}
    if(state.risk>=7){w.防守+=.6;w.机制校验+=.55;w.负向施压-=.35;}
    MODES.forEach(function(k){w[k]=Math.max(.15,w[k]);});
    return w;
  }

  function movePool(){
    var out=[];
    lib('EA_POSITIVE_ATTACK_LIBRARY').forEach(function(m){if(m)out.push({m:m,kind:'正向攻击',source:'正向招式库'});});
    lib('EA_THREAT_LIBRARY').forEach(function(m){if(m)out.push({m:m,kind:'负向攻击面',source:'负向招式库'});});
    lib('EA_BUG_ATTACK_LIBRARY').forEach(function(m){if(m)out.push({m:m,kind:'机制型攻防',source:'机制型招式库'});});
    return out;
  }

  function candidateSpace(state,side){
    var weights=personalityWeights(state.personality,state,side), pool=movePool(), out=[];
    pool.forEach(function(z){
      if(!z.m || state.usedMoves[z.m.id])return;
      var mode=modeOf(z.m);
      if(mode==='机制校验' && state.risk<3 && state.pressure<4 && weights[mode]<1.4)return;
      var d=domain(z.m), score=weights[mode]*6, k=intensity(z.m);
      if(d===state.lastDomain)score-=6;
      if(state.domainCooldown[d]>0)score-=3;
      if(state.lastMode===mode)score-=1.2;
      if(side==='对手' && mode==='负向施压' && state.lastMode!=='负向施压' && state.pressure<3)score-=1.5;
      if(side==='我方' && mode==='负向施压' && state.pressure<4 && state.risk<5)score-=1.2;
      if(mode==='建设' && state.momentum>=7)score-=.5;
      if(mode==='防守' && state.pressure<=1 && state.risk<=2)score-=.5;
      score+=((d!==state.lastDomain)?1.5:0);
      score+=((k>=2 && state.turn>=6)?0.25:0);
      score+=((z.kind==='机制型攻防' && (state.pressure>=5||state.risk>=5))?1.5:0);
      score+=(Math.random()*.12);
      out.push({m:z.m,kind:z.kind,source:z.source,mode:mode,score:score});
    });
    out.sort(function(a,b){return b.score-a.score;});
    return out;
  }

  function pickCandidate(state,side){
    var c=candidateSpace(state,side);
    if(!c.length)return null;
    // 从最高分附近取一个，避免40套棋谱全部机械地走同一张牌。
    var top=Math.min(5,c.length), idx=0, best=-9999;
    for(var j=0;j<top;j++){
      var v=c[j].score + (j===0?0:.35*(top-j));
      if(v>best){best=v;idx=j;}
    }
    return c[idx];
  }

  function updateState(s,m,side){
    var d=domain(m), k=intensity(m), mode=modeOf(m);
    var beforeDomain=s.lastDomain, actor=side==='我方'?'our':'opp';
    var delta={momentum:0,opponentMomentum:0,pressure:0,risk:0,information:0,resource:0};
    if(mode==='建设'){
      delta[actor==='our'?'momentum':'opponentMomentum']+=k>=2?1:.7;
      delta.information+=.15; delta.resource+=Math.max(1,k);
      if(actor==='opp')delta.pressure+=.15;
    }else if(mode==='防守'){
      delta.pressure-=.8; delta.risk-=.35; delta.resource+=.5;
      if(actor==='opp')delta.opponentMomentum+=.2;
    }else if(mode==='试探'){
      delta.information+=1; delta.resource+=.5;
    }else if(mode==='竞争'){
      if(actor==='our'){delta.momentum+=.6;delta.pressure+=.35;}else{delta.opponentMomentum+=.7;delta.pressure+=.65;}
      delta.risk+=.35;delta.resource+=Math.max(1,k);
    }else if(mode==='诱导'){
      delta.information+=.8; delta.pressure+=actor==='opp'?.25:0; delta.resource+=.5;
    }else if(mode==='转移'){
      delta.information+=.4; delta.pressure-=.45; delta.resource+=.8;
    }else if(mode==='反制'){
      delta.pressure-=.75; delta.risk+=.45; delta.momentum+=actor==='our'?.55:0; delta.opponentMomentum+=actor==='opp'?.55:0;
      delta.resource+=Math.max(1,k);
    }else if(mode==='机制校验'){
      delta.information+=1.1; delta.risk+=.15; delta.pressure-=.25; delta.resource+=.7;
    }else if(mode==='负向施压'){
      delta.pressure+=actor==='our'?.8:1.05; delta.risk+=.75; delta.resource+=Math.max(1,k);
      if(actor==='our')delta.momentum-=.15;else delta.opponentMomentum+=.35;
    }
    Object.keys(delta).forEach(function(key){s[key]=Math.max(0,s[key]+delta[key]);});
    s.lastSide=side;s.lastMove=m;s.lastMode=mode;s.lastDomain=d;s.lastIntensity=k;s.turn++;
    s.history.push({side:side,id:m&&m.id,name:m&&m.name,kind:m&&m.kind,mode:mode,domain:d,intensity:k});
    if(d!==beforeDomain)s.domainChanges++;
    s.domainCooldown[d]=2;
    Object.keys(s.domainCooldown).forEach(function(k2){
      if(k2!==d)s.domainCooldown[k2]=Math.max(0,(s.domainCooldown[k2]||0)-1);
    });
    if(m&&m.id)s.usedMoves[m.id]=1;
    return delta;
  }

  function unused(pool,used){
    return pool.filter(function(m){return m && !used[m.id];});
  }

  // 兼容旧调用入口，但实际选牌已经统一进入“共享战略空间”。
  function getPositivePool(i,step,state){
    var z=pickCandidate(state,'我方');
    return z?z.m:null;
  }

  function chooseOur(i,step,state){
    var z=pickCandidate(state,'我方');
    if(!z)return null;
    return {id:z.m.id,name:z.m.name,kind:z.kind,mode:z.mode,role:'我方',source:z.m,
      reason:'人格倾向 + 当前局面 + 对手上一手共同决定动作；我方不再被固定限制为正向招式。'};
  }

  function chooseOpponent(i,step,state){
    var z=pickCandidate(state,'对手');
    if(!z)return null;
    return {id:z.m.id,name:z.m.name,kind:z.kind,mode:z.mode,role:'对手（模拟）',source:z.m,
      reason:'对手共享全部战略动作空间；下一手根据我方上一手、累计压力、风险与人格倾向选择，不再固定等于负向攻击。'};
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
    if(b.length && (state.risk>=7 || state.pressure>=8)){
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

  function stateSignature(s){
    return [Math.round(s.pressure),Math.round(s.risk),Math.round(s.momentum),Math.round(s.opponentMomentum),Math.round(s.information),s.lastMode,s.lastDomain].join('|');
  }

  function evaluateMoveChange(before,after,state,move){
    var delta=Math.abs(after.pressure-before.pressure)+Math.abs(after.risk-before.risk)+
      Math.abs(after.momentum-before.momentum)+Math.abs(after.opponentMomentum-before.opponentMomentum)+
      Math.abs(after.information-before.information);
    var changedDomain=before.lastDomain!==after.lastDomain;
    var changedMode=before.lastMode!==after.lastMode;
    var meaningful=delta>=0.55 || changedDomain || changedMode || intensity(move)>=2;
    if(meaningful){state.meaningfulMoves++;state.staleMoves=0;}
    else state.staleMoves++;
    return {meaningful:meaningful,delta:delta,changedDomain:changedDomain,changedMode:changedMode};
  }

  function shouldEnd(state, stepNo, change){
    // 前6步用于建立基本局面，避免开局过早结束。
    if(stepNo<6)return null;
    if(state.risk>=10)return '风险达到封顶：进入防守/校验收束';
    if(state.pressure>=11 && state.momentum<=1)return '对手压力持续累积：进入防守收束';
    if(state.momentum>=9 && state.pressure<=3 && state.information>=5)return '我方优势已形成：进入成果兑现收束';
    if(state.staleMoves>=2)return '连续两手没有产生足够新的有效变量：停止硬凑步数';
    if(state.domainChanges>=8 && state.pressure<=2 && state.risk<=3)return '主要竞争变量已经轮换完成：进入复盘收束';
    if(stepNo>=state.maxTurns)return '达到安全上限：进入复盘（40步只是上限，不是目标）';
    return null;
  }

  function shouldEnd(state, stepNo, change){
    if(stepNo<6)return null;
    if(state.risk>=10)return '风险达到封顶：进入防守/校验收束';
    if(state.pressure>=11 && state.momentum<=1 && state.opponentMomentum>=5)return '对手优势持续累积：进入防守收束';
    if(state.momentum>=9 && state.opponentMomentum<=3 && state.pressure<=3 && state.information>=5)return '我方优势已形成：进入成果兑现收束';
    if(state.opponentMomentum>=9 && state.momentum<=3 && state.pressure>=8)return '对手优势已形成：进入防守/复盘收束';
    if(state.staleMoves>=2)return '连续两手没有产生足够新的有效变量：停止硬凑步数';
    if(state.domainChanges>=8 && state.pressure<=2 && state.risk<=3)return '主要竞争变量已经轮换完成：进入复盘收束';
    if(stepNo>=state.maxTurns)return '达到安全上限：进入复盘（40步只是上限，不是目标）';
    return null;
  }

  function build(i,x){
    var seq=Array.isArray(x.sequence)&&x.sequence.length?x.sequence:['自适应'];
    var steps=[], state=initialState(i,x);
    for(var n=1;n<=state.maxTurns;n++){
      var phase=phaseFromState(state), m=(n%2===1)?chooseOur(i,n,state):chooseOpponent(i,n,state);
      if(!m){state.endReason='当前没有足够新的未使用有效招式：自然结束';break;}
      var before={
        pressure:state.pressure,risk:state.risk,momentum:state.momentum,
        opponentMomentum:state.opponentMomentum,information:state.information,
        lastDomain:state.lastDomain,lastMode:state.lastMode
      };
      updateState(state,m,n%2?'我方':'对手');
      var after={
        pressure:state.pressure,risk:state.risk,momentum:state.momentum,
        opponentMomentum:state.opponentMomentum,information:state.information,
        lastDomain:state.lastDomain,lastMode:state.lastMode
      };
      var change=evaluateMoveChange(before,after,state,m), endReason=shouldEnd(state,n,change);
      if(endReason)state.endReason=endReason;
      var deltaText=[];
      if(before.lastDomain!==after.lastDomain)deltaText.push('战场从'+before.lastDomain+'切换到'+after.lastDomain);
      if(after.pressure>before.pressure+.1)deltaText.push('对抗压力上升');
      if(after.pressure<before.pressure-.1)deltaText.push('对抗压力下降');
      if(after.risk>before.risk+.1)deltaText.push('风险上升');
      if(after.momentum>before.momentum+.1)deltaText.push('我方动能增加');
      if(after.momentum<before.momentum-.1)deltaText.push('我方动能下降');
      if(after.opponentMomentum>before.opponentMomentum+.1)deltaText.push('对手动能增加');
      if(after.opponentMomentum<before.opponentMomentum-.1)deltaText.push('对手动能下降');
      if(after.information>before.information+.1)deltaText.push('信息量增加');
      if(!deltaText.length)deltaText.push('局面变化有限，下一手需寻找新的有效变量');
      steps.push({
        no:n,side:n%2?'我方':'对手',role:m.role,token:seq[mod(n-1,seq.length)],
        phase:phase,move:m,stateBefore:before,stateAfter:after,stateDelta:deltaText.join('；'),
        meaningful:change.meaningful,
        response:endReason?'本局在本手后自然收束：'+endReason:
          (n%2===1?'我方出牌后，对手读取本手的战略动作、领域、强度和累计状态再响应。':
          '对手刚刚出牌，我方读取其动作及局面变化后再调整。')
      });
      if(endReason)break;
    }
    if(!state.endReason)state.endReason='达到默认安全上限：进入复盘';
    return {
      id:x.id,name:x.name,style:x.style||'',risk:x.risk||'中',signal:x.signal||'',goal:x.goal||'',
      sequence:seq,steps:steps,endReason:state.endReason,meaningfulMoves:state.meaningfulMoves
    };
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
    html+='<div class="subtitle">40种行为人格 · 每个人格一张连续棋谱 · 自然收束 · 三大招式库混合使用</div>';
    html+='<div class="card" style="margin:10px 0 16px;border-left:4px solid var(--accent);background:rgba(255,180,0,.06)"><b>棋谱规则</b><div style="font-size:16px;line-height:1.7;margin-top:6px">';
    html+='不是“我方三步/一轮就结束”，也不是为了凑固定步数。每一套人格是一条完整连续链：<b>我方第1招 → 对手第2招 → 我方第3招 → 对手第4招 → ……</b>，最多40步。';
    html+='三大招式库不再按阵营分配：我方和对手都可以使用建设、防守、试探、竞争、诱导、转移、反制、机制校验、负向施压九类战略动作；人格只改变权重，上一招与累计状态决定下一招。只有局面继续产生有效变化才继续；优势形成、僵持、路线失效或风险封顶时自然收束。对手招式是模拟假设，机制型招式用于识别、校验、隔离和防守。';
    html+='</div></div>';
    html+='<div class="card"><div class="label">40套连续博弈棋谱</div><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:10px;margin-top:12px">';
    H.forEach(function(x,i){
      html+='<div class="game-wrap" data-game="'+esc(x.id)+'"><div class="card"><span class="tag">'+esc(x.id)+'</span><b style="display:block;margin-top:7px">'+esc(x.name)+'</b>';
      html+='<div class="muted" style="margin-top:5px">模式：'+esc(x.style)+' · '+esc(x.risk)+'风险</div><div style="margin-top:5px">信号：'+esc(x.signal)+'</div>';
      html+='<div style="margin-top:5px"><b>人格序列：</b>'+esc((x.sequence||[]).join(' → '))+'</div>';
      html+='<div style="margin-top:7px"><b>连续长度：</b>自然收束，最多40步（40只是上限）</div>';
      html+='<div style="display:flex;gap:8px;margin-top:10px"><button type="button" class="game-card" data-mode="playbook">♟ 查看连续棋谱</button><button type="button" class="game-card" data-mode="reasoning">🧠 查看人格逻辑</button></div></div><div class="game-detail" style="display:none;margin-top:8px"></div></div>';
    });
    html+='</div></div>'+coverage();
    app.innerHTML=html;
  }

  function stepHtml(s){
    var m=s.move;
    var border=m.mode==='建设'?'var(--accent)':m.mode==='负向施压'?'#b44':m.mode==='机制校验'?'#777':'#777';
    var h='<div class="card" style="margin:0 0 8px;border-left:4px solid '+border+'">';
    h+='<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap"><span class="tag">第'+s.no+'步</span><b>'+esc(s.side)+'</b><span class="tag">'+esc(m.kind)+'</span><span class="muted">'+esc(s.phase)+'</span></div>';
    h+='<div style="font-size:17px;margin-top:7px"><span class="tag">'+esc(m.id)+'</span> <b>'+esc(m.name)+'</b></div>';
    h+='<div class="muted" style="margin-top:5px">'+esc(m.reason)+'</div>';
    if(m.source){
      h+='<div class="muted" style="margin-top:4px">战略动作：'+esc(m.mode||'自适应')+' · 原招式库：'+esc(m.kind)+' · 原定义：'+esc(m.source.action||m.source.defense||m.source.mechanism||m.source.signal||'')+'</div>';
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
      h+='<div style="margin-top:12px"><b>一条连续棋谱 · '+data.steps.length+'步自然收束</b></div>';
      h+='<div class="muted" style="margin:5px 0 12px">注意：这里是“连续交锋”，不是每三步重新开始，也不是硬凑40步。40步只是安全上限，局面达到结束条件会提前停止。</div>';
      data.steps.forEach(function(s){h+=stepHtml(s);});
      h+='<div class="notice" style="margin-top:10px"><b>本局收束：</b>'+esc(data.endReason)+' · 有效局面变化 '+data.meaningfulMoves+' 次</div>';
    }else{
      h+='<div style="margin-top:10px;line-height:1.8"><b>这个人格为什么这样走？</b><br>';
      h+='人格序列只负责定义长期行为倾向；真正的棋谱由连续状态驱动。奇数步是我方，偶数步是对手。三类招式不是按阵营锁死的：双方都能从同一战略空间选牌；建设、防守、试探、竞争、诱导、转移、反制、机制校验、负向施压只是战略动作类型。人格改变各类型权重，局面决定下一手。';
      h+='</div><div class="notice" style="margin-top:10px"><b>关键：</b>不是“我方随便打一张牌、对手随机出大招”。下一手必须读取上一手的领域、强度和累计状态；对手强度有上限，只有压力累积后才允许升级。实际系统运行时，再把真实市场反馈替换“模拟假设”。</div>';
      h+='<div style="margin-top:10px"><b>连续战略动作轨迹：</b><div style="line-height:2;margin-top:5px">';
      data.steps.forEach(function(s){h+='<span class="tag" style="margin:2px">'+s.no+' '+esc(s.move.mode||'自适应')+'</span>';});
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