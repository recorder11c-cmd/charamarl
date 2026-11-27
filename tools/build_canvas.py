#!/usr/bin/env python3
"""作家さんの絵のキャンバスアート（100mm角）の売り場を作る。

    python3 tools/build_canvas.py

■ 出どころは characters/canvas.json だけ
    1行＝1点。絵を足す・外すときは、この表を直して回し直す。HTMLは手で直さない。
      no     品番（注文の品名に入る。同じ題名の絵を見分けるため。一度決めたら変えない）
      key    ファイル名・カートの符号（一度決めたら変えない）
      artist 作家の掲載名（ギャラリーと同じ綴り）   slug  作家ページの名前（tools/artist_slugs.json と同じ）
      aid    計測と作家ページの結びつけ用（tools/build_seo.py の ARTIST_OF と同じ）
      title  商品名   gid  ギャラリーの作品ID   linkFrom  作品ページへのリンクを出しはじめる日時（無ければ最初から出す）
      note   その絵だけの但し書き（無くてよい）
      img    売り場の絵（img/canvas/a/・長辺1200pxまで）   thumb  一覧の絵（img/t/canvas/a/・600px）

■ 絵
    作家さんのデータを**縮小して置くだけ**（切らない・色を変えない・補正しない）。
    印刷に使う元のデータは、ここには置かない。

■ 作るもの
    characters/canvas.html           全員ぶんの売り場
    characters/canvas-<slug>.html    作家ごとの売り場（その作家の絵だけ）
    img/og/p/canvas*.jpg             リンクを貼ったとき出る絵
    img/canvas/all_tile.jpg          トップページの札の絵（全点を並べたもの）
    js/products.js                   「CANVAS ここから〜ここまで」の間を入れ替える（作家ページの「買えるもの」に出る）
    index.html                       札の「◯組の作家」と、入口バナーの「作家◯組・◯点」の数だけ合わせる

■ 回したあと
    python3 tools/build_seo.py（sitemap と作家ページ） → python3 tools/check_public.py → push
"""
import os, re, sys, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_seo
from PIL import Image, ImageDraw, ImageFont

ROOT = 'https://charamarl.com'
PRICE = 3300
esc = lambda s: html.escape(str(s or ''), quote=True)
MARK_A, MARK_B = '<!-- OGP ここから（tools/make_og_products.py） -->', '<!-- OGP ここまで -->'
PJS_A, PJS_B = '  // CANVAS ここから（tools/build_canvas.py が書く。手で直さない）', '  // CANVAS ここまで'

TEMPLATE = r'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{TITLE}}</title>
{{OGP}}
<style>
  :root {
    --bg:#0e0e14; --surface:#1a1a26; --card:#1f1f2e;
    --accent:#f5c842; --accent2:#a259ff; --text:#f0f0f0; --muted:#8a8a97; --radius:18px;
  }
  *{margin:0;padding:0;box-sizing:border-box;}
  body{background:var(--bg);color:var(--text);font-family:'Helvetica Neue',Arial,sans-serif;}
  header{display:flex;align-items:center;justify-content:space-between;padding:20px 32px;border-bottom:1px solid rgba(255,255,255,.08);position:sticky;top:0;background:rgba(14,14,20,.92);backdrop-filter:blur(12px);z-index:100;}
  .logo{font-size:22px;font-weight:900;letter-spacing:.1em;background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;text-decoration:none;}
  .back{color:var(--muted);text-decoration:none;font-size:13px;letter-spacing:.06em;}
  .back:hover{color:var(--text);}
  @media(max-width:560px){header{padding:14px 16px;}.back{font-size:12px;}}
  .strip-wrap{max-width:1000px;margin:0 auto;padding:18px 32px 0;}
  .strip-wrap .campaign-strip{border:1px solid rgba(245,200,66,.55);margin-bottom:0;}
  @media(max-width:640px){.strip-wrap{padding:14px 20px 0;}}
  .char-hero{display:grid;grid-template-columns:1fr 1fr;gap:48px;max-width:1000px;margin:0 auto;padding:44px 32px 40px;align-items:center;}
  @media(max-width:640px){.char-hero{grid-template-columns:1fr;gap:26px;padding:24px 20px 24px;}}
  .char-visual{border-radius:24px;aspect-ratio:1;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#fff;box-shadow:0 12px 40px rgba(0,0,0,.4);}
  .char-visual img{width:88%;height:88%;object-fit:contain;}
  .tag-row{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px;}
  .tag{background:rgba(255,255,255,.07);color:var(--muted);font-size:11px;padding:4px 12px;border-radius:12px;letter-spacing:.04em;}
  .char-info h1{font-size:clamp(28px,6vw,44px);font-weight:900;letter-spacing:.02em;margin-bottom:8px;}
  .char-creator{color:var(--muted);font-size:13px;letter-spacing:.06em;margin-bottom:18px;}
  .char-creator a{color:var(--text);}
  .jump{display:none;background:rgba(245,200,66,.14);border:1px solid rgba(245,200,66,.45);color:var(--accent);font-size:13px;font-weight:800;text-decoration:none;padding:9px 18px;border-radius:22px;margin-bottom:18px;}
  @media(max-width:640px){.jump{display:inline-block;}}
  section[id]{scroll-margin-top:78px;}
  .char-desc{color:var(--muted);font-size:14px;line-height:1.8;margin-bottom:16px;}
  .facts{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:0 0 18px;font-size:11.5px;font-weight:700;line-height:1.6;}
  .facts div{background:rgba(255,138,0,.08);border-radius:12px;padding:9px 12px;}
  .facts span{opacity:.7;}
  .sel{border-left:3px solid var(--accent);padding:2px 0 2px 12px;}
  .sel-t{font-size:16px;font-weight:900;line-height:1.5;}
  .sel-by{font-size:12px;font-weight:700;color:var(--accent);margin-top:4px;}
  .sel-note{font-size:12.5px;color:var(--muted);line-height:1.8;margin-top:6px;}
  .sel-link{display:inline-block;font-size:12px;font-weight:700;color:var(--text);margin-top:8px;}
  section{max-width:1000px;margin:0 auto;padding:0 32px 56px;}
  @media(max-width:640px){section{padding:0 20px 44px;}}
  .section-title{font-size:13px;font-weight:700;letter-spacing:.14em;color:var(--accent);text-transform:uppercase;margin-bottom:8px;}
  .section-heading{font-size:clamp(20px,4vw,28px);font-weight:900;margin-bottom:18px;}
  .grp{display:flex;align-items:baseline;gap:10px;margin:26px 0 12px;}
  .grp:first-child{margin-top:0;}
  .grp b{font-size:15px;font-weight:900;}
  .grp a{font-size:11.5px;color:var(--muted);}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px;}
  @media(max-width:420px){.grid{grid-template-columns:1fr 1fr;gap:10px;}}
  .card{background:var(--card);border-radius:var(--radius);padding:12px;border:2px solid transparent;cursor:pointer;transition:transform .2s,border-color .3s;text-align:center;font:inherit;color:inherit;display:block;width:100%;}
  .card:hover{transform:translateY(-3px);}
  .card.selected{border-color:var(--accent);}
  .card .pv{width:100%;aspect-ratio:1;border-radius:12px;margin-bottom:10px;overflow:hidden;background:#fff;display:flex;align-items:center;justify-content:center;}
  .card .pv img{width:92%;height:92%;object-fit:contain;}
  .card .nm{font-size:12px;font-weight:800;line-height:1.45;margin-bottom:3px;}
  .card .by{font-size:10.5px;color:var(--muted);margin-bottom:4px;}
  .card .pr{font-size:13px;font-weight:900;color:var(--accent);}
  .sample{display:grid;grid-template-columns:220px 1fr;gap:22px;align-items:center;background:var(--surface);border-radius:var(--radius);padding:20px;}
  @media(max-width:640px){.sample{grid-template-columns:1fr;}}
  .sample img{width:100%;border-radius:12px;background:#fff;display:block;}
  .sample ul{list-style:none;font-size:13px;color:var(--muted);line-height:1.9;}
  .sample li b{color:var(--text);}
  .sample .cap{font-size:12px;color:var(--muted);margin-top:10px;}
  .sample .cap a{color:var(--text);}
  .about{font-size:11.5px;color:var(--muted);line-height:1.9;border:1px dashed rgba(255,255,255,.22);border-radius:14px;padding:14px 18px;}
  .about b{color:var(--text);}
  .more{display:inline-block;margin-top:18px;font-size:13px;font-weight:800;color:var(--accent);}
  .buy-bar{position:fixed;bottom:0;left:0;right:0;background:rgba(14,14,20,.96);backdrop-filter:blur(16px);border-top:1px solid rgba(255,255,255,.1);padding:16px 32px;display:flex;align-items:center;justify-content:space-between;gap:16px;z-index:200;}
  .buy-bar-info{font-size:13px;color:var(--muted);min-width:0;}
  .buy-bar-info strong{color:var(--text);font-size:16px;display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
  .buy-btn{background:var(--accent);color:#111;border:none;border-radius:32px;padding:14px 40px;font-size:15px;font-weight:900;cursor:pointer;letter-spacing:.06em;transition:opacity .2s;white-space:nowrap;}
  .buy-btn:disabled{background:#333;color:var(--muted);cursor:default;}
  .buy-btn:not(:disabled):hover{opacity:.85;}
  #addCartBtn{background:#fff;border:2px solid var(--accent);color:#8a6a00;border-radius:32px;padding:13px 22px;font-size:14px;font-weight:900;cursor:pointer;white-space:nowrap;}
  @media(max-width:560px){
    .buy-bar{flex-direction:column;align-items:stretch;gap:10px;padding:12px 14px;}
    .buy-bar-info{text-align:center;}
    .buy-bar > div:last-child{display:flex;gap:8px;}
    .buy-bar #addCartBtn,.buy-bar .buy-btn{flex:1;padding:13px 8px;}
  }
  footer{border-top:1px solid rgba(255,255,255,.08);padding:32px;text-align:center;color:var(--muted);font-size:12px;margin-bottom:150px;}
</style>
<link rel="stylesheet" href="../cart.css">
<script defer src="/_vercel/insights/script.js"></script>
<script src="/js/ga.js"></script>
<script src="/js/protect.js"></script>
</head>
<body>
<header>
  <a class="logo" href="../index.html">CHARAMARL</a>
  <div style="display:flex; align-items:center; gap:18px;">
    <a class="back" href="../index.html">← 市場にもどる</a>
    <span data-cart-mount></span>
  </div>
</header>
<div class="strip-wrap"><div data-campaign-strip hidden></div></div>
<div class="char-hero">
  <div class="char-visual"><img src="../{{FIRST_IMG}}" alt="{{FIRST_ALT}}" id="charImg"></div>
  <div class="char-info">
    <div class="tag-row">{{TAGS}}</div>
    <h1>キャンバスアート</h1>
    <div class="char-creator">{{BY}}</div>
    <a class="jump" href="#select">↓ 絵を選ぶ（{{COUNT}}点）</a>
    <p class="char-desc">{{LEAD}}<br><br>W100×H100×D37mm。厚みがあるので、置いても掛けても飾れます。<br>絵は切り取らず、色も変えずに、そのままプリントします。</p>
    <div class="facts">
      <div>🛒 <b>¥3,300</b> 税込・送料込<br><span>追加費用なし・そのままのお値段です</span></div>
      <div>📦 受注生産<br><span id="factShip">ご注文をいただいてからお作りします</span></div>
      <div>🖼 木枠張りキャンバス<br><span>100×100×37mm・置いても掛けても</span></div>
      <div>🎨 絵はそのまま<br><span>絵の端は、側面に少し回ります</span></div>
    </div>
    <div class="sel">
      <div class="sel-t" id="selTitle"></div>
      <div class="sel-by" id="selBy"></div>
      <div class="sel-note" id="selNote" hidden></div>
      <a class="sel-link" id="selLink" hidden>ギャラリーでこの絵を見る →</a>
    </div>
  </div>
</div>
<section id="select">
  <div class="section-title">SELECT</div>
  <div class="section-heading">絵を選ぶ</div>
  <div id="list"></div>
  {{MORE}}
</section>
<section>
  <div class="section-title">SAMPLE</div>
  <div class="section-heading">作りの見本</div>
  <div class="sample">
    <img src="../img/canvas/photo_osaka.jpg" alt="キャンバスアートの見本（旅する恐竜スーさん）" loading="lazy">
    <div>
      <ul>
        <li><b>木枠に張ったキャンバス</b>です。厚みは37mm。立てて置けます</li>
        <li><b>絵は正面いっぱい</b>に入り、端は側面に少し回ります</li>
        <li>布地に刷るので、<b>画面で見る色とは少し違って</b>見えます</li>
      </ul>
      <div class="cap">写真は DinoRenny「<a href="./dino-canvas.html">旅する恐竜スーさん</a>」のキャンバスです。同じ作りでお届けします。</div>
    </div>
  </div>
</section>
<section style="padding-top:0;">
  <div class="about">
    <b>価格について</b> — CHARAMARLのグッズは受注生産の小ロットで丁寧に作っており、売上の一部はアーティスト本人に直接還元されます。「安く大量に」ではなく「欲しい人に届いて、作り手が続けられる」価格設定です。
  </div>
</section>
<footer>© 2026 CHARAMARL / レコルダ合同会社. 絵の権利は、それぞれの作家さんにあります。</footer>
<div class="buy-bar">
  <div class="buy-bar-info">
    <strong id="barName"></strong>
    <span id="barBy"></span> キャンバスアート 100×100×37mm<br><span style="font-size:10px;opacity:.8;" id="barNote"></span>
  </div>
  <div style="display:flex; gap:10px; align-items:center;">
    <button id="addCartBtn" type="button">🛍 カートに追加</button>
    <button class="buy-btn" id="buyBtn" type="button">今すぐ購入 →</button>
  </div>
</div>
<script>
const PRICE = 3300, KIND = "キャンバスアート";
{{ARTIST_ID_LINE}}
const WORKS = {{WORKS}};
const GROUPED = {{GROUPED}};
const yen = n => '¥' + n.toLocaleString();
const esc = s => String(s == null ? '' : s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const BF_END = Date.parse('2026-12-01T00:00:00+09:00');
const SHIP_NOTE = Date.now() < BF_END ? '受注生産｜11/30までのご注文は、12月中旬ごろのお届け' : '受注生産｜約2〜3週間でお届け';
document.getElementById('factShip').textContent = SHIP_NOTE.split('｜')[1];
let selected = WORKS[0];

const list = document.getElementById('list');
let lastArtist = null, grid = null;
WORKS.forEach((w, i) => {
  if (!grid || (GROUPED && w.artist !== lastArtist)) {
    if (GROUPED) {
      const h = document.createElement('div'); h.className = 'grp';
      h.innerHTML = '<b>' + esc(w.artist) + '</b><a href="./canvas-' + esc(w.slug) + '.html">この作家のキャンバスだけ見る</a>';
      list.appendChild(h);
    }
    grid = document.createElement('div'); grid.className = 'grid'; list.appendChild(grid);
    lastArtist = w.artist;
  }
  const card = document.createElement('button');
  card.type = 'button'; card.className = 'card'; card.dataset.key = w.key;
  card.innerHTML = '<div class="pv"><img src="../' + esc(w.thumb) + '" alt="' + esc(w.title) + '" loading="lazy"></div>'
    + '<div class="nm">' + esc(w.title) + '</div>'
    + '<div class="by">' + esc(w.no) + '</div>'
    + '<div class="pr">' + yen(PRICE) + '</div>';
  card.addEventListener('click', () => pick(i, true));
  grid.appendChild(card);
});

function pick(i, byUser){
  selected = WORKS[i];
  const w = selected;
  document.querySelectorAll('.card').forEach(c => c.classList.toggle('selected', c.dataset.key === w.key));
  const im = document.getElementById('charImg'); im.src = '../' + w.img; im.alt = w.title;
  document.getElementById('selTitle').textContent = w.title;
  document.getElementById('selBy').textContent = 'by ' + w.artist + '　品番 ' + w.no;
  const n = document.getElementById('selNote'); n.hidden = !w.note; n.textContent = w.note || '';
  const a = document.getElementById('selLink');
  const open = !w.linkFrom || Date.now() >= Date.parse(w.linkFrom);
  a.hidden = !open; if (open) a.href = '../?g=' + encodeURIComponent(w.gid) + '&utm_source=charamarl_canvas';
  document.getElementById('barName').textContent = w.title;
  document.getElementById('barBy').textContent = w.artist + '｜';
  document.getElementById('barNote').textContent = SHIP_NOTE;
  if (byUser) {
    try { history.replaceState(null, '', location.pathname + '?w=' + encodeURIComponent(w.key)); } catch (e) {}
    if (window.innerWidth <= 640) document.querySelector('.char-hero').scrollIntoView({behavior:'smooth', block:'start'});
    track('view_product');
  }
}
function item(w){ return {item_id:'cv_' + w.key, item_name:w.title + ' ' + KIND, character_id:'cv_' + w.key, artist_id:w.aid, price:PRICE, quantity:1, currency:'JPY'}; }
function track(ev, extra){ if (window.cmEvent) cmEvent(ev, Object.assign(item(selected), extra || {})); }
const lineName = w => w.artist + '（' + w.no + '・受注生産）';

(function(){
  const q = new URLSearchParams(location.search).get('w');
  const i = WORKS.findIndex(w => w.key === q);
  pick(i >= 0 ? i : 0, false);
  setTimeout(() => track('view_product'), 400);
})();

document.getElementById('buyBtn').addEventListener('click', async function(){
  const btn = this, w = selected;
  btn.textContent = '処理中...'; btn.disabled = true;
  const back = () => { btn.textContent = '今すぐ購入 →'; btn.disabled = false; };
  try {
    try { fetch('/api/react', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({id:'cv_' + w.key + '_buy', type:'like', op:'add'})}); } catch (e) {}
    track('begin_checkout', {checkout_type:'buynow'});
    try { localStorage.setItem('cm_pending', JSON.stringify({value:PRICE, type:'buynow', ts:Date.now(),
      items:[{item_id:'cv_' + w.key, item_name:w.title + ' ' + KIND, character_id:'cv_' + w.key, price:PRICE, quantity:1}]})); } catch (e) {}
    const res = await fetch('/api/checkout', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ items: [{ name: w.title + ' ' + KIND + ' ' + lineName(w), price:PRICE, quantity:1, images:['https://charamarl.com/' + w.img] }] }),
    });
    const data = await res.json();
    if (data.url) { window.location.href = data.url; }
    else { alert('エラー: ' + (data.error || '不明')); back(); }
  } catch (e) { alert('通信エラー'); back(); }
});
document.getElementById('addCartBtn').addEventListener('click', function(){
  const w = selected;
  window.CHARAMARL_CART.add('cv_' + w.key, 'canvas', w.title, lineName(w), PRICE, '/' + w.img, KIND);
  const o = this.textContent; this.textContent = '✓ 追加しました'; setTimeout(() => this.textContent = o, 1200);
});
</script>
<script src="../cart.js"></script>
</body>
</html>
'''


def ogp(page, title, desc, img, name):
    url = f'{ROOT}/{page}'
    ld = {'@context': 'https://schema.org', '@type': 'Product', 'name': name, 'image': f'{ROOT}/{img}',
          'description': desc, 'brand': {'@type': 'Brand', 'name': 'CHARAMARL'},
          'offers': {'@type': 'Offer', 'url': url, 'priceCurrency': 'JPY', 'price': str(PRICE),
                     'availability': 'https://schema.org/PreOrder', 'itemCondition': 'https://schema.org/NewCondition'}}
    crumbs = [('CHARAMARL', f'{ROOT}/'), ('キャンバスアート', f'{ROOT}/characters/canvas.html')]
    if page != 'characters/canvas.html':
        crumbs.append((name, url))
    bc = {'@context': 'https://schema.org', '@type': 'BreadcrumbList',
          'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(crumbs)]}
    jl = lambda d: '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False).replace('</', '<\\/') + '</script>\n'
    return (f'{MARK_A}\n'
            f'<link rel="canonical" href="{url}">\n'
            f'<meta name="description" content="{esc(desc)}">\n'
            f'<meta property="og:type" content="product">\n'
            f'<meta property="og:site_name" content="CHARAMARL">\n'
            f'<meta property="og:url" content="{url}">\n'
            f'<meta property="og:title" content="{esc(title)}">\n'
            f'<meta property="og:description" content="{esc(desc)}">\n'
            f'<meta property="og:image" content="{ROOT}/{img}">\n'
            f'<meta property="og:image:width" content="1200">\n'
            f'<meta property="og:image:height" content="630">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n'
            + jl(ld) + jl(bc) + MARK_B)


def js(v):
    return json.dumps(v, ensure_ascii=False).replace('</', '<\\/')


def render(page, works, title, desc, og_img, name, tags, by, lead, more, artist_id, grouped):
    keep = ('no', 'key', 'artist', 'slug', 'aid', 'title', 'gid', 'img', 'thumb', 'note', 'linkFrom')
    s = TEMPLATE
    for k, v in {
        'TITLE': esc(title), 'OGP': ogp(page, title, desc, og_img, name),
        'COUNT': str(len(works)), 'FIRST_IMG': esc(works[0]['img']), 'FIRST_ALT': esc(works[0]['title']),
        'TAGS': ''.join(f'<span class="tag">{esc(t)}</span>' for t in tags), 'BY': by, 'LEAD': esc(lead), 'MORE': more,
        'ARTIST_ID_LINE': f'const ARTIST_ID = "{artist_id}";' if artist_id else '',
        'WORKS': js([{k: w[k] for k in keep if w.get(k)} for w in works]), 'GROUPED': 'true' if grouped else 'false',
    }.items():
        s = s.replace('{{' + k + '}}', v)
    assert '{{' not in s, page
    open(page, 'w', encoding='utf-8').write(s)


def mosaic(works, out, size, cols, cell, pad, head=None):
    """全点を同じ大きさで並べる（縮小だけ。どの絵も切らない）。"""
    W, H = size
    im = Image.new('RGB', (W, H), (255, 253, 245))
    d = ImageDraw.Draw(im)
    y0 = pad
    if head:
        f_logo = ImageFont.truetype(build_seo.FONT, 40)
        d.text((40, 30), 'CHARA', font=f_logo, fill=(255, 138, 0))
        d.text((40 + d.textlength('CHARA', font=f_logo), 30), 'MARL', font=f_logo, fill=(142, 78, 217))
        d.text((W - 40, 52), head, font=ImageFont.truetype(build_seo.FONT, 34), fill=(26, 26, 38), anchor='rm')
        y0 = 98
    rows = (len(works) + cols - 1) // cols
    x0 = (W - (cols * cell + (cols - 1) * pad)) // 2
    y0 += (H - y0 - (rows * cell + (rows - 1) * pad)) // 2
    for i, w in enumerate(works):
        t = Image.open(w['img']).convert('RGB').resize((cell, cell), Image.LANCZOS)
        im.paste(t, (x0 + (i % cols) * (cell + pad), y0 + (i // cols) * (cell + pad)))
    im.save(out, 'JPEG', quality=88)


def main():
    works = json.load(open('characters/canvas.json', encoding='utf-8'))
    slugs = json.load(open('tools/artist_slugs.json', encoding='utf-8'))
    assert len({w['key'] for w in works}) == len(works) and len({w['no'] for w in works}) == len(works), 'key か no が重なっています'
    for w in works:
        assert os.path.exists(w['img']) and os.path.exists(w['thumb']), f"{w['key']}: 絵がありません"
        iw, ih = Image.open(w['img']).size
        assert iw == ih, f"{w['key']}: 正方形ではありません"
        assert slugs.get(w['artist']) == w['slug'], f"{w['key']}: slug が tools/artist_slugs.json とちがいます"
        assert build_seo.ARTIST_OF.get(w['aid']) == w['artist'], f"{w['key']}: aid が tools/build_seo.py の ARTIST_OF にありません"
    artists = []
    for w in works:
        if w['artist'] not in artists:
            artists.append(w['artist'])
    os.makedirs('img/og/p', exist_ok=True)

    # 全員ぶん
    desc = (f'CHARAMARLに並ぶ作家{len(artists)}組・{len(works)}点の絵を、木枠張りのミニキャンバス（100×100×37mm）にしました。'
            '各3,300円（税込・送料込）・受注生産。絵は切り取らず、そのままプリントします。')
    mosaic(works, 'img/og/p/canvas.jpg', (1200, 630), 10, 104, 10, head='キャンバスアート')
    mosaic(works, 'img/canvas/all_tile.jpg', (600, 500), 6, 94, 5)
    render('characters/canvas.html', works, 'キャンバスアート｜CHARAMARL', desc, 'img/og/p/canvas.jpg', 'キャンバスアート',
           [f'{len(artists)}組の作家', 'キャンバスアート', '100×100×37mm', f'{len(works)}点'],
           f'by {len(artists)}組の作家',
           'CHARAMARLに並ぶ作家さんの絵を、木枠張りのミニキャンバスにしました。',
           '', None, True)
    print('OK characters/canvas.html', len(works), '点', len(artists), '組')

    # 作家ごと
    for a in artists:
        mine = [w for w in works if w['artist'] == a]
        sl = mine[0]['slug']
        page, og = f'characters/canvas-{sl}.html', f'img/og/p/canvas-{sl}.jpg'
        build_seo.og_image(a, [{'img': w['img']} for w in mine[:3]], og)
        name = f'{a} キャンバスアート'
        d = (f'{a}さんの絵を、木枠張りのミニキャンバス（100×100×37mm）にしました。'
             f'{"全" + str(len(mine)) + "点・各" if len(mine) > 1 else ""}3,300円（税込・送料込）・受注生産。絵は切り取らず、そのままプリントします。')
        render(page, mine, f'{name}｜CHARAMARL', d, og, name,
               [a, 'キャンバスアート', '100×100×37mm', f'{len(mine)}点'],
               f'by <a href="../artist/{esc(sl)}.html">{esc(a)}</a>',
               f'{a}さんの絵を、木枠張りのミニキャンバスにしました。',
               '<a class="more" href="./canvas.html">ほかの作家さんのキャンバスも見る →</a>', mine[0]['aid'], False)
        print('OK', page, len(mine), '点')

    # 作家ページの「買えるもの」（js/products.js）
    rows = '\n'.join(
        "  { id:%s, name:%s, creator:%s, price:%d, kind:'キャンバスアート', img:%s, page:%s }," % (
            js('cv_' + w['key']), js(w['title'] + ' キャンバス'), js(w['artist']), PRICE,
            js('./' + w['thumb']), js(f"./characters/canvas-{w['slug']}.html?w={w['key']}&utm_source=charamarl_artist"))
        for w in works)
    p = open('js/products.js', encoding='utf-8').read()
    block = f'{PJS_A}\n{rows}\n{PJS_B}\n'
    if PJS_A in p:
        p = p[:p.index(PJS_A)] + block + p[p.index(PJS_B) + len(PJS_B) + 1:]
    else:
        i = p.index('];\n\n// COLOR TAP')
        p = p[:i] + block + p[i:]
    open('js/products.js', 'w', encoding='utf-8').write(p)

    # トップページの札の数
    s = open('index.html', encoding='utf-8').read()
    s2 = re.sub(r'(<div class="pin-sub" data-canvas-artists><span class="av"></span>)[^<]*', lambda m: m.group(1) + f'{len(artists)}組の作家', s)
    # トップページの入口バナーの数
    s2 = re.sub(r'(<span data-canvas-count>)[^<]*', lambda m: m.group(1) + f'作家{len(artists)}組・{len(works)}点', s2)
    if s2 != s:
        open('index.html', 'w', encoding='utf-8').write(s2)
    print(f'{1 + len(artists)} ページ・products.js {len(works)} 行')


if __name__ == '__main__':
    main()
