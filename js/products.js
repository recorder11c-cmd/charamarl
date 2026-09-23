// CHARAMARL 販売中グッズのカタログ（アーティストページ用）
// ※ index.html のヒーロー枠(FEATURED)は別に同じ内容を持っています。
//    商品を増やしたら両方を更新してください。
window.CM_PRODUCTS = [
  { id:'kagechiyo_hoodie', name:'メカニャンパーカー',      creator:'カゲチヨ',        price:14800, kind:'フルグラフィックパーカー', img:'./img/products_t/kagechiyo_hoodie_front.png', page:'./characters/kagechiyo-hoodie.html' },
  { id:'dino_canvas',      name:'旅する恐竜スーさん キャンバス',    creator:'DinoRenny',      price:3300,  kind:'キャンバスアート',        img:'./img/canvas/dino_kyoto.jpg',                 page:'./characters/dino-canvas.html' },
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
  // ピンズ（丸25mm）は絵柄12種から選ぶ商品だが、ここは**絵柄ごとに1行**で持つ。
  // artist.html は creator が作家名と一致した行だけを「買えるもの」に出すので、
  // creator:'12種の絵柄から' のような1行にまとめると、どの作家のページにも出ない。
  // （実際その状態で、カゲチヨさんのページがパーカー1点だけになっていた）
  // 単品¥1,800。?k= でその絵柄を選んだ状態のピンズページへ飛ぶ。
  { id:'pin_sue',          name:'ピンズ スー',               creator:'DinoRenny',      price:1800,  kind:'ピンズ（丸25mm）',        img:'./img/pins/sue.png',          page:'./characters/pins.html?k=sue&utm_source=charamarl_artist' },
  { id:'pin_mossun',       name:'ピンズ モッスン',            creator:'DinoRenny',      price:1800,  kind:'ピンズ（丸25mm）',        img:'./img/pins/mossun.png',       page:'./characters/pins.html?k=mossun&utm_source=charamarl_artist' },
  { id:'pin_putti',        name:'ピンズ プッチィ',            creator:'DinoRenny',      price:1800,  kind:'ピンズ（丸25mm）',        img:'./img/pins/putti.png',        page:'./characters/pins.html?k=putti&utm_source=charamarl_artist' },
  { id:'pin_yurucrazy',    name:'ピンズ ユルクレイジー',       creator:'CRAZY',          price:1800,  kind:'ピンズ（丸25mm）',        img:'./img/pins/yurucrazy.png',    page:'./characters/pins.html?k=yurucrazy&utm_source=charamarl_artist' },
  { id:'pin_danna',        name:'ピンズ だんな',              creator:'赤猫かるま',      price:1800,  kind:'ピンズ（丸25mm）',        img:'./img/pins/danna.png',        page:'./characters/pins.html?k=danna&utm_source=charamarl_artist' },
  { id:'pin_inkumo',       name:'ピンズ インクモ',            creator:"Ink'z Monster",  price:1800,  kind:'ピンズ（丸25mm）',        img:'./img/pins/inkumo.png',       page:'./characters/pins.html?k=inkumo&utm_source=charamarl_artist' },
  { id:'pin_mony',         name:'ピンズ モニィ',              creator:'morry',          price:1800,  kind:'ピンズ（丸25mm）',        img:'./img/pins/mony.png',         page:'./characters/pins.html?k=mony&utm_source=charamarl_artist' },
  { id:'pin_kg_kagechiyo', name:'ピンズ カゲチヨ',            creator:'カゲチヨ',        price:1800,  kind:'ピンズ（丸25mm）',        img:'./img/pins/kg_kagechiyo.png', page:'./characters/pins.html?k=kg_kagechiyo&utm_source=charamarl_artist' },
  { id:'pin_kg_kimi',      name:'ピンズ キミ',                creator:'カゲチヨ',        price:1800,  kind:'ピンズ（丸25mm）',        img:'./img/pins/kg_kimi.png',      page:'./characters/pins.html?k=kg_kimi&utm_source=charamarl_artist' },
  { id:'pin_kg_shigure',   name:'ピンズ シグレ',              creator:'カゲチヨ',        price:1800,  kind:'ピンズ（丸25mm）',        img:'./img/pins/kg_shigure.png',   page:'./characters/pins.html?k=kg_shigure&utm_source=charamarl_artist' },
  { id:'pin_kg_promu',     name:'ピンズ プロム',              creator:'カゲチヨ',        price:1800,  kind:'ピンズ（丸25mm）',        img:'./img/pins/kg_promu.png',     page:'./characters/pins.html?k=kg_promu&utm_source=charamarl_artist' },
  { id:'pin_kg_muchiko',   name:'ピンズ ムチコ',              creator:'カゲチヨ',        price:1800,  kind:'ピンズ（丸25mm）',        img:'./img/pins/kg_muchiko.png',   page:'./characters/pins.html?k=kg_muchiko&utm_source=charamarl_artist' },
];

// COLOR TAP（遊べるページ）。作家ページから「遊ぶ」導線を出すため
window.CM_TAPS = {
  'DinoRenny':['./tap/sue.html','./tap/putti.html','./tap/mossun.html','./tap/gotochi.html'],
  'MARU_GMC':['./tap/gmc.html'],
  'PHAGY':['./tap/moja.html'],
  'ちゅい':['./tap/ufoo.html'],
  'SAYoooooh':['./tap/dogooooo.html'],
  "Ink'z Monster":['./tap/inkumo.html'],
  'チンチロ':['./tap/blockma.html'],
  'CRAZY':['./tap/yurucrazy.html'],
  '赤猫かるま':['./tap/danna.html'],
  'カゲチヨ':['./tap/kagechiyo.html'],
  'CryptoSuperHeroes':['./tap/csh.html'],
  'morry':['./tap/mony.html'],
  'ハンナ':['./tap/rafu.html'],
  'ROKU':['./tap/junkeeees.html'],
  'DREAMER©':['./tap/ghost.html'],
};

// CHARAMARL RUN に出ているキャラ（run.html の CHARS のキー）。
// アクキーの id と同じ綴りなので、そのまま照合できる。
// ここにあるアクキーだけ、NFCでかざしたときに★オーナーモードへ行ける。
// 🔴 PUTTI と MOSSUN はアクキーがあるが RUN にいない＝オーナーモードは使えない。
//    2026-09-22、発表文を「RUNに出ているキャラのアクキーをかざすと」に直した理由がこれ。
//    RUN にキャラを足したら、ここと run.html の両方に足す。
window.CM_RUN_CHARS = ['sue','gmc','ufoo','kagechiyo','yurucrazy',
                       'dogooooo','inkumo','danna','blockma','mony'];
