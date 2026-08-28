// CHARAMARL 計測 (GA4)
window.CM_GA_ID = 'G-PMSD6TMSJW';
(function(){
  // 内部トラフィック除外: ?internal=1 を一度開いた端末は以後計測しない(解除=?internal=0)
  try{
    var q=new URLSearchParams(location.search);
    if(q.get('internal')==='1'){localStorage.setItem('cm_internal','1');console.log('[CM] 内部端末として計測を停止しました');}
    if(q.get('internal')==='0'){localStorage.removeItem('cm_internal');console.log('[CM] 計測を再開しました');}
    if(localStorage.getItem('cm_internal')==='1') return;
  }catch(e){}
  var id = window.CM_GA_ID; if(!id) return;
  var s=document.createElement('script'); s.async=true;
  s.src='https://www.googletagmanager.com/gtag/js?id='+id;
  document.head.appendChild(s);
  window.dataLayer=window.dataLayer||[];
  window.gtag=function(){dataLayer.push(arguments);};
  gtag('js', new Date());
  gtag('config', id);
})();
// 共通イベント送信ヘルパー(内部端末ではgtag未定義のため自動的に無効)
window.cmEvent=function(name,params){try{if(window.gtag)window.gtag('event',name,params||{});}catch(e){}};
