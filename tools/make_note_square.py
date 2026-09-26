#!/usr/bin/env python3
"""連載「市場のひとたち」のサムネイルを作る（正方形＋note用の横長）。

    python3 tools/make_note_square.py            # 4本ぶん・両サイズ
    python3 tools/make_note_square.py 04         # #04 だけ

■ 地の色を明るくした（2026-09-25）
    🔴 **地が暗いと、暗い絵の作家さんが沈む。**
    #01ハンナさんのタイルははっきり見えるのに、#04プラクテルさんのタイルは
    濃紺の地に溶けていた。**作家さんによって見え方が変わるのは、
    トップページを均等な抽選にしている考え方と矛盾する。**
    明るい地なら、どの絵も同じ条件で出る。
    ⚠️ ヘッダーは #01だけ明るいピンク・#02は茶色・#03#04は濃紺と3種類に割れていた。
    連載は必ず並んで出る（noteのマガジン／サイトのINTERVIEWピン／Xのカード）ので揃える。
    配色は作家向けPDF・1か月報告と同じ紙の色。

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
    dict(no='01', artist='ハンナ', sub='ボストンテリアのラフ',
         title='自分に嘘をつかない',
         wide='「月に行って帰ってくるほど、<br>あなたを愛してる」'),
    dict(no='02', artist='ROKU', sub='JUNKeeeeS',
         title='ジャンクフード版<br>アンパンマンを作りたい',
         wide='ジャンクフード版<br>アンパンマンを作りたい'),
    dict(no='03', artist='カゲチヨ', sub='メカニャン',
         title='仕事ではなくて遊びなので、<br>真剣に楽しく遊ぶ',
         wide='仕事ではなくて遊びなので、<br>真剣に楽しく遊ぶ'),
    dict(no='04', artist='プラクテル', sub='',
         title='「デザイナーなのに<br>何もやってない人」<br>という焦りから',
         wide='「デザイナーなのに<br>何もやってない人」<br>という焦りから',
         works=['Punch!!', 'とびっきりの∞KAWAII', 'Fairy pop', 'Comic Angel']),
]

TPL = '''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@700;900&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{w}px;height:{h}px;overflow:hidden;color:#20180F;background:#F6F1E6;
  font-family:"Zen Kaku Gothic New","Hiragino Sans",sans-serif;
  position:relative;padding:{pad}px;display:flex;{flex}}}
.rail{{position:absolute;left:0;right:0;top:0;height:{rail}px;
  background:linear-gradient(90deg,#FF8A00,#FF4D8D 52%,#8E4ED9);}}
.txt{{display:flex;flex-direction:column;justify-content:center;{txtw}}}
.badge{{align-self:flex-start;background:#D2610E;color:#fff;font-size:{bs}px;font-weight:700;
  letter-spacing:.06em;padding:{bp}px {bp2}px;border-radius:999px;margin-bottom:{bm}px;}}
h1{{font-size:{fs}px;font-weight:900;line-height:1.34;letter-spacing:.01em;}}
.by{{margin-top:{bym}px;font-size:{bys}px;font-weight:700;color:#8D8377;letter-spacing:.03em;}}
.by i{{font-style:normal;color:#C0B6A6;margin:0 {gap}px;}}
/* セルは正方形にする。
   🔴 横長のセルに正方形の絵を object-fit:cover で入れると、顔が上下で切れる。 */
.grid{{display:grid;gap:{gg}px;grid-template-columns:{cols};{gw}}}
.cell{{background:#fff;border:1px solid #E7DFD0;border-radius:{r}px;overflow:hidden;aspect-ratio:{ar};
  box-shadow:0 1px 2px rgba(32,24,15,.05), 0 10px 24px -18px rgba(32,24,15,.35);}}
.cell img{{width:100%;height:100%;object-fit:cover;display:block;}}
</style></head><body>
  <div class="rail"></div>
  <div class="txt">
    <div class="badge">市場のひとたち　#{no}</div>
    <h1>{title}</h1>
    <div class="by">{artist}<i>／</i>CHARAMARL</div>
  </div>
  <div class="grid">{cells}</div>
</body></html>'''


def works_for(artist, want, cache):
    """その作家の公開作品を4点。want に題名があればそれを優先。"""
    # 🔴 EVENT と INTERVIEW は作品ではない。
    #    2026-09-25、ROKUさんの枠に JUNKeeeeS FES とクラファンの告知2点が
    #    「作品」として並んだ。告知の画像をインタビュー記事の表紙に使わない。
    SKIP = {'EVENT', 'INTERVIEW'}
    mine = [w for w in cache
            if (w.get('artist') or '').strip() == artist and w.get('cat') not in SKIP]
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

    # 正方形＝サイト/SNSのタイル。横長＝noteのヘッダー。
    SIZES = [
        dict(tag='square', w=1080, h=1080, flex='flex-direction:column;',
             txtw='flex:1;', gw='', pad=62, rail=7, gg=16),
        dict(tag='note', w=1280, h=670, flex='align-items:center;gap:44px;',
             txtw='flex:1.25;', gw='flex:1;', pad=64, rail=6, gg=13),
    ]
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
        n_w = len(ws)
        artist = n['artist'] + (f"（{n['sub']}）" if n.get('sub') else '')

        for S in SIZES:
            title = n['wide'] if S['tag'] == 'note' else n['title']
            # 🔴 行数ではなく「いちばん長い行」で字の大きさを決める。
            #    行数だけで決めると、#03 の「仕事ではなくて遊びなので、」が
            #    幅に入らず「で、」だけ次の行に落ちて崩れた。
            longest = max(len(t) for t in title.split('<br>'))
            base = 76 if longest <= 10 else 66 if longest <= 12 else 56 if longest <= 14 else 50
            fs = base if S['tag'] == 'square' else int(base * 0.74)
            # 🔴 2x2 に固定すると、1点しかない作家（ROKUさん）で3マスが空いて崩れる。
            if S['tag'] == 'note':
                cols = 'repeat(%d,1fr)' % (1 if n_w == 1 else 2)
            else:
                cols = 'repeat(%d,1fr)' % max(n_w, 1)
            ar = '16/9' if n_w == 1 else '1'
            k = S['w'] / 1080.0
            htm = TPL.format(no=n['no'], title=title, artist=html.escape(artist),
                             cells=cells, fs=fs, cols=cols, ar=ar,
                             w=S['w'], h=S['h'], flex=S['flex'], txtw=S['txtw'], gw=S['gw'],
                             pad=S['pad'], rail=S['rail'], gg=S['gg'], r=int(16 * k),
                             bs=int(23 * k), bp=int(9 * k), bp2=int(24 * k),
                             bm=int(34 * k), bym=int(26 * k), bys=int(25 * k), gap=int(16 * k))
            src = os.path.join(tmp, f"card_{S['tag']}.html")
            open(src, 'w', encoding='utf-8').write(htm)
            out = os.path.join(OUT, f"note{n['no']}_{n['artist']}_{S['tag']}.png")
            subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars',
                            '--force-device-scale-factor=1', f"--window-size={S['w']},{S['h']}",
                            '--virtual-time-budget=9000', f'--screenshot={out}', src],
                           capture_output=True)
            print(f"  \u2713 {out}")
        print(f"     作品={', '.join(w['title'][:14] for w in ws)}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
