#!/usr/bin/env python3
"""市の日（毎月18日）の本投稿に貼る「この1か月の新作まとめ」画像（1200×1500・Xにそのまま貼れる）

    python3 tools/make_ichinohi.py                       # 前回の市の日の翌日〜今日に公開された作品
    python3 tools/make_ichinohi.py --since 2026-09-19 --month 10 [--out 出力先.png]

■ 決めていること
    ・対象＝公開済みの作品（ARTWORK / CHARACTER / PRODUCT）。インタビュー記事・イベント告知は入れない
    ・前回の市の日（その日12:00に公開した分は前回の投稿に載せ済み）は --since を翌日にして除く
    ・作品は加工しない（正方形の枠に cover で入れるだけ）。価格・リンクは画像に入れない
    ・作家名は枠の下に小さく
"""
import sys, os, io, json, html, datetime, subprocess, urllib.request

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
W, H = 1200, 1500
API = 'https://charamarl.com/api/gallery'
SKIP_CAT = ('INTERVIEW', 'EVENT')
ROWS = {17: [5, 4, 4, 4], 16: [4, 4, 4, 4], 15: [5, 5, 5], 18: [5, 5, 4, 4], 19: [5, 5, 5, 4], 20: [5, 5, 5, 5]}

TPL = '''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@700;900&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;font-family:'Zen Kaku Gothic New','Hiragino Sans',sans-serif;
 background:#7c4dff radial-gradient(rgba(255,255,255,.16) 2px,transparent 2.5px) 0 0/26px 26px;position:relative;overflow:hidden;color:#fff}}
.flags{{position:absolute;left:0;top:0;width:{W}px;height:150px}}
.head{{position:absolute;top:112px;left:0;right:0;text-align:center}}
.tent{{font-size:64px;line-height:1}}
.ttl{{font-size:116px;font-weight:900;line-height:1.05;letter-spacing:.06em;text-shadow:0 6px 0 rgba(60,20,140,.45)}}
.sub{{margin-top:4px;font-size:38px;font-weight:900}}
.sub b{{background:#fff;color:#7c4dff;border-radius:999px;padding:0 20px;margin:0 6px;font-size:44px}}
.grid{{position:absolute;top:392px;left:0;right:0}}
.row{{display:flex;justify-content:center;gap:22px;margin-bottom:8px}}
.t{{width:{TW}px}}
.t .im{{width:{TW}px;height:{TW}px;border:7px solid #fff;border-radius:14px;box-shadow:0 8px 18px rgba(40,10,110,.45);
 background:#fff center/cover no-repeat}}
.t .nm{{margin:4px -24px 0;font-size:21px;font-weight:700;text-align:center;white-space:nowrap}}
.foot{{position:absolute;bottom:22px;left:0;right:0;display:flex;justify-content:center}}
.card{{background:#fff;border-radius:22px;padding:10px 40px;text-align:center;box-shadow:0 8px 18px rgba(40,10,110,.4)}}
.logo{{font-size:52px;font-weight:900;letter-spacing:.04em;line-height:1.1}}
.logo .a{{color:#f26b1d}}.logo .b{{color:#7c4dff}}
.tag{{font-size:23px;font-weight:900;color:#3a2a6a}}
</style></head><body>
<svg class="flags" viewBox="0 0 {W} 150" preserveAspectRatio="none">{flags}</svg>
<div class="head"><div class="tent">🎪</div><div class="ttl">市の日</div>
<div class="sub">この1か月の新作<b>{n}点</b></div></div>
<div class="grid">{rows}</div>
<div class="foot"><div class="card"><div class="logo"><span class="a">CHARA</span><span class="b">MARL</span></div>
<div class="tag">キャラクターとアートの市場</div></div></div>
</body></html>'''


def fetch(since):
    d = json.load(urllib.request.urlopen(urllib.request.Request(API, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60))['list']
    cut = datetime.datetime.strptime(since, '%Y-%m-%d').timestamp() * 1000
    out = []
    for w in d:
        t = w.get('publishAt') or w.get('ts') or 0
        if t >= cut and w.get('cat') not in SKIP_CAT:
            out.append((t, w))
    return [w for _, w in sorted(out, key=lambda x: x[0])]


def flags_svg():
    cols = ['#f26b1d', '#ffd23f', '#ffffff', '#ff7eb6', '#2ec4b6']
    n, fw = 16, W / 16
    s = '<path d="M0 22 Q{} 70 {} 22" stroke="#fff" stroke-width="4" fill="none"/>'.format(W / 2, W)
    for i in range(n):
        x = i * fw
        # 弧にそって旗を吊るす（二次ベジェの y を近似）
        tm = (x + fw / 2) / W
        y = 22 + 2 * 48 * tm * (1 - tm) * 1.0
        s += '<polygon points="{:.0f},{:.0f} {:.0f},{:.0f} {:.0f},{:.0f}" fill="{}"/>'.format(
            x + 6, y, x + fw - 6, y, x + fw / 2, y + 86, cols[i % len(cols)])
    return s


def main():
    a = sys.argv
    since = a[a.index('--since') + 1] if '--since' in a else None
    if not since:
        raise SystemExit('--since YYYY-MM-DD（前回の市の日の翌日）を指定してください')
    out = a[a.index('--out') + 1] if '--out' in a else os.path.expanduser('~/Library/Mobile Documents/com~apple~CloudDocs/CHARAMARL/03_画像/charamarl_ichinohi_new.png')
    works = fetch(since)
    n = len(works)
    rows = ROWS.get(n)
    if not rows:
        raise SystemExit(f'{n}点：行の割り付けが未定義（ROWS に追加）')
    tmp = os.path.join(os.path.dirname(out), '.ichinohi_tmp')
    os.makedirs(tmp, exist_ok=True)
    tw = 192
    rot = [-2.2, 1.6, -1.2, 2.4, -1.8, 1.2]
    html_rows, i = '', 0
    for r in rows:
        cells = ''
        for _ in range(r):
            w = works[i]
            p = os.path.join(tmp, f'{i:02d}.img')
            open(p, 'wb').write(urllib.request.urlopen(urllib.request.Request(w['img'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read())
            cells += '<div class="t" style="transform:rotate({}deg)"><div class="im" style="background-image:url(file://{})"></div><div class="nm">{}</div></div>'.format(
                rot[i % len(rot)], p, html.escape(w['artist']))
            i += 1
        html_rows += f'<div class="row">{cells}</div>'
    page = os.path.join(tmp, 'page.html')
    open(page, 'w', encoding='utf-8').write(TPL.format(W=W, H=H, TW=tw, n=n, rows=html_rows, flags=flags_svg()))
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', f'--window-size={W},{H}',
                    '--allow-file-access-from-files', '--virtual-time-budget=6000', f'--screenshot={out}', 'file://' + page],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for w in works:
        print(f'  {w["artist"]} 「{w["title"][:20]}」')
    print(f'{n}点 → {out}')


if __name__ == '__main__':
    main()
