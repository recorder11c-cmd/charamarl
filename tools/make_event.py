#!/usr/bin/env python3
"""イベント告知のカードを作る（1200×1500・Xにそのまま貼れる）

    python3 tools/make_event.py <イベントキー> [出力先ディレクトリ]

    例)  python3 tools/make_event.py culturesnack
         python3 tools/make_event.py kanazawa ~/Downloads/CHARAMARL/03_画像/charamarl_event

■ なぜ作るか
    イベント告知の画像は**保存されて当日に見返される**。
    作品だけの絵を貼ると、保存した人が「どこへ行けばいいか」を持ち帰れない。
    日付・時間・場所・ブース番号を絵の中に入れておく。

■ 地の色
    🔴 **白っぽい絵は地を暗くする。**Xのライトモードだと背景と同化して輪郭が消える。
    EVENTS に dark=True を足す。Selfie Bears の線画がその例。

■ 決めていること
    ・作品の上に文字を載せない。絵は絵のまま、情報は下の帯に置く
    ・ブース番号はいちばん大きく出す。当日いちばん要る情報がそれ
    ・主催者名は入れない。こちらが出すのは「この作家さんがここにいる」だけ
"""
import sys, os, json, subprocess, urllib.request, html

API = 'https://charamarl.com/api/gallery'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
W, H = 1200, 1500
OUT_DEFAULT = os.path.expanduser('~/Downloads/CHARAMARL/03_画像/charamarl_event')

EVENTS = {
    'culturesnack': dict(
        artist='Selfie Bears', work='NO SELFIE, NO LIFE',
        name="CULTURE SNACK '26",
        place='GRAND GREEN OSAKA 南館1階屋外スペース',
        booth='ブース No.219',
        days=['10/2(金) 16:00〜21:00', '10/3(土) 11:00〜18:00'],
        dark=True),          # 白い線画。地を暗くしないと輪郭が消える
    'kanazawa': dict(
        artist='ひよ', work='ぽよっとぷりん',
        name='金沢ハンドメイドマルシェ',
        place='石川県産業展示館 3号館',
        booth='ブース D-94',
        days=['10/3(土)・4(日)', '11:00〜17:00'],
        dark=False),
    'nkore': dict(
        artist='YUO.+', work='CLOUD RABBIT',
        name='NコレYOKOHAMA',
        place='相鉄ムービル1F（元「焼メシ焼スパ金太郎」）／入場無料',
        booth='ブース No.08',
        days=['10/3(土)・4(日)', '11:00〜18:00'],
        dark=True),         # 灰色の背景。明るい地だと沈む
    'newbookfair': dict(
        artist='SAYoooooh', work='dogooooo',
        name='横浜Art Center NEW ニューBOOK FAIR',
        place='Art Center NEW（新高島駅 地下1階直結）／入場1,000円・学生無料',
        booth='',
        days=['10/3(土)・4(日)', '12:00〜20:00（19:30最終入場）'],
        dark=False),
    'bside': dict(
        artist='プラクテル', work='腐敗少女',
        name='B-SIDE LABEL ART FES 2026',
        place='グラングリーン大阪 ロートハートスクエア／入場無料',
        booth='ブース No.19',
        days=['10/10(土)・11(日)', '11:00〜19:00'],
        dark=True),
    # 出どころ＝本人の告知 x.com/puracteru（2026-10-04 23:24・お品書き）。日付は「10/10.11」＝2026-10-10(土)・11(日)
    # 出どころ＝本人の告知 x.com/OoooohSay/status/2105453447915114728（2026-10-01）
    # ブース番号は10/1時点で本人の投稿に無い。分からないまま出す（booth を空にすると帯ごと消える）
    # 出どころ＝本人の告知 x.com/YUO_8888（2026-09-29）＋ Nコレ公式 @Nftcolor22（9/16）
    # 出どころ＝本人の告知 x.com/pp_hiyo/status/2097482486418972896（2026-09-09）
    # 🔴 9/9の時点で公開されていたのに、9/29に「ブース番号が分からない」として
    #    本人に聞こうとした。公式アカウントはその投稿にリプまでしていた。
    #    **イベントの詳細は、まず本人のタイムラインを遡る。**
}

TPL = '''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@700;900&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:%dpx;height:%dpx;overflow:hidden;background:{bg};
  font-family:"Zen Kaku Gothic New","Hiragino Sans",sans-serif;
  display:flex;flex-direction:column;position:relative;}}
.rail{{height:8px;background:linear-gradient(90deg,#FF8A00,#FF4D8D 52%%,#8E4ED9);}}
/* 🔴 .art を flex:1 にすると絵が伸びて info を画面外へ押し出す。
   2026-09-29、ブース番号とフッターが切れた。高さは固定で持つこと。 */
.art{{height:866px;display:flex;align-items:center;justify-content:center;padding:40px 44px 8px;}}
.art img{{max-width:100%%;max-height:100%%;object-fit:contain;display:block;}}
.info{{height:626px;background:{band};color:{ink};padding:32px 52px 36px;display:flex;flex-direction:column;justify-content:center;align-items:flex-start;}}
.who{{font-size:28px;font-weight:700;color:{sub};letter-spacing:.03em;margin-bottom:6px;}}
.who b{{color:{ink};font-weight:900;}}
h1{{font-size:50px;font-weight:900;line-height:1.2;letter-spacing:.01em;margin-bottom:20px;}}
.day{{font-size:36px;font-weight:900;line-height:1.5;}}
.place{{margin-top:14px;font-size:25px;font-weight:700;color:{sub};line-height:1.45;}}
.booth{{display:inline-block;margin-top:18px;background:#D2610E;color:#fff;
  font-size:38px;font-weight:900;letter-spacing:.04em;padding:9px 26px;border-radius:999px;}}
.foot{{margin-top:22px;font-size:21px;font-weight:700;color:{sub};letter-spacing:.06em;}}
</style></head><body>
  <div class="rail"></div>
  <div class="art"><img src="{img}"></div>
  <div class="info">
    <div class="who"><b>{artist}</b> さんが出展されます</div>
    <h1>{name}</h1>
    <div class="day">{days}</div>
    <div class="place">{place}</div>
    {booth}
    <div class="foot">CHARAMARL　charamarl.com</div>
  </div>
</body></html>''' % (W, H)


def find_work(artist, title):
    d = json.load(urllib.request.urlopen(API))['list']
    for w in d:
        if (w.get('artist') or '').strip() == artist and (w.get('title') or '').strip() == title:
            return w
    raise SystemExit(f'作品が見つからない: {artist} / {title}')


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in EVENTS:
        raise SystemExit(f'使い方: make_event.py <{"|".join(EVENTS)}> [出力先]')
    key = sys.argv[1]
    e = EVENTS[key]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else OUT_DEFAULT
    os.makedirs(out_dir, exist_ok=True)

    w = find_work(e['artist'], e['work'])
    dark = e.get('dark')
    theme = dict(
        bg='#1A1714' if dark else '#F6F1E6',
        band='#12100E' if dark else '#20180F',
        ink='#fff', sub='#9A9088' if dark else '#B7AFA4')

    booth = f'<div class="booth">{html.escape(e["booth"])}</div>' if e.get('booth') else ''
    htm = TPL.format(
        img=w['img'],
        artist=html.escape(e['artist']),
        name=html.escape(e['name']),
        days='<br>'.join(html.escape(d) for d in e['days']),
        place=html.escape(e['place']),
        booth=booth, **theme)

    hp = os.path.join(out_dir, f'{key}.html')
    op = os.path.join(out_dir, f'{key}.png')
    open(hp, 'w', encoding='utf-8').write(htm)
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars',
                    f'--screenshot={op}', f'--window-size={W},{H}',
                    '--default-background-color=00000000', f'file://{hp}'],
                   check=True, capture_output=True)
    print(f'{op}  ({W}×{H})')
    print(f'{hp}  ← 文言を直して撮り直せる')


if __name__ == '__main__':
    main()
