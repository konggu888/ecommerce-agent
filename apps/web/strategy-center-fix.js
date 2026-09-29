(function(){
  'use strict';

  // 连贯式博弈棋谱：
  // 每个人格 = 一张连续棋谱；没有固定步数，最多40步。
  // 不是“凑40步”，而是：我方一招 → 对手一招 → 我方一招 → 对手一招……
  // 只有局面仍发生有意义的变化才继续；优势形成、僵持、路线失效或风险封顶时自然收束。
  // 三大招式库不按阵营分配：双方共享九类战略动作，由人格、上一招、累计状态和市场反馈共同决定下一招。
  // 商品基础建设完成不等于配置正确；初始配置是复制式基线，后续通过反馈诊断持续纠偏。
  // 所有对手动作均为模拟假设；机制型招式用于识别、校验、隔离和防守，不提供真实漏洞利用步骤。

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
      turn:0,momentum:0,opponentMomentum:0,pressure:0,risk:0,information:7,resource:0,
      lastSide:'',lastMove:null,lastMode:'',lastDomain:'通用',lastIntensity:0,lastOutcome:'',
      // 商品进入博弈前，默认已经完成基础商品建设；博弈从“上线后竞争”开始，而不是从“什么都没做”开始。
      productBaseline:{
        title:{done:true,source:'热门标题/竞争对手关键词'},
        mainImage:{done:true,source:'热门商品与竞争对手主图结构'},
        detail:{done:true,source:'商品卖点、规格、场景与对比信息'},
        reviews:{done:true,count:5,type:'真实正向反馈，不以刷评作为假设'},
        video:{done:true,source:'商品视频介绍'},
        qa:{done:true,source:'问大家/常见问题'},
        seeding:{done:true,source:'内容种草/场景传播'}
      },
      knownSignals:['标题已按市场热门与竞品关键词完成','主图已参考竞争环境完成','详情页已完成','已有5条正向真实评价作为基础反馈','商品视频已完成','问大家已完成','种草内容已完成'],
      unknownSignals:['点击率','转化率','自然流量规模','搜索词实际分布','竞品即时动作','内容扩散效率'],
      productVariables:{
        title:{version:1,confidence:0.35,needsReview:true},
        longTailKeywords:{version:1,confidence:0.2,needsReview:true},
        mainImage:{version:1,confidence:0.35,needsReview:true},
        detail:{version:1,confidence:0.35,needsReview:true},
        video:{version:1,confidence:0.35,needsReview:true},
        qa:{version:1,confidence:0.35,needsReview:true},
        seeding:{version:1,confidence:0.3,needsReview:true},
        reviews:{version:1,confidence:0.45,needsReview:false}
      },
      feedback:{ctr:null,conversion:null,organicTraffic:null,searchTerms:null,competitorMoves:null,contentSpread:null},
      productHistory:[],

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

  function diagnoseProduct(state){
    var f=state.feedback||{}, d=[];
    if(f.searchTerms!==null && f.searchTerms<.8)d.push({key:'longTailKeywords',label:'长尾关键词/搜索匹配',why:'搜索词匹配反馈偏弱'});
    if(f.ctr!==null && f.ctr<.8)d.push({key:'mainImage',label:'主图/标题点击表达',why:'曝光后的点击反馈偏弱'});
    if(f.conversion!==null && f.conversion<.8)d.push({key:'detail',label:'详情页/卖点承接',why:'点击后的转化反馈偏弱'});
    if(f.contentSpread!==null && f.contentSpread<.8)d.push({key:'seeding',label:'视频/种草内容',why:'内容扩散反馈偏弱'});
    if(f.competitorMoves!==null && f.competitorMoves>.7)d.push({key:'competition',label:'竞争变量',why:'对手动作频繁，需要重新观察竞争变量'});
    return d;
  }

  function candidateSpace(state,side){
    var weights=personalityWeights(state.personality,state,side), pool=movePool(), out=[], diagnoses=diagnoseProduct(state);
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
      // 商品已上线但初始配置来自热门/竞品复制；后续博弈可以继续纠偏，不把“已完成”当成“不可修改”。
      var ms=(z.m.name||'')+' '+(z.m.action||'')+' '+(z.m.signal||'');
      if(side==='我方' && /关键词|长尾|搜索/.test(ms)){
        if(state.productVariables.longTailKeywords.needsReview)score+=2.2;
        if(state.feedback.ctr!==null && state.feedback.ctr<0.8)score+=1.4;
      }
      if(side==='我方' && /主图/.test(ms)){
        if(state.feedback.ctr!==null && state.feedback.ctr<0.85)score+=2.5;
      }
      if(side==='我方' && /详情|FAQ|卖点|痛点/.test(ms)){
        if(state.feedback.conversion!==null && state.feedback.conversion<0.85)score+=2.4;
      }
      if(side==='我方' && /视频|UGC|种草|内容/.test(ms)){
        if(state.feedback.contentSpread!==null && state.feedback.contentSpread<0.85)score+=1.8;
      }
      // 反馈诊断优先于人格偏好：棋谱先解决已经暴露的问题，再谈风格。
      if(side==='我方' && diagnoses.length){
        var targetText=ms;
        diagnoses.forEach(function(di){
          var hit=(di.key==='longTailKeywords'&&/关键词|长尾|搜索/.test(targetText)) ||
                  (di.key==='mainImage'&&/主图|标题/.test(targetText)) ||
                  (di.key==='detail'&&/详情|FAQ|卖点|痛点/.test(targetText)) ||
                  (di.key==='seeding'&&/视频|UGC|种草|内容/.test(targetText));
          if(hit)score+=3.2;
        });
      }
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
    // 把“出招”真正映射到商品变量：已上线不等于固定，博弈可以持续修改初始复制配置。
    var nm=(m&&m.name)||'', ac=(m&&m.action)||'';
    function revise(key,boost){
      if(!s.productVariables[key])return;
      s.productVariables[key].version++;
      s.productVariables[key].confidence=Math.min(1,s.productVariables[key].confidence+boost);
      s.productVariables[key].needsReview=false;
    }
    if(side==='我方'){
      if(/核心关键词|关键词重构|长尾关键词/.test(nm+' '+ac)){
        revise('title',.12);revise('longTailKeywords',.18);
        s.feedback.searchTerms=Math.min(1.2,(s.feedback.searchTerms===null?.35:s.feedback.searchTerms)+.12);
        s.feedback.ctr=Math.min(1.2,(s.feedback.ctr===null?.55:s.feedback.ctr)+.06);
      }
      if(/主图/.test(nm+' '+ac)){
        revise('mainImage',.16);
        s.feedback.ctr=Math.min(1.2,(s.feedback.ctr===null?.55:s.feedback.ctr)+.1);
      }
      if(/详情|FAQ|卖点|痛点/.test(nm+' '+ac)){
        revise('detail',.15);
        s.feedback.conversion=Math.min(1.2,(s.feedback.conversion===null?.5:s.feedback.conversion)+.09);
      }
      if(/视频|UGC|种草|内容/.test(nm+' '+ac)){
        revise('video',.12);revise('seeding',.12);
        s.feedback.contentSpread=Math.min(1.2,(s.feedback.contentSpread===null?.5:s.feedback.contentSpread)+.1);
      }
    }
    // 对手动作也会改变反馈环境：不是“真实数据”，而是连续棋谱中的模拟市场反馈。
    if(side==='对手'){
      if(/关键词|搜索/.test(nm+' '+ac))s.feedback.ctr=Math.max(.15,(s.feedback.ctr===null?.55:s.feedback.ctr)-.06);
      if(/主图|点击/.test(nm+' '+ac))s.feedback.ctr=Math.max(.15,(s.feedback.ctr===null?.55:s.feedback.ctr)-.07);
      if(/价格|竞争|压制/.test(nm+' '+ac))s.feedback.conversion=Math.max(.15,(s.feedback.conversion===null?.5:s.feedback.conversion)-.05);
      if(/内容|视频|种草/.test(nm+' '+ac))s.feedback.contentSpread=Math.max(.15,(s.feedback.contentSpread===null?.5:s.feedback.contentSpread)-.06);
      s.feedback.competitorMoves=Math.min(1.2,(s.feedback.competitorMoves===null?.35:s.feedback.competitorMoves)+.1);
    }
    // 每次变量变化都留下版本记录，棋谱才能解释“为什么又改了一次”。
    var touched=[];
    if(/关键词|搜索/.test(nm+' '+ac))touched.push('长尾关键词/标题');
    if(/主图/.test(nm+' '+ac))touched.push('主图');
    if(/详情|FAQ|卖点|痛点/.test(nm+' '+ac))touched.push('详情页');
    if(/视频|UGC/.test(nm+' '+ac))touched.push('商品视频');
    if(/种草|内容/.test(nm+' '+ac))touched.push('种草内容');
    if(touched.length)s.productHistory.push({turn:s.turn+1,side:side,move:nm,variables:touched});
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
  // 统一选牌入口：我方与对手共享三大招式库，不再按阵营锁死。
  function getPositivePool(i,step,state){
    var z=pickCandidate(state,'我方');
    return z?z.m:null;
  }

  function buildMoveReason(state,z,side){
    var m=z.m, last=state.lastMove, parts=[];
    var ms=(m.name||'')+' '+(m.action||'')+' '+(m.signal||'');

    // 棋盘解释统一使用人话：发生了什么 → 看到了什么 → 为什么这么做 → 影响什么 → 下一步看什么。
    if(side==='对手'){
      if(last) parts.push('我方刚才做了“'+(last.name||'未知')+'”。');
      else parts.push('这是开局，对手先根据当前市场情况做出第一步动作。');

      var reason='';
      if(z.mode==='试探'){
        reason=state.information<3
          ?'对手现在还不知道我方会怎么应对，所以先做一个小动作，看看我方和市场会有什么反应。'
          :'对手已经看到一些信号，但还不能确定结果，所以再试一次，确认我方会不会改变路线。';
      }else if(z.mode==='建设'){
        reason=state.opponentMomentum>=5
          ?'对手发现自己的这条路线已经有一些效果，所以继续加强，看看能不能把优势扩大。'
          :'对手认为这条路线值得继续做，所以先把自己的商品、流量或内容做好，再和我方继续竞争。';
      }else if(z.mode==='防守'){
        reason=state.pressure>=5||state.risk>=5
          ?'对手感觉现在的竞争压力已经比较大，所以先减少风险，不急着继续加码。'
          :'对手暂时没有必要硬碰硬，所以先守住现有流量和资源。';
      }else if(z.mode==='竞争'){
        reason=state.pressure>=4
          ?'双方已经在争同一块市场，对手看到我方正在抢，所以也开始加力争夺。'
          :'对手发现这里有机会，准备和我方直接争流量、价格、内容或其他关键位置。';
      }else if(z.mode==='诱导'){
        reason='对手暂时不想直接暴露真实意图，所以先做一个动作，看看我方会不会跟着改变。';
      }else if(z.mode==='转移'){
        reason='对手发现原来的竞争方式效果开始下降，所以换一个地方竞争，不再一直和我方硬碰同一个点。';
      }else if(z.mode==='反制'){
        reason=state.lastMode==='负向施压'||state.pressure>=5
          ?'我方刚才给了对手压力，所以对手马上做针对性的回应，而不是继续按原来的路线走。'
          :'对手发现我方出现了一个可以回应的动作，所以先做一次针对性的反击。';
      }else if(z.mode==='机制校验'){
        reason=state.risk>=5||state.pressure>=5
          ?'对手发现情况有些异常，先确认平台规则、流量或市场状态有没有变化，再决定是否继续投入。'
          :'对手现在拿不准市场到底发生了什么，所以先观察和确认，不急着扩大动作。';
      }else if(z.mode==='负向施压'){
        reason=state.pressure>=4||state.opponentMomentum>=5
          ?'双方竞争已经比较激烈，对手开始给我方增加压力，看看我方会不会被迫改变路线。'
          :'对手想试着给我方增加一点竞争压力，看看我方会不会退让或换路线。';
      }
      parts.push(reason);

      if(/关键词|搜索|长尾/.test(ms)){
        parts.push('这一步主要是在抢搜索和关键词带来的流量。');
      }else if(/主图|点击/.test(ms)){
        parts.push('这一步主要是在争取点击，让用户先看到并点击对手的商品。');
      }else if(/详情|FAQ|卖点|痛点/.test(ms)){
        parts.push('这一步主要是在争转化，让已经进来的用户更容易选择对手。');
      }else if(/视频|UGC|种草|内容/.test(ms)){
        parts.push('这一步主要是在争内容曝光和用户注意力。');
      }

      if(state.feedback){
        var f=state.feedback, fb=[];
        if(f.ctr!==null)fb.push('点击表现约为'+Math.round(f.ctr*100)+'%基准');
        if(f.conversion!==null)fb.push('转化表现约为'+Math.round(f.conversion*100)+'%基准');
        if(f.contentSpread!==null)fb.push('内容扩散约为'+Math.round(f.contentSpread*100)+'%基准');
        if(fb.length)parts.push('目前能看到的模拟市场反馈是：'+fb.join('、')+'。');
      }

      parts.push('下一步，对手会看我方怎么回应，再决定继续抢、换地方、降低投入，还是反过来加大竞争。');
      return parts.join(' ');
    }

    // 我方解释同样使用人话。
    if(!last) parts.push('这是第一步：商品基础已经准备好，现在先进入市场看看真实反馈。');
    else parts.push('对手刚才做了“'+(last.name||'未知')+'”。');

    if(z.mode==='试探') parts.push('现在信息还不够，所以先做一个小动作，看看市场和对手怎么反应，不急着重投入。');
    else if(z.mode==='建设') parts.push(state.momentum>=5?'前面的动作已经出现效果，所以继续加强这条路线。':'现在需要先把这条路线做起来，再看市场是否给出正向反馈。');
    else if(z.mode==='防守') parts.push('现在的压力或风险比较高，所以先守住已经拿到的东西，避免继续扩大损失。');
    else if(z.mode==='竞争') parts.push('对手正在争这部分市场，所以我们开始直接竞争，看看能不能把流量和用户抢回来。');
    else if(z.mode==='诱导') parts.push('现在直接出大招容易让对手看懂，所以先做一个动作，看看对手会不会跟。');
    else if(z.mode==='转移') parts.push('原来的竞争点越来越难，所以换一个地方寻找机会。');
    else if(z.mode==='反制') parts.push('对手刚才给了我们压力，所以现在针对他的动作回应，而不是盲目加码。');
    else if(z.mode==='机制校验') parts.push('现在有些情况还没看清，所以先确认到底发生了什么，再决定下一步。');
    else if(z.mode==='负向施压') parts.push('现在需要给对手增加一点竞争压力，看看他会不会改变路线。');

    var diagnoses=diagnoseProduct(state);
    if(diagnoses.length)parts.push('市场反馈显示：'+diagnoses.slice(0,2).map(function(d){return d.label+'（'+d.why+'）';}).join('、')+'，所以这一步优先处理这个问题。');
    else if(state.turn>=2)parts.push('目前还没有一个特别明确的问题，所以先小幅试探，继续收集反馈。');

    if(/长尾关键词|关键词/.test(ms)){
      parts.push('这一步主要是在调整搜索词，验证用户真正会搜什么。');
    }else if(/主图/.test(ms)){
      parts.push('这一步主要是在调整主图，看看能不能提高点击。');
    }else if(/详情|FAQ|卖点|痛点/.test(ms)){
      parts.push('这一步主要是在调整详情和卖点，看看进来的人为什么没有购买。');
    }else if(/视频|UGC|种草|内容/.test(ms)){
      parts.push('这一步主要是在调整视频和内容，看看怎样获得更多传播。');
    }
    parts.push('基础商品已经做好，但不代表现在的配置就是正确的；后面仍然可以根据新的市场反馈继续修改。');
    return parts.join(' ');
  }

  function chooseOur(i,step,state){
    var z=pickCandidate(state,'我方');
    if(!z)return null;
    return {id:z.m.id,name:z.m.name,kind:z.kind,mode:z.mode,role:'我方',source:z.m,
      reason:buildMoveReason(state,z,'我方')};
  }

  function chooseOpponent(i,step,state){
    var z=pickCandidate(state,'对手');
    if(!z)return null;
    return {id:z.m.id,name:z.m.name,kind:z.kind,mode:z.mode,role:'对手（模拟）',source:z.m,
      reason:buildMoveReason(state,z,'对手')};
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
        lastDomain:state.lastDomain,lastMode:state.lastMode,
        productVariables:JSON.parse(JSON.stringify(state.productVariables)),
        feedback:Object.assign({},state.feedback)
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
        response:endReason?'本手改变了局面，触发自然收束：'+endReason:
          ('本手实际变化：'+deltaText.join('；')+'。'+
           (change.meaningful?' 下一步应围绕这些变化继续调整，而不是重复当前动作。':' 本手没有形成明显新变量，下一步优先换变量或降低投入。'))
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
    var html='<h1 class="page-title">连续博弈策略中心</h1>';
    html+='<div class="subtitle">40种行为人格 · 每个人格一张连续棋谱 · 自然收束 · 三大招式库混合使用</div>';
    html+='<div class="card" style="margin:10px 0 16px;border-left:4px solid var(--accent);background:rgba(255,180,0,.06)"><b>棋谱规则</b><div style="font-size:16px;line-height:1.7;margin-top:6px">';
    html+='不是“我方三步/一轮就结束”，也不是为了凑固定步数。每一套人格是一条完整连续链：<b>我方第1招 → 对手第2招 → 我方第3招 → 对手第4招 → ……</b>，最多40步；40步只是安全上限，不是目标。';
    html+='三大招式库不再按阵营分配：我方和对手共享建设、防守、试探、竞争、诱导、转移、反制、机制校验、负向施压九类战略动作。人格只改变动作权重，不锁死动作类型；上一招、累计状态、对手回应以及当前市场反馈共同决定下一招。对手招式全部是模拟假设，不代表真实对手已经采取该动作；机制型招式用于识别、校验、隔离和防守。';
    html+='同时，商品基础建设完成不等于配置已经正确：初始商品是基于热门/竞品信息形成的复制式基线，进入棋谱后持续通过模拟反馈诊断问题、定位变量并纠偏。每次修改都产生新的反馈，再进入下一手决策，形成“市场反馈 → 问题诊断 → 变量修改 → 对手响应 → 新反馈”的连续闭环。只有局面仍产生有效的新变化才继续；优势形成、僵持、路线失效、反馈不足以支持继续行动或风险封顶时自然收束。';
    html+='</div></div>';
    html+='<div class="card" style="margin:10px 0 16px;border-left:4px solid var(--accent)"><b>商品初始状态：基础建设已完成</b><div style="margin-top:8px;line-height:1.8">标题（热门/竞品关键词） · 主图（竞争参考） · 详情页 · 5条正向真实评价 · 商品视频 · 问大家 · 种草内容</div><div class="muted" style="margin-top:6px">因此棋谱不会从“什么都没做”开始。现在主要观察：点击率、转化率、自然流量、实际搜索词、竞品即时动作、内容扩散效率。</div></div>';
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

  function displayMoveId(id){
    var map={
      CHANGE_KEYWORD:'调整关键词',CHANGE_TARGETING:'调整投放定向',CHANGE_BID:'调整出价',
      CHANGE_BUDGET:'调整预算',CHANGE_CREATIVE:'调整素材',CHANGE_PRICE:'调整价格',
      CHANGE_PRODUCT:'调整商品配置',TEST_KEYWORD:'测试关键词',TEST_TARGETING:'测试投放定向'
    };
    return map[id]||id||'';
  }

  function stepHtml(s){
    var m=s.move;
    var border=m.mode==='建设'?'var(--accent)':m.mode==='负向施压'?'#b44':m.mode==='机制校验'?'#777':'#777';
    var h='<div class="card" style="margin:0 0 8px;border-left:4px solid '+border+'">';
    h+='<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap"><span class="tag">第'+s.no+'步</span><b>'+esc(s.side)+'</b><span class="tag">'+esc(m.kind)+'</span><span class="muted">'+esc(s.phase)+'</span></div>';
    h+='<div style="font-size:17px;margin-top:7px"><span class="tag">'+esc(displayMoveId(m.id))+'</span> <b>'+esc(m.name)+'</b></div>';
    h+='<div class="notice" style="margin-top:7px"><b>为什么现在用这招</b><div style="margin-top:5px;line-height:1.7">'+esc(m.reason)+'</div></div>';
    h+='<div class="muted" style="margin-top:6px"><b>本手目标：</b>'+esc(m.mode||'自适应')+' · <b>前一手：</b>'+esc((s.stateBefore&&s.stateBefore.lastMode)||'开局')+' · '+esc((s.stateBefore&&s.stateBefore.lastDomain)||'通用')+'</div>';
    if(s.stateAfter&&s.stateAfter.productVariables){
      var pv=s.stateAfter.productVariables, f=s.stateAfter.feedback||{};
      var diag=diagnoseProduct(s.stateAfter);
      h+='<div class="notice" style="margin-top:6px"><b>商品变量反馈</b>：';
      if(diag.length)h+='<b>当前优先修正：</b>'+esc(diag.slice(0,2).map(function(d){return d.label;}).join('、'))+' · ';
      else h+='<b>当前没有单一故障变量：</b>继续收集反馈 · ';

      h+='长尾词版本 V'+pv.longTailKeywords.version+'（置信度 '+Math.round(pv.longTailKeywords.confidence*100)+'%）';
      if(f.ctr!==null)h+=' · 点击反馈 '+Math.round(f.ctr*100)+'%基准';
      if(f.conversion!==null)h+=' · 转化反馈 '+Math.round(f.conversion*100)+'%基准';
      h+='</div>';
    }
    if(m.source){
      h+='<details style="margin-top:6px"><summary class="muted" style="cursor:pointer">查看招式来源与原始定义</summary><div class="muted" style="margin-top:4px">战略动作：'+esc(m.mode||'自适应')+' · 原招式库：'+esc(m.kind)+' · 原定义：'+esc(m.source.action||m.source.defense||m.source.mechanism||m.source.signal||'')+'</div></details>';
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