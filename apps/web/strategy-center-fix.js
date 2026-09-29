(function(){
  'use strict';
  var BASE='https://skuoxmrzlxhebzhfgbyn.supabase.co';
  var KEY='sb_publishable_u46tZ4GMUgwqSYhMJNFG8Q_IzYwl95T';
  var CLIENT='ecommerce-agent-sandbox-v1';
  var busy=false;

  function esc(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
  function activeContext(){
    var choices=document.querySelectorAll('.sc-choice'), pick=null;
    for(var i=0;i<choices.length;i++){
      if(String(choices[i].style.borderColor||'').indexOf('accent')>=0){pick=choices[i];break;}
    }
    if(!pick && choices.length) pick=choices[0];
    if(!pick) return {type:'AUTO',id:'',name:'自动选择策略',action:'',signal:'',goal:''};
    var type=pick.dataset.type||'AUTO', id=pick.dataset.id||'', list=type==='positive'?(window.EA_POSITIVE_ATTACK_LIBRARY||[]):type==='threat'?(window.EA_THREAT_LIBRARY||[]):(window.EA_HUMAN_BEHAVIOR_LIBRARY||[]);
    for(var j=0;j<list.length;j++) if(list[j].id===id) return {type:type,id:id,name:list[j].name||'',action:list[j].action||'',signal:list[j].signal||'',goal:list[j].goal||''};
    return {type:type,id:id,name:pick.textContent.trim(),action:'',signal:'',goal:''};
  }
  function setStatus(name,msg,runId){
    var old=document.getElementById('ea-sim-guard');
    if(!old){old=document.createElement('div');old.id='ea-sim-guard';old.className='card';old.style.cssText='position:sticky;top:8px;z-index:20;border:2px solid var(--accent);background:var(--panel);margin-bottom:10px';var app=document.getElementById('app');if(app)app.insertBefore(old,app.firstChild);}
    old.innerHTML='<b>'+esc(name)+'</b><div style="margin-top:6px">'+esc(msg)+'</div>'+(runId?'<div class="muted" style="margin-top:5px">Run: '+esc(runId)+'</div>':'');
  }
  function headers(){return {apikey:KEY,Authorization:'Bearer '+KEY,Accept:'application/json'};}
  function get(url){return fetch(url,{headers:headers(),cache:'no-store'}).then(function(r){return r.text().then(function(t){var d;try{d=JSON.parse(t)}catch(e){throw new Error('HTTP '+r.status+' 返回非JSON')};if(!r.ok)throw new Error('HTTP '+r.status);return d;});});}
  function run(runId){
    return get(BASE+'/rest/v1/sandbox_runs?select=id,status,agent_progress,state&id=eq.'+encodeURIComponent(runId)+'&limit=1').then(function(a){return a&&a[0];});
  }
  function waitRun(runId,attempt){
    run(runId).then(function(r){
      if(!r){setStatus('Sandbox 模拟','找不到新 Run，请重新点击。');busy=false;return;}
      if(r.status==='completed'){setStatus('Sandbox 模拟完成','10轮模拟已完成，正在刷新策略中心……',runId);setTimeout(function(){location.reload();},500);return;}
      if(r.status==='failed'){setStatus('Sandbox 模拟失败',(r.state&&r.state.error)||'Edge Function 执行失败',runId);busy=false;return;}
      setStatus('Sandbox 模拟运行中','已完成 '+Number(r.agent_progress||0)+'%，等待下一轮……',runId);
      if(attempt<90)setTimeout(function(){waitRun(runId,attempt+1);},1200);else{setStatus('Sandbox 模拟超时','Run仍在运行，请点击“读取最新模拟”。',runId);busy=false;}
    }).catch(function(e){setStatus('读取模拟状态失败',e.message,runId);busy=false;});
  }
  function start(){
    if(busy)return;
    busy=true;
    var ctx=activeContext();
    if(!ctx.id){setStatus('Sandbox 模拟','请先选择一个策略。');busy=false;return;}
    setStatus('正在启动 Sandbox 模拟','正在创建独立 Run，请不要重复点击……');
    fetch(BASE+'/functions/v1/sandbox-agent-runner',{
      method:'POST',headers:{apikey:KEY,Authorization:'Bearer '+KEY,'Content-Type':'application/json'},
      body:JSON.stringify({client_key:CLIENT,rounds:10,strategy_context:ctx})
    }).then(function(r){return r.text().then(function(t){var d;try{d=JSON.parse(t)}catch(e){d={}};if(!r.ok)throw new Error(d.error||('HTTP '+r.status));return d;});})
    .then(function(d){if(!d.run_id)throw new Error('Edge Function 未返回 run_id');setStatus('Sandbox 模拟运行中','Run 已创建，正在逐轮生成数据……',d.run_id);waitRun(d.run_id,0);})
    .catch(function(e){setStatus('Sandbox 模拟启动失败',e.message);busy=false;});
  }
  function refresh(){
    if(busy)return;
    busy=true;setStatus('读取最新 Sandbox 模拟','正在读取最近一次 Run……');
    get(BASE+'/rest/v1/sandbox_runs?select=id,status,agent_progress,state&client_key=eq.'+encodeURIComponent(CLIENT)+'&order=updated_at.desc&limit=1')
      .then(function(a){var r=a&&a[0];if(!r)throw new Error('没有找到 sandbox_runs');setStatus('最新 Sandbox 模拟',r.status==='completed'?'已完成，正在刷新……':'当前状态：'+r.status+' · '+Number(r.agent_progress||0)+'%',r.id);if(r.status==='completed')setTimeout(function(){location.reload();},400);else{busy=false;waitRun(r.id,0);}})
      .catch(function(e){setStatus('读取失败',e.message);busy=false;});
  }
  document.addEventListener('click',function(e){
    var t=e.target&&e.target.closest?e.target.closest('.sc-run'):null;
    if(t){e.preventDefault();e.stopImmediatePropagation();start();return;}
    t=e.target&&e.target.closest?e.target.closest('.sc-refresh'):null;
    if(t){e.preventDefault();e.stopImmediatePropagation();refresh();}
  },true);
})();