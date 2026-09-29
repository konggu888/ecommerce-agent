(function () {
  'use strict';
  var app=document.getElementById('app'), nav=document.querySelectorAll('.nav');
  var VERSION='20260929-70';
  var BASE='https://skuoxmrzlxhebzhfgbyn.supabase.co';
  var KEY='sb_publishable_u46tZ4GMUgwqSYhMJNFG8Q_IzYwl95T';
  var CLIENT='ecommerce-agent-sandbox-v1';
  var state={view:location.hash.slice(1)||'overview',run:null,game:[],market:[],ads:{},backtests:[],events:[],memories:[],risk:[],tasks:[],agentRounds:[],simulation:{status:'idle',message:''}};
  var adTables=['sandbox_ad_plans','sandbox_ad_units','sandbox_ad_keywords','sandbox_ad_keyword_moves','sandbox_ad_audiences','sandbox_ad_audience_combos','sandbox_ad_creatives','sandbox_ad_placements','sandbox_ad_regions','sandbox_ad_timeslots','sandbox_ad_negative_keywords','sandbox_ad_agent_actions','sandbox_ad_results','sandbox_ad_reports'];
  function zh(v){var m={'HOLD':'保持观察','CHANGE_KEYWORD':'调整关键词','CHANGE_TARGETING':'调整定向','CHANGE_CONTENT':'调整内容','CHANGE_AUDIENCE':'调整人群','CHANGE_CREATIVE':'调整创意','CHANGE_PRICE':'调整价格','INCREASE_BUDGET':'增加预算','DECREASE_BUDGET':'降低预算','INCREASE_BID':'提高出价','DECREASE_BID':'降低出价','DEFEND_TRAFFIC':'防守流量','SHIFT_CONTENT':'切换内容','VALUE_ATTACK':'价值竞争','NO_CLEAR_GAP':'暂未发现明确突破口','ALLOW':'通过','BLOCK':'拦截','STOP':'停止','CONTINUE':'继续','POSITIVE':'正向','NEGATIVE':'负向','INCONCLUSIVE':'结果不明确','OBSERVE':'观察','DEFENSIVE':'防守','MIXED':'混合','UNKNOWN':'未知','ANALYZE_ONLY':'仅分析','AUTO':'自动选择','OUR_AGENT':'我方智能体','OPP-01':'价格竞争方','OPP-02':'流量竞争方','OPP-03':'内容竞争方','CATARGETING':'定向投放','CA_TARGETING':'定向投放','TARGETING':'定向投放','targeting':'定向投放','catargeting':'定向投放'};return m[v]||v||'';}
  function esc(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
  function show(title,sub,body){app.innerHTML='<h1 class="page-title">'+esc(title)+' <span style="font-size:16px;font-weight:500;color:var(--accent);margin-left:10px">我变 → 对手学 → 我再变</span></h1><div class="subtitle">'+esc(sub)+'</div><div class="card" style="margin:10px 0 16px;border-left:4px solid var(--accent);background:rgba(255,180,0,.06)"><b>连续博弈座右铭</b><div style="font-size:18px;margin-top:6px">我变 → 对手学 → 我再变</div></div>'+body;}
  function notice(v){return '<div class="card"><div class="notice">'+esc(v)+'</div></div>';}
  function table(h,rows){if(!rows.length)return notice('暂无记录');var s='<div class="card"><table class="table"><thead><tr>'+h.map(esc).map(function(x){return'<th>'+x+'</th>';}).join('')+'</tr></thead><tbody>';rows.forEach(function(r){s+='<tr>'+r.map(esc).map(function(x){return'<td>'+x+'</td>';}).join('')+'</tr>';});return s+'</tbody></table></div>';}
  function getJSON(url,options){return fetch(url,Object.assign({headers:{apikey:KEY,Authorization:'Bearer '+KEY,Accept:'application/json'},cache:'no-store'},options||{})).then(function(res){return res.text().then(function(t){var d={};try{d=JSON.parse(t);}catch(e){throw new Error('HTTP '+res.status+' 返回非 JSON');}if(!res.ok)throw new Error('HTTP '+res.status);return d;});});}
  function runURL(name,scoped){var q='?select=*&order=id.desc';if(scoped&&state.run&&state.run.id)q+='&run_id=eq.'+encodeURIComponent(state.run.id);return BASE+'/rest/v1/'+name+q;}
  function loadRun(){return getJSON(BASE+'/rest/v1/sandbox_runs?select=id,status,updated_at,client_key,agent_progress,backtest_progress,risk_progress,memory_count,run_count,state&client_key=eq.'+encodeURIComponent(CLIENT)+'&order=updated_at.desc&limit=1').then(function(r){if(!r.length)throw new Error('没有找到 sandbox_runs');state.run=r[0];});}
  function loadCore(){return Promise.all([getJSON(runURL('sandbox_game_states',true)),getJSON(runURL('sandbox_market_signals',true)),getJSON(runURL('sandbox_backtests',true)),getJSON(runURL('sandbox_events',true)),getJSON(runURL('sandbox_memories',true)),getJSON(runURL('sandbox_risk_results',true)),getJSON(runURL('sandbox_task_results',true)),getJSON(runURL('sandbox_agent_rounds',true))]).then(function(x){state.game=x[0]||[];state.market=x[1]||[];state.backtests=x[2]||[];state.events=x[3]||[];state.memories=x[4]||[];state.risk=x[5]||[];state.tasks=x[6]||[];state.agentRounds=x[7]||[];var s=state.run&&state.run.state||{};if(!state.agentRounds.length&&Array.isArray(s.executedPath))state.agentRounds=s.executedPath.map(function(p,i){return{round:p.round||i+1,action:p.action||'HOLD',actual_opponent_response:p.response||p.actual_opponent_response||'暂无',next_action_hint:p.nextAction||p.next_action_hint||'HOLD',breakthrough:p.breakthrough||'',roi:p.roi,marginal_roi:p.marginal_roi,risk_approved:p.risk_approved!==false,stop_signal:!!p.stop_signal,stop_reason:p.stop_reason||''};});if(!state.risk.length&&state.agentRounds.length){state.risk=state.agentRounds.map(function(x){return{metric:'R'+x.round+' · 风控状态',value:{approved:x.risk_approved!==false,stop_signal:!!x.stop_signal,stop_reason:x.stop_reason||'',action:x.action||'HOLD',marginal_roi:x.marginal_roi==null?null:x.marginal_roi,crowding:x.crowding==null?null:x.crowding},created_at:state.run&&state.run.updated_at||''};});}if(!state.game.length&&Array.isArray(s.game))state.game=s.game;if(!state.market.length&&Array.isArray(s.market))state.market=s.market;if(!state.market.length&&Array.isArray(s.marketSignals))state.market=s.marketSignals;if(!state.backtests.length&&state.agentRounds.length){state.backtests=state.agentRounds.map(function(x){return{scenario:'连续博弈第'+x.round+'轮',rounds:x.round,roi:x.roi==null?'-':x.roi,risk:x.risk_approved===false?'HIGH':'MEDIUM',action:x.action||'HOLD',created_at:state.run&&state.run.updated_at||''};});}if(!state.memories.length&&state.agentRounds.length){state.memories=state.agentRounds.map(function(x){return{memory_type:'ROUND_LEARNING',content:'第'+x.round+'轮：我方'+(x.action||'HOLD')+' → 实际响应'+(x.actual_opponent_response||'暂无')+' → 下一动作'+(x.next_action_hint||'HOLD'),confidence:x.risk_approved===false?0.5:0.8,status:'ACTIVE',created_at:state.run&&state.run.updated_at||''};});}});}
  function loadAds(){return Promise.all(adTables.map(function(n){return getJSON(runURL(n)).then(function(r){state.ads[n]=r||[];});}));}
  function overview(){var rounds=state.agentRounds||[];var last=rounds.length?rounds[rounds.length-1]:null;var chain='<div class="card"><div class="label">连续博弈动态链</div><div style="display:flex;gap:8px;overflow:auto;padding:12px 0">';[['01','输入','我方 + 对手 + 市场'],['02','突破口','识别竞争结构'],['03','策略','选择本轮动作'],['04','风险控制','资金 / 市场 / 对手风险'],['05','执行','模拟价格、投流、内容'],['06','对手响应','记录实际反应'],['07','市场反馈','ROI / 转化 / 拥挤'],['08','学习','进入下一轮']].forEach(function(x){chain+='<div style="min-width:150px;border:1px solid var(--line);border-radius:10px;padding:10px"><span class="tag">'+x[0]+'</span><br><b>'+x[1]+'</b><div class="muted">'+x[2]+'</div></div>';});chain+='</div>'+(last?'<div class="notice">当前：R'+esc(last.round)+' · '+zh(last.action)+' → '+zh(last.actual_opponent_response)+' → '+zh(last.next_action_hint)+'</div>':'<div class="notice">当前 Sandbox 尚无可播放轮次。</div>')+'</div>';
    var rows=rounds.map(function(r){return['R'+(r.round||''),zh(r.action),zh(r.actual_opponent_response),zh(r.next_action_hint),r.roi==null?'-':r.roi,r.risk_approved===false?'拦截':'通过'];});
    var playback='<div class="card"><div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap"><div><div class="label">Agent Sandbox 多轮模拟</div><div class="metric">'+(rounds.length?('已读取 '+rounds.length+' 轮'):'暂无模拟轮次')+'</div></div><div><button class="action" id="sim-start">▶ 开始10轮模拟</button><button class="action" id="sim-refresh">↻ 读取最新模拟</button></div></div>'+(rows.length?table(['轮次','我方动作','实际对手响应','下一动作','ROI','风险'],rows):'<div class="notice">数据库当前没有 Agent 轮次；如果刚完成模拟，请点击“读取最新模拟”。</div>')+'</div>';
    show('商业博弈总览','Sandbox Run · '+(state.run?state.run.status:'未知'),'<div class="grid"><div class="card"><div class="label">Sandbox Run</div><div class="metric">'+esc(state.run?state.run.status:'unknown')+'</div></div><div class="card"><div class="label">商业博弈记录</div><div class="metric">'+state.game.length+'</div></div><div class="card"><div class="label">市场信号</div><div class="metric">'+state.market.length+'</div></div><div class="card"><div class="label">Agent闭环轮次</div><div class="metric">'+rounds.length+'</div></div></div>'+chain+playback);bindSimulationButtons();}
  function bindSimulationButtons(){var a=document.getElementById('sim-start'),b=document.getElementById('sim-refresh');if(a)a.onclick=startSimulation;if(b)b.onclick=function(){loadRun().then(loadCore).then(loadAds).then(render).catch(function(e){alert('读取失败：'+e.message);});};}
  function startSimulation(){var ctx={client_key:CLIENT,rounds:10,strategy_context:{type:'AUTO',id:'',name:'自动选择',action:'',signal:'',goal:''}};var a=document.getElementById('sim-start');if(a){a.disabled=true;a.textContent='正在运行…';}getJSON(BASE+'/functions/v1/sandbox-agent-runner',{method:'POST',headers:{apikey:KEY,Authorization:'Bearer '+KEY,'Content-Type':'application/json'},body:JSON.stringify(ctx)}).then(function(){return loadRun().then(loadCore).then(loadAds);}).then(render).catch(function(e){alert('启动模拟失败：'+e.message);render();});}
  function market(){show('外部市场情报','Sandbox 市场信号',table(['名称','类型','强度','说明'],state.market.map(function(x){return[x.name,x.signal_type,x.strength,x.detail];})));}
  function gameLogic(){var list=window.EA_GAME_LOGICS||[];var h='<div class="card"><div class="label">博弈逻辑库</div><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px">';list.forEach(function(x){h+='<div class="notice"><b>'+esc(x.id)+' '+esc(x.name)+'</b><br><span class="muted">'+esc(x.type||'')+'</span></div>';});h+='</div></div>';show('博弈逻辑','50套博弈逻辑与棋谱',h);}
  function generic(title,key){var list=window[key]||[];show(title,'策略库','<div class="card"><div class="label">'+list.length+'项</div><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px">'+list.map(function(x){return'<div class="notice"><b>'+esc(x.id||'')+' '+esc(x.name||'')+'</b><br><span class="muted">'+esc(x.signal||x.style||x.category||'')+'</span></div>';}).join('')+'</div></div>');}
  function threats(){var list=window.EA_THREAT_LIBRARY||[],books=window.EA_THREAT_PLAYBOOKS||{};var h='<div class="card"><div class="label">对手攻击面 · '+list.length+'套</div><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px">';list.forEach(function(x){var steps=books[x.id]||[],sid='threat-'+x.id;h+='<div class="card" style="cursor:pointer" data-threat="'+esc(x.id)+'"><b>'+esc(x.id)+' · '+esc(x.name)+'</b><div class="muted" style="margin-top:6px">'+esc(x.category||'')+'</div><div class="muted" style="margin-top:6px">'+esc(x.signal||'')+'</div><div id="'+sid+'" style="display:none;margin-top:10px;border-top:1px solid var(--line);padding-top:10px"><b>防守策略</b><div>'+esc(x.defense||'')+'</div><b style="display:block;margin-top:8px">攻击棋谱</b><ol>'+steps.map(function(s){return'<li>'+esc(s)+'</li>';}).join('')+'</ol></div></div>';});h+='</div></div>';show('对手攻击面','40套对手攻击模型与防守策略',h);document.querySelectorAll('[data-threat]').forEach(function(el){el.addEventListener('click',function(){var p=document.getElementById('threat-'+el.getAttribute('data-threat'));if(p)p.style.display=p.style.display==='none'?'block':'none';});});}
  function humanBehavior(){var list=window.EA_HUMAN_BEHAVIOR_LIBRARY||[];var h='<div class="card"><div class="label">人性行为演变 · '+list.length+'种行为模型</div><div class="notice" style="margin:10px 0">先观察行为序列，再形成行为假设；单次异常不直接定性。</div><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px">';list.forEach(function(x){h+='<div class="card" style="cursor:pointer" data-human="'+esc(x.id)+'"><b>'+esc(x.id)+' · '+esc(x.name)+'</b><div class="muted" style="margin-top:6px">模式：'+esc(x.style||'')+'</div><div style="margin-top:6px">信号：'+esc(x.signal||'')+'</div><div class="muted" style="margin-top:6px">序列：'+esc((x.sequence||[]).join(' → '))+'</div><div id="human-'+esc(x.id)+'" style="display:none;margin-top:10px;border-top:1px solid var(--line);padding-top:10px"><div><b>风险：</b>'+esc(x.risk||'未知')+'</div><div style="margin-top:6px"><b>目标：</b>'+esc(x.goal||'')+'</div><div style="margin-top:6px"><b>观察方法：</b>连续多个行为窗口验证，不以单次动作直接归因。</div><div style="margin-top:6px"><b>应对思路：</b>先保护自身指标，再根据后续行为更新假设。</div></div></div>';});h+='</div></div>';show('人性行为演变','40种行为模型 · 行为序列 → 观察 → 假设 → 更新',h);document.querySelectorAll('[data-human]').forEach(function(el){el.addEventListener('click',function(){var p=document.getElementById('human-'+el.getAttribute('data-human'));if(p)p.style.display=p.style.display==='none'?'block':'none';});});}
  function positiveAttacks(){var list=window.EA_POSITIVE_ATTACK_LIBRARY||[],books=window.EA_POSITIVE_ATTACK_PLAYBOOKS||[];var h='<div class="card"><div class="label">正向攻击 · '+list.length+'套策略</div><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px">';list.forEach(function(x){var book=null;for(var bi=0;bi<books.length;bi++){if(books[bi]&&books[bi].id===x.id){book=books[bi];break;}}var steps=book&&Array.isArray(book.stages)?book.stages:[];var id='pos-'+x.id;h+='<div class="card" style="cursor:pointer" data-pos="'+esc(x.id)+'"><b>'+esc(x.id)+' · '+esc(x.name)+'</b><div class="muted" style="margin-top:6px">'+esc(x.category||'')+'</div><div style="margin-top:6px">信号：'+esc(x.signal||'')+'</div><div id="'+id+'" style="display:none;margin-top:10px;border-top:1px solid var(--line);padding-top:10px"><div><b>动作：</b>'+esc((book&&book.action)||x.action||'')+'</div><div style="margin-top:6px"><b>目标：</b>'+esc(x.goal||'')+'</div><b style="display:block;margin-top:8px">五步攻略</b><ol>'+steps.map(function(s){return'<li>'+esc(s)+'</li>';}).join('')+'</ol></div></div>';});h+='</div></div>';show('正向攻击','策略库 · 点击任意策略展开完整攻略',h);document.querySelectorAll('[data-pos]').forEach(function(el){el.addEventListener('click',function(){var p=document.getElementById('pos-'+el.getAttribute('data-pos'));if(p)p.style.display=p.style.display==='none'?'block':'none';});});}
  function strategyCenter(){var list=window.EA_HUMAN_BEHAVIOR_LIBRARY||[];var h='<div class="card"><div class="label">连续博弈策略中心 · '+list.length+'套行为策略</div><div class="notice" style="margin:10px 0">点击策略进入“我变 → 对手学 → 我再变”的连续博弈视图。</div><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px">';list.forEach(function(x){h+='<div class="card" style="cursor:pointer" data-strategy="'+esc(x.id)+'"><b>'+esc(x.id)+' · '+esc(x.name)+'</b><div class="muted" style="margin-top:6px">模式：'+esc(x.style||'')+'</div><div style="margin-top:6px">信号：'+esc(x.signal||'')+'</div><div id="strategy-'+esc(x.id)+'" style="display:none;margin-top:10px;border-top:1px solid var(--line);padding-top:10px"><div><b>行为序列：</b>'+esc((x.sequence||[]).join(' → '))+'</div><div style="margin-top:6px"><b>目标：</b>'+esc(x.goal||'')+'</div><div style="margin-top:6px"><b>连续博弈：</b>我变 → 对手响应 → 学习 → 换路 → 再进入下一轮</div><button type="button" class="action" style="margin-top:10px" data-strategy-sim="'+esc(x.id)+'">▶ 用此策略开始10轮模拟</button></div></div>';});h+='</div></div>';show('连续博弈策略中心','选择行为策略后进入连续博弈 Sandbox',h);document.querySelectorAll('[data-strategy]').forEach(function(el){el.addEventListener('click',function(e){if(e.target&&e.target.getAttribute('data-strategy-sim'))return;var p=document.getElementById('strategy-'+el.getAttribute('data-strategy'));if(p)p.style.display=p.style.display==='none'?'block':'none';});});document.querySelectorAll('[data-strategy-sim]').forEach(function(btn){btn.addEventListener('click',function(e){e.stopPropagation();startSimulation();});});}
  function ads() {
    var a = state.ads;
    var plans = a.sandbox_ad_plans || [];
    var units = a.sandbox_ad_units || [];
    var keywords = a.sandbox_ad_keywords || [];
    var moves = a.sandbox_ad_keyword_moves || [];
    var audiences = a.sandbox_ad_audiences || [];
    var combos = a.sandbox_ad_audience_combos || [];
    var creatives = a.sandbox_ad_creatives || [];
    var placements = a.sandbox_ad_placements || [];
    var regions = a.sandbox_ad_regions || [];
    var timeslots = a.sandbox_ad_timeslots || [];
    var negatives = a.sandbox_ad_negative_keywords || [];
    var actions = a.sandbox_ad_agent_actions || [];
    var results = a.sandbox_ad_results || [];
    var reports = a.sandbox_ad_reports || [];

    var planRows = [];
    for (var p = 0; p < plans.length; p++) {
      var q = plans[p];
      planRows.push([q.name, q.status, q.product, q.scene, q.daily_budget, q.bid_strategy]);
    }

    var unitRows = [];
    for (var u = 0; u < units.length; u++) {
      var un = units[u];
      unitRows.push([un.name, un.product, un.status, un.keyword_count, un.audience_count, un.creative_count]);
    }

    var keywordRows = [];
    for (var i = 0; i < keywords.length; i++) {
      var x = keywords[i];
      keywordRows.push([x.keyword, x.keyword_type, x.match_type, x.bid, x.impressions, x.clicks, x.ctr, x.conversions, x.cvr, x.spend, x.gmv, x.roi]);
    }

    var moveRows = [];
    for (var m = 0; m < moves.length; m++) {
      var mv = moves[m];
      moveRows.push([mv.source_keyword, mv.source_scene, mv.related_keyword, mv.related_scene, mv.move_type, mv.impressions, mv.clicks, mv.conversions, mv.cvr, mv.roi, mv.agent_conclusion, mv.status]);
    }

    var audienceRows = [];
    for (var j = 0; j < audiences.length; j++) {
      var au = audiences[j];
      audienceRows.push([au.name, au.audience_type, au.behavior, au.window_days, au.size, au.coverage, au.cvr, au.roi, au.bid, au.premium, au.overlap, au.status]);
    }

    var comboRows = [];
    for (var k = 0; k < combos.length; k++) {
      var co = combos[k];
      comboRows.push([co.name, JSON.stringify(co.components), co.size, co.overlap, co.cvr, co.roi, co.agent_conclusion]);
    }

    var creativeRows = [];
    for (var cr = 0; cr < creatives.length; cr++) {
      var cv = creatives[cr];
      creativeRows.push([cv.name, cv.creative_type, cv.title, cv.audit_status, cv.impressions, cv.clicks, cv.ctr, cv.conversions, cv.roi, cv.status]);
    }

    var placementRows = [];
    for (var pl = 0; pl < placements.length; pl++) {
      var pp = placements[pl];
      placementRows.push([pp.channel, pp.placement, pp.impressions, pp.clicks, pp.ctr, pp.spend, pp.conversions, pp.cvr, pp.gmv, pp.roi]);
    }

    var regionRows = [];
    for (var rg = 0; rg < regions.length; rg++) {
      var rr = regions[rg];
      regionRows.push([rr.region, rr.impressions, rr.clicks, rr.ctr, rr.spend, rr.conversions, rr.cvr, rr.roi]);
    }

    var timeRows = [];
    for (var ts = 0; ts < timeslots.length; ts++) {
      var tt = timeslots[ts];
      timeRows.push([tt.slot, tt.weekday, tt.impressions, tt.clicks, tt.ctr, tt.cpc, tt.conversions, tt.cvr, tt.roi]);
    }

    var negativeRows = [];
    for (var ng = 0; ng < negatives.length; ng++) {
      var nn = negatives[ng];
      negativeRows.push([nn.keyword, nn.clicks, nn.spend, nn.conversions, nn.agent_conclusion, nn.status]);
    }

    var actionRows = [];
    for (var ac = 0; ac < actions.length; ac++) {
      var aa = actions[ac];
      actionRows.push([aa.action_type, aa.target, aa.reason, JSON.stringify(aa.before_value), JSON.stringify(aa.after_value), aa.result, aa.status]);
    }

    var resultRows = [];
    for (var rs = 0; rs < results.length; rs++) {
      var re = results[rs];
      resultRows.push([re.kind, JSON.stringify(re.payload), re.created_at]);
    }

    var reportRows = [];
    for (var rp = 0; rp < reports.length; rp++) {
      var rd = reports[rp];
      reportRows.push([rd.dimension, rd.dimension_value, rd.impressions, rd.clicks, rd.ctr, rd.cpc, rd.spend, rd.conversions, rd.cvr, rd.gmv, rd.roi, rd.report_date]);
    }

    show(
      '广告 / 流量',
      'BOOT-DEBUG-' + VERSION + ' · Sandbox 模拟数据 · 广告数据链',
      '<div class="grid">' +
      '<div class="card"><div class="label">投放计划</div><div class="metric">' + plans.length + '</div></div>' +
      '<div class="card"><div class="label">投放单元</div><div class="metric">' + units.length + '</div></div>' +
      '<div class="card"><div class="label">关键词</div><div class="metric">' + keywords.length + '</div></div>' +
      '<div class="card"><div class="label">人群</div><div class="metric">' + audiences.length + '</div></div>' +
      '<div class="card"><div class="label">创意</div><div class="metric">' + creatives.length + '</div></div>' +
      '<div class="card"><div class="label">Agent动作</div><div class="metric">' + actions.length + '</div></div>' +
      '</div>' +
      '<h2>投放计划</h2>' + table(['投放计划','状态','商品','场景','日预算','出价策略'], planRows) +
      '<h2>投放单元</h2>' + table(['单元','商品','状态','关键词数','人群数','创意数'], unitRows) +
      '<h2>关键词</h2>' + table(['关键词','类型','匹配','出价','展现','点击','CTR','成交','CVR','消耗','GMV','ROI'], keywordRows) +
      '<h2>关键词迁移 / 扩词</h2>' + table(['源关键词','源场景','关联关键词','关联场景','动作类型','展现','点击','成交','CVR','ROI','Agent结论','状态'], moveRows) +
      '<h2>投放人群</h2>' + table(['人群','类型','行为','窗口天数','规模','覆盖率','CVR','ROI','出价','溢价','重叠','状态'], audienceRows) +
      '<h2>人群组合</h2>' + table(['组合','组成','规模','重叠','CVR','ROI','Agent结论'], comboRows) +
      '<h2>创意</h2>' + table(['名称','类型','标题','审核','展现','点击','CTR','成交','ROI','状态'], creativeRows) +
      '<h2>资源位</h2>' + table(['渠道','资源位','展现','点击','CTR','消耗','成交','CVR','GMV','ROI'], placementRows) +
      '<h2>地域</h2>' + table(['地域','展现','点击','CTR','消耗','成交','CVR','ROI'], regionRows) +
      '<h2>时段</h2>' + table(['时段','星期','展现','点击','CTR','CPC','成交','CVR','ROI'], timeRows) +
      '<h2>否定词</h2>' + table(['关键词','点击','消耗','成交','Agent结论','状态'], negativeRows) +
      '<h2>Agent动作</h2>' + table(['动作','目标','原因','动作前','动作后','结果','状态'], actionRows) +
      '<h2>投放结果</h2>' + table(['类型','Payload','时间'], resultRows) +
      '<h2>广告报告</h2>' + table(['维度','维度值','展现','点击','CTR','CPC','消耗','成交','CVR','GMV','ROI','日期'], reportRows) +
      notice('广告模块已恢复完整 Sandbox 数据链：计划 → 单元 → 关键词/扩词 → 人群 → 创意 → 资源位 → 地域 → 时段 → 否定词 → Agent动作 → 结果/报告。')
    );
  }

  function adBidding(){var items=[
  {id:'01',name:'投流博弈地图',sub:'先看全局，再决定投哪里',body:'把我方预算、出价、关键词、定向、人群、素材、位置、时间，与市场竞争强度放在同一张地图上。核心不是单纯追求曝光，而是寻找“我增加一单位投流资源 → 市场产生多少增量 → 对手可能如何响应 → 边际ROI是否继续成立”。'},
  {id:'02',name:'正向投流',sub:'主动寻找增量',body:'从真实可观测数据出发，寻找低拥挤、高转化或存在需求缺口的投流入口。可以测试关键词、人群、素材、位置和预算，但每次动作都要记录增量ROI、转化变化和市场反馈。'},
  {id:'03',name:'逆向防守',sub:'发现成本异常后先稳住',body:'不是看到流量下降就立刻加预算。先判断是否存在竞价抬升、流量结构变化、转化下降、无效点击增加或平台波动，再决定降价、换词、换人群、缩预算或暂缓投流。'},
  {id:'04',name:'对手响应矩阵',sub:'预测不是事实，实际响应优先',body:'只能根据曝光、点击、转化、价格、排名、流量结构等可观测信号推测对手响应。记录“我方动作 → 市场变化 → 推测响应 → 实际结果”，重复观察后形成对手反制矩阵，不直接假定对手做了看不见的动作。'},
  {id:'05',name:'预算博弈',sub:'预算不是越多越好',body:'把有限预算放进不同关键词、人群、渠道、位置和时间窗口进行竞争。比较边际ROI、获客成本、转化质量、现金占用和竞争拥挤度，决定继续加码、平移预算、降低投入或停止。'},
  {id:'06',name:'投流陷阱',sub:'识别看起来增长、实际上恶化的投流',body:'重点检查高点击低转化、曝光增长但订单不增长、ROI下降、边际ROI快速下降、竞价持续抬升、低质量流量增加、为了排名被迫不断加价等情况。发现陷阱时优先保护现金流和单位经济。'},
  {id:'07',name:'连续投流',sub:'我变 → 对手响应 → 我再变',body:'每一轮只把实际观测到的结果写回下一轮。第一轮测试入口，第二轮观察响应，第三轮根据真实反馈换路或加码，之后持续更新对手反制压力和市场状态，而不是每轮重复同一个动作。'},
  {id:'08',name:'投流攻防演变',sub:'从单次投流进入长期博弈',body:'完整链路：发现机会 → 正向投流 → 对手/市场响应 → 风险控制 → 识别反制 → 换关键词/人群/素材/渠道 → 再投流 → 学习。目标是形成可持续的投流策略，而不是打一场短期价格或竞价战。'}
  ];var h='<div class="card"><div class="label">广告投流博弈地图</div><div class="notice" style="margin:10px 0">核心链路：我方投流 → 市场反馈 → 对手响应 → 风险控制 → 换路 → 再投流</div><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px">';items.forEach(function(x){h+='<div class="card" style="cursor:pointer" data-adgame="'+x.id+'"><b>'+esc(x.id)+' · '+esc(x.name)+'</b><div class="muted" style="margin-top:6px">'+esc(x.sub)+'</div><div id="adgame-'+x.id+'" style="display:none;margin-top:10px;border-top:1px solid var(--line);padding-top:10px;line-height:1.7">'+esc(x.body)+'</div></div>';});h+='</div></div><div class="card"><button type="button" class="action" id="adgame-strategy">进入连续博弈策略中心 →</button></div>';show('广告投流博弈','投流攻防、预算博弈与连续投流',h);document.querySelectorAll('[data-adgame]').forEach(function(el){el.addEventListener('click',function(){var p=document.getElementById('adgame-'+el.getAttribute('data-adgame'));if(p)p.style.display=p.style.display==='none'?'block':'none';});});var b=document.getElementById('adgame-strategy');if(b)b.onclick=function(){state.view='strategy-center';location.hash=state.view;render();};}
  function risk(){var rows=[];for(var i=0;i<state.risk.length;i++){var x=state.risk[i];rows.push([x.metric,JSON.stringify(x.value),x.created_at]);}var progress=state.run?state.run.risk_progress:0;var status=state.run?state.run.status:'未知';var hero='<div class="card"><div class="label">风险控制总状态</div><div class="grid"><div><b>Run状态</b><br>'+esc(status)+'</div><div><b>风险检查进度</b><br>'+esc(progress)+'%</div><div><b>检查记录</b><br>'+state.risk.length+' 条</div><div><b>Agent轮次</b><br>'+state.agentRounds.length+' 轮</div></div></div>';show('风险控制器','Sandbox 风险结果 · 每轮动作进入风险闸门',hero+agentRiskTable()+'<h2>风险检查结果</h2>'+table(['指标','结果','时间'],rows));}function agentRiskTable(){var rounds=state.agentRounds||[];var rows=[];for(var i=0;i<rounds.length;i++){var x=rounds[i];rows.push(['R'+(x.round||''),zh(x.action),x.marginal_roi==null?'-':x.marginal_roi,x.crowding==null?'-':x.crowding,x.risk_approved===false?'拦截':(x.stop_signal?'停止':'通过'),x.stop_reason||'']);}return '<h2>Agent 逐轮风险闸门</h2>'+(rows.length?table(['轮次','动作','边际ROI','竞争拥挤','风控状态','原因'],rows):notice('当前 Run 尚无 Agent 风险轮次。'));}
  function render(){nav.forEach(function(n){n.classList.toggle('active',n.dataset.view===state.view);});try{if(state.view==='overview')overview();else if(state.view==='market')market();else if(state.view==='game-logic')gameLogic();else if(state.view==='positive-attacks')positiveAttacks();else if(state.view==='threats')threats();else if(state.view==='human-behavior')humanBehavior();else if(state.view==='strategy-center')strategyCenter();else if(state.view==='ad-bidding-game')adBidding();else if(state.view==='ads')ads();else if(state.view==='experiments')show('实验与回测','Sandbox',table(['场景','轮次','ROI','风险','动作','时间'],state.backtests.map(function(x){return[x.scenario,x.rounds,x.roi,x.risk,x.action,x.created_at];})));else if(state.view==='risk')risk();else if(state.view==='jobs')show('任务监控','Sandbox Agent',table(['任务类型','状态','进度','时间'],state.tasks.map(function(x){return[x.task_type,x.status,x.progress+'%',x.created_at];}))+'<h2>事件流</h2>'+table(['事件类型','标题','详情','时间'],state.events.map(function(x){return[x.event_type,x.title,x.detail,x.created_at];})));else if(state.view==='memory')show('学习记忆','Sandbox',table(['记忆类型','内容','置信度','状态','时间'],state.memories.map(function(x){return[x.memory_type,x.content,x.confidence,x.status,x.created_at];})));}catch(e){show('当前模块加载失败','其他页面不受影响',notice(e.message));}}
  nav.forEach(function(n){n.addEventListener('click',function(){state.view=n.dataset.view;location.hash=state.view;render();});});
  window.__EA_APPDB_LOADED__=true;window.__EA_APPDB_VERSION__=VERSION;
  loadRun().then(loadCore).then(loadAds).then(render).catch(function(e){show('核心数据读取失败','请检查 Sandbox 数据连接',notice(e.message));});
}());
