#!/usr/bin/env python3
"""固定投稿に貼る「作品の壁」画像（1200×675・6×3の18枚＋下に帯）を作る

    python3 tools/make_pinned_wall.py [--out 出力先.jpg] [--seed 1]

■ 決めていること
    ・作品のみ（INTERVIEW・EVENT は入れない）。1作家につき1点（直近の作品）。18組をシードで選ぶ
    ・数字（組・作品）は公開中のギャラリーから数える（INTERVIEW除く）。投稿の本文の数字と同じになる
    ・作品は加工しない（正方形に cover で入れるだけ）。価格・売上は載せない
    ・毎月18日の貼り替えのたびに作り直す（数字が変わる）
"""
import sys, os, json, random, subprocess, urllib.request

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
API = 'https://charamarl.com/api/gallery'
W, H, N = 1200, 675, 18

TPL = '''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@500;700;900&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;background:#14121c;font-family:'Zen Kaku Gothic New','Hiragino Sans',sans-serif;position:relative;overflow:hidden;color:#fff}}
.grid{{display:grid;grid-template-columns:repeat(6,200px);grid-template-rows:repeat(3,200px)}}
.grid div{{background:#fff center/cover no-repeat}}
.shade{{position:absolute;left:0;right:0;top:420px;height:255px;background:linear-gradient(rgba(20,18,28,0),rgba(20,18,28,.92) 62%,#14121c)}}
.t1{{position:absolute;left:46px;top:560px;font-size:48px;font-weight:900;letter-spacing:.03em}}
.t2{{position:absolute;left:46px;top:622px;font-size:27px;font-weight:500;color:#d9d6e6}}
.t2 b{{font-weight:900;color:#fff}}
.bar{{position:absolute;left:0;top:0;width:{W}px;height:8px;background:linear-gradient(90deg,#f26b1d 0 33%,#ff7eb6 33% 66%,#7c4dff 66%)}}
</style></head><body>
<div class="grid">{cells}</div><div class="bar"></div><div class="shade"></div>
<div class="t1">キャラクターたちが集まる、小さな市場</div>
<div class="t2"><b>{kumi}組・{n}作品</b>　／　charamarl.com</div>
</body></html>'''


def main():
    a = sys.argv
    out = a[a.index('--out') + 1] if '--out' in a else os.path.expanduser('~/Downloads/CHARAMARL/03_画像/charamarl_pinned.png')
    seed = int(a[a.index('--seed') + 1]) if '--seed' in a else 1
    L = json.load(urllib.request.urlopen(urllib.request.Request(API, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60))['list']
    works = [w for w in L if w.get('cat') not in ('INTERVIEW', 'EVENT')]
    pub = [w for w in L if w.get('cat') != 'INTERVIEW']
    kumi = len({w['artist'] for w in pub})
    latest = {}
    for w in sorted(works, key=lambda w: w.get('publishAt') or w.get('ts') or 0):
        latest[w['artist']] = w
    arts = sorted(latest)
    random.Random(seed).shuffle(arts)
    pick = [latest[x] for x in arts[:N]]
    tmp = os.path.join(os.path.dirname(out), '.pinned_tmp')
    os.makedirs(tmp, exist_ok=True)
    cells = ''
    for i, w in enumerate(pick):
        p = os.path.join(tmp, f'{i:02d}.img')
        open(p, 'wb').write(urllib.request.urlopen(urllib.request.Request(w['img'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read())
        cells += f'<div style="background-image:url(file://{p})"></div>'
    page = os.path.join(tmp, 'page.html')
    open(page, 'w', encoding='utf-8').write(TPL.format(W=W, H=H, cells=cells, kumi=kumi, n=len(pub)))
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', f'--window-size={W},{H}',
                    '--allow-file-access-from-files', '--virtual-time-budget=6000', f'--screenshot={out}', 'file://' + page],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f'{kumi}組・{len(pub)}作品 / 18組を選択（{", ".join(w["artist"] for w in pick)}）→ {out}')


if __name__ == '__main__':
    main()
