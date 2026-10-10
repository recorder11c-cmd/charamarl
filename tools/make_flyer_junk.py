# JUNKeeeeS FES 協賛チラシ(CHARAMARLの1枚・A5片面)。指示書: 04_企画/チラシ_JUNKeeeeS_指示書_20261007.md
# 使い方: python3 tools/make_flyer_junk.py [A|B|both]   → ~/Downloads/CHARAMARL/03_画像/charamarl_print/charamarl_flyer_junk_A5_<案>.{png,pdf,html}
import os, io, base64, subprocess, sys, glob, segno
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.expanduser('~/Downloads/CHARAMARL/03_画像/charamarl_print'); os.makedirs(OUT, exist_ok=True)
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
DPI = 300; TRIM = (148, 210); BLEED = 3
W = round((TRIM[0] + BLEED*2) / 25.4 * DPI); H = round((TRIM[1] + BLEED*2) / 25.4 * DPI)   # 1819x2551
px = lambda mm: round(mm / 25.4 * DPI)
URL = 'https://charamarl.com/tap/junkeeees.html?utm_source=flyer&utm_medium=print&utm_campaign=junk_fes_bag'
SHORT = 'charamarl.com/tap/junkeeees.html'
# 🔴 FES情報は tap/junkeeees.html と一字一句同じ
FES = ['JUNKeeeeS FES 2026 in KYOTO', '2026.10.24 SAT 10:00〜22:00 ／ 10.25 SUN 10:00〜17:30', 'ROOT2 青果 二条（京都市中京区西ノ京船塚町17）', 'JR・地下鉄 二条駅から徒歩7分', '入場 大人500円／大学生以下 無料']
def b64_file(p): return base64.b64encode(open(p,'rb').read()).decode()
def b64_qr():
    buf = io.BytesIO(); segno.make(URL, error='h').save(buf, kind='png', scale=24, border=4, dark='#111111', light='#FFFFFF'); return base64.b64encode(buf.getvalue()).decode()
def b64_img(im, fmt='JPEG', q=92):
    buf = io.BytesIO(); im.save(buf, fmt, quality=q); return base64.b64encode(buf.getvalue()).decode()
FONT = b64_file(os.path.join(ROOT, 'tools', 'mplus900.ttf'))
BASE = f'''*{{margin:0;padding:0;box-sizing:border-box}}
@font-face{{font-family:"MPLUSR";src:url(data:font/ttf;base64,{FONT}) format("truetype");font-weight:900}}
body{{width:{W}px;height:{H}px;overflow:hidden;position:relative;background:#FFD400;font-family:"Hiragino Sans","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif;-webkit-font-smoothing:antialiased;color:#111}}
.disp{{font-family:"MPLUSR","Hiragino Sans",sans-serif;font-weight:900}}
.logo{{font-family:"Helvetica Neue",Arial,sans-serif;font-weight:800;letter-spacing:.10em}} .logo .a{{color:#F97316}} .logo .b{{color:#8B5CF6}}
.qrbox{{background:#fff;border:{px(1.2)}px solid #111;border-radius:{px(4)}px;padding:{px(2)}px;display:inline-block}}
.qrbox img{{display:block;width:{px(34)}px;height:{px(34)}px}}
.url{{font-family:"Helvetica Neue",Arial,sans-serif;font-weight:700;font-size:{px(3.4)}px;letter-spacing:.01em;margin-top:{px(1.5)}px}}
.fes{{font-size:{px(2.75)}px;line-height:1.6;font-weight:700}} .fes b{{font-size:{px(3.4)}px;display:block;margin-bottom:{px(.6)}px;white-space:nowrap}} .fes .nw{{white-space:nowrap}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:{px(12)}px;background:#111;color:#fff;display:flex;align-items:center;justify-content:center;gap:{px(4)}px;font-size:{px(2.9)}px;font-weight:700}}
.foot .logo{{font-size:{px(5.2)}px}} .foot .url2{{font-family:"Helvetica Neue",Arial,sans-serif;opacity:.9}}
'''
FOOT = f'<div class="foot"><span class="logo"><span class="a">CHARA</span><span class="b">MARL</span></span><span>キャラクターたちが集まる、小さな市場</span><span class="url2">charamarl.com</span></div>'
FOOT_SNS = f'<div class="foot"><span class="logo"><span class="a">CHARA</span><span class="b">MARL</span></span><span class="url2">charamarl.com</span><span class="url2">X @charamarl</span><span class="url2">Instagram @charamarlinfo</span></div>'
FOOT_SHORT = f'<div class="foot"><span class="logo"><span class="a">CHARA</span><span class="b">MARL</span></span><span class="url2">charamarl.com</span></div>'   # 上の帯に同じ一文がある面(C案・裏面)用
def fes_html():
    d = FES[1].replace('　', '　<span class="nw">') + '</span>'   # 全角スペースで折り返せる(時刻は途中で切らない)
    v = FES[2].replace('（', '<span class="nw">（') + '</span>'
    return f'<div class="fes"><b>{FES[0]}</b><span class="nw">{d}<br>{v}<br><span class="nw">{FES[3]}</span><br><span class="nw">{FES[4]}</span></div>'
def cards36():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'tap/art/junk/j*.jpg'))):
        im = Image.open(f).convert('RGB'); im.thumbnail((330, 420)); out.append(f'<img src="data:image/jpeg;base64,{b64_img(im, q=88)}">')
    return ''.join(out)
def pageA():
    # 36人の並び版: 上=見出し、中=36枚のカードを9×4で敷き詰め、下=QR(左)＋FES情報(右)
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>{BASE}
.top{{position:absolute;left:0;right:0;top:0;height:{px(54)}px;padding:{px(3+8)}px {px(3+9)}px 0}}
.h1{{font-size:{px(9.6)}px;line-height:1.22;letter-spacing:.01em}}
.h1 span{{background:#111;color:#FFD400;padding:0 {px(1.5)}px;border-radius:{px(1.2)}px;display:inline-block;line-height:1.25;margin-bottom:{px(1.4)}px}}
.lead{{font-size:{px(3.2)}px;line-height:1.6;font-weight:700;margin-top:{px(2.5)}px}}
.grid{{position:absolute;left:{px(3+8)}px;right:{px(3+8)}px;top:{px(57)}px;display:grid;grid-template-columns:repeat(9,1fr);gap:{px(1.2)}px}}
.grid img{{width:100%;aspect-ratio:640/809;object-fit:cover;border-radius:{px(1.2)}px;border:{px(.5)}px solid #111;display:block}}
.bottom{{position:absolute;left:{px(3+9)}px;right:{px(3+9)}px;top:{px(137)}px;display:flex;gap:{px(6)}px;align-items:flex-start}}
.qrcol{{text-align:center;flex:none}}
.qrlabel{{font-size:{px(3.6)}px;font-weight:900;margin-bottom:{px(1.5)}px}}
.info{{flex:1;padding-top:{px(2)}px}}
.info .note{{font-size:{px(3.0)}px;line-height:1.6;font-weight:700;margin-bottom:{px(3)}px}}
</style></head><body>
<div class="top"><div class="h1 disp"><span>JUNKeeeeSの36人が、</span><br><span>スマホに集まる。</span></div>
<div class="lead">画面をタップするたびに、ひとりずつキャラクターが現れます。<br>36人ぜんぶ集めると、図鑑ができあがります。<br>会場の3か所にあるNFCにスマホをかざすと、ここでしか出会えない1枚も。</div></div>
<div class="grid">{cards36()}</div>
<div class="bottom"><div class="qrcol"><div class="qrlabel disp">▼ QRを読んで、図鑑をひらく</div><div class="qrbox"><img src="data:image/png;base64,{b64_qr()}"></div><div class="url">{SHORT}</div></div>
<div class="info"><div class="note">ログイン・アプリ不要。ブラウザでそのまま遊べます。<br>集めた人数は、同じスマホで開けば次に来たときも残ります。</div>{fes_html()}</div></div>
{FOOT}</body></html>'''
def pageB():
    # 主役版: 上=ROKUさんのFES絵(図鑑ページで公開済み)を大きく、下=見出し・説明・QR・FES情報
    src = Image.open(os.path.join(ROOT, 'tap/art/junkeeees_fes.jpg')).convert('RGB')
    hero = src.crop((0, 492, 620, 905))   # アゲルとポテトの部分(文字を含まない範囲)
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>{BASE}
.hero{{position:absolute;left:0;right:0;top:0;height:{px(86)}px;overflow:hidden;background:#FF0F2E}}
.hero img{{width:100%;height:100%;object-fit:cover;display:block}}
.hero .band{{position:absolute;left:0;right:0;bottom:0;height:{px(2.4)}px;background:#111}}
.mid{{position:absolute;left:{px(3+9)}px;right:{px(3+9)}px;top:{px(90)}px}}
.h1{{font-size:{px(8.2)}px;line-height:1.22}}
.h1 span{{background:#111;color:#FFD400;padding:0 {px(1.5)}px;border-radius:{px(1.2)}px;display:inline-block;line-height:1.25;margin-bottom:{px(1.2)}px}}
.lead{{font-size:{px(3.2)}px;line-height:1.6;font-weight:700;margin-top:{px(2.5)}px}}
.bottom{{position:absolute;left:{px(3+9)}px;right:{px(3+9)}px;top:{px(135)}px;display:flex;gap:{px(6)}px;align-items:flex-start}}
.qrcol{{text-align:center;flex:none}} .qrlabel{{font-size:{px(3.6)}px;font-weight:900;margin-bottom:{px(1.5)}px}}
.info{{flex:1;padding-top:{px(2)}px}} .info .note{{font-size:{px(3.1)}px;line-height:1.6;font-weight:700;margin-bottom:{px(3)}px}}
</style></head><body>
<div class="hero"><img src="data:image/jpeg;base64,{b64_img(hero, q=93)}"><div class="band"></div></div>
<div class="mid"><div class="h1 disp"><span>JUNKeeeeSの36人が、</span><br><span>スマホに集まる。</span></div>
<div class="lead">画面をタップするたびに、ひとりずつキャラクターが現れます。<br>36人ぜんぶ集めると、図鑑ができあがります。<br>会場の3か所にあるNFCにスマホをかざすと、ここでしか出会えない1枚も。</div></div>
<div class="bottom"><div class="qrcol"><div class="qrlabel disp">▼ QRを読んで、図鑑をひらく</div><div class="qrbox"><img src="data:image/png;base64,{b64_qr()}"></div><div class="url">{SHORT}</div></div>
<div class="info"><div class="note">ログイン・アプリ不要。ブラウザでそのまま遊べます。</div>{fes_html()}</div></div>
{FOOT}</body></html>'''
def pageC():
    # C案(依頼者の方針): CHARAMARLのPRが主。その中に「いま来ているJUNKeeeeSの36人」。会場配布なのでFES情報は載せない
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>{BASE}
body{{background:#FFFDF8}}
.rail{{position:absolute;top:0;left:0;right:0;height:{px(5)}px;background:linear-gradient(90deg,#FF8A00 0%,#FF4D8D 52%,#8E4ED9 100%)}}
.top{{position:absolute;left:0;right:0;top:{px(5)}px;padding:{px(9)}px {px(3+9)}px 0;text-align:center}}
.top .logo{{font-size:{px(13)}px;display:block}}
.tag{{font-size:{px(3.6)}px;font-weight:700;color:#6E6884;letter-spacing:.12em;margin-top:{px(1.8)}px}}
.h1{{font-size:{px(7.4)}px;line-height:1.3;margin-top:{px(6)}px;text-align:left}}
.h1 span{{background:#111;color:#FFD400;padding:0 {px(1.5)}px;border-radius:{px(1.2)}px;display:inline-block;line-height:1.25;margin-bottom:{px(1.2)}px}}
.lead{{font-size:{px(3.2)}px;line-height:1.65;font-weight:700;margin-top:{px(2)}px;text-align:left}}
.grid{{position:absolute;left:{px(3+8)}px;right:{px(3+8)}px;top:{px(84)}px;display:grid;grid-template-columns:repeat(9,1fr);gap:{px(1.2)}px}}
.grid img{{width:100%;aspect-ratio:640/809;object-fit:cover;border-radius:{px(1.2)}px;border:{px(.5)}px solid #111;display:block}}
.bottom{{position:absolute;left:{px(3+9)}px;right:{px(3+9)}px;top:{px(160)}px;display:flex;gap:{px(6)}px;align-items:flex-start}}
.qrcol{{text-align:center;flex:none}} .qrlabel{{font-size:{px(3.4)}px;font-weight:900;margin-bottom:{px(1.2)}px}}
.qrbox img{{width:{px(31)}px;height:{px(31)}px}}
.info{{flex:1;padding-top:{px(1)}px;font-size:{px(3.0)}px;line-height:1.7;font-weight:700}}
.info b{{display:block;font-size:{px(3.6)}px;margin-bottom:{px(1)}px}}
''' + f'''</style></head><body><div class="rail"></div>
<div class="top"><span class="logo"><span class="a">CHARA</span><span class="b">MARL</span></span><div class="tag">キャラクターたちが集まる、小さな市場</div>
<div class="h1 disp"><span>いま、JUNKeeeeSの36人が</span><br><span>来ています。</span></div>
<div class="lead">CHARAMARLは、いろいろな作家さんのキャラクターが集まる場所です。<br>スマホで図鑑をひらくと、タップするたびに1人ずつ現れます。<br>36人ぜんぶ集めると、図鑑が完成します。</div></div>
<div class="grid">{cards36()}</div>
<div class="bottom"><div class="qrcol"><div class="qrlabel disp">▼ JUNKeeeeSの図鑑をひらく</div><div class="qrbox"><img src="data:image/png;base64,{b64_qr()}"></div><div class="url">{SHORT}</div></div>
<div class="info"><b>CHARAMARLでできること</b>・気に入ったキャラクターに♥を送る<br>・作家さんの活動場所（X・ショップ・イベント）へすぐ行ける<br>・気に入った作品を保存して、あとで見返す<br><span style="font-family:Helvetica Neue,Arial,sans-serif">charamarl.com</span></div></div>
{FOOT_SHORT}</body></html>'''
AR_URL = 'https://charamarl.com/ar/fes/?utm_source=flyer&utm_medium=print&utm_campaign=junk_fes_bag&utm_content=ar'
BACK_QR = [
  ('ギャラリー', '参加作家のキャラクターと<br>作品を1枚ずつ見られます。<br>気に入ったら♥を。', 'https://charamarl.com/?utm_source=flyer&utm_medium=print&utm_campaign=junk_fes_bag&utm_content=gallery#discover', 'charamarl.com'),
  ('キャラクター<br>（アクキー・ピンズ）', 'キャラクターのアクキーとピンズ。<br>アクキーはかざすと<br>作家さんのページがひらきます。', 'https://charamarl.com/characters/keyrings.html?utm_source=flyer&utm_medium=print&utm_campaign=junk_fes_bag&utm_content=keyrings', 'charamarl.com/characters/<wbr>keyrings.html'),
  ('作家・企業の方へ', 'タップで30秒、CHARAMARLがわかります。<br>そのあと、掲載・グッズ化・イベントの相談へ。', 'https://charamarl.com/join.html?utm_source=flyer&utm_medium=print&utm_campaign=junk_fes_bag&utm_content=join', 'charamarl.com/join.html'),
]
def b64_qr_url(url):
    buf = io.BytesIO(); segno.make(url, error='h').save(buf, kind='png', scale=18, border=4, dark='#111111', light='#FFFFFF'); return base64.b64encode(buf.getvalue()).decode()
GRID_H = 556   # gallery_grid_36.jpg のグリッド部分の高さ(下の文字帯の手前)
def pageBack():
    # 裏面: 上=ロゴ＋見出し、中=2列(ギャラリー=ピンタレスト風UIの図、キャラクター=スマホとアクキーのモック)＋QR、下=作家・企業の方へ(横配置)、SNS
    g, k, ap = BACK_QR
    # ピンタレスト風UI(図形だけ。作品は使わない)
    # 🔴 他作家の絵は使わない。自社キャラ(SUE/PUTTI/MOSSUN)の絵・アクキー・ピンズだけ
    IMG = os.path.expanduser('~/Downloads/CHARAMARL/03_画像')
    def photo(path, box, crop=None, q=90):
        im = Image.open(os.path.join(IMG, path)).convert('RGB')
        if crop: im = im.crop(crop)
        im.thumbnail(box); return b64_img(im, 'JPEG', q)
    # 営業ツール: 名刺(表裏の実寸イメージ)
    # ギャラリー: 依頼者指定のギャラリー画像(6×3の作品グリッド、_assets/gallery_grid_36.jpg)。下の文字帯は外してグリッドだけ使う
    # 10/10 依頼者「グッズ採用の作家さんにも営業ツールへの許可を得ている」→ 全作家の作品を入れる
    gsrc = Image.open(os.path.expanduser('~/Downloads/CHARAMARL/03_画像/charamarl_print/_assets/gallery_grid_36.jpg')).convert('RGB')
    grid = gsrc.crop((0, 0, gsrc.width, GRID_H))
    pin = '<div class="tool grid"><img src="data:image/jpeg;base64,' + b64_img(grid, 'JPEG', 92) + '"></div>'

    # グッズ: 依頼者指定の営業OK素材(ポストカード表 charamarl_postcard_front.png = アクキー11種・ピンズ12種)から、上段=アクキー、下段=ピンズを切り出す
    pc = Image.open(os.path.join(OUT, '_assets', 'goods_postcard_front.png')).convert('RGB')   # 10/10 依頼者添付(アクキー11・ピンズ12の新版)
    kc = pc.crop((95, 385, 1090, 880)); kc.thumbnail((1000, 600)); pins_ph = b64_img(kc, 'JPEG', 92)   # 左右の余白を詰める
    pn = pc.crop((85, 970, 1095, 1320)); pn.thumbnail((1000, 400)); ship_ph = b64_img(pn, 'JPEG', 92)
    phone = '<div class="goods"><img src="data:image/jpeg;base64,' + pins_ph + '"><img src="data:image/jpeg;base64,' + ship_ph + '"></div>'
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>{BASE}
body{{background:#FFFDF8}}
.rail{{position:absolute;top:0;left:0;right:0;height:{px(5)}px;background:linear-gradient(90deg,#FF8A00 0%,#FF4D8D 52%,#8E4ED9 100%)}}
.top{{position:absolute;left:0;right:0;top:{px(5)}px;padding:{px(9)}px {px(3+9)}px 0;text-align:center}}
.top .logo{{font-size:{px(12)}px;display:block}}
.tag{{font-size:{px(3.4)}px;font-weight:700;color:#6E6884;letter-spacing:.12em;margin-top:{px(1.6)}px}}
.h1{{font-size:{px(5.6)}px;line-height:1.35;margin-top:{px(5)}px}}
.h1 span{{background:#111;color:#FFD400;padding:0 {px(1.5)}px;border-radius:{px(1.2)}px;display:inline-block;line-height:1.3;margin-bottom:{px(1)}px}}
.cols{{position:absolute;left:{px(3+8)}px;right:{px(3+8)}px;top:{px(60)}px;display:flex;gap:{px(5)}px}}
.col{{flex:1 1 0;min-width:0;background:#fff;border:{px(.6)}px solid #111;border-radius:{px(4)}px;padding:{px(3)}px {px(3)}px {px(3)}px;text-align:center}}
.ill{{height:{px(36)}px;border-radius:{px(2.5)}px;background:#F6F2FA;border:{px(.4)}px solid #DDD6EA;overflow:hidden;position:relative;margin-bottom:{px(2.5)}px}}
.tool{{height:100%;display:flex;align-items:center;justify-content:center;padding:{px(1.5)}px}} .tool img{{width:100%;height:auto;object-fit:contain;border-radius:{px(1)}px;box-shadow:{px(.4)}px {px(.6)}px {px(1.2)}px rgba(0,0,0,.18)}} .tool.grid{{padding:0}} .tool.grid img{{width:100%;height:100%;object-fit:cover;object-position:center;border-radius:0;box-shadow:none}}
.col .ill{{height:auto;aspect-ratio:2/1}}
.goods{{height:100%;display:flex;flex-direction:column;gap:{px(1)}px;padding:{px(1)}px}} .goods img{{min-height:0;width:100%;object-fit:contain;background:#FFFDF8;border-radius:{px(1.6)}px;border:{px(.35)}px solid #111}} .goods img:first-child{{flex:1.4}} .goods img:last-child{{flex:1}}
.pin{{display:flex;gap:{px(1.2)}px;padding:{px(1.6)}px}} .pc{{flex:1;display:flex;flex-direction:column;gap:{px(1.2)}px}}
.pt{{border-radius:{px(1.4)}px;border:{px(.35)}px solid #111;position:relative;overflow:hidden}} .pt img{{width:100%;height:100%;display:block;padding:{px(.5)}px}}
.pt .hv{{position:absolute;right:{px(.8)}px;bottom:{px(.6)}px;font-size:{px(2)}px;font-weight:900;color:#FF4D8D;background:#fff;border-radius:999px;padding:0 {px(.8)}px;line-height:1.5}}
.mock{{display:flex;align-items:center;justify-content:center;gap:{px(4)}px;height:100%}}
.phone{{width:{px(16)}px;height:{px(31)}px;background:#111;border:{px(.6)}px solid #111;border-radius:{px(2.6)}px;padding:{px(.7)}px;position:relative;box-shadow:{px(.6)}px {px(.6)}px 0 #111;overflow:hidden}} .phone .scr{{width:100%;height:100%;object-fit:cover;object-position:top;border-radius:{px(2)}px;display:block}}
.pbar{{width:40%;height:{px(.7)}px;background:#111;border-radius:999px;margin:0 auto {px(1)}px}}
.pimg{{height:{px(13)}px;border-radius:{px(1.4)}px;background:linear-gradient(135deg,#FFD9B8,#E9DAFB);border:{px(.35)}px solid #111;display:flex;align-items:center;justify-content:center}}
.face{{width:{px(7)}px;height:{px(7)}px;background:#FFE000;border:{px(.4)}px solid #111;border-radius:50%;position:relative}}
.face i{{position:absolute;top:38%;width:{px(.8)}px;height:{px(.8)}px;background:#111;border-radius:50%}} .face i:first-child{{left:28%}} .face i:nth-child(2){{right:28%}}
.face b{{position:absolute;left:30%;right:30%;bottom:24%;height:{px(1.4)}px;border:{px(.4)}px solid #111;border-top:none;border-radius:0 0 {px(2)}px {px(2)}px}}
.face.sm{{width:{px(5.2)}px;height:{px(5.2)}px}}
.prow{{display:flex;justify-content:space-between;align-items:center;margin:{px(1)}px 0}}
.pl{{font-size:{px(1.9)}px;font-weight:900;color:#FF4D8D}} .pb{{width:{px(5)}px;height:{px(1.2)}px;background:#DDD6EA;border-radius:999px}}
.pbtn{{height:{px(2.6)}px;border-radius:999px;background:#F97316;margin-top:{px(1)}px}} .pbtn.s{{background:#8B5CF6}}
.key{{position:relative;width:{px(24)}px;height:{px(31)}px;display:flex;align-items:flex-start;justify-content:center}} .key > img{{width:100%;height:{px(27)}px;object-fit:contain;background:#E9DAFB;border-radius:{px(2)}px;border:{px(.5)}px solid #111}}
.ring{{position:absolute;left:50%;top:0;width:{px(4.5)}px;height:{px(4.5)}px;border:{px(.7)}px solid #111;border-radius:50%;transform:translateX(-50%)}}
.plate{{position:absolute;left:0;right:0;top:{px(4)}px;bottom:{px(4)}px;background:rgba(255,255,255,.85);border:{px(.6)}px solid #111;border-radius:{px(2.2)}px;display:flex;align-items:center;justify-content:center;box-shadow:{px(.5)}px {px(.5)}px 0 #111}}
.nfc{{position:absolute;left:0;right:0;bottom:0;text-align:center;font-family:"Helvetica Neue",Arial,sans-serif;font-size:{px(1.9)}px;font-weight:800;color:#8B5CF6;letter-spacing:.05em}}
.ct{{font-size:{px(3.8)}px;line-height:1.3;white-space:nowrap}}
.cd{{font-size:{px(2.5)}px;line-height:1.55;font-weight:700;color:#333;margin:{px(1)}px 0 {px(1.8)}px;white-space:nowrap}}
.col .qrbox{{padding:{px(1.2)}px;border-width:{px(.6)}px}} .col .qrbox img{{width:{px(22)}px;height:{px(22)}px}}
.col .url{{font-size:{px(2.4)}px;margin-top:{px(1.2)}px}}
.ar{{position:absolute;left:{px(3+8)}px;right:{px(3+8)}px;top:{px(146)}px;height:{px(27)}px;background:var(--yellow,#FFD400);background:#FFD400;border:{px(.6)}px solid #111;border-radius:{px(4)}px;padding:{px(2)}px {px(3.5)}px;display:flex;align-items:center;gap:{px(3.5)}px}}
.ar .hero{{flex:none;width:{px(19)}px;height:{px(19)}px;object-fit:contain}}
.ar .at{{font-size:{px(3.4)}px;line-height:1.3;margin-bottom:{px(.8)}px}}
.ar .ad{{font-size:{px(2.5)}px;line-height:1.55;font-weight:700;color:#111;white-space:nowrap}}
.ar .l{{flex:1}} .ar .r{{flex:none;text-align:center}}
.ar .qrbox{{padding:{px(.8)}px;border-width:{px(.5)}px}} .ar .qrbox img{{width:{px(18)}px;height:{px(18)}px}}
.ar .url{{font-size:{px(2)}px;margin-top:{px(.6)}px}}
.biz{{position:absolute;left:{px(3+8)}px;right:{px(3+8)}px;top:{px(175)}px;height:{px(27)}px;background:#111;color:#fff;border-radius:{px(4)}px;padding:{px(2)}px {px(4)}px;display:flex;align-items:center;gap:{px(4)}px}}
.biz .bt{{font-size:{px(3.4)}px;color:#FFD400;margin-bottom:{px(.6)}px}}
.biz .bd{{font-size:{px(2.4)}px;line-height:1.55;font-weight:700;white-space:nowrap}} .biz .bd .em{{font-family:"Helvetica Neue",Arial,sans-serif;font-weight:800;color:#fff}}
.biz .l{{flex:1}} .biz .r{{flex:none;text-align:center}}
.biz .qrbox{{padding:{px(.8)}px;border-color:#fff;border-width:{px(.5)}px}} .biz .qrbox img{{width:{px(18)}px;height:{px(18)}px}}
.biz .url{{font-size:{px(2.2)}px;margin-top:{px(.8)}px;color:#fff}}
.sns{{position:absolute;left:0;right:0;top:{px(194)}px;text-align:center;font-size:{px(2.8)}px;font-weight:700;color:#333}}
.sns .em{{font-family:"Helvetica Neue",Arial,sans-serif;font-weight:800;color:#111}}
</style></head><body><div class="rail"></div>
<div class="top"><span class="logo"><span class="a">CHARA</span><span class="b">MARL</span></span><div class="tag">キャラクターたちが集まる、小さな市場</div>
<div class="h1 disp"><span>JUNKeeeeSのほかにも、</span><br><span>キャラクターが集まっています。</span></div></div>
<div class="cols">
  <div class="col"><div class="ill">{pin}</div><div class="ct disp">{g[0]}</div><div class="cd">{g[1]}</div><div class="qrbox"><img src="data:image/png;base64,{b64_qr_url(g[2])}"></div><div class="url">{g[3]}</div></div>
  <div class="col"><div class="ill">{phone}</div><div class="ct disp">{k[0].replace('<br>','')}</div><div class="cd">{k[1]}</div><div class="qrbox"><img src="data:image/png;base64,{b64_qr_url(k[2])}"></div><div class="url">{k[3]}</div></div>
</div>
<div class="ar"><img class="hero" src="data:image/png;base64,{b64_file(os.path.join(ROOT, 'run-junkeees/art/ageru.png'))}"><div class="l"><div class="at disp">このチラシの表に、アゲルがかくれてる。</div><div class="ad">QRを開いて、チラシの表にカメラをむけてね。<br>アゲルが飛び出して、あいさつします。<br>写真を撮って、Xでシェアしてね！ #JUNKeeeeS</div></div><div class="r"><div class="qrbox"><img src="data:image/png;base64,{b64_qr_url(AR_URL)}"></div><div class="url">charamarl.com/ar/fes/</div></div></div>
<div class="biz"><div class="l"><div class="bt disp">{ap[0]}</div><div class="bd">{ap[1]}<br>メール <span class="em">charamarlinfo@gmail.com</span></div></div><div class="r"><div class="qrbox"><img src="data:image/png;base64,{b64_qr_url(ap[2])}"></div><div class="url">{ap[3]}</div></div></div>
{FOOT_SNS}</body></html>'''
def render(html, name):
    htmlp = os.path.join(OUT, name + '.html'); png = os.path.join(OUT, name + '.png'); pdf = os.path.join(OUT, name + '.pdf')
    open(htmlp, 'w', encoding='utf-8').write(html)
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1', f'--window-size={W},{H}', '--virtual-time-budget=15000', f'--screenshot={png}', htmlp], check=True, capture_output=True)
    im = Image.open(png).convert('RGB'); im.save(pdf, 'PDF', resolution=DPI)
    im.resize((W//3, H//3), Image.LANCZOS).save(os.path.join(OUT, name + '_preview.png'))
    # QR読み取り確認
    import cv2, numpy as np
    arr = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    det = cv2.QRCodeDetector()
    if name.endswith('_back'):
        # 白いQRの箱を全部見つけて個別に読む(位置に依存しない)。周りを白で囲むと暗い背景でも読める
        Wd, Hd = im.size; arr0 = np.array(im); white = (arr0.min(axis=2) > 200).astype(np.uint8)
        n, lab, stats, _ = cv2.connectedComponentsWithStats(white); found = []
        for k in range(1, n):
            x, y, w, h, a = stats[k]
            if w < 150 or h < 150 or w > 500 or abs(w - h) > 20: continue
            box = im.crop((x, y, x+w, y+h)); pad = Image.new('RGB', (w+200, h+200), 'white'); pad.paste(box, (100, 100))
            d, _, _ = det.detectAndDecode(cv2.cvtColor(np.array(pad), cv2.COLOR_RGB2BGR))
            if d: found.append(d)
        expect = sorted([u for _,_,u,_ in BACK_QR] + [AR_URL])
        print(name, im.size, 'QR:', 'OK (%d)' % len(found) if sorted(found) == expect else f'NG found={found}')
    else:
        data, pts, _ = det.detectAndDecode(arr); print(name, im.size, 'QR:', 'OK' if data == URL else f'NG ({data[:60]!r})')
which = sys.argv[1] if len(sys.argv) > 1 else 'both'
if which in ('A', 'both'): render(pageA(), 'charamarl_flyer_junk_A5_A')
if which in ('B', 'both'): render(pageB(), 'charamarl_flyer_junk_A5_B')
if which in ('C', 'both'): render(pageC(), 'charamarl_flyer_junk_A5_C')
if which in ('back', 'both'): render(pageBack(), 'charamarl_flyer_junk_A5_back')
