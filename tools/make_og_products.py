#!/usr/bin/env python3
"""商品ページ（characters/<id>.html）に、リンクを貼ったとき出る絵（OGP）を入れる。

    python3 tools/make_og_products.py

■ なぜ（2026-11-19）
    商品ページには og:image が無く、Xなどに貼っても絵が出なかった（一覧の keyrings / pins だけあった）。

■ 作るもの
    img/og/p/<id>.jpg     1200×630。商品写真を**縮小して置くだけ**（切らない・補正しない）。
    characters/<id>.html  <title> の直後に OGP のタグを入れる（入っていれば入れ替える）。本文は触らない。

■ 商品名・作家名・説明・写真
    トップページ（index.html）の FEATURED と商品タイルから読む。ここに無い商品は EXTRA に書く。
    価格は絵にも説明にも入れない（変えたとき古くなるため）。
    ⚠️ characters/kagechiyo-acrylic.html は未販売（noindex）なので入れない。
"""
import os, re, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_seo

ROOT = 'https://charamarl.com'
OUT = 'img/og/p'
esc = lambda s: html.escape(str(s or ''), quote=True)
# FEATURED に無い商品:  id → (商品名, 作家名, 説明, 写真)
EXTRA = {
    'dino-canvas': ('旅する恐竜スーさん キャンバスアート', 'DinoRenny',
                    'DinoRennyの看板恐竜「SUE」が、日本各地をめぐるシリーズ。その土地の名物や文化をまとった姿を、木枠張りのミニキャンバスにプリントしました。', 'img/canvas/dino_kyoto.jpg'),
}
MARK_A, MARK_B = '<!-- OGP ここから（tools/make_og_products.py） -->', '<!-- OGP ここまで -->'


def items():
    s = open('index.html', encoding='utf-8').read()
    tiles = {}   # ページ → タイルの写真（縮小前の元ファイルに読み替える）
    for m in re.finditer(r'<div class="pin[^"]*"([^>]*)>\s*<div class="pin-img[^"]*"[^>]*><img src="\./img/t/(products_t/[^"]+)\.webp"', s):
        a = dict(re.findall(r'data-([a-z]+)="([^"]*)"', m.group(1)))
        page = a.get('href') or (f"./characters/{a['char']}.html" if a.get('char') else None)
        if page:
            tiles.setdefault(os.path.basename(page)[:-5], 'img/' + m.group(2) + '.png')
    out = []
    blk = s[s.index('const FEATURED = ['):]
    blk = blk[:blk.index('\n  ];')] + '\n'
    for m in re.finditer(r"\{ id:'([^']+)',(.*?)\},?\n", blk):
        f = dict(re.findall(r"(\w+):'((?:[^'\\]|\\.)*)'", '{' + m.group(2)))
        fid = os.path.basename(f.get('page', ''))[:-5]
        if m.group(1) in ('pins',) or not fid or fid not in tiles:
            continue
        creator = re.search(r'creator:"([^"]+)"', m.group(2))
        out.append((fid, f.get('drop') or f.get('name'), creator.group(1) if creator else f.get('creator'), f.get('desc'), tiles[fid]))
    out += [(k,) + v for k, v in EXTRA.items()]
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    n = 0
    for pid, name, creator, desc, photo in items():
        page = f'characters/{pid}.html'
        if not os.path.exists(page) or not os.path.exists(photo):
            print('とばす（ファイルなし）', pid, photo); continue
        s = open(page, encoding='utf-8').read()
        if 'noindex' in s[:1500]:
            print('とばす（noindex）', pid); continue
        img = f'{OUT}/{pid}.jpg'
        build_seo.og_image(creator, [{'img': photo}], img)
        title = f'{name} — CHARAMARL'
        tags = (f'{MARK_A}\n'
                f'<meta name="description" content="{esc(desc)}">\n'
                f'<meta property="og:type" content="product">\n'
                f'<meta property="og:site_name" content="CHARAMARL">\n'
                f'<meta property="og:url" content="{ROOT}/{page}">\n'
                f'<meta property="og:title" content="{esc(title)}">\n'
                f'<meta property="og:description" content="{esc(desc)}">\n'
                f'<meta property="og:image" content="{ROOT}/{img}">\n'
                f'<meta property="og:image:width" content="1200">\n'
                f'<meta property="og:image:height" content="630">\n'
                f'<meta name="twitter:card" content="summary_large_image">\n'
                f'{MARK_B}')
        if MARK_A in s:
            s = s[:s.index(MARK_A)] + tags + s[s.index(MARK_B) + len(MARK_B):]
        else:
            if re.search(r'<meta name="description"', s[:3000]):   # 既にあるなら description は重ねない
                tags = tags.replace(f'<meta name="description" content="{esc(desc)}">\n', '')
            i = s.index('</title>') + len('</title>')
            s = s[:i] + '\n' + tags + s[i:]
        open(page, 'w', encoding='utf-8').write(s)
        n += 1
        print('OK', pid, '|', name, '|', creator)
    print(f'{n} ページに入れました')


if __name__ == '__main__':
    main()
