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
  // CANVAS ここから（tools/build_canvas.py が書く。手で直さない）
  { id:"cv_inkz_nakayoshi", name:"仲良し キャンバス", creator:"Ink'z Monster", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/inkz_nakayoshi.webp", page:"./characters/canvas-inkz-monster.html?w=inkz_nakayoshi&utm_source=charamarl_artist", gid:"gb83e96e0f1a3" },
  { id:"cv_inkz_mono", name:"Ink'z Mönster（モノクロ） キャンバス", creator:"Ink'z Monster", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/inkz_mono.webp", page:"./characters/canvas-inkz-monster.html?w=inkz_mono&utm_source=charamarl_artist", gid:"g13fdc199965d" },
  { id:"cv_inkz_softcream", name:"ソフトクリーム キャンバス", creator:"Ink'z Monster", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/inkz_softcream.webp", page:"./characters/canvas-inkz-monster.html?w=inkz_softcream&utm_source=charamarl_artist", gid:"g4397fd9bf8cf" },
  { id:"cv_dogooooo_02", name:"dogooooo 02 キャンバス", creator:"SAYoooooh", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/dogooooo_02.webp", page:"./characters/canvas-sayoooooh.html?w=dogooooo_02&utm_source=charamarl_artist", gid:"g2178e075ce32" },
  { id:"cv_dogooooo_03", name:"dogooooo 03 キャンバス", creator:"SAYoooooh", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/dogooooo_03.webp", page:"./characters/canvas-sayoooooh.html?w=dogooooo_03&utm_source=charamarl_artist", gid:"g8bb35b15394e" },
  { id:"cv_hanna_takou", name:"多幸 キャンバス", creator:"ハンナ", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/hanna_takou.webp", page:"./characters/canvas-hanna.html?w=hanna_takou&utm_source=charamarl_artist", gid:"g804bc204be01" },
  { id:"cv_csh_pizzaboy", name:"Pizza Boy キャンバス", creator:"CryptoSuperHeroes", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/csh_pizzaboy.webp", page:"./characters/canvas-cryptosuperheroes.html?w=csh_pizzaboy&utm_source=charamarl_artist", gid:"g4df484fa9830" },
  { id:"cv_morry_hishochi", name:"わたしの避暑地 キャンバス", creator:"morry", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/morry_hishochi.webp", page:"./characters/canvas-morry.html?w=morry_hishochi&utm_source=charamarl_artist", gid:"gf0e1e125a451" },
  { id:"cv_utsu_1", name:"無題 キャンバス", creator:"恋するウツウツ", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/utsu_1.webp", page:"./characters/canvas-koisuru-utsuutsu.html?w=utsu_1&utm_source=charamarl_artist", gid:"g412eb34c5915" },
  { id:"cv_utsu_2", name:"無題 キャンバス", creator:"恋するウツウツ", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/utsu_2.webp", page:"./characters/canvas-koisuru-utsuutsu.html?w=utsu_2&utm_source=charamarl_artist", gid:"g5e35f3d594ad" },
  { id:"cv_utsu_3", name:"無題 キャンバス", creator:"恋するウツウツ", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/utsu_3.webp", page:"./characters/canvas-koisuru-utsuutsu.html?w=utsu_3&utm_source=charamarl_artist", gid:"gfb4ca63687c3" },
  { id:"cv_utsu_4", name:"無題 キャンバス", creator:"恋するウツウツ", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/utsu_4.webp", page:"./characters/canvas-koisuru-utsuutsu.html?w=utsu_4&utm_source=charamarl_artist", gid:"g3a22ef608936" },
  { id:"cv_tk_franken", name:"TKchan（フランケンシュタイン） キャンバス", creator:"AKIRA", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/tk_franken.webp", page:"./characters/canvas-akira.html?w=tk_franken&utm_source=charamarl_artist", gid:"g3fdcece8a934" },
  { id:"cv_tk_wolf", name:"TKchan（狼男） キャンバス", creator:"AKIRA", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/tk_wolf.webp", page:"./characters/canvas-akira.html?w=tk_wolf&utm_source=charamarl_artist", gid:"g9b034d4c1eb0" },
  { id:"cv_tk_yamanba", name:"TKchan（ヤマンバ） キャンバス", creator:"AKIRA", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/tk_yamanba.webp", page:"./characters/canvas-akira.html?w=tk_yamanba&utm_source=charamarl_artist", gid:"g85b3157f46f4" },
  { id:"cv_tk_vampire", name:"TKchan（ヴァンパイア） キャンバス", creator:"AKIRA", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/tk_vampire.webp", page:"./characters/canvas-akira.html?w=tk_vampire&utm_source=charamarl_artist", gid:"geaac1e79e5c0" },
  { id:"cv_blockma", name:"ぶろっくま キャンバス", creator:"チンチロ", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/blockma.webp", page:"./characters/canvas-chinchillo.html?w=blockma&utm_source=charamarl_artist", gid:"g53905fbdc117" },
  { id:"cv_karuki_hamburger", name:"てなわんちゃん（ハンバーガー） キャンバス", creator:"かるき", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/karuki_hamburger.webp", page:"./characters/canvas-karuki.html?w=karuki_hamburger&utm_source=charamarl_artist", gid:"g6cf6aa1404f1" },
  { id:"cv_karuki_tsuruko", name:"日本の夜明けよ♡つるこちゃん キャンバス", creator:"かるき", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/karuki_tsuruko.webp", page:"./characters/canvas-karuki.html?w=karuki_tsuruko&utm_source=charamarl_artist", gid:"g38423e962565" },
  { id:"cv_santama_kagechiyo", name:"サンタマ探検！メカニャン「カゲチヨ」 キャンバス", creator:"カゲチヨ", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/santama_kagechiyo.webp", page:"./characters/canvas-kagechiyo.html?w=santama_kagechiyo&utm_source=charamarl_artist", gid:"g8d69be3f1e86" },
  { id:"cv_santama_kimi", name:"サンタマ探検！メカニャン「キミ」 キャンバス", creator:"カゲチヨ", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/santama_kimi.webp", page:"./characters/canvas-kagechiyo.html?w=santama_kimi&utm_source=charamarl_artist", gid:"g05f095ebcd22" },
  { id:"cv_santama_shigure", name:"サンタマ探検！メカニャン「シグレ」 キャンバス", creator:"カゲチヨ", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/santama_shigure.webp", page:"./characters/canvas-kagechiyo.html?w=santama_shigure&utm_source=charamarl_artist", gid:"g6d608c6e2e1d" },
  { id:"cv_santama_promu", name:"サンタマ探検！メカニャン「プロム」 キャンバス", creator:"カゲチヨ", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/santama_promu.webp", page:"./characters/canvas-kagechiyo.html?w=santama_promu&utm_source=charamarl_artist", gid:"g782f040ed7df" },
  { id:"cv_santama_muchiko", name:"サンタマ探検！メカニャン「ムチコ」 キャンバス", creator:"カゲチヨ", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/santama_muchiko.webp", page:"./characters/canvas-kagechiyo.html?w=santama_muchiko&utm_source=charamarl_artist", gid:"g29f757913d3f" },
  { id:"cv_selfie_human_01", name:"Selfie...Human? 01 キャンバス", creator:"Selfie Bears", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/selfie_human_01.webp", page:"./characters/canvas-selfie-bears.html?w=selfie_human_01&utm_source=charamarl_artist", gid:"g71f387c4f0a5" },
  { id:"cv_selfie_human_02", name:"Selfie...Human? 02 キャンバス", creator:"Selfie Bears", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/selfie_human_02.webp", page:"./characters/canvas-selfie-bears.html?w=selfie_human_02&utm_source=charamarl_artist", gid:"g6f274b0c486c" },
  { id:"cv_selfie_human_03", name:"Selfie...Human? 03 キャンバス", creator:"Selfie Bears", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/selfie_human_03.webp", page:"./characters/canvas-selfie-bears.html?w=selfie_human_03&utm_source=charamarl_artist", gid:"g9f98df9e9a4e" },
  { id:"cv_selfie_human_04", name:"Selfie...Human? 04 キャンバス", creator:"Selfie Bears", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/selfie_human_04.webp", page:"./characters/canvas-selfie-bears.html?w=selfie_human_04&utm_source=charamarl_artist", gid:"ga9cac55d5a61" },
  { id:"cv_selfie_human_05", name:"Selfie...Human? 05 キャンバス", creator:"Selfie Bears", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/selfie_human_05.webp", page:"./characters/canvas-selfie-bears.html?w=selfie_human_05&utm_source=charamarl_artist", gid:"gd972624d5f31" },
  { id:"cv_tosakamami_moni", name:"moni キャンバス", creator:"トサカマミ", price:3300, kind:'キャンバスアート', img:"./img/t/canvas/a/tosakamami_moni.webp", page:"./characters/canvas-tosakamami.html?w=tosakamami_moni&utm_source=charamarl_artist", gid:"g790db8ff45a3" },
  // CANVAS ここまで
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
