// ギャラリーAPIができる前からサイトに並んでいる作品。
// /api/gallery には入っていないので、**このファイルが唯一の出どころ**。
//
// index.html のモーダル（ARTWORKS）と artist.html の「作品」欄が、両方ここを読む。
// 以前は index.html の中だけに書いてあり、artist.html からは見えなかった。
// そのため DinoRenny さんのページに SUE・PUTTI・MOSSUN が出ず、
// ♥と送客の合計もこの7点ぶん少なく出ていた（2026-09-19 に修正）。
//
// ■ artist は「リンク用の正式名」。表示はここに handle を足して組み立てる。
//   ここに「DinoRenny (@dino_renny)」のような表示名を入れると、
//   artist.html?a=... がその文字列のまま飛んで「作品が見つかりません」になる。
window.CM_LEGACY_WORKS = [
  { id:'gmc',      title:'レコマル',            artist:'MARU_GMC',  handle:'@maru_nft_',  cat:'CHARACTER',
    img:'./img/gallery/gmc.png',               site:'./characters/gmc.html',
    desc:'DJ MARUが生んだレコードのキャラクター「レコマル」。音楽とともに歩くレコード盤のボディがトレードマーク。公式カラーは赤。' },
  { id:'sue',      title:'SUE',                artist:'DinoRenny', handle:'@dino_renny', cat:'CHARACTER',
    img:'./img/colors_nobg/sue_red.png',       site:'./characters/sue.html',
    desc:'DinoRennyを代表するティラノサウルス「SUE」。力強い表情とポップなカラーが魅力の、市場1号店の看板キャラクター。' },
  { id:'putti',    title:'PUTTI',              artist:'DinoRenny', handle:'@dino_renny', cat:'CHARACTER',
    img:'./img/colors_nobg/putti_yellow.png',  site:'./characters/putti.html',
    desc:'空を自由に舞うプテラノドン「PUTTI」。元気いっぱいの表情と鮮やかなイエローが魅力。' },
  { id:'mossun',   title:'MOSSUN',             artist:'DinoRenny', handle:'@dino_renny', cat:'CHARACTER',
    img:'./img/colors_nobg/mossun_blue.png',   site:'./characters/mossun.html',
    desc:'海を泳ぐモササウルス「MOSSUN」。クールな表情と力強い存在感が魅力。' },
  { id:'roar',     title:'ROAR!',              artist:'DinoRenny', handle:'@dino_renny', cat:'ARTWORK',
    img:'./img/gallery/gallery_roar.png',      site:'https://x.com/dino_renny',
    desc:'ネオンピンクに吠えるDinoRenny。稲妻とビビッドカラーが弾ける、エネルギー全開のアートワーク。' },
  { id:'worldcup', title:'WORLD CUP EDITION',  artist:'DinoRenny', handle:'@dino_renny', cat:'ARTWORK',
    img:'./img/gallery/gallery_worldcup.png',  site:'https://x.com/dino_renny',
    desc:'サッカーユニフォーム姿のSUE。"PLAY FOR THE PRIDE" ―ワールドカップ・エディション。' },
  { id:'nodino',   title:'NO DINO NO LIFE',    artist:'DinoRenny', handle:'@dino_renny', cat:'ARTWORK',
    img:'./img/gallery/gallery_nodino.png',    site:'https://x.com/dino_renny',
    desc:'"NO DINO NO LIFE." 王冠をかぶったブラックダイナソーのエンブレム。EST.2023。' },
];

// index.html のモーダルが使う形（id をキーにした連想配列）に変換する。
window.CM_LEGACY_MAP = (function(){
  var m = {};
  (window.CM_LEGACY_WORKS || []).forEach(function(w){
    m[w.id] = {
      img: w.img, title: w.title, site: w.site, desc: w.desc, likes: 0,
      artist: 'by ' + w.artist + (w.handle ? ' (' + w.handle + ')' : ''),  // 表示用
      artistName: w.artist                                                 // リンク用
    };
  });
  return m;
})();
