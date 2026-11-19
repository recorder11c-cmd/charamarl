#!/usr/bin/env python3
"""COLOR TAP のページ（tap/<名前>.html）に、ページごとの title・説明・canonical・OGP を入れる。

    python3 tools/make_tap_meta.py

■ なぜ（2026-11-19）
    19ページすべての title が「COLOR TAP — CHARAMARL」で、説明も canonical も無かった。
    検索から見ると同じページが19枚ある状態で、キャラクター名で探しても出てこない。

■ 作るもの
    tap/<名前>.html        <title> を入れ替え、その直後に説明・canonical・OGP を入れる（入っていれば入れ替える）。
                           実行時に title を書き換えていた1行（document.title = …）は外す。遊びの中身は触らない。
    img/og/tap/<名前>.jpg  1200×630。そのページのキーアートを**縮小して置くだけ**（切らない・補正しない）。

■ キャラクター名・作家名
    ページの中の CONFIG.character と CM_NEXT.artist を読む（ここで決めない）。
    説明と絵を手で書いてあるページ（MOJA）は、そちらを残して title と canonical だけ合わせる。
    ページの表示名とキャラクター名がちがうものだけ NAME に書く。
    「タップで色が変わる」が当てはまらないページ（ヒーローが交代する・県が切り替わる など）は WHAT に書く。
    「グッズのNFCタグからも開けます」は、グッズがあるページ（CM_NEXT.goods）にだけ入れる。
"""
import os, re, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_seo

ROOT = 'https://charamarl.com'
OUT = 'img/og/tap'
esc = lambda s: html.escape(str(s or ''), quote=True)
MARK_A, MARK_B = '<!-- META ここから（tools/make_tap_meta.py） -->', '<!-- META ここまで -->'

# ページの表示名（CONFIG.character）とキャラクター名がちがうもの
NAME = {'gmc': 'レコマル'}
# 名前 → (title の真ん中, 説明の2文目)。無いものは「タップで色が変わる」
WHAT = {
    'csh':     ('タップでヒーローが交代', 'タップするたびにヒーローが交代します。'),
    'rafu':    ('タップで頭の上がかわる', 'タップするたびに頭の上がかわる「キモチずかん」です。'),
    'gotochi': ('タップで県が切り替わる', 'タップするたびに県が切り替わります。'),
}
# title をもともと持っているページ（title は触らない）:  名前 → 説明
OWN = {'junkeeees': 'JUNKeeeeSのキャラクター図鑑。タップでキャラクターを集められます。全36人。'}


def main():
    os.makedirs(OUT, exist_ok=True)
    titles = {}
    for f in sorted(os.listdir('tap')):
        if not f.endswith('.html'):
            continue
        key, page = f[:-5], f'tap/{f}'
        s = open(page, encoding='utf-8').read()
        ch = re.search(r'character:\s*"([^"]+)"', s)
        art = re.search(r'const CM_NEXT = \{"artist": "([^"]*)", "out": "[^"]*", "goods": "([^"]*)"\}', s)
        base = re.search(r'baseImage:\s*"([^"]+)"', s)
        assert ch and art and base, f'{page}: CONFIG / CM_NEXT が読めません'
        name, artist, goods = NAME.get(key, ch.group(1)), art.group(1), art.group(2)
        who = name if artist == name else f'{name}（{artist}）'
        if key in OWN:
            title = html.unescape(re.search(r'<title>([^<]*)</title>', s).group(1))
            desc = OWN[key]
        else:
            mid, what = WHAT.get(key, ('タップで色が変わる', 'タップするたびに色が変わります。'))
            title = f'{name} COLOR TAP｜{mid}｜CHARAMARL'
            desc = f'{who}のCOLOR TAPページ。{what}'
            # NFCタグが入っているのはアクリルキーホルダーだけ（パーカー・キャンバスには無い）
            keyring = goods and 'アクリルキーホルダー' in open(os.path.join('characters', goods), encoding='utf-8').read()[:600]
            desc += 'グッズのNFCタグからも開けます。' if keyring else ('グッズもあります。' if goods else 'CHARAMARLで作品も見られます。')
        assert title not in titles, f'title が重なりました: {title}（{titles.get(title)} と {page}）'
        titles[title] = page
        img = f'{OUT}/{key}.jpg'
        build_seo.og_image(artist, [{'img': os.path.join('tap', base.group(1))}], img)
        url = f'{ROOT}/{page}'
        tags = (f'{MARK_A}\n'
                f'<meta name="description" content="{esc(desc)}">\n'
                f'<link rel="canonical" href="{url}">\n'
                f'<meta property="og:type" content="website">\n'
                f'<meta property="og:site_name" content="CHARAMARL">\n'
                f'<meta property="og:url" content="{url}">\n'
                f'<meta property="og:title" content="{esc(title)}">\n'
                f'<meta property="og:description" content="{esc(desc)}">\n'
                f'<meta property="og:image" content="{ROOT}/{img}">\n'
                f'<meta property="og:image:width" content="1200">\n'
                f'<meta property="og:image:height" content="630">\n'
                f'<meta name="twitter:card" content="summary_large_image">\n'
                f'{MARK_B}')
        s = re.sub(r'<title>[^<]*</title>', lambda m: f'<title>{esc(title)}</title>', s, count=1)
        # 実行時に title を「<表示名> COLOR TAP | CHARAMARL」へ書き換えていた行。上の title と食い違うので外す
        s = re.sub(r'\n[ \t]*document\.title = CONFIG\.character \+ " COLOR TAP \| CHARAMARL";[^\n]*', '', s)
        if MARK_A in s:
            s = s[:s.index(MARK_A)] + tags + s[s.index(MARK_B) + len(MARK_B):]
        elif re.search(r'<meta property="og:image"', s[:4000]):
            # 手で書いた説明と絵を持っているページ（MOJA）。そちらを残して、title と canonical だけ合わせる
            s = re.sub(r'<meta property="og:title" content="[^"]*">', lambda m: f'<meta property="og:title" content="{esc(title)}">', s, count=1)
            if 'rel="canonical"' not in s[:4000]:
                i = s.index('</title>') + len('</title>')
                s = s[:i] + f'\n<link rel="canonical" href="{url}">' + s[i:]
            os.remove(img)
        else:
            i = s.index('</title>') + len('</title>')
            s = s[:i] + '\n' + tags + s[i:]
        open(page, 'w', encoding='utf-8').write(s)
        print('OK', key, '|', title, '|', desc)
    print(f'{len(titles)} ページに入れました')


if __name__ == '__main__':
    main()
