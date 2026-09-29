(function(){
  'use strict';
  var EASEL={
    name:'Easel · 社交媒体运营 AI Agent',
    url:'https://github.com/ZJU-REAL/Easel',
    desc:'开源社交媒体运营 AI Agent：热点发现、账号画像、内容策划、内容制作、多平台发布与数据复盘。'
  };

  function cleanOldSlogan(){
    var nodes=document.querySelectorAll('*');
    for(var i=0;i<nodes.length;i++){
      var el=nodes[i];
      if(el.children.length===0 && /我变\s*→\s*对手学\s*→\s*我再变/.test(el.textContent||'')){
        var p=el.parentElement;
        if(p && /连续博弈座右铭/.test(p.textContent||'')) p.remove();
        else el.remove();
      }
    }
    var titles=document.querySelectorAll('.page-title');
    for(var j=0;j<titles.length;j++){
      titles[j].textContent=titles[j].textContent.replace(/\s*我变\s*→\s*对手学\s*→\s*我再变\s*/g,'');
    }
  }

  function addEasel(){
    if(location.hash.slice(1)!=='external-links') return;
    var app=document.getElementById('app');
    if(!app || app.querySelector('[data-easel-link]')) return;
    var cards=app.querySelectorAll('.card');
    var target=null;
    for(var i=0;i<cards.length;i++){
      if((cards[i].textContent||'').indexOf('免费 / 开源参考')>=0){target=cards[i];break;}
    }
    if(!target) return;
    var wrap=document.createElement('div');
    wrap.className='card';
    wrap.setAttribute('data-easel-link','1');
    wrap.style.marginTop='12px';
    wrap.innerHTML='<div class="label">新增参考</div><a href="'+EASEL.url+'" target="_blank" rel="noopener noreferrer" style="text-decoration:none;display:block;color:#fff !important;margin-top:10px"><b style="color:#fff !important">'+EASEL.name+'</b><div style="margin-top:6px;color:#fff;opacity:.78">'+EASEL.desc+'</div><div style="margin-top:8px;color:#fff">打开项目 →</div></a>';
    target.parentElement.insertBefore(wrap,target.nextSibling);
  }

  function run(){cleanOldSlogan();addEasel();}
  var observer=new MutationObserver(function(){run();});
  observer.observe(document.body,{childList:true,subtree:true});
  window.addEventListener('hashchange',function(){setTimeout(run,0);});
  setTimeout(run,0);
})();