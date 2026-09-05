// CHARAMARL 販売中グッズのカタログ（アーティストページ用）
// ※ index.html のヒーロー枠(FEATURED)は別に同じ内容を持っています。
//    商品を増やしたら両方を更新してください。
window.CM_PRODUCTS = [
  { id:'kagechiyo_hoodie', name:'メカニャンパーカー',      creator:'カゲチヨ',        price:14800, kind:'フルグラフィックパーカー', img:'./img/products_t/kagechiyo_hoodie_front.png', page:'./characters/kagechiyo-hoodie.html' },
  { id:'dino_canvas',      name:'ご当地スー キャンバス',    creator:'DinoRenny',      price:3300,  kind:'キャンバスアート',        img:'./img/canvas/dino_kyoto.jpg',                 page:'./characters/dino-canvas.html' },
  { id:'sue',              name:'SUE',                     creator:'DinoRenny',      price:1500,  kind:'アクリルキーホルダー',    img:'./img/products_t/sue_red.png',                page:'./characters/sue.html' },
  { id:'putti',            name:'PUTTI',                   creator:'DinoRenny',      price:1500,  kind:'アクリルキーホルダー',    img:'./img/products_t/putti_yellow.png',           page:'./characters/putti.html' },
  { id:'mossun',           name:'MOSSUN',                  creator:'DinoRenny',      price:1500,  kind:'アクリルキーホルダー',    img:'./img/products_t/mossun_blue.png',            page:'./characters/mossun.html' },
  { id:'gmc',              name:'レコマル',                 creator:'MARU_GMC',       price:1500,  kind:'アクリルキーホルダー',    img:'./img/products_t/gmc_red.png',                page:'./characters/gmc.html' },
  { id:'ufoo',             name:'う〜ほ〜',                 creator:'ちゅい',          price:1500,  kind:'アクリルキーホルダー',    img:'./img/products_t/ufoo_white.png',             page:'./characters/ufoo.html' },
  { id:'dogooooo',         name:'dogooooo',                creator:'SAYoooooh',      price:1500,  kind:'アクリルキーホルダー',    img:'./img/products_t/dogooooo_pink.png',          page:'./characters/dogooooo.html' },
  { id:'inkumo',           name:'インクモ',                 creator:"Ink'z Monster",  price:1500,  kind:'アクリルキーホルダー',    img:'./img/products_t/inkumo_mono.png',            page:'./characters/inkumo.html' },
  { id:'danna',            name:'だんな',                   creator:'赤猫かるま',      price:1500,  kind:'アクリルキーホルダー',    img:'./img/products_t/danna_blue.png',             page:'./characters/danna.html' },
  { id:'blockma',          name:'ぶろっくま',               creator:'チンチロ',        price:1500,  kind:'アクリルキーホルダー',    img:'./img/products_t/blockma.png',                page:'./characters/blockma.html' },
  { id:'mony', name:'モニィ', creator:'morry', price:1500, kind:'アクリルキーホルダー', img:'./img/products_t/mony.png', page:'./characters/mony.html' },
  { id:'yurucrazy',        name:'ユルクレイジー',            creator:'CRAZY',          price:1500,  kind:'アクリルキーホルダー',    img:'./img/products_t/yurucrazy.png',              page:'./characters/yurucrazy.html' },
];

// COLOR TAP（遊べるページ）。作家ページから「遊ぶ」導線を出すため
window.CM_TAPS = {
  'DinoRenny':['./tap/sue.html','./tap/putti.html','./tap/mossun.html','./tap/gotochi.html'],
  'MARU_GMC':['./tap/gmc.html'],
  'ちゅい':['./tap/ufoo.html'],
  'SAYoooooh':['./tap/dogooooo.html'],
  "Ink'z Monster":['./tap/inkumo.html'],
  'チンチロ':['./tap/blockma.html'],
  'CRAZY':['./tap/yurucrazy.html'],
  'カゲチヨ':['./tap/kagechiyo.html'],
  'CryptoSuperHeroes':['./tap/csh.html'],
  'morry':['./tap/mony.html'],
  'ハンナ':['./tap/rafu.html'],
  'ROKU':['./tap/junkeeees.html'],
};
