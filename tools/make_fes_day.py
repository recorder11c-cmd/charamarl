#!/usr/bin/env python3
"""JUNKeeeeS FES 当日の応援投稿の画像（1200×675）を作る

    python3 tools/make_fes_day.py [出力先ディレクトリ]

    day1 … 24日 開幕：4人のキャラが並ぶ「会場で、スマホをかざそう」
    day2 … 25日 2日目：GOLD（24日）＋SILVER（25日）のカードが並ぶ「2DAYS COMPLETE」

■ 決めていること
    ・🔴 **QRコードやスタンプのURLは画像に入れない**（画像のQRをリモートで読むと、会場に居ない人のスタンプ・fes_spot が増えて、数字が汚れる）
    ・キャラはROKUさんのもの（FESの協力）。加工せず、並べるだけ
    ・開催時間は書かない（ROKUさんの確認事項のまま）
"""
import sys, os, base64, subprocess, tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICLOUD = os.path.expanduser('~/Library/Mobile Documents/com~apple~CloudDocs/CHARAMARL')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
W, H = 1200, 675


def b64(p, mime):
    return f'data:{mime};base64,' + base64.b64encode(open(p, 'rb').read()).decode()


CSS = '''@import url('https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@700;900&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{width:1200px;height:675px;background:#FFD600;font-family:'Zen Kaku Gothic New','Hiragino Sans',sans-serif;color:#111;position:relative;overflow:hidden}
.frame{position:absolute;left:22px;top:22px;right:22px;bottom:22px;background:#fff;border:6px solid #111;border-radius:34px;padding:30px 44px}
.k{font-size:30px;font-weight:900;color:#555;letter-spacing:.04em}
.t{font-size:78px;font-weight:900;line-height:1.1;margin-top:6px}
.s{font-size:38px;font-weight:900;margin-top:10px}
.row{display:flex;gap:18px;justify-content:center;margin-top:18px}
.row img{width:210px;height:210px;object-fit:contain}
.cards{display:flex;gap:40px;justify-content:center;margin-top:10px}
.cards img{height:255px;border-radius:14px;box-shadow:0 8px 18px rgba(0,0,0,.28)}
.foot{position:absolute;left:44px;right:44px;bottom:30px;display:flex;justify-content:space-between;font-size:26px;font-weight:900;color:#555}
'''


def page(body):
    return f'<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><style>{CSS}</style></head><body><div class="frame">{body}</div></body></html>'


def shot(html, out):
    tmp = tempfile.mkdtemp()
    p = os.path.join(tmp, 'p.html'); open(p, 'w', encoding='utf-8').write(html)
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', f'--window-size={W},{H}',
                    '--virtual-time-budget=6000', f'--screenshot={out}', 'file://' + p], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ICLOUD, '03_画像')
    art = os.path.join(REPO, 'run-junkeees', 'art')
    imgs = ''.join(f'<img src="{b64(os.path.join(art, n + ".png"), "image/png")}">' for n in ('patty', 'bull', 'clown', 'ageru'))
    d1 = page(f'''<div class="k">JUNKeeeeS FES 2026　京都・ルートツー青果 NIJO</div>
<div class="t">きょうから、2日間。</div><div class="s">10/24(土)・25(日)　会場で、スマホをかざそう</div>
<div class="row">{imgs}</div>
<div class="foot"><span>JUNKeeeeS by ROKU</span><span>CHARAMARL</span></div>''')
    shot(d1, os.path.join(out, 'fes_day1_開幕.png'))
    g = b64(os.path.join(ICLOUD, '03_画像', 'fes_nfc_qr', 'レジェンダリーカード_GOLD_1024.jpg'), 'image/jpeg')
    s = b64(os.path.join(ICLOUD, '03_画像', 'fes_nfc_qr', 'レジェンダリーカード_SILVER_1025.jpg'), 'image/jpeg')
    d2 = page(f'''<div class="k">JUNKeeeeS FES 2026　2日目</div>
<div class="t">きょうは、SILVER。</div><div class="s" style="font-size:34px">24日のGOLDと、25日のSILVER。そろえて2DAYS COMPLETE</div>
<div class="cards"><img src="{g}"><img src="{s}"></div>
<div class="foot"><span>JUNKeeeeS by ROKU</span><span>CHARAMARL</span></div>''')
    shot(d2, os.path.join(out, 'fes_day2_2日目.png'))
    print('ok', out)


if __name__ == '__main__':
    main()
