(function(){
  'use strict';
  var M={
    CHANGE_KEYWORD:'调整关键词',CHANGE_TARGETING:'调整定向',CHANGE_CONTENT:'调整内容',CHANGE_AUDIENCE:'调整人群',CHANGE_CREATIVE:'调整创意',
    DEFEND_TRAFFIC:'防守流量',TRAFFIC_DEFENSE:'流量防守',PRICE_WAR:'价格竞争',VALUE_DEFENSE:'价值防守',VALUE_ATTACK:'价值竞争',
    HOLD:'保持观察',CHANGE_PRICE:'调整价格',INCREASE_BUDGET:'增加预算',DECREASE_BUDGET:'降低预算',INCREASE_BID:'提高出价',DECREASE_BID:'降低出价',
    MATCH_PRICE:'跟价',MATCH_OR_UNDERCUT_PRICE:'跟价或低价竞争',RAISE_BID:'提高出价',RAISE_BID_AND_DEFEND_TRAFFIC:'提高出价并防守流量',
    IMPROVE_CONVERSION:'提升转化',SHIFT_CONTENT:'切换内容',SHIFT_TO_CONTENT:'转向内容',CONTENT_VIDEO:'视频内容',CONTENT_MATRIX:'内容矩阵',
    NO_CLEAR_GAP:'暂未发现明确突破口',ALLOW:'通过',BLOCK:'拦截',STOP:'停止',CONTINUE:'继续',POSITIVE:'正向',NEGATIVE:'负向',
    INCONCLUSIVE:'结果不明确',OBSERVE:'观察',DEFENSIVE:'防守',MIXED:'混合',UNKNOWN:'未知',ANALYZE_ONLY:'仅分析',AUTO:'自动选择',
    OUR_AGENT:'我方智能体',CATARGETING:'定向投放',CA_TARGETING:'定向投放',TARGETING:'定向投放',catargeting:'定向投放',targeting:'定向投放',
    RISK_CONTROLLER:'风险控制器',RISK_CONTROLLER_BLOCK:'风险控制器拦截',SANDBOX:'沙盒模拟',RUNNING:'运行中',COMPLETED:'已完成',FAILED:'失败',
    INPUT:'输入',BREAKTHROUGH:'突破口',STRATEGY:'策略',EXECUTION:'执行',OPPONENT:'对手',MARKET:'市场',FEEDBACK:'反馈',LEARNING:'学习',
    STOP_SIGNAL:'停止信号',RISK_APPROVED:'风险通过',ACTUAL_OPPONENT_RESPONSE:'实际对手响应',NEXT_ACTION:'下一动作',CURRENT_ACTION:'当前动作',CURRENT_ROUND:'当前轮次',
    STRATEGY_SOURCE:'选择策略来源',POSITIVE_ATTACK:'正向策略',NEGATIVE_ATTACK:'负向策略',HUMAN_BEHAVIOR:'人性行为',
    KEYWORD:'关键词',TARGETING:'定向',AUDIENCE:'人群',CREATIVE:'创意',BUDGET:'预算',BID:'出价',CONTENT:'内容',TRAFFIC:'流量',PRICE:'价格'
  };
  function translate(s){
    var out=s;
    Object.keys(M).sort(function(a,b){return b.length-a.length;}).forEach(function(k){
      out=out.split(k).join(M[k]);
    });
    return out;
  }
  function walk(root){
    if(!root)return;
    var w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,null,false),n,arr=[];
    while(n=w.nextNode())arr.push(n);
    arr.forEach(function(x){var t=translate(x.nodeValue);if(t!==x.nodeValue)x.nodeValue=t;});
    root.querySelectorAll && root.querySelectorAll('[title],[aria-label],[data-label]').forEach(function(el){
      ['title','aria-label','data-label'].forEach(function(a){if(el.hasAttribute(a))el.setAttribute(a,translate(el.getAttribute(a)));});
    });
  }
  function run(){walk(document.getElementById('app')||document.body);}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run);else run();
  new MutationObserver(function(){run();}).observe(document.documentElement,{childList:true,subtree:true});
})();
