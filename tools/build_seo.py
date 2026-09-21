#!/usr/bin/env python3
"""作品ごとの固有ページ（/w/<id>.html）と sitemap.xml を作る。

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

■ 作らない理由があるもの
    ・ログイン後の画面（mypage/login/success/cancel/apply-admin）は noindex 相当なので入れない
    ・`characters/kagechiyo-acrylic.html` は委託分で未販売。noindex なので入れない
    ・作品ページは **API の公開分だけ**。予約公開はその時刻を過ぎてから次回生成で入る

■ 作品画像について
    画像は blob のURLをそのまま指す（コピーしない）。
    右クリック等の抑止は既存の js/protect.js をそのまま読み込む。
"""
import sys, os, json, html, re, urllib.request
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


def page(w):
    t, a = w.get('title') or '', w.get('artist') or ''
    desc = re.sub(r'\s+', ' ', (w.get('desc') or '')).strip()
    short = (desc[:110] + '…') if len(desc) > 110 else desc
    if not short:
        short = f'{a} さんの作品「{t}」。CHARAMARLに掲載しています。'
    url = f'{ROOT}/w/{w["id"]}.html'
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- tools/build_seo.py が自動生成。直接編集しない。作品データは /api/gallery が出どころ。 -->
<title>{esc(t)} — {esc(a)} ｜ CHARAMARL</title>
<meta name="description" content="{esc(short)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(t)} — {esc(a)}">
<meta property="og:description" content="{esc(short)}">
<meta property="og:image" content="{esc(w.get('img'))}">
<meta name="twitter:card" content="summary_large_image">
<style>
  :root{{--bg:#0e0e14;--card:#1f1f2e;--accent:#f5c842;--accent2:#a259ff;--text:#f0f0f0;--muted:#8b8b99;}}
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{background:var(--bg);color:var(--text);font-family:'Helvetica Neue',Arial,sans-serif;}}
  header{{display:flex;align-items:center;justify-content:space-between;padding:18px 24px;border-bottom:1px solid rgba(255,255,255,.08);}}
  .logo{{font-size:20px;font-weight:900;letter-spacing:.1em;background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;text-decoration:none;}}
  .back{{color:var(--muted);text-decoration:none;font-size:13px;}}
  main{{max-width:760px;margin:0 auto;padding:30px 20px 60px;}}
  .art{{background:#fff;border-radius:18px;overflow:hidden;display:flex;align-items:center;justify-content:center;margin-bottom:22px;}}
  .art img{{width:100%;height:auto;display:block;}}
  .cat{{font-size:11px;font-weight:800;letter-spacing:.14em;color:var(--accent);}}
  h1{{font-size:clamp(24px,5vw,36px);font-weight:900;margin:6px 0 4px;line-height:1.3;}}
  .by{{color:var(--muted);font-size:14px;margin-bottom:18px;}}
  .by a{{color:var(--text);text-decoration:none;border-bottom:1px solid rgba(255,255,255,.25);}}
  p.desc{{font-size:14.5px;line-height:1.95;color:#d5d2dd;margin-bottom:26px;white-space:pre-wrap;}}
  .row{{display:flex;gap:10px;flex-wrap:wrap;}}
  .btn{{display:inline-flex;align-items:center;gap:7px;border-radius:24px;padding:12px 22px;
   font-size:14px;font-weight:900;text-decoration:none;}}
  .btn.p{{background:var(--accent);color:#1a1a26;}}
  .btn.s{{background:var(--card);color:var(--text);}}
  .note{{margin-top:30px;padding-top:18px;border-top:1px solid rgba(255,255,255,.08);
   font-size:12px;line-height:1.9;color:var(--muted);}}
  footer{{text-align:center;color:var(--muted);font-size:12px;padding:24px;}}
</style>
<script defer src="/_vercel/insights/script.js"></script>
<script src="/js/ga.js"></script>
<script src="/js/protect.js"></script>
</head>
<body>
<header>
  <a class="logo" href="/">CHARAMARL</a>
  <a class="back" href="/">← 市場にもどる</a>
</header>
<main>
  <div class="art"><img src="{esc(w.get('img'))}" alt="{esc(t)}"></div>
  <div class="cat">{esc(w.get('cat') or 'ARTWORK')}</div>
  <h1>{esc(t)}</h1>
  <div class="by">by <a href="/artist.html?a={esc(a)}">{esc(a)}</a></div>
  <p class="desc">{esc(desc)}</p>
  <div class="row">
    <a class="btn p" href="/?g={esc(w['id'])}">🎪 市場で見る（♥で応援できます）</a>
    <a class="btn s" href="/artist.html?a={esc(a)}">{esc(a)} の作品をすべて見る</a>
  </div>
  <div class="note">
    CHARAMARLは、キャラクターたちが集まる小さな市場です。掲載は無料。<br>
    掲載作品を<b>生成AIの学習には利用しません</b>（規約に明記）。
  </div>
</main>
<footer>© 2026 CHARAMARL / レコルダ合同会社</footer>
</body>
</html>
'''


def sitemap(ws, artists):
    today = datetime.now(JST).strftime('%Y-%m-%d')
    u = []
    for path, pri, freq in STATIC:
        u.append(f'  <url><loc>{ROOT}{path}</loc><lastmod>{today}</lastmod>'
                 f'<changefreq>{freq}</changefreq><priority>{pri}</priority></url>')
    for w in ws:
        d = datetime.fromtimestamp((w.get('ts') or 0) / 1000, JST).strftime('%Y-%m-%d')
        u.append(f'  <url><loc>{ROOT}/w/{w["id"]}.html</loc><lastmod>{d}</lastmod>'
                 f'<changefreq>monthly</changefreq><priority>0.7</priority></url>')
    for a in sorted(artists):
        q = urllib.parse.quote(a, safe='')
        u.append(f'  <url><loc>{ROOT}/artist.html?a={q}</loc><lastmod>{today}</lastmod>'
                 f'<changefreq>weekly</changefreq><priority>0.7</priority></url>')
    already = {u.split('<loc>')[1].split('</loc>')[0] for u in u}   # STATIC と重複させない
    for d, sub in (('characters', '0.6'), ('tap', '0.6')):
        for f in sorted(os.listdir(d)):
            if not f.endswith('.html') or f'{d}/{f}' in SKIP_HTML:
                continue
            if f'{ROOT}/{d}/{f}' in already:
                continue
            u.append(f'  <url><loc>{ROOT}/{d}/{f}</loc><lastmod>{today}</lastmod>'
                     f'<changefreq>monthly</changefreq><priority>{sub}</priority></url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemap.org/schemas/sitemap/0.9">\n'
            .replace('sitemap.org', 'sitemaps.org')
            + '\n'.join(u) + '\n</urlset>\n')


def main():
    check = '--check' in sys.argv
    ws = works()
    artists = {w.get('artist') for w in ws if w.get('artist')}
    os.makedirs(OUTD, exist_ok=True)

    made, same = 0, 0
    keep = set()
    for w in ws:
        p = os.path.join(OUTD, f'{w["id"]}.html')
        keep.add(os.path.basename(p))
        body = page(w)
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

    sm = sitemap(ws, artists)
    n_urls = sm.count('<url>')
    if not check:
        open('sitemap.xml', 'w', encoding='utf-8').write(sm)

    print(f'作品ページ  新規/更新 {made} ／ 変更なし {same} ／ 削除 {len(gone)}')
    print(f'sitemap.xml  {n_urls} URL（作品{len(ws)} ＋ 作家{len(artists)} ＋ 静的{len(STATIC)} ＋ characters/tap）')
    if check:
        print('※ --check なので書いていません')
    return 0


if __name__ == '__main__':
    import urllib.parse
    sys.exit(main())
