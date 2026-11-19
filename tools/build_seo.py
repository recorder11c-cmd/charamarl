#!/usr/bin/env python3
"""作品ごとの固有ページ（/w/<id>.html）・作家の固有ページ（/artist/<名前>.html）・シェア用ページ（/a/・/g/）・sitemap.xml を作る。

    python3 tools/build_seo.py          # 生成
    python3 tools/build_seo.py --check  # 差分だけ見る（書かない）

■ なぜ作るか（2026-09-21）
    1か月レポートの結論は「転換率1.37%は正常。足りないのは訪問者」だった。
    そこで入口を数えたら、検索から入れるページが49枚しかなかった。

      ・sitemap.xml が無い（404）
      ・作品126点に固有URLが無い。`?g=<id>` はモーダルを開くだけで、
        title も OGP もトップページのまま。**Googleから見ると作品は存在しない**
      ・作家39人のページも `artist.html?a=` のクエリで、中身はJSで後から入る

    Xの表示は月2〜3万あるのに訪問は366人。X以外の入口が無いのが効いている。
    作品126・作家39・TAP17 は**もう手元にある資産**で、URLを与えるだけで入口になる。

■ 作るもの
    w/<id>.html     作品1点＝1ページ。title・description・OGP・画像・作家名・説明。
                    本編（/?g=<id>）へ誘導する。canonical は自分自身。
    sitemap.xml     静的ページ＋作品＋作家＋TAP＋商品ページ。

■ 作家のシェア用ページ（2026-11-18）
    a/<符号>.html          作家1組＝1ページ。OGPだけ持っていて、開くと artist.html?a=<作家名> へ移る。
    img/og/a/<符号>_*.jpg  リンクを貼ったときに出る絵（1200×630）。その作家の作品を新しい順に3点まで並べる。
                           **絵は縮小して置くだけ**（切らない・補正しない）。
    なぜ要るか: artist.html は中身をJSで入れるので、Xに貼っても画像が出なかった。
    符号は作家名のFNV-1a（8桁）。artist.html / index.html の cmArtistSlug() と同じ計算。
    ⚠️ 作品が増えたら、このスクリプトを回すまで絵は古いまま（ページが無い作家は従来のURLでシェアされる）。

■ 作品のシェア用ページ（2026-11-19）
    g/<作品ID>.html         作品の🚀ボタンが貼るURL。OGPだけ持っていて、開くと /?g=<作品ID>（本編）へ移る。
    img/og/g/<作品ID>_*.jpg  その作品1点を、切らずに収めた絵（1200×630）。
    w/<id>.html（検索用の固有ページ）とは別物。w/ は検索から来た人が読むページなので移動させない。

■ 作家の固有ページ（2026-11-19）
    artist/<名前>.html   作家1組＝1ページ。title・説明・h1・作品の一覧（w/ へのリンク）・グッズ・活動場所へのリンクを
                         **HTMLに直接書く**（JSで後から入れない）。検索に載せるのはこちら。
    artist/index.html    アーティスト一覧。
    artist/slugs.json    artist.html?a=<作家名> が、自分の固有ページを canonical に指すための表。
    なぜ要るか: artist.html?a= は全員が同じHTMLで title も同じ。検索からは1ページの重複に見えて、作家名で探しても出なかった。
    名前の表は tools/artist_slugs.json に固定してある（変えると検索とリンクが切れる）。
    英数字の作家名は自動で足す。**日本語の作家名は表に手で足す**（足すまでその作家のページは作られず、警告が出る）。

■ 作品ページの説明文（2026-11-19）
    検索結果に出る説明を120〜200字にした。足しているのは**データにある事実だけ**
    （作家名・種類・作品名・掲載点数・グッズの有無）。絵の中身は書き足さない（現物を見ずに書かないため）。

■ sitemap の日付（2026-11-19）
    一律の「今日」にしない。作品は登録・編集の日、作家は最新作の日、ほかは git の最終変更日。
    作品には画像（image:image）も付ける。artist.html?a= は載せない。

■ 作らない理由があるもの
    ・ログイン後の画面（mypage/login/success/cancel/apply-admin）は noindex 相当なので入れない
    ・`characters/kagechiyo-acrylic.html` は委託分で未販売。noindex なので入れない
    ・作品ページは **API の公開分だけ**。予約公開はその時刻を過ぎてから次回生成で入る

■ 作品画像について
    画像は blob のURLをそのまま指す（コピーしない）。
    右クリック等の抑止は既存の js/protect.js をそのまま読み込む。
"""
import sys, os, json, html, re, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

API   = 'https://charamarl.com/api/gallery'
ROOT  = 'https://charamarl.com'
OUTD  = 'w'
JST   = timezone(timedelta(hours=9))

# sitemap に入れる静的ページ（優先度つき）
STATIC = [
    ('/',                              '1.0', 'daily'),
    ('/characters/keyrings.html',      '0.9', 'weekly'),
    ('/characters/pins.html',          '0.9', 'weekly'),
    ('/run.html',                      '0.8', 'weekly'),
    ('/about.html',                    '0.6', 'monthly'),
    ('/join.html',                     '0.6', 'monthly'),
    ('/apply.html',                    '0.6', 'monthly'),
    ('/promo.html',                    '0.4', 'monthly'),
    ('/terms.html',                    '0.3', 'yearly'),
    ('/privacy.html',                  '0.3', 'yearly'),
    ('/tokushoho.html',                '0.3', 'yearly'),
]
# 入れない（ログイン後・管理・未販売）
SKIP_HTML = {'mypage.html', 'login.html', 'success.html', 'cancel.html',
             'apply-admin.html', 'stats.html', 'artist.html', 'index.html',
             'characters/kagechiyo-acrylic.html'}

esc = lambda s: html.escape(str(s or ''), quote=True)


def works():
    d = json.load(urllib.request.urlopen(API))
    return d.get('list', [])


CAT_JA = {'ARTWORK': 'アート作品', 'CHARACTER': 'キャラクター', 'PRODUCT': 'グッズ', 'EVENT': 'イベントのお知らせ',
          'MAKING': '制作風景', 'INTERVIEW': 'インタビュー'}
STYLE = """<style>
  :root{--bg:#0e0e14;--card:#1f1f2e;--accent:#f5c842;--accent2:#a259ff;--text:#f0f0f0;--muted:#8b8b99;}
  *{margin:0;padding:0;box-sizing:border-box}
  body{background:var(--bg);color:var(--text);font-family:'Helvetica Neue',Arial,'Hiragino Sans',sans-serif;}
  header{display:flex;align-items:center;justify-content:space-between;padding:18px 24px;border-bottom:1px solid rgba(255,255,255,.08);}
  .logo{font-size:20px;font-weight:900;letter-spacing:.1em;background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;text-decoration:none;}
  .back{color:var(--muted);text-decoration:none;font-size:13px;}
  main{max-width:760px;margin:0 auto;padding:30px 20px 60px;}
  .art{background:#fff;border-radius:18px;overflow:hidden;display:flex;align-items:center;justify-content:center;margin-bottom:22px;}
  .art img{width:100%;height:auto;display:block;}
  .cat{font-size:11px;font-weight:800;letter-spacing:.14em;color:var(--accent);}
  h1{font-size:clamp(24px,5vw,36px);font-weight:900;margin:6px 0 4px;line-height:1.3;}
  .by{color:var(--muted);font-size:14px;margin-bottom:18px;}
  .by a,.lk a,ul.names a{color:var(--text);text-decoration:none;border-bottom:1px solid rgba(255,255,255,.25);}
  p.desc{font-size:14.5px;line-height:1.95;color:#d5d2dd;margin-bottom:26px;white-space:pre-wrap;}
  p.about{font-size:13px;line-height:1.95;color:#b9b6c4;margin:26px 0 0;}
  .row{display:flex;gap:10px;flex-wrap:wrap;}
  .btn{display:inline-flex;align-items:center;gap:7px;border-radius:24px;padding:12px 22px;
   font-size:14px;font-weight:900;text-decoration:none;}
  .btn.p{background:var(--accent);color:#1a1a26;}
  .btn.s{background:var(--card);color:var(--text);}
  h2{font-size:15px;font-weight:900;margin:36px 0 12px;}
  .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;}
  .grid.all{grid-template-columns:repeat(auto-fill,minmax(150px,1fr));}
  .t{display:block;text-decoration:none;color:var(--text);min-width:0;}
  .ti{display:block;aspect-ratio:1;background:#fff;border-radius:12px;overflow:hidden;}
  .ti img{width:100%;height:100%;object-fit:contain;display:block;}
  .tt{display:block;font-size:12px;font-weight:700;line-height:1.5;margin-top:6px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
  ul.lk{list-style:none;font-size:13.5px;line-height:2.2;}
  ul.names{list-style:none;columns:2;column-gap:24px;font-size:14px;}
  ul.names li{break-inside:avoid;line-height:1.6;padding:5px 0;overflow-wrap:anywhere;}
  ul.names span{color:var(--muted);font-size:12px;margin-left:6px;white-space:nowrap;}
  .note{margin-top:30px;padding-top:18px;border-top:1px solid rgba(255,255,255,.08);
   font-size:12px;line-height:1.9;color:var(--muted);}
  footer{text-align:center;color:var(--muted);font-size:12px;padding:24px;line-height:2.1;}
  footer a{color:var(--muted);}
</style>"""
FOOT = ('<footer>\n  <a href="/characters/keyrings.html">アクリルキーホルダー</a> ・ <a href="/characters/pins.html">ピンズ</a> ・ '
        '<a href="/artist/">アーティスト一覧</a> ・ <a href="/join.html">作家登録</a> ・ <a href="/about.html">ABOUT</a><br>\n'
        '  © 2026 CHARAMARL / レコルダ合同会社\n</footer>')
HEAD_JS = ('<script defer src="/_vercel/insights/script.js"></script>\n<script src="/js/ga.js"></script>\n'
           '<script src="/js/protect.js"></script>')
NOTE = ('  <div class="note">\n    CHARAMARLは、キャラクターたちが集まる小さな市場です。掲載は無料。<br>\n'
        '    掲載作品を<b>生成AIの学習には利用しません</b>（規約に明記）。\n  </div>')

def one(s):
    return re.sub(r'\s+', ' ', s or '').strip()

def cut(s, n):
    return s if len(s) <= n else s[:max(n - 1, 0)] + '…'

def thumb(u, w=256):
    """一覧用の小さい絵。トップページの thumbUrl() と同じ（Vercel が縮小して配る）。"""
    return '/_vercel/image?url=' + urllib.parse.quote(u, safe='') + f'&w={w}&q=75'

def when(w):
    return int(w.get('publishAt') or w.get('ts') or 0)

def artist_url(a, ctx):
    sl = ctx['slugs'].get(a)
    return f'/artist/{sl}.html' if sl else '/artist.html?a=' + urllib.parse.quote(a, safe='')

def tile(w, size=256):
    t, a = w.get('title') or '', (w.get('artist') or '').strip()
    return (f'<a class="t" href="/w/{esc(w["id"])}.html"><span class="ti"><img loading="lazy" src="{esc(thumb(w["img"], size))}" '
            f'alt="{esc(t if t == a else t + "（" + a + "）")}"></span><span class="tt">{esc(t)}</span></a>')

def work_text(w, ctx):
    """作品ページの説明（検索結果に出る120〜200字）と、本文に置く紹介文。
    ここで足すのは**データにある事実だけ**（作家名・種類・作品名・掲載点数・グッズの有無）。絵の中身は書き足さない。"""
    t, a = w.get('title') or '', (w.get('artist') or '').strip()
    mine = [x for x in ctx['by'].get(a, []) if x['id'] != w['id']]
    prods = [p for p in ctx['prods'] if p['artist'] == a]
    cat = CAT_JA.get(w.get('cat'), '作品')
    ours = a == 'CHARAMARL'
    s1 = f'CHARAMARLの連載{cat}「{t}」。' if ours else (f'{cat}「{t}」。' if t == a else f'{a}さんの{cat}「{t}」。')
    if mine:
        names = '」「'.join(cut(x.get('title') or '', 16) for x in mine[:2])
        s2 = (f'ほかに「{names}」など{len(mine)}本を掲載しています。' if ours else
              f'CHARAMARLでは{a}さんの作品を{len(mine) + 1}点掲載中です（ほかに「{names}」など）。')
    else:
        s2 = '' if ours else f'CHARAMARLでは{a}さんの作品を掲載しています。'
    s3 = ('グッズ（' + '・'.join(p['name'] for p in prods[:3]) + '）も買えます。') if prods else ''
    link = w.get('link') or ''
    s4 = ('全文はnoteで読めます。' if 'note.com' in link else '作品のページから、作家さんの活動場所へそのまま行けます。') if link else ''
    s5 = 'CHARAMARLは、キャラクターとアートが集まる小さな市場。掲載作品を生成AIの学習には利用しません。'
    fixed = s1 + s2 + s3 + s4
    base = one(w.get('desc'))
    room = 200 - len(fixed)
    lead = cut(base, room) if base and room >= 24 else ''
    meta = s1 + lead + s2 + s3 + s4
    if len(meta) < 120:
        meta += s5
    if len(meta) < 120:
        meta += '気に入ったら♥で応援できます。'
    return cut(meta, 200), s1 + s2 + s3


def page(w, ctx):
    t, a = w.get('title') or '', (w.get('artist') or '').strip()
    ours = a == 'CHARAMARL'
    meta, about = work_text(w, ctx)
    url = f'{ROOT}/w/{w["id"]}.html'
    title = f'{t}｜CHARAMARL' if ours or not a or t == a else f'{t} — {a}｜CHARAMARL'
    if 'CHARAMARL' in t:
        title = t if ours or not a else f'{t} — {a}'
    alt = f'{t}（{a}）' if a and a != t else t
    au = artist_url(a, ctx)
    others = sorted([x for x in ctx['by'].get(a, []) if x['id'] != w['id'] and x.get('img')], key=lambda x: -when(x))[:3]
    prods = [p for p in ctx['prods'] if p['artist'] == a]
    more = ''
    if others:
        head = 'ほかの読みもの' if ours else f'{esc(a)} さんのほかの作品'
        more += f'  <h2>{head}</h2>\n  <div class="grid">\n    ' + '\n    '.join(tile(x) for x in others) + '\n  </div>\n'
    lk = [f'<li><a href="{esc(au)}">{"CHARAMARLの読みもの一覧" if ours else esc(a) + " さんのページ（作品一覧）"}</a></li>']
    lk += [f'<li><a href="/characters/{esc(p["file"])}">{esc(p["name"])}（グッズ）</a></li>' for p in prods[:4]]
    more += '  <h2>関連ページ</h2>\n  <ul class="lk">\n    ' + '\n    '.join(lk) + '\n  </ul>\n'
    all_label = '読みものをすべて見る' if ours else f'{esc(a)} の作品をすべて見る'
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noai, noimageai">
<title>{esc(title)}</title>
<meta name="description" content="{esc(meta)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="CHARAMARL">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(meta)}">
<meta property="og:image" content="{esc(w.get('img'))}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/img/icon-192.png">
{STYLE}
{HEAD_JS}
</head>
<body>
<header>
  <a class="logo" href="/">CHARAMARL</a>
  <a class="back" href="/">← 市場にもどる</a>
</header>
<main>
  <div class="art"><img src="{esc(w.get('img'))}" alt="{esc(alt)}"></div>
  <div class="cat">{esc(w.get('cat') or 'ARTWORK')}</div>
  <h1>{esc(t)}</h1>
  <div class="by">by <a href="{esc(au)}">{esc(a)}</a></div>
  <p class="desc">{esc((w.get('desc') or '').strip())}</p>
  <div class="row">
    <a class="btn p" href="/?g={esc(w['id'])}">🎪 市場で見る（♥で応援できます）</a>
    <a class="btn s" href="/artist.html?a={esc(urllib.parse.quote(a, safe=''))}">{all_label}</a>
  </div>
  <p class="about">{esc(about)}</p>
{more}{NOTE}
</main>
{FOOT}
</body>
</html>
'''


# ---- 作家の固有ページ（検索用） ----
AR_DIR = 'artist'
SLUG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'artist_slugs.json')
# 商品ページの ARTIST_ID → ギャラリーの掲載名
ARTIST_OF = {'dinorenny': 'DinoRenny', 'maru': 'MARU_GMC', 'chui': 'ちゅい', 'sayoooooh': 'SAYoooooh',
             'inkzmonster': "Ink'z Monster", 'calma': '赤猫かるま', 'crazy': 'CRAZY', 'morry': 'morry',
             'chinchillo': 'チンチロ', 'kagechiyo': 'カゲチヨ'}

def products():
    """販売中の商品ページ。名前・価格・作家は**ページに書いてあるもの**を読む（ここで決めない）。"""
    out = []
    for f in sorted(os.listdir('characters')):
        if not f.endswith('.html'):
            continue
        s = open(os.path.join('characters', f), encoding='utf-8').read()
        price, aid = re.search(r'\bPRICE = (\d+)', s), re.search(r'ARTIST_ID *= *"([^"]+)"', s)
        name = re.search(r'<meta property="og:title" content="([^"]+)"', s)
        if 'noindex' in s[:1500] or not (price and aid and name):
            continue
        out.append({'file': f, 'price': int(price.group(1)), 'artist': ARTIST_OF.get(aid.group(1)),
                    'name': re.sub(r'\s*[—｜|]\s*CHARAMARL$', '', html.unescape(name.group(1)))})
    return out

def nice_slugs(names, check):
    """作家名 → /artist/<名前>.html の名前。表（tools/artist_slugs.json）に固定してある。"""
    table = json.load(open(SLUG_FILE, encoding='utf-8'))
    added = False
    for n in sorted(names):
        if n in table:
            continue
        s = re.sub(r'[^a-z0-9]+', '-', n.lower()).strip('-') if all(ord(c) < 128 for c in n) else ''
        if s and s not in table.values():
            table[n] = s; added = True
            print(f'作家ページの名前を足しました: {n} → {s}')
        else:
            print(f'⚠️ {n} さんの作家ページを作れません。tools/artist_slugs.json に英数字の名前を足してください')
    vals = [v for k, v in table.items() if k != '_note']
    assert len(vals) == len(set(vals)), 'artist_slugs.json の名前が重なっています'
    if added and not check:
        json.dump(table, open(SLUG_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    return {n: table[n] for n in names if n in table}

def link_label(u):
    h = urllib.parse.urlparse(u).netloc.lower().replace('www.', '')
    for k, v in (('instagram.com', 'Instagram'), ('x.com', 'X'), ('twitter.com', 'X'), ('lit.link', 'リンク集'),
                 ('note.com', 'note'), ('booth.pm', 'BOOTH'), ('youtube.com', 'YouTube'), ('tiktok.com', 'TikTok')):
        if h == k or h.endswith('.' + k):
            return v
    return h

def artist_static(a, ctx):
    ours = a == 'CHARAMARL'
    mine = sorted(ctx['by'][a], key=lambda x: -when(x))
    prods = [p for p in ctx['prods'] if p['artist'] == a]
    sl = ctx['slugs'][a]
    url = f'{ROOT}/{AR_DIR}/{sl}.html'
    cats = []
    for x in mine:
        c = CAT_JA.get(x.get('cat'), '作品')
        if c not in cats:
            cats.append(c)
    top = pick_works(mine) or mine[:3]
    names = '」「'.join(cut(x.get('title') or '', 18) for x in top)
    if ours:
        title = '連載「市場のひとたち」読みもの一覧｜CHARAMARL'
        desc = (f'CHARAMARLの連載インタビュー「市場のひとたち」の一覧。「{names}」など{len(mine)}本。'
                '参加している作家さんに、キャラクターが生まれたきっかけや制作のことを聞いています。全文はnoteで読めます。')
        h1 = 'CHARAMARL'
    else:
        title = f'{a} の作品・グッズ一覧｜CHARAMARL' if prods else f'{a} の作品一覧｜CHARAMARL'
        d1 = f'{a}のキャラクターと作品一覧。「{names}」など{"・".join(cats)}を{len(mine)}点掲載しています。'
        d3 = '♥で応援できて、作品から作家さんの活動場所へそのまま行けます。'
        for k in (4, 3, 2, 1, 0):   # 160字に収まるだけグッズ名を入れる（途中で切らない）
            more = f'ほか{len(prods) - k}点' if len(prods) > k else ''
            d2 = ('グッズ（' + '・'.join([p['name'] for p in prods[:k]] + ([more] if more else [])) + '）は CHARAMARL で買えます。') if prods and k else \
                 ('グッズも CHARAMARL で買えます。' if prods else '')
            desc = d1 + d2 + d3
            if len(desc) <= 160:
                break
        for pad in ('CHARAMARLは、キャラクターとアートが集まる小さな市場です。', '掲載作品を生成AIの学習には利用しません。'):
            if len(desc) < 120:
                desc += pad
        h1 = a
    desc = cut(desc, 160)
    links, seen = [], set()
    home = (ctx['homes'].get(a.lower()) or {}).get('home')
    for u in [home] + [x.get('link') for x in mine]:
        if u and re.match(r'https?://', u) and u.rstrip('/') not in seen and len(links) < 6:
            seen.add(u.rstrip('/'))
            links.append(f'<a class="btn s" href="{esc(u)}" target="_blank" rel="noopener">{esc(link_label(u))} ↗</a>')
    body_links = ('  <h2>' + ('読める場所' if ours else '作家さんの活動場所') + '</h2>\n  <div class="row">\n    ' + '\n    '.join(links) + '\n  </div>\n') if links else ''
    goods = ''
    if prods:
        goods = ('  <h2>グッズ</h2>\n  <ul class="lk">\n    '
                 + '\n    '.join(f'<li><a href="/characters/{esc(p["file"])}">{esc(p["name"])}</a>　¥{p["price"]:,}（税込・送料込）</li>' for p in prods)
                 + '\n  </ul>\n')
    grid = '\n    '.join(tile(x, 384) for x in mine if x.get('img'))
    q = urllib.parse.quote(a, safe='')
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noai, noimageai">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="profile">
<meta property="og:site_name" content="CHARAMARL">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{esc(ctx['og'].get(a) or ROOT + '/img/og.png')}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/img/icon-192.png">
{STYLE}
{HEAD_JS}
</head>
<body>
<header>
  <a class="logo" href="/">CHARAMARL</a>
  <a class="back" href="/artist/">← アーティスト一覧</a>
</header>
<main>
  <div class="cat">{'CHARAMARL' if ours else 'ARTIST'}</div>
  <h1>{esc(h1)}</h1>
  <div class="by">{esc('・'.join(cats))}　{len(mine)}{'本' if ours else '点'}</div>
  <p class="desc">{esc(desc)}</p>
  <div class="row">
    <a class="btn p" href="/artist.html?a={esc(q)}">🎪 市場で見る（♥で応援できます）</a>
  </div>
{body_links}{goods}  <h2>{'読みもの' if ours else '作品'}</h2>
  <div class="grid all">
    {grid}
  </div>
{NOTE}
</main>
{FOOT}
</body>
</html>
'''

def artist_index(ctx):
    rows = sorted(((a, sl) for a, sl in ctx['slugs'].items() if a != 'CHARAMARL' and a in ctx['by']), key=lambda x: x[0].lower())
    n = len(rows)
    title = f'アーティスト一覧（{n}組）｜CHARAMARL'
    desc = (f'CHARAMARLに参加しているアーティスト{n}組の一覧。オリジナルキャラクターとアート作品を作家ごとに見られます。'
            '気に入った作品は♥で応援できて、作家さんのInstagram・X・ショップへそのまま行けます。掲載は無料・1点から参加できます。')
    li = '\n    '.join(f'<li><a href="/{AR_DIR}/{sl}.html">{esc(a)}</a><span>{len(ctx["by"][a])}点</span></li>' for a, sl in rows)
    url = f'{ROOT}/{AR_DIR}/'
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noai, noimageai">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="CHARAMARL">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{ROOT}/img/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/img/icon-192.png">
{STYLE}
{HEAD_JS}
</head>
<body>
<header>
  <a class="logo" href="/">CHARAMARL</a>
  <a class="back" href="/">← 市場にもどる</a>
</header>
<main>
  <div class="cat">ARTISTS</div>
  <h1>アーティスト一覧</h1>
  <div class="by">{n}組が参加しています</div>
  <ul class="names">
    {li}
  </ul>
  <h2>読みもの</h2>
  <ul class="lk">
    <li><a href="/{AR_DIR}/charamarl.html">連載インタビュー「市場のひとたち」</a></li>
  </ul>
  <h2>参加したい方へ</h2>
  <ul class="lk">
    <li><a href="/join.html">作家登録のご案内</a>（掲載は無料・1点から）</li>
  </ul>
{NOTE}
</main>
{FOOT}
</body>
</html>
'''

def build_artist_static(ctx, check):
    os.makedirs(AR_DIR, exist_ok=True)
    files = {f'{ctx["slugs"][a]}.html': artist_static(a, ctx) for a in sorted(ctx['by']) if a in ctx['slugs']}
    files['index.html'] = artist_index(ctx)
    # artist.html?a=<名前> が、自分の固有ページを canonical に指すための表
    files['slugs.json'] = json.dumps({a: sl for a, sl in sorted(ctx['slugs'].items()) if a in ctx['by']}, ensure_ascii=False, indent=0)
    made = same = 0
    for f, body in files.items():
        p = os.path.join(AR_DIR, f)
        old = open(p, encoding='utf-8').read() if os.path.exists(p) else None
        if old == body:
            same += 1
            continue
        made += 1
        if not check:
            open(p, 'w', encoding='utf-8').write(body)
    gone = [f for f in os.listdir(AR_DIR) if f not in files]
    if not check:
        for f in gone:
            os.remove(os.path.join(AR_DIR, f))
    print(f'作家の固有ページ  新規/更新 {made} ／ 変更なし {same} ／ 削除 {len(gone)}')


# ---- 作家のシェア用ページ ----
A_DIR, A_IMG = 'a', 'img/og/a'
# 表示名を変えた作家:  前の名前 → 今の名前
RENAMED = {'株式会社トゥインキィープロジェクト': 'トゥインキィー（TWINKII）'}
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mplus900.ttf')

def slug(name):
    """作家名 → 8桁の符号（FNV-1a 32bit）。JS側 cmArtistSlug() と同じ。"""
    h = 0x811c9dc5
    for b in name.strip().encode('utf-8'):
        h = ((h ^ b) * 0x01000193) & 0xffffffff
    return f'{h:08x}'

def pick_works(mine):
    """絵に並べる3点。イベント告知・制作風景より作品を先に、あとは新しい順。"""
    key = lambda w: (w.get('cat') in ('EVENT', 'MAKING'), -int(w.get('publishAt') or w.get('ts') or 0))
    return sorted([w for w in mine if w.get('img')], key=key)[:3]

def og_image(name, picks, out):
    import io
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630
    im = Image.new('RGB', (W, H), (255, 253, 245))
    d = ImageDraw.Draw(im)
    # 上の帯: 左にロゴ、右に作家名
    f_logo = ImageFont.truetype(FONT, 44)
    d.text((44, 44), 'CHARA', font=f_logo, fill=(255, 138, 0))
    d.text((44 + d.textlength('CHARA', font=f_logo), 44), 'MARL', font=f_logo, fill=(142, 78, 217))
    size = 56
    while size > 28 and d.textlength(name, font=ImageFont.truetype(FONT, size)) > 760:
        size -= 2
    f_name = ImageFont.truetype(FONT, size)
    if name:
        d.text((W - 44, 70), name, font=f_name, fill=(26, 26, 38), anchor='rm')
        lab = ImageFont.truetype(FONT, 20)
        d.text((W - 44 - d.textlength(name, font=f_name) - 18, 72), 'ARTIST', font=lab, fill=(255, 138, 0), anchor='rm')
    # 下に作品を並べる（白い札の中に、絵の全体を収める。切らない）
    X0, X1, Y0, Y1, GAP, PAD = 40, 1160, 136, 596, 20, 14
    srcs = []
    for w in picks:
        if not re.match(r'https?://', w['img']):   # 手元のファイル（商品写真など）
            srcs.append(Image.open(w['img']).convert('RGBA'))
            continue
        req = urllib.request.Request(w['img'], headers={'User-Agent': 'Mozilla/5.0'})
        srcs.append(Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=60).read())).convert('RGBA'))
    n, ih = len(srcs), Y1 - Y0 - PAD * 2
    if n == 1:   # 1点だけのときは、札の幅を絵に合わせる
        tws = [max(460, min(X1 - X0, round(srcs[0].width * ih / srcs[0].height) + PAD * 2))]
    else:
        tws = [(X1 - X0 - GAP * (n - 1)) // n] * n
    x = X0 + ((X1 - X0) - (sum(tws) + GAP * (n - 1))) // 2
    for src, tw in zip(srcs, tws):
        d.rounded_rectangle((x, Y0, x + tw, Y1), radius=26, fill=(255, 255, 255), outline=(232, 226, 214), width=2)
        src.thumbnail((tw - PAD * 2, ih), Image.LANCZOS)
        im.paste(src, (x + (tw - src.width) // 2, Y0 + (Y1 - Y0 - src.height) // 2), src)
        x += tw + GAP
    im.save(out, 'JPEG', quality=88)

def share_page(dest, title, desc, og_url, img_url, link_text, og_type='website', canonical=None):
    """OGPだけ持っていて、開くと dest（サイト内のパス）へ移るページ。"""
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="{ROOT}{esc(canonical or dest)}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="CHARAMARL">
<meta property="og:url" content="{esc(og_url)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{esc(img_url)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/img/icon-192.png">
<script>
(function(){{
  var q=location.search.slice(1), d={json.dumps(dest)};
  if(!/(^|&)utm_source=/.test(q)){{
    try{{var h=document.referrer?new URL(document.referrer).hostname:'';
      if(h&&h!=='charamarl.com')q+=(q?'&':'')+'utm_source='+encodeURIComponent(h)+'&utm_medium=referral';}}catch(e){{}}
  }}
  location.replace(d+(q?(d.indexOf('?')<0?'?':'&')+q:''));
}})();
</script>
</head>
<body style="font-family:sans-serif;background:#fffdf5;color:#1a1a26;text-align:center;padding:60px 20px;">
<p><a href="{esc(dest)}" style="color:inherit;font-weight:bold;">{esc(link_text)}</a></p>
</body>
</html>
'''

def artist_page(name, n_works, img_url, canonical=None):
    q = urllib.parse.quote(name, safe='')
    return share_page(f'/artist.html?a={q}', f'{name} の作品 — CHARAMARL',
                      f'{name} さんの作品を CHARAMARL で見られます。♥で応援できて、作家さんのページやお店へそのまま行けます。',
                      f'{ROOT}/{A_DIR}/{slug(name)}.html', img_url, f'{name} の作品を見る →', 'profile', canonical)

G_DIR, G_IMG = 'g', 'img/og/g'

def build_work_shares(ws, check):
    import hashlib
    os.makedirs(G_DIR, exist_ok=True); os.makedirs(G_IMG, exist_ok=True)
    made = same = 0
    keep_html, keep_img = set(), set()
    for w in ws:
        wid, t, a = w['id'], w.get('title') or '', (w.get('artist') or '').strip()
        if not w.get('img') or not re.fullmatch(r'[A-Za-z0-9_-]+', wid):
            continue
        ver = hashlib.sha1(w['img'].encode()).hexdigest()[:6]
        img = f'{wid}_{ver}.jpg'
        keep_html.add(f'{wid}.html'); keep_img.add(img)
        ip, hp = os.path.join(G_IMG, img), os.path.join(G_DIR, f'{wid}.html')
        if not os.path.exists(ip) and not check:
            og_image('' if a == 'CHARAMARL' else a, [w], ip)
        desc = re.sub(r'\s+', ' ', (w.get('desc') or '')).strip()
        desc = (desc[:110] + '…') if len(desc) > 110 else desc
        if not desc:
            desc = f'{a} さんの作品「{t}」。CHARAMARL で見られます。' if a and a != 'CHARAMARL' else f'{t} — CHARAMARL'
        title = f'{t} — {a}｜CHARAMARL' if a and a not in ('CHARAMARL', t) else f'{t}｜CHARAMARL'
        body = share_page(f'/?g={wid}', title, desc, f'{ROOT}/{G_DIR}/{wid}.html', f'{ROOT}/{G_IMG}/{img}', f'{t} を見る →', 'article', f'/w/{wid}.html')
        old = open(hp, encoding='utf-8').read() if os.path.exists(hp) else None
        if old == body:
            same += 1
            continue
        made += 1
        if not check:
            open(hp, 'w', encoding='utf-8').write(body)
    gone = [os.path.join(G_DIR, f) for f in os.listdir(G_DIR) if f.endswith('.html') and f not in keep_html] \
         + [os.path.join(G_IMG, f) for f in os.listdir(G_IMG) if f.endswith('.jpg') and f not in keep_img]
    if not check:
        for f in gone:
            os.remove(f)
    print(f'作品のシェア用ページ  新規/更新 {made} ／ 変更なし {same} ／ 削除 {len(gone)}')

def build_artists(ws, check, slugs_nice=None):
    import hashlib
    os.makedirs(A_DIR, exist_ok=True); os.makedirs(A_IMG, exist_ok=True)
    by = {}
    for w in ws:
        a = (w.get('artist') or '').strip()
        if a and a != 'CHARAMARL' and w.get('cat') != 'INTERVIEW':
            by.setdefault(a, []).append(w)
    slugs = {}
    for a in by:
        assert slug(a) not in slugs, f'符号が重なった: {a} / {slugs[slug(a)]}'
        slugs[slug(a)] = a
    made = same = 0
    og = {}
    keep_html, keep_img = set(), set()
    for sl, a in sorted(slugs.items(), key=lambda x: x[1]):
        picks = pick_works(by[a])
        if not picks:
            continue
        ver = hashlib.sha1('|'.join(w['id'] for w in picks).encode()).hexdigest()[:6]
        img = f'{sl}_{ver}.jpg'
        keep_html.add(f'{sl}.html'); keep_img.add(img)
        ip, hp = os.path.join(A_IMG, img), os.path.join(A_DIR, f'{sl}.html')
        if not os.path.exists(ip) and not check:
            og_image(a, picks, ip)
        og[a] = f'{ROOT}/{A_IMG}/{img}'
        nice = (slugs_nice or {}).get(a)
        body = artist_page(a, len(by[a]), og[a], f'/artist/{nice}.html' if nice else None)
        old = open(hp, encoding='utf-8').read() if os.path.exists(hp) else None
        if old == body:
            same += 1
            continue
        made += 1
        if not check:
            open(hp, 'w', encoding='utf-8').write(body)
    # 表示名を変えた作家。前の名前で貼られたシェア用リンクが切れないよう、前の符号のページも残す（中身は今の名前）
    for was, now in RENAMED.items():
        if now in by and slug(now) in slugs and f'{slug(now)}.html' in keep_html:
            body = open(os.path.join(A_DIR, f'{slug(now)}.html'), encoding='utf-8').read() if not check else ''
            keep_html.add(f'{slug(was)}.html')
            if not check:
                open(os.path.join(A_DIR, f'{slug(was)}.html'), 'w', encoding='utf-8').write(body)
    gone = [os.path.join(A_DIR, f) for f in os.listdir(A_DIR) if f.endswith('.html') and f not in keep_html] \
         + [os.path.join(A_IMG, f) for f in os.listdir(A_IMG) if f.endswith('.jpg') and f not in keep_img]
    if not check:
        for f in gone:
            os.remove(f)
    print(f'作家のシェア用ページ  新規/更新 {made} ／ 変更なし {same} ／ 削除 {len(gone)}')
    return og


_DIRTY = None

def lastmod(path, today):
    """そのファイルを最後に変えた日（git の記録）。まだ commit していない変更があれば今日。"""
    import subprocess
    global _DIRTY
    if _DIRTY is None:   # 1回だけ調べる（ファイルごとに git status を呼ぶと数分かかる）
        out = subprocess.run(['git', 'status', '--porcelain', '-uall'], capture_output=True, text=True).stdout
        _DIRTY = {l[3:].strip().strip('"') for l in out.splitlines()}
    if path in _DIRTY:
        return today
    d = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', path], capture_output=True, text=True).stdout.strip()
    return d or today

def day_of(ms):
    return datetime.fromtimestamp(int(ms or 0) / 1000, JST).strftime('%Y-%m-%d')

def touched(w):
    return max(when(w), int(w.get('edited') or 0))

def sitemap(ws, ctx):
    """lastmod は一律の「今日」にしない。作品は登録・編集の日、作家は最新作の日、ほかは git の最終変更日。"""
    today = datetime.now(JST).strftime('%Y-%m-%d')
    u, seen = [], set()
    def add(path, mod, freq, pri, extra=''):
        if path in seen:
            return
        seen.add(path)
        u.append(f'  <url><loc>{ROOT}{path}</loc><lastmod>{mod}</lastmod>'
                 f'<changefreq>{freq}</changefreq><priority>{pri}</priority>{extra}</url>')
    newest = day_of(max(touched(w) for w in ws))
    for path, pri, freq in STATIC:
        mod = lastmod('index.html' if path == '/' else path.lstrip('/'), today)
        add(path, max(mod, newest) if path == '/' else mod, freq, pri)
    for w in ws:
        t, a = w.get('title') or '', (w.get('artist') or '').strip()
        img = (f'<image:image><image:loc>{esc(w["img"])}</image:loc>'
               f'<image:title>{esc(t)}（{esc(a)}）</image:title></image:image>') if w.get('img') else ''
        add(f'/w/{w["id"]}.html', day_of(touched(w)), 'monthly', '0.7', img)
    add(f'/{AR_DIR}/', newest, 'weekly', '0.7')
    for a in sorted(ctx['by']):
        if a in ctx['slugs']:
            add(f'/{AR_DIR}/{ctx["slugs"][a]}.html', day_of(max(touched(w) for w in ctx['by'][a])), 'weekly', '0.7')
    for d, sub in (('characters', '0.6'), ('tap', '0.6')):
        for f in sorted(os.listdir(d)):
            if not f.endswith('.html') or f'{d}/{f}' in SKIP_HTML:
                continue
            add(f'/{d}/{f}', lastmod(f'{d}/{f}', today), 'monthly', sub)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
            + '\n'.join(u) + '\n</urlset>\n')


def sync_counts(n_artists, check):
    """トップページの説明に書いてある「◯組のアーティストが参加中」を実数に合わせる（手で直すと古くなる）。"""
    s = open('index.html', encoding='utf-8').read()
    t = re.sub(r'\d+組のアーティストが参加中', f'{n_artists}組のアーティストが参加中', s)
    if t != s:
        print(f'index.html の参加組数を {n_artists}組 に直しました')
        if not check:
            open('index.html', 'w', encoding='utf-8').write(t)


def main():
    check = '--check' in sys.argv
    d = json.load(urllib.request.urlopen(API))
    ws = d.get('list', [])
    by = {}
    for w in ws:
        a = (w.get('artist') or '').strip()
        if a:
            by.setdefault(a, []).append(w)
    ctx = {'by': by, 'homes': d.get('artists') or {}, 'prods': products(), 'slugs': nice_slugs(set(by), check), 'og': {}}
    os.makedirs(OUTD, exist_ok=True)

    ctx['og'] = build_artists(ws, check, ctx['slugs'])
    build_work_shares(ws, check)
    build_artist_static(ctx, check)

    made, same = 0, 0
    keep = set()
    for w in ws:
        p = os.path.join(OUTD, f'{w["id"]}.html')
        keep.add(os.path.basename(p))
        body = page(w, ctx)
        old = open(p, encoding='utf-8').read() if os.path.exists(p) else None
        if old == body:
            same += 1
            continue
        made += 1
        if not check:
            open(p, 'w', encoding='utf-8').write(body)

    # 非公開になった作品のページは残さない
    gone = [f for f in os.listdir(OUTD) if f.endswith('.html') and f not in keep]
    if not check:
        for f in gone:
            os.remove(os.path.join(OUTD, f))

    sync_counts(len([a for a in by if a != 'CHARAMARL']), check)
    sm = sitemap(ws, ctx)
    n_urls = sm.count('<url>')
    if not check:
        open('sitemap.xml', 'w', encoding='utf-8').write(sm)

    print(f'作品ページ  新規/更新 {made} ／ 変更なし {same} ／ 削除 {len(gone)}')
    print(f'sitemap.xml  {n_urls} URL（作品{len(ws)} ＋ 作家{len(ctx["slugs"])}＋一覧 ＋ 静的{len(STATIC)} ＋ characters/tap）')
    if check:
        print('※ --check なので書いていません')
    return 0


if __name__ == '__main__':
    sys.exit(main())
