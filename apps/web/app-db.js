(function () {
  'use strict';
  var app = document.getElementById('app');
  var nav = Array.prototype.slice.call(document.querySelectorAll('.nav'));
  var SUPA = 'https://skuoxmrzlxhebzhfgbyn.supabase.co';
  var API = SUPA + '/functions/v1/sandbox-state';
  var KEY = 'ecommerce-agent-sandbox-v1';
  var ANON = 'sb_publishable_u46tZ4GMUgwqSYhMJNFG8Q_IzYwl95T';
  var s = { view: location.hash.slice(1) || 'overview', run: null, db: {}, loading: false, error: null, diag: { supabase: '未开始', run: '未开始', modules: '未开始', state: '未开始', details: [] } };

  function esc(v) {
    return String(v == null ? '' : v).split('&').join('&amp;').split('<').join('&lt;').split('>').join('&gt;').split('"').join('&quot;').split("'").join('&#39;');
  }
  function page(title, sub, body) { return '<h1 class="page-title">' + esc(title) + '</h1><div class="subtitle">' + esc(sub) + '</div>' + body; }
  function table(head, rows) {
    if (!rows || !rows.length) return '<div class="card"><div class="notice">数据库当前没有该页面的数据。</div></div>';
    return '<div class="card"><table class="table"><thead><tr>' + head.map(function (x) { return '<th>' + esc(x) + '</th>'; }).join('') + '</tr></thead><tbody>' + rows.map(function (r) { return '<tr>' + r.map(function (x) { return '<td>' + esc(x) + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table></div>';
  }
  function getJSON(url, timeout) {
    var c = new AbortController();
    var t = setTimeout(function () { c.abort(); }, timeout || 5000);
    return fetch(url, { headers: { apikey: ANON, Authorization: 'Bearer ' + ANON, Accept: 'application/json' }, mode: 'cors', cache: 'no-store', signal: c.signal })
      .then(function (r) { return r.text().then(function (x) { var j; try { j = JSON.parse(x); } catch (e) { throw Error('HTTP ' + r.status + ' 返回非JSON'); } if (!r.ok) throw Error('HTTP ' + r.status + '：' + (j.message || j.error || x.slice(0, 120))); return j; }); })
      .catch(function (e) { if (e.name === 'AbortError') throw Error('请求超过' + (timeout || 5000) + '毫秒未返回'); throw e; })
      .finally(function () { clearTimeout(t); });
  }
  function directRun() { return getJSON(SUPA + '/rest/v1/sandbox_runs?select=id,status,updated_at,client_key&client_key=eq.' + encodeURIComponent(KEY) + '&order=updated_at.desc&limit=1', 5000).then(function (a) { if (!a.length) throw Error('数据库已连接，但没有找到当前 Sandbox run'); return a[0]; }); }
  function rest(name) { return getJSON(SUPA + '/rest/v1/' + name + '?run_id=eq.' + encodeURIComponent(s.run.id) + '&order=created_at.desc', 5000); }
  function stateRun() { return getJSON(API + '?client_key=' + encodeURIComponent(KEY), 5000).then(function (j) { if (!j.data) throw Error('状态服务没有返回 data'); return j.data; }); }
  function diagnostic() { var rows = [['JavaScript', '✓ 已执行'], ['Supabase', s.diag.supabase], ['sandbox_runs', s.diag.run], ['模块数据库', s.diag.modules], ['sandbox-state（辅助层）', s.diag.state]]; return page('数据库连接诊断', 'DATABASE-DEBUG-20260929-14 · 直接定位前端、数据库和状态层', table(['检查项', '结果'], rows.concat(s.diag.details))); }
  function render() {
    nav.forEach(function (b) { b.classList.toggle('active', b.dataset.view === s.view); });
    if (!s.run) { app.innerHTML = diagnostic(); return; }
    app.innerHTML = (views[s.view] || overview)();
  }
  function overview() { var d = s.db; return page('商业博弈总览', '结果来自 Supabase 独立模块数据库 · Sandbox', '<div class="grid">' + [['Agent任务', (d.tasks || []).length, '条'], ['实验回测', (d.backtests || []).length, '个场景'], ['风险结果', (d.risks || []).length, '条'], ['学习记忆', (d.memories || []).length, '条'], ['市场信号', (d.market || []).length, '条'], ['广告关键词', ((d.ads || {}).keywords || []).length, '个']].map(function (x) { return '<div class="card"><div class="label">' + x[0] + '</div><div class="metric">' + x[1] + '</div><div class="label">' + x[2] + '</div></div>'; }).join('') + '</div><div class="card"><div class="label">Sandbox Run</div><div>状态：' + esc(s.run.status || 'ready') + ' · 更新时间：' + esc(s.run.updated_at || '') + '</div></div>'); }
  function market() { var d = s.db.market || []; return page('Web 市场情报', '直接读取 sandbox_market_signals', table(['观察','类型','强度','说明'], d.map(function (x) { return [x.name,x.signal_type,x.strength,x.detail]; }))); }
  function game() { var x = (s.db.game || [])[0] || {}; return page('商业博弈', '直接读取 sandbox_game_states', table(['变量','数值'], [['产品',x.product],['竞品',x.competitor],['场景',x.scenario],['竞品价格','¥'+x.competitor_price],['我方价格','¥'+x.our_price],['CPC','¥'+x.cpc],['CVR',(x.cvr || 0)+'%']])); }
  function ads() { var a=s.db.ads||{}; return page('广告 / 流量','直接读取广告模块独立数据库表', table(['投放计划','状态','商品','场景','日预算','出价策略'],(a.plans||[]).map(function(x){return[x.name,x.status,x.product,x.scene,'¥'+x.daily_budget,x.bid_strategy];})) + table(['关键词','类型','匹配','出价','展现','点击','CTR','成交','CVR','消耗','GMV','ROI','趋势'],(a.keywords||[]).map(function(x){return[x.keyword,x.keyword_type,x.match_type,'¥'+x.bid,x.impressions,x.clicks,x.ctr+'%',x.conversions,x.cvr+'%',x.spend,x.gmv,x.roi,x.trend];})) + table(['迁移类型','原关键词/场景','新关键词/场景','点击','成交','CVR','ROI','Agent结论','状态'],(a.moves||[]).map(function(x){return[x.move_type,x.source_keyword+' / '+x.source_scene,x.related_keyword+' / '+x.related_scene,x.clicks,x.conversions,x.cvr+'%',x.roi,x.agent_conclusion,x.status];})) + table(['人群','类型','行为','窗口','规模','覆盖','CVR','ROI','出价','溢价','重合'],(a.audiences||[]).map(function(x){return[x.name,x.audience_type,x.behavior,x.window_days+'天',x.size,x.coverage+'%',x.cvr+'%',x.roi,x.bid,x.premium+'%',x.overlap+'%'];})) + table(['人群组合','规模','重合','CVR','ROI','Agent结论'],(a.combos||[]).map(function(x){return[x.name,x.size,x.overlap+'%',x.cvr+'%',x.roi,x.agent_conclusion];})) + table(['创意','类型','标题','审核','展现','点击','CTR','成交','ROI','状态'],(a.creatives||[]).map(function(x){return[x.name,x.creative_type,x.title,x.audit_status,x.impressions,x.clicks,x.ctr+'%',x.conversions,x.roi,x.status];})) + table(['渠道','资源位','展现','点击','CTR','消耗','成交','CVR','GMV','ROI'],(a.placements||[]).map(function(x){return[x.channel,x.placement,x.impressions,x.clicks,x.ctr+'%',x.spend,x.conversions,x.cvr+'%',x.gmv,x.roi];})) + table(['地域','展现','点击','CTR','消耗','成交','CVR','ROI'],(a.regions||[]).map(function(x){return[x.region,x.impressions,x.clicks,x.ctr+'%',x.spend,x.conversions,x.cvr+'%',x.roi];})) + table(['时段','星期','展现','点击','CTR','CPC','成交','CVR','ROI'],(a.timeslots||[]).map(function(x){return[x.slot,x.weekday,x.impressions,x.clicks,x.ctr+'%',x.cpc,x.conversions,x.cvr+'%',x.roi];})) + table(['否定/屏蔽词','点击','消耗','成交','Agent结论','状态'],(a.negative||[]).map(function(x){return[x.keyword,x.clicks,x.spend,x.conversions,x.agent_conclusion,x.status];})) + table(['Agent动作','目标','原因','结果','状态'],(a.actions||[]).map(function(x){return[x.action_type,x.target,x.reason,x.result,x.status];})); }
  function experiments(){return page('实验与回测','直接读取 sandbox_backtests',table(['场景','轮数','ROI','风险','动作'],(s.db.backtests||[]).map(function(x){return[x.scenario,x.rounds,x.roi,x.risk,x.action];})));}
  function risk(){return page('风险控制器','直接读取 sandbox_risk_results',table(['风险指标','结果'],(s.db.risks||[]).map(function(x){return[x.metric,typeof x.value==='object'?JSON.stringify(x.value):x.value];})));}
  function jobs(){return page('任务监控','直接读取 sandbox_task_results',table(['任务ID','类型','状态','进度'],(s.db.tasks||[]).map(function(x){return[x.task_id,x.task_type,x.status,(x.progress||0)+'%'];})));}
  function memory(){return page('学习记忆','直接读取 sandbox_memories',table(['类型','内容','置信度','状态'],(s.db.memories||[]).map(function(x){return[x.memory_type,x.content,x.confidence,x.status];})));}
  var views={overview:overview,market:market,game:game,ads:ads,experiments:experiments,risk:risk,jobs:jobs,memory:memory};
  var adTables=['sandbox_ad_plans','sandbox_ad_units','sandbox_ad_keywords','sandbox_ad_keyword_moves','sandbox_ad_audiences','sandbox_ad_audience_combos','sandbox_ad_creatives','sandbox_ad_placements','sandbox_ad_regions','sandbox_ad_timeslots','sandbox_ad_negative_keywords','sandbox_ad_agent_actions'];
  async function load(){
    try {
      s.diag.supabase='请求 sandbox_runs 中…'; render();
      s.run=await directRun();
      s.diag.supabase='✓ 连接成功'; s.diag.run='✓ 找到 run '+s.run.id; render();
      var names=['sandbox_market_signals','sandbox_game_states','sandbox_backtests','sandbox_risk_results','sandbox_task_results','sandbox_memories'].concat(adTables);
      s.diag.modules='并行读取 '+names.length+' 个模块…'; render();
      var vals=await Promise.all(names.map(function(n){return rest(n).then(function(v){return{ok:true,name:n,value:v};}).catch(function(e){return{ok:false,name:n,error:e.message,value:[]};});}));
      var failed=vals.filter(function(x){return !x.ok;});
      s.db.market=vals[0].value; s.db.game=vals[1].value; s.db.backtests=vals[2].value; s.db.risks=vals[3].value; s.db.tasks=vals[4].value; s.db.memories=vals[5].value;
      s.db.ads={plans:vals[6].value,units:vals[7].value,keywords:vals[8].value,moves:vals[9].value,audiences:vals[10].value,combos:vals[11].value,creatives:vals[12].value,placements:vals[13].value,regions:vals[14].value,timeslots:vals[15].value,negative:vals[16].value,actions:vals[17].value};
      s.diag.modules=failed.length?'部分失败':'✓ 全部模块读取成功'; s.diag.details=failed.map(function(x){return[x.name,'❌ '+x.error];}); render();
      try { s.diag.state='连接中…'; render(); var p=await stateRun(); s.diag.state=p&&p.id===s.run.id?'✓ sandbox-state 已连接（辅助层）':'⚠ sandbox-state 返回的 run 不一致'; } catch(e) { s.diag.state='⚠ sandbox-state 不可用：'+e.message; }
      render();
    } catch(e) {
      s.diag.supabase=s.diag.supabase.indexOf('请求')===0?'❌ '+e.message:s.diag.supabase;
      s.diag.run=s.diag.run.indexOf('✓')===0?s.diag.run:'❌ '+e.message;
      s.error=e.message; console.error('DATABASE_CONNECT_ERROR',e); render();
    } finally { s.loading=false; }
  }
  nav.forEach(function(b){b.addEventListener('click',function(e){e.preventDefault();if(views[b.dataset.view]){s.view=b.dataset.view;location.hash=s.view;render();}});});
  addEventListener('hashchange',function(){s.view=location.hash.slice(1)||'overview';render();});
  app.innerHTML=page('数据库连接诊断','BOOT-DEBUG-20260929-14 · JavaScript 已启动，准备读取数据库', '<div class="card"><div class="notice">正在启动诊断…</div></div>');
  render();
  load();
  setInterval(function(){if(!document.hidden&&s.run)load();},5000);
})();