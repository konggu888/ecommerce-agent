(function(){
'use strict';
var VIEW='ad-bidding-game';
var MODES=[
{id:'map',name:'投流博弈地图',desc:'从目标、预算、出价一直走到对手响应和下一轮。',steps:['确定商品、利润线、目标','设预算上限、成本线、停止线','选择关键词/人群/素材/资源位','小规模测试并记录可见数据','判断变化来自哪个变量','建立对手响应假设并标记为推测','改变变量再次验证'],branches:['成本上升但转化稳定','点击上升但转化下降','流量下降且竞争增强','没有明显变化']},
{id:'positive',name:'正向投流',desc:'用真实商品、内容、素材和渠道优势主动获得增量。',steps:['找到增长变量','小预算测试','确认增量','逐步放量','观察边际ROI','建立第二入口','对手进入后换增长变量'],branches:['扩量成功','扩量后边际ROI下降','对手进入','新入口表现更好']},
{id:'defense',name:'逆向防守',desc:'竞争压力出现时先保护预算、利润和数据。',steps:['发现异常','确认是否超过正常波动','定位关键词/人群/资源位/时段','降低单点依赖','设置保护线','持续观察','恢复或继续防守'],branches:['压力持续','压力消失','单入口异常','原因不明']},
{id:'continuous',name:'连续投流',desc:'每轮结果进入下一轮，形成真正的连续博弈。',steps:['R1我方动作','记录真实反馈','提出对手响应假设','R2改变一个关键变量','比较差异','更新对手模型','进入R3并重复'],branches:['对手跟随','对手换入口','对手不响应','无法判断']},
{id:'budget',name:'预算博弈',desc:'预算不是越多越好，而是动态分配。',steps:['设总预算和利润底线','分配初始预算','观察边际ROI','削减低效增量','把预算迁移到有效入口','竞争升温时重新分配'],branches:['高ROI无法扩量','扩量后ROI下降','竞争抬高成本','多个入口同时有效']},
{id:'bid',name:'出价博弈',desc:'研究出价变化、流量质量与竞争强度之间的关系。',steps:['建立基准出价','小幅调整','观察CPC/CPA/转化','判断是否存在跟价','测试替代入口','设置最高成本线'],branches:['对手跟价','对手不跟','成本突然上升','替代入口更优']},
{id:'keyword',name:'关键词博弈',desc:'关键词迁移、长尾扩张、否定词和对手跟随。',steps:['建立词池','区分高意向与探索词','小批量测试','发现有效关联词','扩展相邻场景','清理低价值词','对手跟随后迁移'],branches:['核心词竞争加剧','长尾词有效','对手跟随','词路衰减']},
{id:'audience',name:'人群博弈',desc:'通过人群组合和窗口迁移降低单一人群依赖。',steps:['基础人群','行为窗口测试','人群组合','观察重叠与转化','降低高竞争人群依赖','寻找新入口'],branches:['人群重叠','新客增长','竞争集中','转化下降']},
{id:'creative',name:'素材博弈',desc:'主图、短视频、标题、卖点持续迭代。',steps:['拆素材变量','一次改变关键变量','小规模测试','观察点击与转化','保留有效素材','对手模仿后改变表达变量'],branches:['点击高转化低','素材衰减','对手模仿','新素材胜出']},
{id:'time',name:'时段博弈',desc:'寻找竞争强度和流量质量的时间窗口。',steps:['建立全天基线','分时测试','识别竞争窗口','寻找低竞争有效窗口','调整预算权重','持续监测活动和季节变化'],branches:['高峰竞争','低峰有效','全天无明显差异','活动导致异常']},
{id:'placement',name:'资源位博弈',desc:'分散入口，避免单一资源位依赖。',steps:['建立资源位基线','测试多个入口','比较成本和质量','削减低效位置','增加有效入口','竞争进入后重新分散'],branches:['单点高效','多点均衡','竞争集中','资源位衰减']},
{id:'trap',name:'投流陷阱识别',desc:'识别看起来有效但不可持续的投流结果。',steps:['发现指标突然变化','拆分点击/转化/成本/利润','比较平均与边际ROI','检查单变量依赖','检查时间窗口','小规模复验','确认稳定后扩量'],branches:['高点击低转化','高ROI低规模','扩量后下降','短期异常','数据不足']},
{id:'cycle',name:'投流攻防演变',desc:'正向增长→防守→反击→再布局。',steps:['建立正常状态','发现竞争变化','切换防守','寻找新增长变量','小规模验证','对手学习','改变路线重新布局'],branches:['竞争升级','对手退出','双方换入口','市场整体变化']}
];
function esc(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function app(){return document.getElementById('app');}
function detail(m){
 var h='<div class="card" style="border:2px solid var(--accent)"><span class="tag">当前博弈</span><h2>'+esc(m.name)+'</h2><div class="notice">'+esc(m.desc)+'</div>';
 h+='<div class="label">博弈链</div><div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center">';
 for(var i=0;i<m.steps.length;i++)h+='<div class="notice" style="flex:1;min-width:150px"><b>R'+(i+1)+'</b><br>'+esc(m.steps[i])+'</div>'+(i<m.steps.length-1?'<b>→</b>':'');
 h+='</div><div class="grid" style="margin-top:14px"><div class="notice"><b>对手可能响应</b><br>'+m.branches.map(esc).join('<br>')+'</div><div class="notice"><b>我方防守</b><br>保护预算与利润线<br>降低单点依赖<br>保留时间线和原始数据<br>无法验证时标记“未知”</div><div class="notice"><b>我方正向进攻</b><br>测试新关键词/人群/素材<br>扩大真实增量<br>建立第二入口<br>优先寻找难复制的商品与内容优势</div></div>';
 h+='<div class="notice" style="margin-top:12px"><b>镜像回应</b><br>只研究和回应可观察的竞争机制；不复制刷量、虚假评价、恶意举报等违规方式。</div></div>';
 return h;
}
function render(){if(location.hash.slice(1)!==VIEW)return;var a=app();if(!a)return;var html='<h1 class="page-title">广告投流博弈 <span style="color:var(--accent);font-size:16px">我投 → 对手学 → 我再变</span></h1><div class="subtitle">广告专用连续博弈引擎 · 不是广告数据页，而是“动作—响应—分支—下一动作”推演页</div>';
 html+='<div class="card" style="border-left:4px solid var(--accent)"><b>核心状态链</b><div style="font-size:20px;margin-top:7px">我方动作 → 市场可见反馈 → 对手响应假设 → 我方调整 → 再验证</div><div class="muted" style="margin-top:6px">对手不可见数据一律标记为“推测”，不把推测当事实。</div></div>';
 html+='<div class="grid" style="margin:12px 0"><div class="card"><div class="label">博弈模块</div><div class="metric">'+MODES.length+'</div></div><div class="card"><div class="label">行动方式</div><div class="metric">防守 / 正攻 / 镜像</div></div><div class="card"><div class="label">核心循环</div><div class="metric">R1 → R2 → R3 → …</div></div></div>';
 html+='<div class="label">选择博弈模型</div><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px">';
 MODES.forEach(function(m,i){html+='<button class="ad-v2-choice" data-i="'+i+'" style="text-align:left;padding:14px;border:2px solid '+(i===0?'var(--accent)':'var(--line)')+';border-radius:10px;background:transparent;color:inherit;cursor:pointer"><b>'+esc(m.name)+'</b><div class="muted" style="margin-top:5px">'+esc(m.desc)+'</div></button>';});
 html+='</div><div id="ad-v2-detail" style="margin-top:14px"></div>';a.innerHTML=html;var d=document.getElementById('ad-v2-detail');d.innerHTML=detail(MODES[0]);document.querySelectorAll('.ad-v2-choice').forEach(function(b){b.onclick=function(){var i=Number(this.dataset.i);d.innerHTML=detail(MODES[i]);document.querySelectorAll('.ad-v2-choice').forEach(function(x){x.style.borderColor='var(--line)'});this.style.borderColor='var(--accent)';};});}
function boot(){if(location.hash.slice(1)===VIEW)render();}
window.addEventListener('hashchange',boot);if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
})();
