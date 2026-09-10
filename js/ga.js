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
// 訪問者の種別をGA4に渡す（「外部のお客さんだけ」の数字を出すため）
//   visitor  … 一般の来場者
//   member   … ログインしたことがある端末（作家・出店者）
//   operator … 運営アカウント
// 一度ログインした端末は member のまま固定する。作家さん本人の閲覧を
// 外部顧客の母数から外すのが目的なので、ログアウト後も外れたままで正しい。
(function(){
  function apply(role){
    try{
      localStorage.setItem('cm_role', role);
      if(window.gtag) window.gtag('set','user_properties',{cm_role:role});
    }catch(e){}
  }
  var cached=null;
  try{ cached=localStorage.getItem('cm_role'); }catch(e){}
  if(cached) apply(cached);                       // 既知ならページ表示と同時に反映
  try{ if(sessionStorage.getItem('cm_role_done')) return; }catch(e){}
  fetch('/api/auth').then(function(r){return r.ok?r.json():null;}).then(function(d){
    try{ sessionStorage.setItem('cm_role_done','1'); }catch(e){}
    if(!d) return;
    if(d.user) apply(d.user.admin ? 'operator' : 'member');
    else if(!cached) apply('visitor');
  }).catch(function(){});
})();

// 共通イベント送信ヘルパー(内部端末ではgtag未定義のため自動的に無効)
window.cmEvent=function(name,params){try{if(window.gtag)window.gtag('event',name,params||{});}catch(e){}};

// ===== 送客ボタンの分割計測 =====
// /api/out は「何人送ったか」しか出せない(リダイレクト先が1本しか登録できないため)。
// 作家さんに「どこへ送ったのか」を返せるように、行き先の種別をGA4側で分ける。
//   instagram / x / shop(通販) / link(リンクまとめ) / sns(YouTube・TikTok・note・pixiv) / other
// ※ 種別はドメインで判定する。判定できないものは other に落とす(推測で振り分けない)。
window.cmOutKind=function(url){
  var h='';
  try{ h=new URL(url,location.href).hostname.replace(/^www\./,'').toLowerCase(); }catch(e){ return 'other'; }
  var is=function(re){ return re.test(h); };
  if(is(/(^|\.)instagram\.com$/)) return 'instagram';
  if(is(/(^|\.)(x\.com|twitter\.com|t\.co)$/)) return 'x';
  if(is(/(^|\.)(base\.shop|thebase\.in|theshop\.jp|booth\.pm|stores\.jp|suzuri\.jp|shop-pro\.jp|minne\.com|creema\.jp|myshopify\.com|bigcartel\.com|etsy\.com|fanbox\.cc|opensea\.io)$/)) return 'shop';
  if(is(/(^|\.)(lit\.link|linktr\.ee|potofu\.me|profcard\.info|bio\.link|linkin\.bio)$/)) return 'link';
  if(is(/(^|\.)(youtube\.com|youtu\.be|tiktok\.com|note\.com|pixiv\.net|nicovideo\.jp|threads\.net|bsky\.app)$/)) return 'sns';
  return 'other';
};
// 送客ボタンを押したときに呼ぶ。click_artist_{種別} と、横断集計用の click_artist を両方送る。
//   url   … 実際の行き先(/api/out?g=... ではなく、登録されている外部URLを渡すこと)
//   opt   … { place:'どの画面か', id:'作品ID', artist:'作家名' }
window.cmOutClick=function(url,opt){
  opt=opt||{};
  // サイト内リンク(作品ページ等)は送客ではない。混ぜると送客数の水増しになるので数えない。
  // ※ 静的ピンの一部は data-site が ./characters/*.html を指している
  var u=null; try{ u=new URL(url,location.href); }catch(e){}
  if(!u || u.origin===location.origin) return;
  var kind=window.cmOutKind(url), host='';
  try{ host=u.hostname.replace(/^www\./,''); }catch(e){}
  var p={ destination:kind, host:host, place:opt.place||'' };
  if(opt.id) p.item_id=opt.id;
  if(opt.artist) p.artist=opt.artist;
  if(window.cmEvent){ window.cmEvent('click_artist_'+kind,p); window.cmEvent('click_artist',p); }
};
