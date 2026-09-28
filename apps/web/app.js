const state={view:'overview'};
const signals=[
 ['竞争对手降价','PRICE_PRESSURE','高','竞品可见价格较昨日下降约6%','12分钟前'],
 ['流量成本上升','TRAFFIC_COST_PRESSURE','中高','同类广告CPC连续3个窗口上升','28分钟前'],
 ['需求变化','DEMAND_CHANGE','中','搜索/内容热度上升，尚未完成归因','41分钟前'],
 ['平台规则','PLATFORM_SIGNAL','待验证','发现活动/流量规则信息，等待官方来源确认','1小时前']
];
const jobs=[
 ['WEB-20260929-001','Web 市场扫描','RUNNING',72],
 ['BT-20260929-004','30×8 回测','COMPLETED',100],
 ['SYNC-20260929-002','店铺数据同步','RUNNING',37]
];
function page(title,sub,body){return '<h1 class="page-title">'+title+'</h1><div class="subtitle">'+sub+'</div>'+body}
function cards(items){return '<div class="grid">'+items.map(function(x){return '<div class="card"><div class="label">'+x[0]+'</div><div class="metric">'+x[1]+'</div><div class="label">'+(x[2]||'')+'</div></div>'}).join('')+'</div>'}
function render(){
 var a=document.getElementById('app'),h='';
 if(state.view==='overview'){
  h=page('商业博弈总览','把店铺数据、Web 外部市场、竞争、利润、库存、现金流、风险和执行放在同一个控制台。',
  cards([['当前市场状态','MIXED','置信度 0.62'],['今日广告消耗','¥1,284','预算 ¥2,000'],['当前 ROI','3.18','目标 ≥ 2.60'],['可执行策略','7','3 个需审批']])+
  '<div class="grid2"><div class="card"><h3 class="section-title">完整决策链</h3><div class="timeline">'+['平台/店铺数据','Web 市场情报','市场状态识别','竞争对手假设','利润/库存/现金流约束','候选策略与实验','Risk Controller','人工审批 / 自动执行','结果 → Memory'].map(function(x,i){return '<div class="event"><b>'+String(i+1).padStart(2,'0')+' · '+x+'</b><small>'+['已接入','已接入','运行中','有证据支持','已校验','已生成','已拦截风险动作','Read-only','持续学习'][i]+'</small></div>'}).join('')+'</div></div><div class="card"><h3 class="section-title">店铺</h3><div class="notice"><b>淘宝模拟店</b><br><span class="tag">taobao</span> GMV ¥12,860 · ROI 3.42</div><div class="notice"><b>拼多多模拟店</b><br><span class="tag">pinduoduo</span> GMV ¥8,420 · ROI 2.91</div></div></div>');
 }else if(state.view==='inputs'){
 h=page('博弈输入','把“我、对手、市场”拆开输入；系统再把三者合成博弈状态。',
 '<div class="grid2"><div class="card"><h3 class="section-title">① 我方</h3><table class="table"><tr><td>商品售价</td><td><input class="input" value="89"></td></tr><tr><td>毛利率</td><td><input class="input" value="32"></td></tr><tr><td>库存天数</td><td><input class="input" value="18"></td></tr><tr><td>可用现金</td><td><input class="input" value="42600"></td></tr><tr><td>CTR</td><td><input class="input" value="2.8"></td></tr><tr><td>CVR</td><td><input class="input" value="2.1"></td></tr><tr><td>ROI</td><td><input class="input" value="3.18"></td></tr></table></div><div class="card"><h3 class="section-title">② 对手</h3><table class="table"><tr><td>竞品价格</td><td><input class="input" value="83.7"></td></tr><tr><td>竞品CPC</td><td><input class="input" value="2.31"></td></tr><tr><td>竞品评价量</td><td><input class="input" value="12800"></td></tr><tr><td>竞品CVR</td><td><input class="input" value="4.8"></td></tr><tr><td>内容活跃度</td><td><input class="input" value="高"></td></tr><tr><td>供应稳定性</td><td><input class="input" value="高"></td></tr></table></div></div><div class="card" style="margin-top:12px"><h3 class="section-title">③ 市场</h3><table class="table"><tr><td>类目需求</td><td><input class="input" value="+11%"></td></tr><tr><td>平均CPC</td><td><input class="input" value="2.14"></td></tr><tr><td>类目CVR</td><td><input class="input" value="4.8%"></td></tr><tr><td>价格趋势</td><td><input class="input" value="-6%"></td></tr><tr><td>平台规则变化</td><td><input class="input" value="待验证"></td></tr></table><button class="primary" onclick="runGame()">运行博弈搜索</button><div id="gameResult" class="notice">等待运行。当前页面数据为 Sandbox 示例。</div></div>');
}else if(state.view==='market'){
  h=page('Web 市场情报','Web 不直接执行动作，只提供带时间戳、来源和可信度的市场证据。',
  '<div class="card"><h3 class="section-title">外部市场信号</h3><table class="table"><thead><tr><th>观察</th><th>状态</th><th>强度</th><th>证据</th><th>时间</th></tr></thead><tbody>'+signals.map(function(x){return '<tr><td>'+x[0]+'</td><td><span class="tag">'+x[1]+'</span></td><td>'+x[2]+'</td><td>'+x[3]+'</td><td>'+x[4]+'</td></tr>'}).join('')+'</tbody></table></div><div class="grid2"><div class="card"><h3 class="section-title">Web → Game Agent</h3><div class="notice">事实 → 市场信号 → 竞争假设 → 证据 → 商业博弈</div><div class="notice">每条信号保留 URL、标题、抓取时间、来源类型、可信度；过期信号自动降权。</div></div><div class="card"><h3 class="section-title">扫描范围</h3><span class="tag">竞品价格</span><span class="tag">活动/促销</span><span class="tag">类目趋势</span><span class="tag">流量成本</span><span class="tag">平台规则</span><span class="tag">内容热点</span></div></div>');
 }else if(state.view==='game'){
  h=page('商业博弈','输入我、对手、市场三组数据，寻找突破口；不是单纯 ROI 规则。',
  '<div class="grid2"><div class="card"><h3 class="section-title">对手与市场</h3><table class="table"><tr><th>变量</th><th>当前</th><th>变化</th></tr><tr><td>竞品价格</td><td>¥89</td><td class="danger">-6.1%</td></tr><tr><td>平均 CPC</td><td>¥2.14</td><td class="danger">+14.2%</td></tr><tr><td>类目 CVR</td><td>4.8%</td><td class="warning">-8.3%</td></tr><tr><td>库存覆盖</td><td>18 天</td><td class="positive">安全</td></tr><tr><td>现金可用</td><td>¥42,600</td><td class="positive">安全</td></tr></table></div><div class="card"><h3 class="section-title">策略候选</h3><button class="action"><b>提高核心词出价</b><br><span class="muted">+8% bid · ¥620/日 · APPROVAL_REQUIRED</span></button><button class="action"><b>保持预算</b><br><span class="muted">hold · ¥500/日 · AUTO_LIMITED</span></button><button class="action"><b>降低低毛利计划预算</b><br><span class="muted">-12% budget · ¥330/日 · APPROVAL_REQUIRED</span></button></div></div>');
 }else if(state.view==='breakthrough'){
 h=page('突破口','不是告诉你“做什么”，而是展示：为什么这里可能是突破口、对手会怎么反击、下一步怎么走。',
 '<div class="grid"><div class="card"><div class="label">当前突破口</div><div class="metric">转化 / 内容</div><div class="label">置信度 0.65 · 多轮搜索</div></div><div class="card"><div class="label">博弈鲁棒性</div><div class="metric">0.71</div><div class="label">对手反击后仍可继续</div></div><div class="card"><div class="label">对手威胁</div><div class="metric">3 类</div><div class="label">价格 / 流量 / 声誉</div></div></div>'+
 '<div class="grid2"><div class="card"><h3 class="section-title">博弈路径</h3><div class="event"><b>01 · 我方：CONTENT_ANGLE</b><small>利用注意力、好奇心改善有效点击</small></div><div class="event"><b>02 · 对手：改变内容打法</b><small>可能复制创意方向，概率需实验校准</small></div><div class="event"><b>03 · 我方：DIFFERENTIATE_PRODUCT</b><small>提高复制成本，避免继续单纯价格战</small></div><div class="event"><b>04 · 对手异常竞争分支</b><small>评价/举报/声誉攻击进入防御压力测试</small></div></div><div class="card"><h3 class="section-title">为什么不是直接降价？</h3><div class="notice">降价容易被复制，并可能把博弈带入价格战。</div><div class="notice">当前模型更关注“对手反击以后是否仍然成立”。</div><div class="notice"><span class="tag">事实</span> 当前为模拟数据；真实突破口必须用店铺数据和实验结果重新计算。</div></div></div>');
}else if(state.view==='ads'){
  h=page('广告 / 流量','统一观察预算、出价、CPC、CTR、CVR、ROI，并由风险层决定是否允许执行。',
  cards([['广告预算','¥2,000/日','上限'],['已消耗','¥1,284','64.2%'],['CPC','¥2.14','+14.2%'],['边际 ROAS','2.86','可继续测试']])+
  '<div class="card" style="margin-top:12px"><h3 class="section-title">预算使用率</h3><div class="bar"><i style="width:64.2%"></i></div><div class="subtitle">风险控制：单次预算调整 ≤ 12%，每日总消耗不得突破硬上限。</div></div>');
 }else if(state.view==='experiments'){
  h=page('实验与回测','先在模拟市场验证，再进入受控执行。',
  '<div class="card"><table class="table"><thead><tr><th>实验</th><th>状态</th><th>样本</th><th>结果</th></tr></thead><tbody><tr><td>出价 +8% vs hold</td><td>RUNNING</td><td>1,842 点击</td><td>边际 ROI 2.86</td></tr><tr><td>低毛利计划降预算</td><td>COMPLETED</td><td>14 天</td><td>现金占用下降 9.4%</td></tr><tr><td>竞争降价情景</td><td>BACKTEST</td><td>240 rounds</td><td>待报告</td></tr></tbody></table></div>');
 }else if(state.view==='risk'){
  h=page('Risk Controller','所有写操作都经过权限、预算、频率、置信度和库存/现金流约束。',
  cards([['ANALYZE_ONLY','只分析','当前默认'],['APPROVAL_REQUIRED','需审批','高风险动作'],['AUTO_LIMITED','受限自动','小幅调整'],['AUTO_DISABLED','禁止','突破硬限制']])+
  '<div class="notice">当前真实平台仍保持 Read-only；没有真实店铺凭证时使用 Sandbox/Mock，不允许把模拟结果伪装成真实执行。</div>');
 }else if(state.view==='jobs'){
  h=page('任务监控','所有长任务显示 QUEUED → RUNNING → COMPLETED / FAILED，并保留进度。',
  '<div class="card"><table class="table"><thead><tr><th>任务</th><th>类型</th><th>状态</th><th>进度</th></tr></thead><tbody>'+jobs.map(function(x){return '<tr><td>'+x[0]+'</td><td>'+x[1]+'</td><td>'+x[2]+'</td><td><div class="bar"><i style="width:'+x[3]+'%"></i></div><small>'+x[3]+'%</small></td></tr>'}).join('')+'</tbody></table></div>');
 }else{
  h=page('学习记忆','记录预期策略与实际结果，只有有足够证据时才更新策略权重。',
  '<div class="card"><table class="table"><thead><tr><th>策略</th><th>预期 ROI</th><th>实际 ROI</th><th>信号</th></tr></thead><tbody><tr><td>出价 +8%</td><td>3.10</td><td>2.86</td><td class="warning">低于预期</td></tr><tr><td>保持预算</td><td>2.70</td><td>2.74</td><td class="positive">符合</td></tr><tr><td>低毛利降预算</td><td>1.90</td><td>2.21</td><td class="positive">正向</td></tr></tbody></table></div>');
 }
 a.innerHTML=h;
}
function runGame(){
 var r=document.getElementById('gameResult'); if(!r)return;
 r.innerHTML='<b>正在搜索：</b>我方策略 → 对手反应 → 第二轮 → 异常竞争分支 → 突破口…';
 setTimeout(function(){r.innerHTML='<b>搜索完成（Sandbox）：</b><br>突破方向：内容/转化；第一步 CONTENT_ANGLE；预计对手反应：改变内容打法；第二步 DIFFERENTIATE_PRODUCT；若出现异常评价/举报信号，切换防御分支。<br><span class="tag">待真实数据验证</span>';},350);
}
document.querySelectorAll('.nav').forEach(function(b){b.onclick=function(){document.querySelectorAll('.nav').forEach(function(x){x.classList.remove('active')});b.classList.add('active');state.view=b.dataset.view;render()}});
render();