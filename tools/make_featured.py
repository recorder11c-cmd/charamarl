#!/usr/bin/env python3
"""「今日の注目アーティスト」のX投稿セット（本文・リプ・画像）を作る。

    python3 tools/make_featured.py                # 今日のぶん
    python3 tools/make_featured.py 2026-11-20     # 日付を指定（複数可）
    python3 tools/make_featured.py --list 14      # 今日から14日ぶんの予定を表示するだけ

■ 何をするか
    その日にトップページの「今日の注目アーティスト」に出る作家を調べ、
    02_文面/00_未送信/MMDD_今日の注目アーティスト/ に次の4つを置く。
        0_手順.txt        投稿の手順
        1_本投稿.txt      本文（リンクは入れない）
        2_リプ_リンク.txt  リプ欄に貼るリンク（utm つき）
        画像_<作家名>.jpg  作家さんの作品を新しい順に3点まで並べた絵（縮小して並べただけ）

■ 誰が出るかの計算
    index.html の中の計算（pickFeatured）を node でそのまま動かす。ここに同じ計算を書き写さない
    （サイト側を直したとき、ずれるため）。

■ @ について
    HANDLES に確認済みのものだけ書いてある。**載っていない作家は @ を付けず名前だけ**にする。
    推測で足さない（別人に飛ぶ）。増やすときは、プロフィールを開いて確かめてから。

■ 文面について
    作風の説明は書かない（現物を見ずに書かないため）。掲載中の作品名だけを出す。
    一言足したいときは、作品を見てから 1_本投稿.txt に手で足す。
"""
import sys, os, re, json, glob, shutil, subprocess, tempfile, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_seo

API = 'https://charamarl.com/api/gallery'
JST = timezone(timedelta(hours=9))
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.expanduser('~/Library/Mobile Documents/com~apple~CloudDocs/CHARAMARL/02_文面/00_未送信')

# 確認済みの X の @（掲載名 → @）。載っていない作家は名前だけで出す
HANDLES = {
    'ahoyoung': 'hatch0hme', 'DinoRenny': 'dino_renny', 'MARU_GMC': 'maru_nft_', "Ink'z Monster": 'Koooseee_InkzM',
    'ちゅい': 'im_chui_', 'SAYoooooh': 'OoooohSay', '赤猫かるま': 'Calma_94', 'カゲチヨ': 'MechaMeow_CAT01',
    'CRAZY': 'Crazy_Ukiyo_E', 'チンチロ': 'chinchillo_p', 'かるき': 'mutikin10111005', 'YUO.+': 'YUO_8888',
    'ハンナ': 'hanna_iwanuma33', 'ROKU': 'junkeeees_ROKU', 'chanyama': 'chanyamaINK0202', 'PHAGY': 'phagy_nft',
    'えぃす': 'a_basenft', 'トサカマミ': 'tosakamami', 'なりぷと': 'nachauzY', 'プラクテル': 'puracteru',
    'SHiNO': '404SHiNO403', 'morry': 'Morry369', 'エリー': 'melly_design', 'カラフルまじっく': 'colorful_masic',
    'NK.art': 'NKart_NFT', 'Beerno Mocca': 'beernomocca', 'ひよ': 'pp_hiyo', 'DREAMER©': 'DREAMER_RPG',
    'Selfie Bears': 'selfie_bears227', 'CryptoSuperHeroes': 'pizzaboy_csh', 'Fz': '_gwanzi', 'テンテン': 'TENTENTENJIN',
    'みやもとさぶろう': 'chatoramesuneko', 'AKIRA': 'tkchan_official', 'ガングリアン': 'gangurien', 'あめいメア': 'amei_mea',
    'らすべっと': 'rassvet_oekaki', '海音': 'NK_kanon_', '恋するウツウツ': 'koiutuforchild', 'がんぐりお': 'gangxxlion',
    'theM.U.G': 'shitsugyou_otou',
    'トゥインキィー（TWINKII）': 'twinkii_project',   # 11/19 このアカウントとDMでやり取り済み
}


def day_no(d):
    """日本時間の日付 → 通し番号（index.html の FA_DAY と同じ）"""
    return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp() // 86400)


def featured(days, gallery):
    """その日に出る作家名。index.html の計算を node で動かす。"""
    html_src = open(os.path.join(REPO, 'index.html'), encoding='utf-8').read()
    a0, a1 = html_src.index('  const FEATURED_ARTISTS = ['), html_src.index('  // 読み込み直後:')
    js = ('const d=JSON.parse(require("fs").readFileSync(process.argv[2],"utf8"));\n'
          'const days=JSON.parse(process.argv[3]);\n'
          + html_src[a0:a1] +
          '\nconsole.log(JSON.stringify(days.map(n=>featuredFromGallery(d,n).name)));\n')
    with tempfile.TemporaryDirectory() as t:
        open(os.path.join(t, 'g.json'), 'w', encoding='utf-8').write(json.dumps(gallery))
        open(os.path.join(t, 'f.js'), 'w', encoding='utf-8').write(js)
        r = subprocess.run(['node', os.path.join(t, 'f.js'), os.path.join(t, 'g.json'), json.dumps(days)],
                           capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def xlen(s):
    """Xの文字数（半角1・全角2）。上限280。"""
    return sum(1 if ord(c) < 0x1100 else 2 for c in s)


def short(t, n=18):
    return t if len(t) <= n else t[:n] + '…'


def kit(d, name, gallery):
    mine = [w for w in gallery['list'] if (w.get('artist') or '').strip() == name and w.get('cat') != 'INTERVIEW']
    picks = build_seo.pick_works(mine)
    titles = []
    for w in picks:
        t = (w.get('title') or '').strip()
        if t and t not in titles:
            titles.append(t)
    rest = len(mine) - len(titles[:2])
    works = ''.join(f'「{short(t)}」' for t in titles[:2]) + (f' ほか{rest}点' if rest > 0 else '')
    at = HANDLES.get(name)
    who = f'{name} さん（@{at}）' if at else f'{name} さん'
    body = (f'🎪 今日の注目アーティスト\n\n{who}\n\n'
            f'CHARAMARLに{works}を掲載中です。\n作品と、作家さんの活動場所へのリンクはリプ欄に。\n\n#CHARAMARL')
    sl = build_seo.slug(name)
    url = (f'https://charamarl.com/a/{sl}.html?utm_source=x&utm_medium=social'
           f'&utm_campaign=featured_artist&utm_content={d:%Y%m%d}')
    try:
        st = urllib.request.urlopen(urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).status
    except Exception as e:
        st = getattr(e, 'code', 0)
    imgs = glob.glob(os.path.join(REPO, 'img/og/a', f'{sl}_*.jpg'))
    out = os.path.join(OUT, f'{d:%m%d}_今日の注目アーティスト')
    os.makedirs(out, exist_ok=True)
    safe = re.sub(r'[\\/:*?"<>|]', '_', name)
    open(os.path.join(out, '1_本投稿.txt'), 'w', encoding='utf-8').write(body + '\n')
    open(os.path.join(out, '2_リプ_リンク.txt'), 'w', encoding='utf-8').write(f'作品はこちらから🎪\n{url}\n')
    if imgs:
        shutil.copy(imgs[0], os.path.join(out, f'画像_{safe}.jpg'))
    warn = []
    if xlen(body) > 280: warn.append(f'⚠️ 本文が長い（{xlen(body)}／280）。作品名を削る')
    if not at: warn.append('⚠️ @ が未確認。名前だけで出している')
    if st != 200: warn.append(f'⚠️ リプのリンクが開けない（{st}）。tools/build_seo.py を回して push してから投稿する')
    if not imgs: warn.append('⚠️ 画像が無い。tools/build_seo.py を回す')
    open(os.path.join(out, '0_手順.txt'), 'w', encoding='utf-8').write(
        f'{d:%m/%d}（{"月火水木金土日"[d.weekday()]}）今日の注目アーティスト ＝ {name} さん\n'
        f'状態：送付待ち（投稿したら 01_送信済み へ移す）\n\n'
        f'1. 1_本投稿.txt を本文に貼り、画像_{safe}.jpg を付けて投稿（本文 {xlen(body)}／280）\n'
        f'2. その投稿のリプ欄に 2_リプ_リンク.txt を貼る\n'
        f'3. 公式の投稿は1日2本まで。この1本を数に入れる\n\n'
        f'・サイトのトップ「今日の注目アーティスト」も、この日は同じ作家さんが出ている（0:00に切り替わる）\n'
        f'・画像は作品を縮小して並べただけ（切っていない・補正していない）\n'
        f'・一言足すなら、作品を見てから。作風を名前から推測して書かない\n'
        + ('\n' + '\n'.join(warn) + '\n' if warn else ''))
    return out, xlen(body), warn


def main():
    args = sys.argv[1:]
    gallery = json.load(urllib.request.urlopen(urllib.request.Request(API, headers={'User-Agent': 'Mozilla/5.0'})))
    today = datetime.now(JST).date()
    if '--list' in args:
        n = int(args[args.index('--list') + 1]) if len(args) > args.index('--list') + 1 else 14
        ds = [today + timedelta(days=i) for i in range(n)]
        for d, name in zip(ds, featured([day_no(d) for d in ds], gallery)):
            print(f'{d:%m/%d}（{"月火水木金土日"[d.weekday()]}） {name}' + ('' if name in HANDLES else '   ※@未確認'))
        return 0
    ds = [datetime.strptime(a, '%Y-%m-%d').date() for a in args] or [today]
    for d, name in zip(ds, featured([day_no(d) for d in ds], gallery)):
        out, n, warn = kit(d, name, gallery)
        print(f'{d:%m/%d} {name} → {out}（本文 {n}／280）' + (''.join('\n   ' + w for w in warn)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
