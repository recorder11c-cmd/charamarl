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
.bottom{{position:absolute;left:{px(3+9)}px;right:{px(3+9)}px;top:{px(164)}px;display:flex;gap:{px(6)}px;align-items:flex-start}}
.qrcol{{text-align:center;flex:none}} .qrlabel{{font-size:{px(3.4)}px;font-weight:900;margin-bottom:{px(1.2)}px}}
.qrbox img{{width:{px(26)}px;height:{px(26)}px}}
.info{{flex:1;padding-top:{px(1)}px;font-size:{px(3.0)}px;line-height:1.7;font-weight:700}}
.info b{{display:block;font-size:{px(3.6)}px;margin-bottom:{px(1)}px}}
''' + f'''</style></head><body><div class="rail"></div>
<div class="top"><span class="logo"><span class="a">CHARA</span><span class="b">MARL</span></span><div class="tag">キャラクターたちが集まる、小さな市場</div>
<div class="h1 disp"><span>いま、JUNKeeeeSの36人が</span><br><span>来ています。</span></div>
<div class="lead">CHARAMARLは、いろいろな作家さんのキャラクターが集まる場所です。<br>スマホで図鑑をひらくと、タップするたびに1人ずつ現れます。<br>36人ぜんぶ集めると、図鑑が完成します。</div></div>
<div class="grid">{cards36()}</div>
<div class="bottom"><div class="qrcol"><div class="qrlabel disp">▼ JUNKeeeeSの図鑑をひらく</div><div class="qrbox"><img src="data:image/png;base64,{b64_qr()}"></div><div class="url">{SHORT}</div></div>
<div class="info"><b>CHARAMARLでできること</b>・気に入ったキャラクターに♥を送る<br>・作家さんの活動場所（X・ショップ・イベント）へすぐ行ける<br>・お気に入りを集めて、自分の図鑑にする<br><span style="font-family:Helvetica Neue,Arial,sans-serif">charamarl.com</span></div></div>
{FOOT}</body></html>'''
BACK_QR = [
  ('ギャラリー', '参加作家のキャラクターと<br>作品を1枚ずつ見られます。<br>気に入ったら♥を。', 'https://charamarl.com/?utm_source=flyer&utm_medium=print&utm_campaign=junk_fes_bag&utm_content=gallery#discover', 'charamarl.com'),
  ('キャラクター<br>（アクキー・ピンズ）', 'キャラクターのアクキーとピンズ。<br>アクキーはかざすと<br>作家さんのページがひらきます。', 'https://charamarl.com/characters/keyrings.html?utm_source=flyer&utm_medium=print&utm_campaign=junk_fes_bag&utm_content=keyrings', 'charamarl.com/characters/<wbr>keyrings.html'),
  ('作家・企業の方へ', 'キャラクターの掲載・<br>グッズ化・イベントの<br>ご相談は、こちらから。', 'https://charamarl.com/apply.html?utm_source=flyer&utm_medium=print&utm_campaign=junk_fes_bag&utm_content=apply', 'charamarl.com/apply.html'),
]
def b64_qr_url(url):
    buf = io.BytesIO(); segno.make(url, error='h').save(buf, kind='png', scale=18, border=4, dark='#111111', light='#FFFFFF'); return base64.b64encode(buf.getvalue()).decode()
def pageBack():
    cols = ''.join(f'''<div class="col"><div class="ct disp">{t}</div><div class="cd">{d}</div><div class="qrbox"><img src="data:image/png;base64,{b64_qr_url(u)}"></div><div class="url">{sh}</div></div>''' for t,d,u,sh in BACK_QR)
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>{BASE}
body{{background:#FFFDF8}}
.rail{{position:absolute;top:0;left:0;right:0;height:{px(5)}px;background:linear-gradient(90deg,#FF8A00 0%,#FF4D8D 52%,#8E4ED9 100%)}}
.top{{position:absolute;left:0;right:0;top:{px(5)}px;padding:{px(12)}px {px(3+9)}px 0;text-align:center}}
.top .logo{{font-size:{px(14)}px;display:block}}
.tag{{font-size:{px(3.8)}px;font-weight:700;color:#6E6884;letter-spacing:.12em;margin-top:{px(2)}px}}
.h1{{font-size:{px(6.2)}px;line-height:1.35;margin-top:{px(10)}px}}
.h1 span{{background:#111;color:#FFD400;padding:0 {px(1.5)}px;border-radius:{px(1.2)}px;display:inline-block;line-height:1.3}}
.cols{{position:absolute;left:{px(3+8)}px;right:{px(3+8)}px;top:{px(78)}px;display:flex;gap:{px(5)}px}}
.col{{flex:1;text-align:center;background:#fff;border:{px(.6)}px solid #111;border-radius:{px(4)}px;padding:{px(5)}px {px(2.5)}px {px(4)}px}}
.ct{{font-size:{px(3.9)}px;line-height:1.3;min-height:{px(11)}px;display:flex;align-items:center;justify-content:center}}
.cd{{font-size:{px(2.6)}px;line-height:1.65;font-weight:700;color:#333;min-height:{px(16)}px;margin:{px(2)}px 0 {px(3)}px;white-space:nowrap}}
.col .qrbox{{padding:{px(1.2)}px;border-width:{px(.6)}px}} .col .qrbox img{{width:{px(24)}px;height:{px(24)}px}}
.col .url{{font-size:{px(2.4)}px;margin-top:{px(1.5)}px}}
.contact{{position:absolute;left:{px(3+9)}px;right:{px(3+9)}px;top:{px(170)}px;text-align:center;font-size:{px(3.1)}px;line-height:1.7;font-weight:700;color:#333}}
.contact .em{{font-family:"Helvetica Neue",Arial,sans-serif;font-weight:800;color:#111}}
</style></head><body><div class="rail"></div>
<div class="top"><span class="logo"><span class="a">CHARA</span><span class="b">MARL</span></span><div class="tag">キャラクターたちが集まる、小さな市場</div>
<div class="h1 disp"><span>JUNKeeeeSのほかにも、</span><br><span>キャラクターが集まっています。</span></div></div>
<div class="cols">{cols}</div>
<div class="contact">CHARAMARLは、いろいろな作家さんのキャラクターが集まる場所です。<br>お問い合わせ <span class="em">charamarlinfo@gmail.com</span>　／　X <span class="em">@charamarl</span></div>
{FOOT}</body></html>'''
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
        Wd, Hd = im.size; found = []
        for i in range(3):
            crop = im.crop((int(Wd*(0.04+i*0.31)), int(Hd*0.45), int(Wd*(0.04+(i+1)*0.31)), int(Hd*0.85)))
            d, _, _ = det.detectAndDecode(cv2.cvtColor(np.array(crop), cv2.COLOR_RGB2BGR)); found.append(d)
        print(name, im.size, 'QR:', 'OK' if found == [u for _,_,u,_ in BACK_QR] else f'NG found={found}')
    else:
        data, pts, _ = det.detectAndDecode(arr); print(name, im.size, 'QR:', 'OK' if data == URL else f'NG ({data[:60]!r})')
which = sys.argv[1] if len(sys.argv) > 1 else 'both'
if which in ('A', 'both'): render(pageA(), 'charamarl_flyer_junk_A5_A')
if which in ('B', 'both'): render(pageB(), 'charamarl_flyer_junk_A5_B')
if which in ('C', 'both'): render(pageC(), 'charamarl_flyer_junk_A5_C')
if which in ('back', 'both'): render(pageBack(), 'charamarl_flyer_junk_A5_back')
