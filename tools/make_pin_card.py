#!/usr/bin/env python3
"""ピンズ実物の写真から、販売カード（1200×1500・Xにそのまま貼れる）を作る

    python3 tools/make_pin_card.py <キー> [出力先ディレクトリ]      キー＝dino3 / kagechiyo / both
    （both＝アクキー11種とピンズ12種を並べた「ともに販売中」カード。写真は使わず商品画像のみ）
    python3 tools/make_pin_card.py akey <id|all> [出力先]   … アクキー1体の「販売中」カード（作家さんに渡す用）。id＝gmc／sue など
    python3 tools/make_pin_card.py pin  <key|all> [出力先]  … ピンズ1絵柄の「販売中」カード。key＝sue／kg_kimi など

    例)  python3 tools/make_pin_card.py dino3
         python3 tools/make_pin_card.py kagechiyo

■ なぜ作るか
    ピンズの実物写真は、そのままでは机の上の写真でしかない。
    保存した人が「いくらで、いつ届くのか」を持ち帰れるように、
    価格・納期・仕様を絵の中に入れておく。

■ 決めていること
    ・写真は加工しない。切り出して、枠に入れるだけ（色・形を変えない）
    ・価格と納期は商品ページ（characters/pins.html）と同じ文言にする。
      🔴 9/18のリリース画像は「ご注文から約2週間」と書いてあり、今のページ
         （毎月末締め・翌月中旬ごろ）と食い違っている。**数字は必ずページから写す。**
    ・売上・販売数は載せない
    ・作家名は写真の下に小さく。主役はピンズの実物

■ 高さは固定で持つ（make_event.py と同じ理由。flex:1 にすると情報が切れる）
"""
import sys, os, html, subprocess

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
W, H = 1200, 1500
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTO_DIR = os.path.expanduser('~/Downloads/CHARAMARL/03_画像/charamarl_pins_実物')
OUT_DEFAULT = PHOTO_DIR

# 商品ページ characters/pins.html の文言（2026-10-02 時点）
PRICE = [('単品', '¥1,800'), ('4個セット', '1個 ¥1,100')]
PRICE_NOTE = '税込・送料込｜4個セットは作家さんをまたいで混ぜられます'
SPEC = '直径25mm・金属フレーム＋ドーム加工・裏面バタフライピン'
LEAD = '受注生産｜毎月末締め・翌月中旬ごろのお届け'

CARDS = {
    'dino3': dict(
        kicker='ピンズ ／ 実物',
        title='モッスン・スー・プッチィ',
        photo='PR_3種_真上_card用.jpg',
        labels=[('モッスン', 'DinoRenny'), ('スー', 'DinoRenny'), ('プッチィ', 'DinoRenny')],
        thumbs=[]),
    'kagechiyo': dict(
        kicker='ピンズ ／ 実物',
        title='カゲチヨ（メカニャン）',
        photo='PR_カゲチヨ_正面_1080.jpg',
        labels=[],
        thumbs=[('kg_kagechiyo', 'カゲチヨ'), ('kg_kimi', 'キミ'), ('kg_shigure', 'シグレ'),
                ('kg_promu', 'プロム'), ('kg_muchiko', 'ムチコ')],
        thumb_caption='全5種（作家：カゲチヨ）'),
}

TPL = '''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@700;900&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:%dpx;height:%dpx;overflow:hidden;background:#FFFDF8;color:#17161F;
  font-family:"Zen Kaku Gothic New","Hiragino Sans",sans-serif;position:relative;}}
body::before{{content:"";position:absolute;inset:0;
  background:radial-gradient(800px 420px at 92%% 0%%,#FFE9D2 0%%,rgba(255,233,210,0) 62%%),
             radial-gradient(700px 420px at 0%% 100%%,#ECE4FB 0%%,rgba(236,228,251,0) 60%%);}}
.wrap{{position:relative;height:100%%;}}
.rail{{height:8px;background:linear-gradient(90deg,#FF8A00,#FF4D8D 52%%,#8E4ED9);}}
.hd{{height:170px;padding:40px 52px 0;}}
.kick{{font-size:24px;font-weight:700;color:#8E8CA3;letter-spacing:.08em;}}
h1{{margin-top:6px;font-size:64px;font-weight:900;line-height:1.15;letter-spacing:.01em;}}
.ph{{height:660px;margin:0 52px;border-radius:28px;overflow:hidden;
  box-shadow:0 10px 30px rgba(20,18,32,.14);background:#E9EBF0;}}
.ph img{{width:100%%;height:100%%;object-fit:cover;object-position:center;display:block;}}
.sub{{height:158px;padding:22px 52px 0;}}
.lab{{display:flex;}}
.lab div{{flex:1;text-align:center;}}
.lab b{{display:block;font-size:34px;font-weight:900;}}
.lab span{{font-size:21px;font-weight:700;color:#8E8CA3;}}
.th{{display:flex;align-items:center;gap:22px;}}
.th figure{{width:96px;text-align:center;}}
.th .c{{width:96px;height:96px;border-radius:50%%;overflow:hidden;box-shadow:0 4px 12px rgba(20,18,32,.16);}}
.th img{{width:100%%;height:100%%;object-fit:cover;transform:scale(1.1);display:block;}}
.th figcaption{{margin-top:6px;font-size:17px;font-weight:700;color:#3B3949;white-space:nowrap;}}
.th .cap{{margin-left:auto;font-size:25px;font-weight:900;color:#3B3949;}}
.info{{height:504px;margin:0 52px;border-top:2px solid #E4E2EC;padding-top:26px;}}
.pr{{display:flex;align-items:baseline;gap:34px;}}
.pr div{{font-size:34px;font-weight:900;}}
.pr small{{font-size:24px;font-weight:700;color:#3B3949;margin-right:10px;}}
.pn{{margin-top:8px;font-size:21px;font-weight:700;color:#8E8CA3;}}
.spec{{margin-top:22px;font-size:26px;font-weight:700;line-height:1.5;color:#3B3949;}}
.lead{{display:inline-block;margin-top:18px;background:#D2610E;color:#fff;font-size:30px;
  font-weight:900;letter-spacing:.03em;padding:10px 26px;border-radius:999px;}}
.ft{{position:absolute;left:52px;right:52px;bottom:40px;display:flex;align-items:flex-end;}}
.logo{{font-family:"Helvetica Neue",Arial,sans-serif;font-weight:800;font-size:44px;letter-spacing:.10em;}}
.logo .a{{color:#F97316}}.logo .b{{color:#8B5CF6}}
.url{{margin-left:auto;font-size:26px;font-weight:700;color:#8E8CA3;padding-bottom:6px;}}
</style></head><body><div class="wrap">
<div class="rail"></div>
<div class="hd"><div class="kick">{kicker}</div><h1>{title}</h1></div>
<div class="ph"><img src="file://{photo}"></div>
<div class="sub">{sub}</div>
<div class="info">
  <div class="pr">{price}</div>
  <div class="pn">{price_note}</div>
  <div class="spec">{spec}</div>
  <div class="lead">{lead}</div>
</div>
<div class="ft"><div class="logo"><span class="a">CHARA</span><span class="b">MARL</span></div>
  <div class="url">charamarl.com</div></div>
</div></body></html>''' % (W, H)


# --- 「アクキーとピンズ、ともに販売中」カード（商品画像のみ・写真なし） ---
AKI = ['sue_red', 'putti_yellow', 'mossun_blue', 'gmc_red', 'ufoo_white', 'dogooooo_pink',
       'inkumo_mono', 'danna_blue', 'blockma', 'mony', 'yurucrazy']          # img/products_t/
PINS = ['kg_kagechiyo', 'kg_kimi', 'kg_shigure', 'kg_promu', 'kg_muchiko', 'sue',
        'mossun', 'putti', 'yurucrazy', 'danna', 'inkumo', 'mony']          # img/pins/
# 文言の出どころ: characters/gmc.html（アクキー）・characters/pins.html（ピンズ）。2026-10-02時点
AKI_PRICE = '¥1,500'
AKI_SPEC = '50mm・NFCタグ付き'
BOTH_LEAD = '同じ締めなので、両方ご注文でも1回でお届けします'

TPL_BOTH = '''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@700;900&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:%dpx;height:%dpx;overflow:hidden;background:#FFFDF8;color:#17161F;
  font-family:"Zen Kaku Gothic New","Hiragino Sans",sans-serif;position:relative;}}
body::before{{content:"";position:absolute;inset:0;
  background:radial-gradient(800px 420px at 92%% 0%%,#FFE9D2 0%%,rgba(255,233,210,0) 62%%),
             radial-gradient(700px 420px at 0%% 100%%,#ECE4FB 0%%,rgba(236,228,251,0) 60%%);}}
.wrap{{position:relative;height:100%%;padding:0 52px;}}
.rail{{position:absolute;top:0;left:0;right:0;height:8px;background:linear-gradient(90deg,#FF8A00,#FF4D8D 52%%,#8E4ED9);}}
.hd{{height:214px;padding-top:44px;}}
.kick{{font-size:24px;font-weight:700;color:#8E8CA3;letter-spacing:.08em;}}
h1{{margin-top:6px;font-size:70px;font-weight:900;line-height:1.15;letter-spacing:.01em;}}
.lead{{margin-top:12px;font-size:27px;font-weight:700;color:#3B3949;}}
.blk{{padding-top:22px;border-top:2px solid #E4E2EC;}}
.blk.a{{height:470px;}} .blk.b{{height:412px;}}
.bh{{display:flex;align-items:baseline;flex-wrap:wrap;gap:4px 18px;margin-bottom:14px;}}
.bh b{{font-size:38px;font-weight:900;}}
.bh .pr{{font-size:34px;font-weight:900;color:#D2610E;}}
.bh .sp{{font-size:22px;font-weight:700;color:#8E8CA3;}}
.ga{{display:grid;grid-template-columns:repeat(6,1fr);gap:8px 14px;}}
.ga div{{height:170px;display:flex;align-items:center;justify-content:center;}}
.ga img{{max-width:100%%;max-height:100%%;object-fit:contain;filter:drop-shadow(0 6px 10px rgba(30,24,50,.18));}}
.gp{{display:grid;grid-template-columns:repeat(6,1fr);gap:16px 14px;}}
.gp div{{aspect-ratio:1;border-radius:50%%;overflow:hidden;box-shadow:0 5px 14px rgba(20,18,32,.22);}}
.gp img{{width:100%%;height:100%%;object-fit:cover;transform:scale(1.1);display:block;}}
.ft{{position:absolute;left:52px;right:52px;bottom:38px;}}
.cut{{display:inline-block;background:#D2610E;color:#fff;font-size:29px;font-weight:900;letter-spacing:.03em;padding:10px 26px;border-radius:999px;}}
.sub{{margin-top:12px;font-size:23px;font-weight:700;color:#3B3949;}}
.row{{margin-top:20px;display:flex;align-items:flex-end;}}
.logo{{font-family:"Helvetica Neue",Arial,sans-serif;font-weight:800;font-size:44px;letter-spacing:.10em;}}
.logo .a{{color:#F97316}}.logo .b{{color:#8B5CF6}}
.url{{margin-left:auto;font-size:26px;font-weight:700;color:#8E8CA3;padding-bottom:6px;}}
</style></head><body><div class="rail"></div><div class="wrap">
<div class="hd"><div class="kick">CHARAMARL グッズ</div><h1>アクキーとピンズ、販売中</h1>
  <div class="lead">どちらも受注生産｜毎月末締め・翌月中旬ごろのお届け</div></div>
<div class="blk a"><div class="bh"><b>アクリルキーホルダー</b><span class="pr">{aki_price}</span><span class="sp">11種｜{aki_spec}</span></div>
  <div class="ga">{aki}</div></div>
<div class="blk b"><div class="bh"><b>ピンズ</b><span class="pr">¥1,800</span><span class="sp">12種｜直径25mm・ドーム加工｜4個セットは1個 ¥1,100</span></div>
  <div class="gp">{pins}</div></div>
<div class="ft"><div class="cut">{lead}</div><div class="sub">税込・送料込｜売上の一部は、絵を描いた作家さんにお渡ししています</div>
  <div class="row"><div class="logo"><span class="a">CHARA</span><span class="b">MARL</span></div><div class="url">charamarl.com</div></div></div>
</div></body></html>''' % (W, H)


def render_both(out_dir):
    aki = ''.join(f'<div><img src="file://{REPO}/img/products_t/{k}.png"></div>' for k in AKI)
    pins = ''.join(f'<div><img src="file://{REPO}/img/pins/{k}.png"></div>' for k in PINS)
    htm = TPL_BOTH.format(aki=aki, pins=pins, aki_price=AKI_PRICE, aki_spec=AKI_SPEC, lead=BOTH_LEAD)
    hp = os.path.join(out_dir, 'card_both.html')
    op = os.path.join(out_dir, 'card_both.png')
    open(hp, 'w', encoding='utf-8').write(htm)
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files',
                    f'--screenshot={op}', f'--window-size={W},{H}', '--default-background-color=00000000',
                    f'file://{hp}'], check=True, capture_output=True)
    print(f'{op}  ({W}×{H})')


# --- アクキー1体の「販売中」カード（作家さんに渡して、ご自身の投稿に使ってもらう） ---
# (id, 表示名, 作家, 商品画像 img/products_t/<file>.png, 商品ページ)
AKEY = {
    'sue':       ('SUE',           'DinoRenny',      'sue_red',       'characters/sue.html'),
    'putti':     ('PUTTI',         'DinoRenny',      'putti_yellow',  'characters/putti.html'),
    'mossun':    ('MOSSUN',        'DinoRenny',      'mossun_blue',   'characters/mossun.html'),
    'gmc':       ('レコマル',       'MARU_GMC',       'gmc_red',       'characters/gmc.html'),
    'ufoo':      ('う〜ほ〜',       'ちゅい',          'ufoo_white',    'characters/ufoo.html'),
    'dogooooo':  ('dogooooo',      'SAYoooooh',      'dogooooo_pink', 'characters/dogooooo.html'),
    'inkumo':    ('インクモ',       "Ink'z Monster",  'inkumo_mono',   'characters/inkumo.html'),
    'danna':     ('だんな',         '赤猫かるま',      'danna_blue',    'characters/danna.html'),
    'blockma':   ('ぶろっくま',     'チンチロ',        'blockma',       'characters/blockma.html'),
    'mony':      ('モニィ',         'morry',          'mony',          'characters/mony.html'),
    'yurucrazy': ('ユルクレイジー', 'CRAZY',          'yurucrazy',     'characters/yurucrazy.html'),
}

TPL_AKEY = '''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@700;900&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:%dpx;height:%dpx;overflow:hidden;background:#FFFDF8;color:#17161F;
  font-family:"Zen Kaku Gothic New","Hiragino Sans",sans-serif;position:relative;}}
body::before{{content:"";position:absolute;inset:0;
  background:radial-gradient(800px 420px at 92%% 0%%,#FFE9D2 0%%,rgba(255,233,210,0) 62%%),
             radial-gradient(700px 420px at 0%% 100%%,#ECE4FB 0%%,rgba(236,228,251,0) 60%%);}}
.wrap{{position:relative;height:100%%;}}
.rail{{height:8px;background:linear-gradient(90deg,#FF8A00,#FF4D8D 52%%,#8E4ED9);}}
.hd{{height:170px;padding:40px 52px 0;}}
.kick{{font-size:24px;font-weight:700;color:#8E8CA3;letter-spacing:.08em;}}
h1{{margin-top:6px;font-size:64px;font-weight:900;line-height:1.15;letter-spacing:.01em;}}
.ph{{height:700px;margin:0 52px;border-radius:28px;background:#EAE7F2;
  display:flex;align-items:center;justify-content:center;box-shadow:0 10px 30px rgba(20,18,32,.12);}}
.ph img{{height:92%%;max-width:90%%;object-fit:contain;filter:drop-shadow(0 18px 24px rgba(30,24,50,.28));}}
.by{{height:96px;padding:26px 52px 0;font-size:30px;font-weight:700;color:#3B3949;}}
.by b{{font-weight:900;}}
.info{{height:420px;margin:0 52px;border-top:2px solid #E4E2EC;padding-top:26px;}}
.pr{{display:flex;align-items:baseline;gap:20px;}}
.pr b{{font-size:54px;font-weight:900;}}
.pr span{{font-size:25px;font-weight:700;color:#3B3949;}}
.spec{{margin-top:16px;font-size:26px;font-weight:700;line-height:1.5;color:#3B3949;}}
.lead{{display:inline-block;margin-top:18px;background:#D2610E;color:#fff;font-size:30px;font-weight:900;
  letter-spacing:.03em;padding:10px 26px;border-radius:999px;}}
.ft{{position:absolute;left:52px;right:52px;bottom:40px;display:flex;align-items:flex-end;}}
.logo{{font-family:"Helvetica Neue",Arial,sans-serif;font-weight:800;font-size:44px;letter-spacing:.10em;}}
.logo .a{{color:#F97316}}.logo .b{{color:#8B5CF6}}
.url{{margin-left:auto;font-size:25px;font-weight:700;color:#8E8CA3;padding-bottom:6px;}}
</style></head><body><div class="wrap">
<div class="rail"></div>
<div class="hd"><div class="kick">アクリルキーホルダー ／ 販売中</div><h1>{name}</h1></div>
<div class="ph"><img src="file://{img}"></div>
<div class="by">作家：<b>{artist}</b></div>
<div class="info">
  <div class="pr"><b>¥1,500</b><span>税込・送料込</span></div>
  <div class="spec">50mm・NFCタグ付き<br>売上の一部は、絵を描いた作家さんにお渡ししています</div>
  <div class="lead">受注生産｜毎月末締め・翌月中旬ごろの発送</div>
</div>
<div class="ft"><div class="logo"><span class="a">CHARA</span><span class="b">MARL</span></div><div class="url">{url}</div></div>
</div></body></html>''' % (W, H)


def render_akey(cid, out_dir):
    name, artist, imgf, page = AKEY[cid]
    htm = TPL_AKEY.format(name=html.escape(name), artist=html.escape(artist),
                          img=f'{REPO}/img/products_t/{imgf}.png', url='charamarl.com/' + page)
    safe = artist.replace('/', '_')
    hp = os.path.join(out_dir, f'akey_{cid}.html'); op = os.path.join(out_dir, f'akey_{cid}.png')
    open(hp, 'w', encoding='utf-8').write(htm)
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files',
                    f'--screenshot={op}', f'--window-size={W},{H}', '--default-background-color=00000000',
                    f'file://{hp}'], check=True, capture_output=True)
    os.remove(hp)
    print(f'{op}  ({W}×{H})  {name} / {artist}')


# --- ピンズ1絵柄の「販売中」カード ---
# key: (表示名, 作家)   画像は img/pins/<key>.png（丸い商品画像）
PINCARD = {
    'sue': ('スー', 'DinoRenny'), 'mossun': ('モッスン', 'DinoRenny'), 'putti': ('プッチィ', 'DinoRenny'),
    'yurucrazy': ('ユルクレイジー', 'CRAZY'), 'danna': ('だんな', '赤猫かるま'),
    'inkumo': ('インクモ', "Ink'z Monster"), 'mony': ('モニィ', 'morry'),
    'kg_kagechiyo': ('カゲチヨ', 'カゲチヨ'), 'kg_kimi': ('キミ', 'カゲチヨ'), 'kg_shigure': ('シグレ', 'カゲチヨ'),
    'kg_promu': ('プロム', 'カゲチヨ'), 'kg_muchiko': ('ムチコ', 'カゲチヨ'),
}


def render_pin(key, out_dir):
    name, artist = PINCARD[key]
    t = TPL_AKEY
    t = t.replace('アクリルキーホルダー ／ 販売中', 'ピンズ ／ 販売中')
    t = t.replace('<div class="pr"><b>¥1,500</b><span>税込・送料込</span></div>',
                  '<div class="pr"><b>¥1,800</b><span>税込・送料込｜4個セットなら1個 ¥1,100</span></div>')
    t = t.replace('50mm・NFCタグ付き<br>', '直径25mm・金属フレーム＋ドーム加工<br>')
    t = t.replace('毎月末締め・翌月中旬ごろの発送', '毎月末締め・翌月中旬ごろのお届け')
    t = t.replace('.ph img{{height:92%;max-width:90%;object-fit:contain;filter:drop-shadow(0 18px 24px rgba(30,24,50,.28));}}',
                  '.ph img{{height:80%;max-width:86%;object-fit:contain;border-radius:50%;filter:drop-shadow(0 18px 24px rgba(30,24,50,.28));}}')
    htm = t.format(name=html.escape(name), artist=html.escape(artist),
                   img=f'{REPO}/img/pins/{key}.png', url='charamarl.com/characters/pins.html')
    hp = os.path.join(out_dir, f'pin_{key}.html'); op = os.path.join(out_dir, f'pin_{key}.png')
    open(hp, 'w', encoding='utf-8').write(htm)
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files',
                    f'--screenshot={op}', f'--window-size={W},{H}', '--default-background-color=00000000',
                    f'file://{hp}'], check=True, capture_output=True)
    os.remove(hp)
    print(f'{op}  ({W}×{H})  {name} / {artist}')


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in (*CARDS, 'both', 'akey', 'pin'):
        raise SystemExit(f'使い方: make_pin_card.py <{"|".join([*CARDS, "both", "akey", "pin"])}> [出力先]')
    key = sys.argv[1]
    if key == 'akey':
        cid = sys.argv[2] if len(sys.argv) > 2 else 'all'
        out = sys.argv[3] if len(sys.argv) > 3 else os.path.expanduser('~/Downloads/CHARAMARL/03_画像/charamarl_akey_cards')
        os.makedirs(out, exist_ok=True)
        for k in (AKEY if cid == 'all' else [cid]):
            render_akey(k, out)
        return
    if key == 'pin':
        k = sys.argv[2] if len(sys.argv) > 2 else 'all'
        out = sys.argv[3] if len(sys.argv) > 3 else os.path.expanduser('~/Downloads/CHARAMARL/03_画像/charamarl_pin_cards')
        os.makedirs(out, exist_ok=True)
        for kk in (PINCARD if k == 'all' else [k]):
            render_pin(kk, out)
        return
    if key == 'both':
        out = sys.argv[2] if len(sys.argv) > 2 else OUT_DEFAULT
        os.makedirs(out, exist_ok=True)
        return render_both(out)
    c = CARDS[key]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else OUT_DEFAULT
    os.makedirs(out_dir, exist_ok=True)

    if c['labels']:
        sub = '<div class="lab">' + ''.join(
            f'<div><b>{html.escape(n)}</b><span>{html.escape(a)}</span></div>' for n, a in c['labels']) + '</div>'
    else:
        sub = '<div class="th">' + ''.join(
            f'<figure><div class="c"><img src="file://{REPO}/img/pins/{k}.png"></div>'
            f'<figcaption>{html.escape(n)}</figcaption></figure>' for k, n in c['thumbs']) + \
            f'<div class="cap">{html.escape(c.get("thumb_caption", ""))}</div></div>'

    price = ''.join(f'<div><small>{html.escape(a)}</small>{html.escape(b)}</div>' for a, b in PRICE)
    htm = TPL.format(kicker=html.escape(c['kicker']), title=html.escape(c['title']),
                     photo=os.path.join(PHOTO_DIR, c['photo']), sub=sub, price=price,
                     price_note=html.escape(PRICE_NOTE), spec=html.escape(SPEC), lead=html.escape(LEAD))

    hp = os.path.join(out_dir, f'card_{key}.html')
    op = os.path.join(out_dir, f'card_{key}.png')
    open(hp, 'w', encoding='utf-8').write(htm)
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars',
                    '--allow-file-access-from-files',
                    f'--screenshot={op}', f'--window-size={W},{H}',
                    '--default-background-color=00000000', f'file://{hp}'],
                   check=True, capture_output=True)
    print(f'{op}  ({W}×{H})')


if __name__ == '__main__':
    main()
