(function(){
  'use strict';
  function removeLegacyGame(){
    var btn=document.querySelector('.nav[data-view="game"]');
    if(btn) btn.remove();
    if(location.hash==='#game'){
      location.hash='strategy-center';
      return true;
    }
    return false;
  }
  if(removeLegacyGame()) return;
  document.addEventListener('DOMContentLoaded',removeLegacyGame);
  window.addEventListener('hashchange',removeLegacyGame);
})();
