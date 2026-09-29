(function(){
  'use strict';
  var VIEW='ad-bidding-game';
  var modes=[
    {id:'map',name:'① 投流博弈地图',desc:'把一次广告投放拆成目标、预算、出价、关键词、人群、素材、资源位、转化、对手响应和下一轮。',steps:['确定商品、利润线和投流目标','设定预算上限、单次成本线和停止线','选择关键词/人群/素材/资源位作为初始变量','小规模投放并记录真实可见指标','根据结果判断哪个变量产生了变化','把对手行为只作为“推测”输入下一轮','改变一个或一组关键变量再次验证'],branches:['成本上升但转化稳定','点击上升但转化下降','流量下降且竞争增强','数据无明显变化'],signals:['预算消耗','点击率CTR','转化率CVR','CPC/CPA','GMV/ROI','时间段变化'],defense:['设置预算与成本硬线','避免单一关键词、人群或资源位依赖','保留每轮投放时间线'],offense:['寻找新的关键词、人群、素材和资源位组合','优先测试可验证的真实增量'],mirror:['观察竞争变量后进行小规模合法跟随实验，不复制违规手段']},
    {id:'positive',name:'② 正向投流',desc:'通过真实商品、内容、素材、人群和渠道优势主动扩大有效流量。',steps:['确定最有价值的转化变量','小预算验证关键词/人群/素材','保留有效组合并逐步增加预算','观察边际ROI而不是只看平均ROI','扩大第二入口降低单点依赖','竞争加剧后转向新的增长变量'],branches:['有效组合继续扩量','扩量后边际ROI下降','对手进入同一流量入口','新增入口表现更好'],signals:['增量转化','边际ROI','新增流量占比','素材衰减','入口集中度'],defense:['设置扩量保护线','发现边际ROI持续下降时暂停扩量'],offense:['商品力、内容、素材、服务、关键词、人群和渠道的建设性组合'],mirror:['如果对手模仿素材，切换到更难复制的商品与内容变量']},
    {id:'defense',name:'③ 逆向防守',desc:'出现竞争压力或异常波动时，先保护预算、利润和数据，再寻找替代入口。',steps:['发现CPC、流量、转化或预算异常','确认是否超过历史正常波动','判断压力可能来自关键词、人群、资源位或时段','降低单点暴露并保留替代入口','设置成本和预算保护线','观察压力是否持续后再恢复投放'],branches:['竞争压力持续','压力短暂消失','某个入口异常而其他入口正常','无法确定原因'],signals:['成本突变','流量突变','转化突变','单入口占比','异常时间窗口'],defense:['预算隔离','入口分散','暂停异常变量','保留证据和时间线'],offense:['用替代关键词、人群、素材和渠道获得真实增量'],mirror:['只回应可观察的竞争变量，不根据不可见信息采取确定性结论']},
    {id:'continuous',name:'④ 连续投流',desc:'核心逻辑：我投 → 市场反馈 → 对手响应假设 → 我调整 → 再验证。',steps:['R1选择一个可验证动作','记录R1真实结果','提出对手响应假设并标记置信度','R2只改变关键变量','比较R1与R2的差异','更新对手模型','进入下一轮而不是追求一次性最优'],branches:['对手跟随','对手换入口','对手不响应','无法判断对手行为'],signals:['连续窗口变化','行为转折点','竞争强度','自身指标变化','对手可见信号'],defense:['每轮保留原始数据','不把推测写成事实','设置最大试错成本'],offense:['通过连续实验寻找对手难以长期跟随的真实优势'],mirror:['根据对手学习速度调整变量切换速度']},
    {id:'budget',name:'⑤ 预算博弈',desc:'围绕总预算、边际ROI和竞争强度动态分配资金。',steps:['设定总预算和最低利润保护线','给关键词/人群/素材/资源位初始预算','观察每个变量的边际ROI','削减低效增量而非机械停掉全部投放','把预算迁移到更稳定的增量入口','竞争升温时重新分配而不是盲目加钱'],branches:['高ROI但无法扩量','扩量后边际ROI下降','竞争导致成本上升','多个入口同时有效'],signals:['边际ROI','预算消耗速度','CPA','增量成交','预算集中度'],defense:['设置单入口预算上限','设置日消耗速度保护线','保留实验预算'],offense:['把预算从成熟变量逐步迁移到新增长变量'],mirror:['观察竞争升温后改变预算结构，而不是单纯竞价']},
    {id:'response',name:'⑥ 对手响应矩阵',desc:'把对手可能的响应拆成跟价、换词、抢人群、换素材、不响应等分支。',steps:['记录我方上一轮动作','列出可观察的市场变化','建立多个对手响应假设','为每个假设设置下一步观察信号','只根据新增证据提高或降低置信度','选择成本最低的验证动作'],branches:['跟价','换关键词','换人群','换素材','抢资源位','暂不响应','无法判断'],signals:['公开可见排名/价格变化','流量变化','自身成本变化','时间窗口同步性'],defense:['每个假设必须有验证信号','没有信号就标记“未知”'],offense:['优先进入竞争者难以快速复制的真实优势变量'],mirror:['可以研究对手的竞争机制，但不采取虚假、刷量、恶意举报等违规行为']},
    {id:'trap',name:'⑦ 投流陷阱识别',desc:'识别看起来有效、实际可能不可持续的投流结果。',steps:['发现指标突然变好或变坏','拆分点击、转化、成本和利润','比较平均ROI与边际ROI','检查是否存在单一变量依赖','检查是否只是短时窗口或活动效应','扩大前先做小规模复验','确认稳定后才进入扩量'],branches:['高点击低转化','高ROI低规模','扩量后ROI下降','短时异常好转','数据不足'],signals:['边际ROI','转化稳定性','窗口长度','入口集中度','成本波动'],defense:['设置最小样本和观察窗口','不因单个好指标直接放量'],offense:['寻找能同时改善流量质量和利润的变量'],mirror:['对手短期异常动作只作为观察信号，不立即跟随']},
    {id:'attack-cycle',name:'⑧ 投流攻防演变',desc:'把正向增长、防守、反击、再布局组合成完整循环。',steps:['建立正常投流状态','发现竞争或市场变化','切换防守保护利润','寻找对手没有覆盖的增长变量','小规模反击验证','对手学习后改变路线','重新建立新的投流组合'],branches:['竞争持续升级','对手退出','双方都改变入口','市场整体变化','原因不明确'],signals:['竞争强度','成本变化','流量结构','转化质量','对手行为的连续性'],defense:['先保利润和数据再追求份额','设置退出条件'],offense:['通过产品、内容、服务和新流量入口建立差异'],mirror:['只镜像竞争机制，不镜像违规方式']}
  ];
  function esc(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
  function getApp(){return document.getElementById('app');}
  function tagList(a,cls){var h='';for(var i=0;i<(a||[]).length;i++)h+='<span class="tag '+(cls||'')+'" style="margin:3px">'+esc(a[i])+'</span>';return h;}
  function detail(x){
    var s='<div class="card" style="border:2px solid var(--accent)"><span class="tag">广告博弈</span><h2>'+esc(x.name)+'</h2><div class="notice">'+esc(x.desc)+'</div>';
    s+='<div class="label">完整博弈过程</div><div style="display:grid;gap:7px">';
    for(var j=0;j<x.steps.length;j++)s+='<div class="notice"><b>第'+(j+1)+'步</b>　'+esc(x.steps[j])+'</div>';
    s+='</div><div class="label" style="margin-top:14px">对手可能分支</div><div class="notice">'+tagList(x.branches)+'</div>';
    s+='<div class="label" style="margin-top:14px">真实可见信号</div><div class="notice">'+tagList(x.signals)+'</div>';
    s+='<div class="label" style="margin-top:14px">三套行动方案</div><div class="grid">'+
      '<div class="notice"><b>① 防守</b><br>'+x.defense.map(esc).join('<br>')+'</div>'+ 
      '<div class="notice"><b>② 正向进攻</b><br>'+x.offense.map(esc).join('<br>')+'</div>'+ 
      '<div class="notice"><b>③ 镜像回应</b><br>'+x.mirror.map(esc).join('<br>')+'</div></div>';
    s+='<div class="card" style="margin-top:14px"><b>连续学习链</b><div style="font-size:18px;margin-top:6px">我方动作 → 实际反馈 → 对手响应假设 → 我方调整 → 再验证</div><div class="muted" style="margin-top:6px">对手不可见数据只能作为推测；页面不会把推测显示成事实。</div></div>';
    s+='<div class="card" style="margin-top:14px"><b>建议接入</b><div style="margin-top:6px">本模块的实验结果可以进入「实验与回测」，风险结果进入「风险控制器」，连续学习结果进入「连续博弈策略中心」。</div></div></div>';
    return s;
  }
  function render(){
    if(location.hash.slice(1)!==VIEW)return;
    var app=getApp();if(!app)return;
    var selected=modes[0];
    var html='<h1 class="page-title">广告投流博弈 <span style="font-size:16px;font-weight:500;color:var(--accent);margin-left:10px">我投 → 对手学 → 我再变</span></h1>'+
      '<div class="subtitle">广告投流专用博弈引擎 · 8层模块 · 防守 / 正向进攻 / 连续博弈 / 风险控制</div>'+
      '<div class="card" style="border-left:4px solid var(--accent)"><b>核心规则</b><div style="font-size:19px;margin-top:6px">我投 → 市场反馈 → 对手响应假设 → 我调整 → 再验证</div><div class="muted" style="margin-top:6px">平台通常只提供部分可见数据，因此对手动作、竞争强度和原因必须区分【可见】与【推测】。</div></div>'+
      '<div class="grid" style="margin:12px 0">'+
      '<div class="card"><div class="label">8个博弈模块</div><div class="metric">8</div></div>'+ 
      '<div class="card"><div class="label">行动层</div><div class="metric">防守 / 正攻 / 镜像</div></div>'+ 
      '<div class="card"><div class="label">核心状态</div><div class="metric">连续学习</div></div></div>'+
      '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:8px;margin:12px 0">';
    for(var i=0;i<modes.length;i++)html+='<button class="ad-game-choice" data-id="'+modes[i].id+'" style="text-align:left;padding:12px;border:1px solid '+(i===0?'var(--accent)':'var(--line)')+';border-radius:8px;background:transparent;color:inherit;cursor:pointer"><b>'+esc(modes[i].name)+'</b><div class="muted" style="margin-top:5px">'+esc(modes[i].desc)+'</div></button>';
    html+='</div><div id="ad-game-detail"></div>';
    app.innerHTML=html;
    document.getElementById('ad-game-detail').innerHTML=detail(selected);
    var bs=document.querySelectorAll('.ad-game-choice');
    for(var k=0;k<bs.length;k++)bs[k].addEventListener('click',function(){
      var id=this.dataset.id,x=modes[0];for(var z=0;z<modes.length;z++)if(modes[z].id===id)x=modes[z];
      document.getElementById('ad-game-detail').innerHTML=detail(x);
      for(var q=0;q<bs.length;q++)bs[q].style.borderColor=bs[q].dataset.id===id?'var(--accent)':'var(--line)';
    });
  }
  function install(){
    var sidebar=document.querySelector('.sidebar');if(!sidebar)return;
    var b=document.querySelector('[data-view="ad-bidding-game"]');
    if(!b){b=document.createElement('button');b.className='nav';b.dataset.view=VIEW;b.textContent='广告投流博弈';var anchor=document.querySelector('[data-view="ads"]');if(anchor&&anchor.parentNode)anchor.parentNode.insertBefore(b,anchor);else sidebar.appendChild(b);}
    b.onclick=function(){location.hash=VIEW;setTimeout(render,0);};
    if(location.hash.slice(1)===VIEW)render();
  }
  window.addEventListener('hashchange',function(){if(location.hash.slice(1)===VIEW)render();});
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install);else install();
})();
