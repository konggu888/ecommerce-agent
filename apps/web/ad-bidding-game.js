(function(){
  'use strict';
  var VIEW='ad-bidding-game';
  var modes=[
    {id:'positive',name:'正向投流',desc:'通过关键词、人群、素材、预算、出价和时段组合主动扩大有效流量。',steps:['确定商品与核心目标','筛选高意向关键词/人群','小预算测试素材与出价','观察点击率、转化率、ROI','把有效组合逐步放量','对手响应后切换新的增长变量']},
    {id:'reverse',name:'逆向投流',desc:'识别竞争对手可能造成的流量压力，并设计合规的防守与替代入口。',steps:['发现流量异常或竞争加剧','判断压力来自关键词/人群/资源位/时段','降低单一入口依赖','建立替代关键词与人群','调整预算和出价保护利润','观察对手是否继续跟随']},
    {id:'continuous',name:'连续投流博弈',desc:'把每次投放结果变成下一轮策略输入。核心不是一次最优，而是持续改变。',steps:['我方选择动作','市场出现结果','观察对手可能响应','记录真实可见信号','更新对手模型','我方改变下一轮路线','重复验证']},
    {id:'budget',name:'预算博弈',desc:'围绕预算、边际ROI和竞争强度进行动态分配。',steps:['设定总预算和保护线','按渠道/关键词分配初始预算','观察边际ROI变化','降低低效消耗','把增量预算给有效变量','出现竞争升温时重新分配']},
    {id:'bid',name:'出价博弈',desc:'围绕出价变化、流量质量和竞争强度建立动态响应。',steps:['建立基准出价','小幅调整','观察流量与成本变化','识别是否存在跟价/抬价','寻找替代流量入口','设置最高成本和停止线']},
    {id:'keyword',name:'关键词博弈',desc:'围绕核心词、长尾词、场景词和否定词进行持续迁移。',steps:['建立关键词池','区分高意向与探索词','测试小批量流量','发现有效关联词','扩展相邻场景','加入低价值词否定规则','对手跟随后再次换入口']},
    {id:'audience',name:'人群博弈',desc:'通过人群组合、窗口和重叠控制寻找竞争压力较小的有效人群。',steps:['建立基础人群','测试行为窗口','组合人群变量','观察重叠与转化','降低高竞争人群依赖','寻找新的人群入口']},
    {id:'creative',name:'素材博弈',desc:'通过主图、短视频、标题和卖点不断测试，而不是长期暴露单一素材。',steps:['建立素材变量','一次只改变关键变量','小规模测试','观察点击与转化','保留有效素材','对手模仿后切换表达变量']},
    {id:'time',name:'时段博弈',desc:'利用不同时间窗口测试竞争强度和流量质量。',steps:['建立全天基线','分时段测试','识别高竞争窗口','寻找低竞争有效窗口','调整预算权重','持续监测季节与活动变化']},
    {id:'placement',name:'资源位博弈',desc:'比较不同资源位的流量成本和转化质量，避免单点依赖。',steps:['建立资源位基线','测试多个入口','比较成本与质量','削减低效资源位','增加有效入口','对手进入后重新分散']},
    {id:'defense',name:'投流防守',desc:'发现恶意消耗、异常流量或竞争冲击时先保护预算、利润和数据。',steps:['识别异常信号','确认是否超过正常波动','保护预算与成本线','隔离异常变量','保留证据和时间线','恢复正常投放并复盘']},
    {id:'counter',name:'镜像反制',desc:'可以回应对手使用的竞争机制，但只使用真实商品、真实投放和平台允许的方法。',steps:['识别对方竞争变量','确认我方是否具备真实优势','在同一变量做小规模实验','比较结果','发现无优势立即退出','转向对手难以复制的变量']}
  ];
  function esc(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
  function getApp(){return document.getElementById('app');}
  function render(){
    if(location.hash.slice(1)!==VIEW)return;
    var app=getApp(); if(!app)return;
    var selected=modes[0];
    var html='<h1 class="page-title">广告投流博弈 <span style="font-size:16px;font-weight:500;color:var(--accent);margin-left:10px">我投 → 对手响应 → 我变</span></h1>'+
      '<div class="subtitle">独立广告博弈层 · 正向投流 / 逆向防守 / 连续博弈 / 预算 / 出价 / 关键词 / 人群 / 素材</div>'+
      '<div class="card" style="border-left:4px solid var(--accent)"><b>广告投流博弈原则</b><div style="font-size:18px;margin-top:6px">我投 → 市场反馈 → 对手响应 → 我调整 → 再验证</div><div class="muted" style="margin-top:5px">平台通常只提供部分可见数据，因此对手动作必须标记为“推测”，不能把不可见数据当成事实。</div></div>'+
      '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px;margin:12px 0">';
    for(var i=0;i<modes.length;i++) html+='<button class="ad-game-choice" data-id="'+modes[i].id+'" style="text-align:left;padding:12px;border:1px solid '+(i===0?'var(--accent)':'var(--line)')+';border-radius:8px;background:transparent;color:inherit;cursor:pointer"><b>'+esc(modes[i].name)+'</b><div class="muted" style="margin-top:5px">'+esc(modes[i].desc)+'</div></button>';
    html+='</div><div id="ad-game-detail"></div>';
    app.innerHTML=html;
    function detail(x){
      var s='<div class="card" style="border:2px solid var(--accent)"><span class="tag">广告博弈</span><h2>'+esc(x.name)+'</h2><div class="notice">'+esc(x.desc)+'</div><div class="label">完整博弈过程</div>';
      for(var j=0;j<x.steps.length;j++) s+='<div class="notice" style="margin-top:7px"><b>第'+(j+1)+'步</b>　'+esc(x.steps[j])+(j<x.steps.length-1?'　<span class="muted">↓</span>':'')+'</div>';
      s+='<div class="label" style="margin-top:14px">三套输出</div><div class="grid">'+
        '<div class="notice"><b>① 防守</b><br>预算保护、成本线、异常监测、入口分散、证据留存。</div>'+ 
        '<div class="notice"><b>② 正向进攻</b><br>关键词、人群、素材、商品、内容和渠道的真实增量实验。</div>'+ 
        '<div class="notice"><b>③ 镜像回应</b><br>可以回应竞争机制，但不复制刷量、虚假评价、恶意举报等违规方式。</div></div>'+ 
        '<div class="card" style="margin-top:14px;background:rgba(255,180,0,.06)"><b>连续学习</b><div style="font-size:17px;margin-top:5px">本轮动作 → 实际反馈 → 对手响应假设 → 下一轮变化</div></div></div>';
      return s;
    }
    document.getElementById('ad-game-detail').innerHTML=detail(selected);
    var bs=document.querySelectorAll('.ad-game-choice');
    for(var k=0;k<bs.length;k++)bs[k].addEventListener('click',function(){
      var id=this.dataset.id,x=modes[0];for(var z=0;z<modes.length;z++)if(modes[z].id===id)x=modes[z];
      document.getElementById('ad-game-detail').innerHTML=detail(x);
      for(var q=0;q<bs.length;q++)bs[q].style.borderColor=bs[q].dataset.id===id?'var(--accent)':'var(--line)';
    });
  }
  function install(){
    var sidebar=document.querySelector('.sidebar'); if(!sidebar)return;
    if(!document.querySelector('[data-view="ad-bidding-game"]')){
      var b=document.createElement('button');b.className='nav';b.dataset.view=VIEW;b.textContent='广告投流博弈';
      var anchor=document.querySelector('[data-view="ads"]');
      if(anchor&&anchor.parentNode)anchor.parentNode.insertBefore(b,anchor.nextSibling);else sidebar.appendChild(b);
      b.addEventListener('click',function(){location.hash=VIEW;setTimeout(render,0);});
    }
    if(location.hash.slice(1)===VIEW)render();
  }
  window.addEventListener('hashchange',function(){if(location.hash.slice(1)===VIEW)render();});
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install);else install();
})();