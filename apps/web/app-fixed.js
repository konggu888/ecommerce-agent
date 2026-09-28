(function () {
  'use strict';

  var app = document.getElementById('app');
  var nav = Array.prototype.slice.call(document.querySelectorAll('.nav'));
  var state = { view: location.hash ? location.hash.slice(1) : 'overview', runs: 0 };

  var signals = [
    ['竞争对手降价','PRICE_PRESSURE','高','竞品可见价格较昨日下降约6%','12分钟前'],
    ['流量成本上升','TRAFFIC_COST_PRESSURE','中高','同类广告 CPC 连续3个窗口上升','28分钟前'],
    ['需求变化','DEMAND_CHANGE','中','搜索/内容热度上升，尚未完成归因','41分钟前'],
    ['平台规则','PLATFORM_SIGNAL','待验证','活动/流量规则信息等待官方来源确认','1小时前']
  ];

  function esc(v){return String(v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
  function page(title,sub,body){return '<h1 class="page-title">'+esc(title)+'</h1><div class="subtitle">'+esc(sub)+'</div>'+body;}
  function cards(items){return '<div class="grid">'+items.map(function(x){return '<div class="card"><div class="label">'+esc(x[0])+'</div><div class="metric">'+esc(x[1])+'</div><div class="label">'+esc(x[2]||'')+'</div></div>';}).join('')+'</div>';}
  function table(headers, rows){return '<div class="card"><table class="table"><thead><tr>'+headers.map(function(h){return '<th>'+esc(h)+'</th>';}).join('')+'</tr></thead><tbody>'+rows.map(function(r){return '<tr>'+r.map(function(c){return '<td>'+c+'</td>';}).join('')+'</tr>';}).join('')+'</tbody></table></div>';}

  function renderOverview(){
    return page('商业博弈总览','Sandbox 模拟数据 · 当前系统状态',cards([
      ['市场状态','MIXED','置信度 0.62'],['今日广告消耗','¥1,284','预算 ¥2,000'],['当前 ROI','3.18','目标 ≥ 2.60'],['可执行策略','7','3 个需审批']
    ])+'<div class="grid2"><div class="card"><h3 class="section-title">完整决策链</h3>'+['平台/店铺数据','Web 市场情报','市场状态识别','竞争对手假设','利润/库存/现金流约束','候选策略与实验','Risk Controller','人工审批 / 自动执行','结果 → Memory'].map(function(x,i){return '<div class="event"><b>'+String(i+1).padStart(2,'0')+' · '+esc(x)+'</b><small>'+['Sandbox 已接入','Sandbox 已接入','运行中','有证据支持','已校验','已生成','统一风险层','Read-only','持续学习'][i]+'</small></div>';}).join('')+'</div><div class="card"><h3 class="section-title">模拟店铺</h3><div class="notice"><b>淘宝模拟店</b><br><span class="tag">TAOBAO</span> GMV ¥12,860 · ROI 3.42</div><div class="notice"><b>拼多多模拟店</b><br><span class="tag">PINDUODUO</span> GMV ¥8,420 · ROI 2.91</div></div></div>');
  }

  function renderMarket(){return page('Web 市场情报','Sandbox 外部市场信号，不代表真实平台抓取',table(['观察','状态','强度','证据','时间'],signals.map(function(x){return [esc(x[0]),'<span class="tag">'+esc(x[1])+'</span>',esc(x[2]),esc(x[3]),esc(x[4])];}))+'<div class="grid2"><div class="card"><h3 class="section-title">Web → Game Agent</h3><div class="notice">事实 → 市场信号 → 竞争假设 → 证据 → 商业博弈</div></div><div class="card"><h3 class="section-title">扫描范围</h3><span class="tag">竞品价格</span> <span class="tag">活动/促销</span> <span class="tag">类目趋势</span> <span class="tag">流量成本</span> <span class="tag">平台规则</span> <span class="tag">内容热点</span></div></div>');}

  function renderGame(){return page('商业博弈','输入我、对手、市场，运行多轮 Sandbox Agent', '<div class="grid2"><div class="card"><h3 class="section-title">对手与市场</h3>'+table(['变量','当前','变化'],[['竞品价格','¥83.70','<span class="danger">-6.1%</span>'],['平均 CPC','¥2.14','<span class="danger">+14.2%</span>'],['类目 CVR','4.8%','<span class="warning">-8.3%</span>'],['库存覆盖','18 天','<span class="positive">安全</span>'],['现金可用','¥42,600','<span class="positive">安全</span>']]).replace('<div class="card">','').replace('</div>','')+'</div><div class="card"><h3 class="section-title">策略候选</h3><button class="action" data-action="run-agent"><b>运行 Sandbox Agent</b><br><span class="muted">多轮博弈 → 对手响应 → 突破口</span></button><button class="action" data-action="run-agent"><b>提高核心词出价</b><br><span class="muted">+8% bid · 先模拟</span></button><button class="action" data-action="run-agent"><b>降低低毛利计划预算</b><br><span class="muted">-12% budget · 先模拟</span></button></div></div><div class="card" style="margin-top:12px"><h3 class="section-title">Agent 输出</h3><div id="agentOutput" class="notice">等待运行。</div></div>');}

  function renderAds(){return page('广告 / 流量','模拟广告策略、边际 ROI 与预算变化',cards([['今日消耗','¥1,284','预算 ¥2,000'],['平均 CPC','¥2.14','竞价压力 +14.2%'],['CTR','3.1%','Sandbox'],['边际 ROI','1.86','进入观察区']])+'<div class="grid2"><div class="card"><h3 class="section-title">动作</h3><button class="action" data-action="run-agent">模拟 +10% 预算</button><button class="action" data-action="run-agent">模拟 -10% 预算</button><button class="action" data-action="run-agent">模拟降低竞价</button></div><div class="card"><h3 class="section-title">非线性反馈</h3><div class="event"><b>流量拥挤</b><small>预算越高，边际流量收益递减</small></div><div class="event"><b>竞价升级</b><small>CPC 随竞争压力上升</small></div><div class="event"><b>停止信号</b><small>边际 ROI 低于阈值时停止扩张</small></div></div></div>');}

  function renderExperiments(){var scenarios=['NORMAL','COMPETITION','TRAFFIC_COST','LOW_CVR','PRICE_WAR','LOW_STOCK','CASH_TIGHT','DEMAND_SURGE'];var rows=scenarios.map(function(s,i){var roi=[3.42,2.91,2.31,1.88,2.16,2.74,2.03,3.86][i];return ['<b>'+s+'</b>', '30', '¥'+(900+i*117), roi.toFixed(2), i%3===0?'HIGH':'MEDIUM', '<span class="tag">'+(i%2?'SWITCH':'CONTINUE')+'</span>'];});return page('实验与回测','8 场景 × 30 轮 · Sandbox 压力测试',cards([['场景','8','全部已生成'],['轮次','240','8 × 30'],['风险拦截','17','模拟统计'],['学习信号','128','模拟统计']])+table(['场景','轮数','投入','最终 ROI','风险','策略状态'],rows)+'<div class="card"><button class="primary" data-action="rerun">重新运行全部模拟</button><div id="runStatus" class="notice">尚未在本页面重新运行。</div></div>');}

  function renderRisk(){return page('07 · Risk Controller','统一执行前 + 执行后风险状态机',cards([['综合风险','MEDIUM','当前模拟'],['资金风险','0.18','低'],['单位经济','0.42','边际 ROI 下降'],['市场风险','0.58','拥挤/竞价'],['经营风险','0.08','库存安全'],['对手风险','0.61','反击可能']])+'<div class="grid2"><div class="card"><h3 class="section-title">执行前</h3><div class="event"><b>ALLOW / CONDITIONAL / BLOCK</b><small>先决定能不能做、能做多少</small></div><div class="event"><b>建议投入幅度：≤ 10%</b><small>高风险时降档</small></div></div><div class="card"><h3 class="section-title">执行后</h3><div class="event"><b>边际 ROI</b><small>低于 0.8 → 停止</small></div><div class="event"><b>现金 / 库存</b><small>约束触发 → 停止扩张</small></div><div class="event"><b>市场停止信号</b><small>触发 → 下一轮禁止激进扩张</small></div></div></div>');}

  function renderJobs(){return page('任务监控','Sandbox Agent / Web 扫描 / 回测任务状态',table(['任务','状态','进度','类型'],[['WEB-20260929-001','RUNNING','72%','Web 市场扫描'],['BT-20260929-004','COMPLETED','100%','30×8 回测'],['AGENT-20260929-005','READY','0%','商业博弈 Agent'],['RISK-20260929-006','READY','0%','Risk Controller']])+ '<div class="card"><button class="primary" data-action="rerun">刷新任务状态</button><div id="runStatus" class="notice">等待刷新。</div></div>');}

  function renderMemory(){return page('学习记忆','Agent 从每一轮结果中保存的模拟学习信号',table(['类型','内容','置信度','状态'],[['DECISION','降低低毛利计划预算','0.82','USEFUL'],['COUNTER_EVIDENCE','竞品降价后转化未继续下降','0.67','USEFUL'],['STOP_SIGNAL','边际 ROI 持续下降','0.91','USEFUL'],['BREAKTHROUGH','转换到内容/产品差异化','0.65','TESTING'],['OPPONENT','竞品可能跟随内容打法','0.58','HYPOTHESIS']])+ '<div class="card"><h3 class="section-title">学习闭环</h3><div class="notice">结果 → 评价 → 校准误差 → Memory → 下一轮策略</div></div>');}

  function renderBreakthrough(){return page('突破口','Agent 根据失败信号自动切换突破路径',cards([['当前突破口','转化 / 内容','Sandbox 置信度 0.65'],['博弈鲁棒性','0.71','对手反击后仍可继续'],['对手威胁','3 类','价格 / 流量 / 内容']])+'<div class="card"><h3 class="section-title">博弈路径</h3>'+['我方：CONTENT_ANGLE','对手：SHIFT_TO_CONTENT','我方：DIFFERENTIATE_PRODUCT','防御：进入 Risk Controller','如果连续失败：切换突破口'].map(function(x,i){return '<div class="event"><b>'+String(i+1).padStart(2,'0')+' · '+esc(x)+'</b><small>Sandbox 模拟路径</small></div>';}).join('')+'</div>');}

  function renderInputs(){return page('博弈输入','把“我、对手、市场”拆开输入，再交给 Agent','<div class="card"><div class="grid2"><div><h3 class="section-title">① 我方</h3>'+[['商品售价','89'],['毛利率','32%'],['库存天数','18'],['可用现金','42600'],['CTR','2.8%'],['CVR','2.1%']].map(function(x){return '<div class="event"><b>'+x[0]+'</b><input class="input" value="'+x[1]+'"></div>';}).join('')+'</div><div><h3 class="section-title">② 对手 / ③ 市场</h3>'+[['竞品价格','83.7'],['竞品 CPC','2.31'],['竞品 CVR','4.8%'],['类目需求','+11%'],['平均 CPC','2.14'],['价格趋势','-6%']].map(function(x){return '<div class="event"><b>'+x[0]+'</b><input class="input" value="'+x[1]+'"></div>';}).join('')+'</div></div><button class="primary" data-action="run-agent">运行 Sandbox Agent</button><div id="inputAgentOutput" class="notice">等待运行。</div></div>');}

  var renders={overview:renderOverview,market:renderMarket,game:renderGame,ads:renderAds,experiments:renderExperiments,risk:renderRisk,jobs:renderJobs,memory:renderMemory,breakthrough:renderBreakthrough,inputs:renderInputs};

  function runAgent(){state.runs++;var out='第 '+state.runs+' 次 Sandbox Agent 已完成：发现【边际 ROI 下降】→ 模拟对手反应 → 风险层复核 → 建议先降低低毛利预算 10%，再测试内容/转化突破口。<br><br><b>状态：</b>CONTINUE_WITH_LIMIT · <b>下一步：</b>小额验证 · <b>停止条件：</b>边际 ROI &lt; 0.8';['agentOutput','inputAgentOutput'].forEach(function(id){var e=document.getElementById(id);if(e)e.innerHTML=out;});}
  function render(){var fn=renders[state.view]||renders.overview;app.innerHTML=fn();nav.forEach(function(b){b.classList.toggle('active',b.getAttribute('data-view')===state.view);});window.scrollTo(0,0);}

  nav.forEach(function(btn){btn.addEventListener('click',function(e){e.preventDefault();state.view=btn.getAttribute('data-view');location.hash=state.view;render();});});
  document.addEventListener('click',function(e){var a=e.target.closest('[data-action]');if(!a)return;var action=a.getAttribute('data-action');if(action==='run-agent')runAgent();if(action==='rerun'){var s=document.getElementById('runStatus');if(s)s.innerHTML='已刷新：Sandbox 数据重新计算完成。时间：'+new Date().toLocaleTimeString();}});
  window.addEventListener('hashchange',function(){state.view=location.hash.slice(1)||'overview';render();});
  window.runSandboxAgent=runAgent;
  window.runSandboxBenchmark=function(){state.view='experiments';location.hash='experiments';render();var s=document.getElementById('runStatus');if(s)s.innerHTML='8 场景 × 30 轮模拟已重新运行。';};
  render();
})();
