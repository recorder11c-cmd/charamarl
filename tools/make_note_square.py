#!/usr/bin/env python3
"""連載「市場のひとたち」のサムネイルを、正方形で作る。

    python3 tools/make_note_square.py            # 4本ぶん作る
    python3 tools/make_note_square.py 04         # #04 だけ

■ なぜ正方形か（2026-09-23）
    note のヘッダー画像は 1280x670（横長）で、それをそのまま
    サイトの INTERVIEW ピンにも使っていた。
    DISCOVER も作家ページも**正方形のタイル**なので、横長の絵は
    上下に余白が入って小さく見える。「noteの画像だけ小さい」状態だった。

    note に貼るヘッダーは 1280x670 のまま。**サイト用に正方形を別で作る。**

■ 作り方
    上半分  バッジ（市場のひとたち #0N）＋ タイトル ＋ 作家名
    下半分  その作家さんの作品を 2x2

    作品は /api/gallery から**その作家さんの公開作品**を取ってくる。
    ⚠️ 絵は作家さんのもの。記事のために借りているという前提は変えない。

■ 出力
    03_画像/note_square/noteNN_<作家>_square.png（1080x1080）
"""
import sys, os, json, html, subprocess, urllib.request, tempfile, base64

API = 'https://charamarl.com/api/gallery'
OUT = os.path.expanduser('~/Downloads/CHARAMARL/03_画像/note_square')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

# 連載の各回。works は「その作家の作品からどれを使うか」（空なら新しい順に4点）
NOTES = [
    dict(no='01', artist='ハンナ',    title='自分に嘘をつかない'),
    dict(no='02', artist='ROKU',      title='ジャンクフード版<br>アンパンマンを作りたい'),
    dict(no='03', artist='カゲチヨ',   title='仕事ではなくて遊びなので、<br>真剣に楽しく遊ぶ'),
    dict(no='04', artist='プラクテル', title='「デザイナーなのに<br>何もやってない人」<br>という焦りから',
         works=['Punch!!', 'とびっきりの∞KAWAII', 'Fairy pop', 'Comic Angel']),
]

TPL = '''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@700;900&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1080px;overflow:hidden;color:#fff;
  font-family:"Zen Kaku Gothic New","Hiragino Sans",sans-serif;
  background:linear-gradient(135deg,#171B2E 0%,#1E2238 45%,#2B1E3F 100%);
  display:flex;flex-direction:column;padding:62px;}}
.top{{flex:1;display:flex;flex-direction:column;justify-content:center;}}
.badge{{align-self:flex-start;background:#F0662B;color:#fff;font-size:23px;font-weight:700;
  letter-spacing:.06em;padding:9px 24px;border-radius:999px;margin-bottom:34px;}}
h1{{font-size:{fs}px;font-weight:900;line-height:1.32;letter-spacing:.01em;}}
.by{{margin-top:26px;font-size:25px;font-weight:700;color:#B9BCCB;letter-spacing:.03em;}}
.by i{{font-style:normal;color:#6E7386;margin:0 16px;}}
/* セルは正方形にする。
   🔴 横長のセルに正方形の絵を object-fit:cover で入れると、顔が上下で切れる。
      ハンナさんの4点が全部そのようになっていた。 */
.grid{{display:grid;gap:16px;grid-template-columns:{cols};}}
.cell{{background:#fff;border-radius:16px;overflow:hidden;aspect-ratio:{ar};}}
.cell img{{width:100%;height:100%;object-fit:cover;display:block;}}
</style></head><body>
<div class="top">
  <div class="badge">市場のひとたち　#{no}</div>
  <h1>{title}</h1>
  <div class="by">{artist}<i>／</i>CHARAMARL</div>
</div>
<div class="grid">{cells}</div>
</body></html>'''


def works_for(artist, want, cache):
    """その作家の公開作品を4点。want に題名があればそれを優先。"""
    mine = [w for w in cache if (w.get('artist') or '').strip() == artist]
    picked = []
    for t in (want or []):
        for w in mine:
            if w.get('title') == t and w not in picked:
                picked.append(w)
    for w in sorted(mine, key=lambda x: -(x.get('ts') or 0)):
        if len(picked) >= 4:
            break
        if w not in picked:
            picked.append(w)
    return picked[:4]


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    os.makedirs(OUT, exist_ok=True)
    cache = json.load(urllib.request.urlopen(API))['list']

    for n in NOTES:
        if only and n['no'] != only:
            continue
        ws = works_for(n['artist'], n.get('works'), cache)
        if len(ws) < 4:
            print(f"  ⚠️ #{n['no']} {n['artist']}: 作品が{len(ws)}点しかない。4点そろってから作り直す")
        tmp = tempfile.mkdtemp()
        cells = ''
        for i, w in enumerate(ws):
            f = os.path.join(tmp, f'w{i}.jpg')
            urllib.request.urlretrieve(w['img'], f)
            b64 = base64.b64encode(open(f, 'rb').read()).decode()
            cells += f'<div class="cell"><img src="data:image/jpeg;base64,{b64}"></div>'
        # 🔴 行数ではなく「いちばん長い行」で字の大きさを決める。
        #    行数だけで決めると、#03 の「仕事ではなくて遊びなので、」が
        #    幅に入らず「で、」だけ次の行に落ちて崩れた。
        rows_t = n['title'].split('<br>')
        longest = max(len(t) for t in rows_t)
        fs = 76 if longest <= 10 else 66 if longest <= 12 else 56 if longest <= 14 else 50
        # 作品が4点そろわないときは並びを変える。
        # 🔴 2x2 に固定すると、1点しかない作家（ROKUさん）で3マスが空いて崩れる。
        n_w = len(ws)
        cols = 'repeat(%d,1fr)' % max(n_w, 1)
        ar = '16/9' if n_w == 1 else '1'   # 1点だけのときは横長の帯で見せる
        htm = TPL.format(no=n['no'], title=n['title'], artist=html.escape(n['artist']),
                         cells=cells, fs=fs, cols=cols, ar=ar)
        src = os.path.join(tmp, 'card.html')
        open(src, 'w', encoding='utf-8').write(htm)
        out = os.path.join(OUT, f"note{n['no']}_{n['artist']}_square.png")
        subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars',
                        '--force-device-scale-factor=1', '--window-size=1080,1080',
                        '--virtual-time-budget=9000', f'--screenshot={out}', src],
                       capture_output=True)
        print(f"  ✓ #{n['no']} {n['artist']}  作品={', '.join(w['title'][:14] for w in ws)}")
        print(f"     {out}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
