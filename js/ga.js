// CHARAMARL 計測 (GA4)
// 測定ID(G-XXXXXXXXXX)をセットすると有効化。空なら何もしない(検算用Redisカウンターは別系統で常時動作)
window.CM_GA_ID = 'G-PMSD6TMSJW';
(function(){
  var id = window.CM_GA_ID; if(!id) return;
  var s=document.createElement('script'); s.async=true;
  s.src='https://www.googletagmanager.com/gtag/js?id='+id;
  document.head.appendChild(s);
  window.dataLayer=window.dataLayer||[];
  window.gtag=function(){dataLayer.push(arguments);};
  gtag('js', new Date());
  gtag('config', id);
})();
// 共通イベント送信ヘルパー
window.cmEvent=function(name,params){try{if(window.gtag)window.gtag('event',name,params||{});}catch(e){}};
