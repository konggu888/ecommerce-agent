(function(){'use strict';
  var M={
    RUNNING:'运行中',COMPLETED:'已完成',FAILED:'失败',STOP:'停止',CONTINUE:'继续',ALLOW:'通过',BLOCK:'拦截',
    CHANGE_KEYWORD:'调整关键词',CHANGE_TARGETING:'调整定向',CHANGE_CONTENT:'调整内容',CHANGE_AUDIENCE:'调整人群',CHANGE_CREATIVE:'调整创意',
    DEFEND_TRAFFIC:'防守流量',TRAFFIC_DEFENSE:'流量防守',HOLD:'保持观察',INCREASE_BUDGET:'增加预算',DECREASE_BUDGET:'降低预算',INCREASE_BID:'提高出价',DECREASE_BID:'降低出价',
    PRICE_WAR:'价格竞争',MATCH_PRICE:'跟价',RAISE_BID:'提高出价',SHIFT_CONTENT:'切换内容',IMPROVE_CONVERSION:'提升转化',
    ROUND_STARTED:'轮次开始',ROUND_COMPLETED:'轮次完成',AGENT_ACTION:'我方动作',OPPONENT_RESPONSE:'对手响应',RISK_CHECK:'风险检查',RISK_BLOCK:'风险拦截',RUN_CREATED:'模拟创建',RUN_COMPLETED:'模拟完成',RUN_FAILED:'模拟失败',MEMORY_UPDATED:'学习记忆更新',BACKTEST_COMPLETED:'回测完成'
  };
  function tr(s){var x=String(s==null?'':s);Object.keys(M).forEach(function(k){x=x.split(k).join(M[k]);});return x;}
  function cleanTable(table,removeNames){var th=table.querySelectorAll('thead th');var remove=[];for(var i=0;i<th.length;i++){if(removeNames.indexOf(th[i].textContent.trim())>=0)remove.push(i);}if(!remove.length)return;var rows=table.querySelectorAll('tr');for(var r=0;r<rows.length;r++){var cells=rows[r].children;for(var j=remove.length-1;j>=0;j--){if(cells[remove[j]])cells[remove[j]].remove();}}}
  function clean(){if(location.hash.slice(1)!=='jobs')return;var app=document.getElementById('app');if(!app)return;
    var all=app.querySelectorAll('*');for(var i=0;i<all.length;i++){if(all[i].children.length===0&&all[i].textContent)all[i].textContent=tr(all[i].textContent);}
    var tables=app.querySelectorAll('table');for(var t=0;t<tables.length;t++){cleanTable(tables[t],['任务ID','Payload']);}
    var cards=app.querySelectorAll('.notice');for(var c=0;c<cards.length;c++){var s=cards[c].textContent;if(s.indexOf('Run：')===0){var m=s.match(/状态：([^　]+).*进度：([^%]+%)/);if(m)cards[c].textContent='状态：'+tr(m[1])+'　进度：'+m[2];}}
    var h=app.querySelectorAll('h2');for(var k=0;k<h.length;k++){if(h[k].textContent.indexOf('事件流')>=0){h[k].textContent='事件流 · 业务时间线';}}
  }
  function run(){setTimeout(clean,20);setTimeout(clean,250);setTimeout(clean,900);}
  window.addEventListener('hashchange',run);new MutationObserver(run).observe(document.documentElement,{childList:true,subtree:true});run();
})();
