#!/usr/bin/env python3
"""作家さんに渡す「紹介カード」を作る（2400×1350・XやInstagramにそのまま貼れる）

左に作品、右にCHARAMARLのロゴと作家名・作品名・ページURL。
COLOR TAP がある作家は、色違いを並べて「タップで色が変わる」を画像だけで伝える。

■ 使い方
    python3 tools/make_card.py <作家名> [出力先ディレクトリ] [--work=<作品ID>]

    例)  python3 tools/make_card.py エリー
         python3 tools/make_card.py 'DREAMER©' ~/Downloads/charamarl_share
         python3 tools/make_card.py ハンナ --work=g880d0bb94576

    作家名は /api/gallery の artist と完全一致させる。
    既定はその作家のいちばん新しい作品。--work で1点を指名できる。
    COLOR TAP がある作家は TAPS 側で作品を固定しているので、新作が出ても差し替わらない。

■ 仕組み
    HTMLを組み立てて、ヘッドレスChromeでスクリーンショットを撮る。
    画像はギャラリーのURLをそのまま読ませるので、手元に落とす必要がない。
    HTMLも一緒に残るので、文言を直して撮り直せる。

■ 注意
  - **白っぽいキャラは地を暗くする**（DARK_BG に作家名を足す）。明るい地だと消える。
  - COLOR TAP の色違いは tap/art/colors/{key}_{色}.png を読む（TAPS に定義）。
"""
import sys, os, json, html, subprocess, urllib.request, base64

API = 'https://charamarl.com/api/gallery'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
TAPDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tap', 'art', 'colors')

# COLOR TAP があり、事前生成PNGを並べられる作家 → (imageKey, 色キーの順番, TAPページ, 作品ID)
# ⚠️ 色見本と主役の絵は同じキャラでないと成立しない。作家が新作を出すと「いちばん新しい作品」は
#    TAPと別のキャラになるので、TAPがある作家はここで作品を固定する。
TAPS = {
    'DREAMER©': ('ghost', ['orig', 'pumpkin', 'poison', 'blood', 'midnight', 'ice'], 'tap/ghost.html', 'g0ba427b52450'),
    'チンチロ': ('blockma', ['orig', 'candy', 'neon', 'flame', 'ocean', 'gold'], 'tap/blockma.html', 'g53905fbdc117'),
    'CryptoSuperHeroes': ('csh', ['pizza', 'shark', 'fly', 'water', 'drdangerous', 'ultimate'], 'tap/csh.html', 'g4df484fa9830'),
    'MARU_GMC': ('gmc', ['red', 'yellow', 'green', 'cyan', 'blue', 'pink'], 'tap/gmc.html', None),
}
# 作品の地を暗くする作家（白いキャラで、明るい地だと消えるもの）
DARK_BG = {'DREAMER©'}


def b64(path):
    return base64.b64encode(open(path, 'rb').read()).decode()


def build(artist, outdir, work_id=None):
    works = json.load(urllib.request.urlopen(API))['list']
    mine = [w for w in works if (w.get('artist') or '') == artist]
    if not mine:
        raise SystemExit(f'「{artist}」の作品が見つかりません（artist名を完全一致で指定する）')
    mine.sort(key=lambda w: -(w.get('ts') or 0))

    tap = TAPS.get(artist)
    pin = work_id or (tap[3] if tap and len(tap) > 3 else None)
    w = next((x for x in mine if x['id'] == pin), None) if pin else None
    if pin and not w:
        raise SystemExit(f'作品ID {pin} が「{artist}」の作品にありません')
    if not w:
        w = mine[0]
    dark = artist in DARK_BG
    sws = ''
    if tap:
        key, colors = tap[0], tap[1]
        sws = '<div class="sws">' + ''.join(
            f'<img class="sw" src="data:image/png;base64,{b64(f"{TAPDIR}/{key}_{c}.png")}">'
            for c in colors) + '</div>'

    page = 'charamarl.com'
    # 作家ページのURLは ?a=作家名 が要るので、カードには載せない（載せると押せないURLになる）
    sub = '/tap/' + tap[2].split('/')[-1] if tap else ''
    line = '🎨 タップすると色が変わります' if tap else f'「{w["title"]}」を掲載中'
    # 作品名が長いとピルが2行になるので、長さで字を小さくする
    pill_fs = 25 if len(line) <= 16 else 22 if len(line) <= 22 else 19

    doc = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1200px;height:675px;overflow:hidden;position:relative;background:#f4f4f8;
 font-family:"Hiragino Sans","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif}}
body::before{{content:"";position:absolute;inset:0;
 background:radial-gradient(900px 500px at 88% 4%, #ffe9d2 0%, rgba(255,233,210,0) 62%),
            radial-gradient(700px 500px at 2% 98%, #ece4fb 0%, rgba(236,228,251,0) 60%)}}
.wrap{{position:relative;display:flex;align-items:center;gap:52px;padding:56px 64px;height:100%}}
.card{{width:494px;height:563px;flex:none;background:{'#12121c' if dark else '#fff'};border-radius:34px;
 box-shadow:0 18px 48px rgba(20,18,32,.16);display:flex;flex-direction:column;
 align-items:center;justify-content:center;gap:20px;padding:{'30px' if tap else '0'};overflow:hidden}}
.card img.main{{width:{'300px' if tap else '100%'};height:{'300px' if tap else '100%'};
 object-fit:{'contain' if tap else 'cover'};display:block;{'image-rendering:pixelated;' if tap else ''}}}
.sws{{display:flex;gap:10px}}
img.sw{{width:58px;height:58px;object-fit:contain;image-rendering:pixelated;
 background:rgba(255,255,255,.05);border-radius:12px;padding:4px}}
.cap{{font-size:18px;font-weight:700;color:#8b89a0;letter-spacing:.06em}}
.right{{flex:1;min-width:0}}
.logo{{font-family:"Helvetica Neue",Arial,sans-serif;font-weight:800;font-size:53px;
 letter-spacing:.10em;line-height:1;margin-bottom:9px}}
.logo .a{{color:#F97316}}.logo .b{{color:#8B5CF6}}
.tag{{font-size:19px;font-weight:700;color:#8e8ca3;margin-bottom:38px}}
.who{{font-size:47px;font-weight:800;color:#17161f;line-height:1.2;
 white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.who small{{font-size:27px;font-weight:700;margin-left:6px}}
.work{{font-size:27px;font-weight:700;color:#17161f;margin-top:12px;line-height:1.4}}
.tap{{margin-top:26px;display:inline-flex;align-items:center;gap:12px;background:#12121c;color:#fff;
 border-radius:999px;padding:15px 28px;font-size:{pill_fs}px;font-weight:800;line-height:1.3}}
.url{{margin-top:22px;font-size:25px;font-weight:800;color:#3b3949}}
.url span{{color:#8e8ca3;font-weight:700}}
</style></head><body><div class="wrap">
 <div class="card"><img class="main" src="{html.escape(w['img'])}">{sws}
 {f'<div class="cap">{html.escape(w["title"])}</div>' if tap else ''}</div>
 <div class="right">
  <div class="logo"><span class="a">CHARA</span><span class="b">MARL</span></div>
  <div class="tag">キャラクターたちが集まる小さな市場</div>
  <div class="who">{html.escape(artist)}<small>さん</small></div>
  <div class="tap">{html.escape(line)}</div>
  <div class="url">{page}<span>{sub}</span></div>
 </div></div></body></html>'''

    os.makedirs(outdir, exist_ok=True)
    slug = ''.join(c for c in artist if c.isalnum() or c in '_-') or 'card'
    base = os.path.join(outdir, f'charamarl_card_{slug}')
    open(base + '.html', 'w', encoding='utf-8').write(doc)
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars',
                    '--force-device-scale-factor=2', '--window-size=1200,675',
                    '--virtual-time-budget=12000', f'--screenshot={base}.png', base + '.html'],
                   check=True, capture_output=True)
    print(f'{base}.png  （{artist} ／ {w["title"]}）')


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--work=')]
    wid = next((a[7:] for a in sys.argv[1:] if a.startswith('--work=')), None)
    if not args:
        raise SystemExit('使い方: python3 tools/make_card.py <作家名> [出力先] [--work=<作品ID>]')
    build(args[0], os.path.expanduser(args[1] if len(args) > 1
                                      else '~/Downloads/charamarl_share'), wid)
