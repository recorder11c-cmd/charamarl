#!/usr/bin/env python3
"""「今日の1点」の帯付き画像を作る（1200×1596・Xにそのまま貼れる）

    python3 tools/make_daily.py <作品ID> [出力先ディレクトリ] [--n=015]

    例)  python3 tools/make_daily.py gc84efe2895f9
         python3 tools/make_daily.py gc84efe2895f9 ~/Downloads/CHARAMARL/03_画像/charamarl_daily_img --n=015

■ 何をするか
    作品画像を 1200×1596 いっぱいに収め、その上に 96px の帯を重ねて
    「作品名」と作家名、右端に charamarl.com を置く。
    帯の上には CHARAMARL のグラデーション 5px。

■ カンバスの高さ
    既定は 1200×1596（縦長）。ただし**絵が横長のときは絵に合わせて縮める**。
    横長の絵を縦長の枠に入れると上下が余白だらけになるため。

■ 地の色
    作品の四隅から拾う。作品の地色とカンバスの地色が同じになるので、
    枠に収めたときに余白が出ず、一枚の絵として見える。
    四隅がばらついている（＝地色が無い絵）ときは暗いグレーに落とす。

■ 出力名
    --n を渡すと NNN_<作品ID>.jpg（キューの番号つき）。無ければ <作品ID>.jpg。
    既存の99枚は ~/Downloads/CHARAMARL/03_画像/charamarl_daily_img/ にある。
"""
import sys, os, json, html, base64, subprocess, urllib.request, io
from PIL import Image

API = 'https://charamarl.com/api/gallery'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
W, H, BAND = 1200, 1596, 96          # 帯は下から96px（うち5pxがグラデーション）
OUT_DEFAULT = os.path.expanduser('~/Downloads/CHARAMARL/03_画像/charamarl_daily_img')


def corner_bg(im):
    """四隅の色から地色を決める。ばらついていたら地色なしと見なす。"""
    im = im.convert('RGB')
    w, h = im.size
    pts = [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]
    cs = [im.getpixel(p) for p in pts]
    avg = tuple(sum(c[i] for c in cs) // 4 for i in range(3))
    spread = max(max(abs(c[i] - avg[i]) for i in range(3)) for c in cs)
    return avg if spread <= 24 else (26, 25, 32)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    num = next((a[4:] for a in sys.argv[1:] if a.startswith('--n=')), '')
    if not args:
        raise SystemExit('使い方: python3 tools/make_daily.py <作品ID> [出力先] [--n=015]')
    gid = args[0]
    outdir = os.path.expanduser(args[1]) if len(args) > 1 else OUT_DEFAULT

    works = json.load(urllib.request.urlopen(API))['list']
    w = next((x for x in works if x['id'] == gid), None)
    if not w:
        raise SystemExit(f'作品 {gid} が公開一覧にありません（予約公開中か、未承認かもしれません）')

    raw = urllib.request.urlopen(w['img']).read()
    im = Image.open(io.BytesIO(raw))
    bg = corner_bg(im)

    # 🔴 横長の絵を 1200x1596 に入れると、上下に帯ほどの余白が出て絵が小さく見える。
    #    らすべっとさんの「夏がこのビー玉だけ残していっちゃった」(1600x645)で
    #    絵の占有が3割を切った。**カンバスの高さを絵に合わせる。**
    #    Xのタイムラインは16:9で切るので、それより縦長になるぶんには問題ない。
    global H
    iw, ih = im.size
    fit = round(W * ih / iw) + BAND
    H = max(min(H, fit), 600)
    # 白っぽい地は帯とのコントラストが弱いので、そのまま使う（絵を優先する）
    b64 = base64.b64encode(raw).decode()
    mime = 'image/png' if raw[:4] == b'\x89PNG' else 'image/jpeg'

    doc = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:rgb{bg};
 font-family:"Hiragino Sans","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif}}
.art{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;overflow:hidden}}
.art img{{width:100%;height:100%;object-fit:contain;display:block}}
.foot{{position:absolute;left:0;right:0;bottom:0}}
.stripe{{height:5px;background:linear-gradient(90deg,#FF8A00 0%,#FF4D8D 52%,#8E4ED9 100%)}}
.band{{height:{BAND-5}px;background:#18171D;display:flex;align-items:center;
 padding:0 26px;gap:16px}}
.who{{min-width:0;flex:1}}
.t{{color:#fff;font-size:30px;font-weight:700;line-height:1.15;
 white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.a{{color:#9B96A6;font-size:19px;font-weight:600;line-height:1.3;margin-top:4px;
 white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.url{{color:#8E8998;font-size:21px;font-weight:600;letter-spacing:.02em;flex:none}}
</style></head><body>
 <div class="art"><img src="data:{mime};base64,{b64}"></div>
 <div class="foot">
 <div class="stripe"></div>
 <div class="band">
   <div class="who">
     <div class="t">「{html.escape(w['title'])}」</div>
     <div class="a">{html.escape(w.get('artist') or '')}</div>
   </div>
   <div class="url">charamarl.com</div>
 </div>
 </div>
</body></html>'''

    os.makedirs(outdir, exist_ok=True)
    base = os.path.join(outdir, (f'{num}_{gid}' if num else gid))
    tmp = base + '.html'
    open(tmp, 'w', encoding='utf-8').write(doc)
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars',
                    '--force-device-scale-factor=1', f'--window-size={W},{H}',
                    '--virtual-time-budget=12000', f'--screenshot={base}.png', tmp],
                   check=True, capture_output=True)
    Image.open(base + '.png').convert('RGB').save(base + '.jpg', quality=92, optimize=True)
    os.remove(base + '.png'); os.remove(tmp)
    print(f'{base}.jpg  （{w["artist"]} ／ {w["title"]}）')


if __name__ == '__main__':
    main()
