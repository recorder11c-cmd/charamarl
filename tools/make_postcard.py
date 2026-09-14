#!/usr/bin/env python3
"""同梱するポストカード（はがき 100×148mm・両面）を作る。

    python3 tools/make_postcard.py [出力先ディレクトリ]

作るもの
    charamarl_postcard_front.png / .pdf   … 全キャラ＋THANK YOU（取っておいてもらう面）
    charamarl_postcard_back.png  / .pdf   … QR・割引コード・ひとこと

■ なぜ2面に分けるか
    表は「捨てられない理由」、裏は「次に来る理由」。役割を混ぜると、どちらも効かない。

■ QRのURLには必ず utm を付ける
    付けないと、カードが効いたのかどうかが永久に分からない。

■ 印刷
    300dpi・塗り足し3mm込みで 106×154mm（1252×1819px）で書き出す。
    塗り足し不要なら BLEED_MM = 0 にする。フチなし印刷ができない家庭用プリンタなら 0 のほうがよい。
"""
import os, sys, base64, subprocess, io
import segno
from PIL import Image

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DPI = 300
CARD_MM = (100, 148)          # はがき
BLEED_MM = 0                  # 家庭用プリンタ想定。業者に出すときは 3 にする

QR_URL = 'https://charamarl.com/?utm_source=card&utm_medium=print&utm_campaign=akikey'
CODE = 'THANKS200'
OFF = '¥200'

# 表に並べるアクキー11種（img/products_t/<名前>.png・背景透過）
CHARS = [
    ('sue_red', 'SUE'), ('putti_yellow', 'PUTTI'), ('mossun_blue', 'MOSSUN'),
    ('gmc_red', 'レコマル'), ('ufoo_white', 'う〜ほ〜'), ('dogooooo_pink', 'dogooooo'),
    ('inkumo_mono', 'インクモ'), ('danna_blue', 'だんな'), ('blockma', 'ぶろっくま'),
    ('mony', 'モニィ'), ('yurucrazy', 'ユルクレイジー'),
]


def px(mm):
    return round(mm / 25.4 * DPI)


def b64_file(path):
    return base64.b64encode(open(path, 'rb').read()).decode()


def b64_qr(url):
    buf = io.BytesIO()
    # error='h' … 中央にロゴを置いても読める強さ。border は静音域（規格上4以上が安全）
    segno.make(url, error='h').save(buf, kind='png', scale=20, border=4,
                                    dark='#1A1824', light='#FFFFFF')
    return base64.b64encode(buf.getvalue()).decode()


def render(html, out_png, w, h):
    tmp = out_png.replace('.png', '.html')
    open(tmp, 'w', encoding='utf-8').write(html)
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars',
                    '--force-device-scale-factor=1', f'--window-size={w},{h}',
                    '--virtual-time-budget=15000', f'--screenshot={out_png}', tmp],
                   check=True, capture_output=True)
    os.remove(tmp)


BASE_CSS = '''
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;overflow:hidden;position:relative;
 font-family:"Hiragino Sans","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif;
 -webkit-font-smoothing:antialiased}}
.logo{{font-family:"Helvetica Neue",Arial,sans-serif;font-weight:800;letter-spacing:.10em;line-height:1}}
.logo .a{{color:#F97316}} .logo .b{{color:#8B5CF6}}
'''


def front(W, H):
    tiles = ''.join(
        f'<div class="t"><img src="data:image/png;base64,{b64_file(f"{ROOT}/img/products_t/{k}.png")}"></div>'
        for k, _ in CHARS)
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>
{BASE_CSS.format(W=W, H=H)}
body{{background:#FFFDF8}}
body::before{{content:"";position:absolute;inset:0;
 background:radial-gradient(620px 420px at 88% -6%, #FFE3C4 0%, rgba(255,227,196,0) 62%),
            radial-gradient(560px 420px at -8% 104%, #E7DBFB 0%, rgba(231,219,251,0) 60%)}}
.rail{{position:absolute;top:0;left:0;right:0;height:{px(3)}px;
 background:linear-gradient(90deg,#FF8A00 0%,#FF4D8D 52%,#8E4ED9 100%)}}
.wrap{{position:relative;height:100%;display:flex;flex-direction:column;
 padding:{px(10)}px {px(7)}px {px(8)}px}}
.hd{{text-align:center;margin-bottom:{px(2)}px}}
.logo{{font-size:{px(9.4)}px;margin-bottom:{px(1.6)}px}}
.tag{{font-size:{px(2.7)}px;font-weight:700;color:#8E8AA0;letter-spacing:.16em}}
.grid{{flex:1;min-height:0;display:flex;flex-wrap:wrap;gap:{px(2)}px;
 align-content:center;justify-content:center}}
.t{{width:calc(25% - {px(1.5)}px);height:{px(24)}px;
 display:flex;align-items:center;justify-content:center}}
.t img{{max-width:100%;max-height:100%;object-fit:contain;display:block;
 filter:drop-shadow(0 {px(.7)}px {px(1.2)}px rgba(30,24,50,.18))}}

.ft{{text-align:center;margin-top:{px(2)}px;flex:none}}
.thanks{{font-size:{px(5.4)}px;white-space:nowrap;font-weight:800;color:#1D1A28;letter-spacing:.02em}}
.sub{{font-size:{px(3)}px;font-weight:700;color:#6E6884;margin-top:{px(1.8)}px;line-height:1.7}}
</style></head><body>
<div class="rail"></div>
<div class="wrap">
  <div class="hd">
    <div class="logo"><span class="a">CHARA</span><span class="b">MARL</span></div>
    <div class="tag">キャラクターたちが集まる小さな市場</div>
  </div>
  <div class="grid">{tiles}</div>
  <div class="ft">
    <div class="thanks">おむかえ、ありがとうございます。</div>
    <div class="sub">11のキャラクター、9人の作家。<br>ぜんぶ、別の人が描いています。</div>
  </div>
</div></body></html>'''


def back(W, H):
    qr = b64_qr(QR_URL)
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>
{BASE_CSS.format(W=W, H=H)}
body{{background:#FFFDF8}}
.rail{{position:absolute;bottom:0;left:0;right:0;height:{px(3)}px;
 background:linear-gradient(90deg,#FF8A00 0%,#FF4D8D 52%,#8E4ED9 100%)}}
.wrap{{position:relative;height:100%;display:flex;flex-direction:column;
 padding:{px(10)}px {px(9)}px {px(9)}px}}
h1{{font-size:{px(5.2)}px;font-weight:800;color:#1D1A28;line-height:1.5;letter-spacing:.01em}}
.lead{{font-size:{px(3.1)}px;font-weight:600;color:#544E68;line-height:1.85;margin-top:{px(3)}px}}
.qrbox{{display:flex;align-items:center;gap:{px(5)}px;margin-top:{px(6)}px}}
.qr{{width:{px(27)}px;height:{px(27)}px;flex:none;background:#fff;border-radius:{px(2)}px;
 padding:{px(1.4)}px;box-shadow:0 {px(.6)}px {px(2)}px rgba(30,24,50,.14)}}
.qr img{{width:100%;height:100%;display:block;image-rendering:pixelated}}
.qrt{{min-width:0}}
.qrt .b{{font-size:{px(3.6)}px;font-weight:800;color:#1D1A28;line-height:1.5}}
.qrt .s{{font-size:{px(2.8)}px;font-weight:600;color:#6E6884;margin-top:{px(1.2)}px;line-height:1.7}}
.qrt .u{{font-size:{px(3.1)}px;font-weight:800;color:#3B3949;margin-top:{px(1.6)}px;letter-spacing:.01em}}
.coupon{{margin-top:{px(6)}px;border:{px(.5)}px dashed #C9C1D8;border-radius:{px(2.6)}px;
 padding:{px(4.4)}px {px(4)}px;background:#fff;text-align:center}}
.coupon .lb{{font-size:{px(2.7)}px;font-weight:800;color:#8E8AA0;letter-spacing:.14em}}
.code{{font-family:"Helvetica Neue",Arial,sans-serif;font-size:{px(8.6)}px;font-weight:800;
 letter-spacing:.06em;color:#1D1A28;margin-top:{px(1.4)}px;line-height:1}}
.coupon .hw{{font-size:{px(2.8)}px;font-weight:600;color:#6E6884;margin-top:{px(2.2)}px;line-height:1.7}}
.tail{{margin-top:auto;padding-top:{px(4)}px;font-size:{px(2.5)}px;font-weight:600;
 color:#8E8AA0;line-height:1.8;border-top:1px solid #EDE7DF}}
.tail b{{color:#3B3949}}
</style></head><body>
<div class="wrap">
  <h1>この子には、<br>まだ10人の仲間がいます。</h1>
  <div class="lead">
    CHARAMARLは、いろんな作家さんのキャラクターが並ぶ小さな市場です。
    画面をタップすると色が変わるページもあります。おなじ子の、見たことのない色に会えます。
  </div>

  <div class="qrbox">
    <div class="qr"><img src="data:image/png;base64,{qr}"></div>
    <div class="qrt">
      <div class="b">のぞいてみてください</div>
      <div class="s">キャラクターも、グッズも、<br>まいにち増えています。</div>
      <div class="u">charamarl.com</div>
    </div>
  </div>

  <div class="coupon">
    <div class="lb">NEXT ORDER &nbsp;{OFF} OFF</div>
    <div class="code">{CODE}</div>
    <div class="hw">お会計の画面で入力してください。</div>
  </div>

  <div class="tail">
    ご自身のキャラクターを置いてみたい作家さんへ &nbsp;<b>charamarl.com/apply.html</b><br>
    CHARAMARL ／ レコルダ合同会社
  </div>
</div>
<div class="rail"></div>
</body></html>'''


def main():
    outdir = os.path.expanduser(sys.argv[1]) if len(sys.argv) > 1 else os.path.expanduser('~/Downloads/charamarl_print')
    os.makedirs(outdir, exist_ok=True)
    W, H = px(CARD_MM[0] + BLEED_MM * 2), px(CARD_MM[1] + BLEED_MM * 2)

    for name, html in (('front', front(W, H)), ('back', back(W, H))):
        p = os.path.join(outdir, f'charamarl_postcard_{name}.png')
        render(html, p, W, H)
        im = Image.open(p).convert('RGB')
        im.save(p, dpi=(DPI, DPI))
        im.save(p.replace('.png', '.pdf'), 'PDF', resolution=DPI)
        print(f'{p}  ({im.size[0]}×{im.size[1]}px / {CARD_MM[0]+BLEED_MM*2}×{CARD_MM[1]+BLEED_MM*2}mm @ {DPI}dpi)')
    print(f'\nQRの行き先: {QR_URL}')
    print(f'割引コード: {CODE}（{OFF} OFF）')


if __name__ == '__main__':
    main()
