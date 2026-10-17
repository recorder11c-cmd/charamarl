#!/usr/bin/env python3
"""受け取った画像のうち、まだ作品として登録されていないものを洗い出す（取りこぼし防止）

    python3 tools/pending_check.py              # 2026-08-01以降に受け取った画像
    python3 tools/pending_check.py --since 2026-10-01
    python3 tools/pending_check.py --all        # 登録済みと一致したものも表示

■ なぜ作るか
    2026-10-16、Fzさんの2点（Please, KING SIZE／TOO MUCH TEQUILA）が、受け取ってから約1か月
    登録されないままだった。「週1で出す」という計画はメモにだけあり、サイトには何も入っていなかった。
    画像は受け取りフォルダ（fz2.jpg／fz3.jpg）に入っていたのに、探し方が悪くて見つけられなかった。

■ 何を見るか
    ① 受け取りフォルダの画像（jpg/png/webp）を、公開中・承認済み・予約中の全作品の画像と
       見た目の近さ（dHash）で突き合わせる。**一致しない画像＝未登録の疑い**
    ② 予約公開の一覧（いつ・どの作品が出るか）
    ③ 承認待ち・却下の作品
    🔴 対象外にしてよい画像（スクショ・チラシ・作品でないもの）は
       `01_記録/掲載台帳_対象外.txt` に1行1ファイル名（先頭一致）で書く。**書いたら、その理由も1行添える**

■ 使う場面
    ・毎朝の定例（「おはよう」）で1回
    ・画像を受け取ったとき（保存した直後）
    ・「週1で出す」のような計画を立てたとき → **その場で全部を登録し、予約公開（publishAt）まで入れる**。
       計画をメモにだけ書かない。

■ 管理キー
    ~/.charamarl_admin_key（X-Admin-Key ヘッダー）。値は表示しない。
"""
import sys, os, io, json, glob, datetime, unicodedata, urllib.request
from PIL import Image

API = 'https://charamarl.com/api/gallery?status=all'
INCOMING = os.path.expanduser('~/Downloads/CHARAMARL/00_受け取り/charamarl_incoming')
IGNORE = os.path.expanduser('~/Downloads/CHARAMARL/01_記録/掲載台帳_対象外.txt')
CACHE = os.path.expanduser('~/.cache/charamarl_pending_hash.json')
EXT = ('.jpg', '.jpeg', '.png', '.webp')
HAMMING_MAX = 14   # 64bit中、これ以下なら同じ絵とみなす


def admin_key():
    k = os.environ.get('CHARAMARL_KEY')
    if k:
        return k
    try:
        return open(os.path.expanduser('~/.charamarl_admin_key'), encoding='utf-8').readline().strip()
    except OSError:
        raise SystemExit('管理キーが見つからない（~/.charamarl_admin_key）')


def dhash(im):
    im = im.convert('L').resize((9, 8), Image.LANCZOS)
    px = list(im.getdata())
    bits = 0
    for r in range(8):
        for c in range(8):
            bits = (bits << 1) | (1 if px[r * 9 + c] > px[r * 9 + c + 1] else 0)
    return bits


def ham(a, b):
    return bin(a ^ b).count('1')


def load_cache():
    try:
        return json.load(open(CACHE))
    except Exception:
        return {}


def save_cache(c):
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(c, open(CACHE, 'w'))


def fetch_gallery():
    req = urllib.request.Request(API, headers={'X-Admin-Key': admin_key(), 'User-Agent': 'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=60))['list']


def gallery_hashes(works, cache):
    out = {}
    for w in works:
        k = 'g:' + w['id'] + ':' + str(w.get('edited') or w.get('ts'))
        if k not in cache:
            try:
                data = urllib.request.urlopen(urllib.request.Request(w['img'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read()
                cache[k] = dhash(Image.open(io.BytesIO(data)))
            except Exception:
                continue
        out[w['id']] = cache[k]
    return out


def ignored(name, rules):
    # 濁点などの表記ゆれ（NFC/NFD）で取りこぼさない
    n = unicodedata.normalize('NFC', name)
    return any(n.startswith(unicodedata.normalize('NFC', r)) for r in rules)


def main():
    since = datetime.datetime(2026, 8, 1)
    show_all = '--all' in sys.argv
    if '--since' in sys.argv:
        since = datetime.datetime.strptime(sys.argv[sys.argv.index('--since') + 1], '%Y-%m-%d')
    rules = []
    if os.path.exists(IGNORE):
        for ln in open(IGNORE, encoding='utf-8'):
            ln = ln.split('#')[0].strip()
            if ln:
                rules.append(ln)

    works = fetch_gallery()
    cache = load_cache()
    gh = gallery_hashes(works, cache)
    now = datetime.datetime.now().timestamp() * 1000

    # ① 受け取り画像と作品の突き合わせ
    unmatched, matched = [], []
    for f in sorted(glob.glob(os.path.join(INCOMING, '*'))):
        name = os.path.basename(f)
        if not name.lower().endswith(EXT):
            continue
        mt = datetime.datetime.fromtimestamp(os.path.getmtime(f))
        if mt < since or ignored(name, rules):
            continue
        k = 'f:' + name + ':' + str(int(os.path.getmtime(f)))
        if k not in cache:
            try:
                cache[k] = dhash(Image.open(f))
            except Exception:
                continue
        h = cache[k]
        best = min(((ham(h, v), wid) for wid, v in gh.items()), default=(99, None))
        (matched if best[0] <= HAMMING_MAX else unmatched).append((name, mt, best))
    save_cache(cache)

    byid = {w['id']: w for w in works}
    print(f'■ ① 未登録の疑い（受け取り画像のうち、どの作品とも一致しない）: {len(unmatched)} 枚')
    for name, mt, best in unmatched:
        near = byid.get(best[1], {})
        print(f'   {mt:%m/%d} {name}   (いちばん近い作品: {near.get("artist","-")} 「{(near.get("title") or "")[:14]}」 差{best[0]})')
    if show_all:
        print(f'■ 登録済みと一致: {len(matched)} 枚')
        for name, mt, best in matched:
            w = byid.get(best[1], {})
            print(f'   {mt:%m/%d} {name} → {w.get("artist")} 「{(w.get("title") or "")[:16]}」')

    # ② 予約公開
    sched = sorted([w for w in works if w.get('status') == 'approved' and (w.get('publishAt') or 0) > now], key=lambda w: w['publishAt'])
    print(f'\n■ ② 予約公開（これから出る）: {len(sched)} 点')
    for w in sched:
        print('   {} {} 「{}」'.format(datetime.datetime.fromtimestamp(w['publishAt'] / 1000).strftime('%m/%d(%a) %H:%M'), w['artist'], w['title'][:20]))

    # ③ 承認待ち・却下
    waiting = [w for w in works if w.get('status') not in ('approved',)]
    print(f'\n■ ③ 承認待ち・却下: {len(waiting)} 点')
    for w in waiting:
        print('   [{}] {} 「{}」 {}'.format(w.get('status'), w['artist'], w['title'][:20], w['id']))

    # ④ 台帳の保留（未登録のまま止まっているもの）
    ledger = os.path.expanduser('~/Downloads/CHARAMARL/01_記録/掲載予定台帳.md')
    if os.path.exists(ledger):
        rows = [ln for ln in open(ledger, encoding='utf-8') if ln.startswith('## B.')]
        text = open(ledger, encoding='utf-8').read()
        b = text.split('## B.')[1].split('## C.')[0] if '## B.' in text else ''
        held = [ln for ln in b.split('\n') if ln.startswith('| ') and not ln.startswith('| 作家') and not ln.startswith('|---')]
        print(f'\n■ ④ 台帳の保留（受け取り済みで未登録）: {len(held)} 件   ← 掲載予定台帳.md の B')
        for ln in held:
            c = [x.strip() for x in ln.strip('|\n').split('|')]
            print('   {} / {} … {}'.format(c[0], c[1][:26], c[2][:40]))
        d = text.split('## D.')[1].split('\n## ')[0] if '## D.' in text else ''
        dl = [ln for ln in d.split('\n') if ln.startswith('- ') and '（なし）' not in ln]
        print(f'■ ⑤ 計画だけで未登録: {len(dl)} 件（0件が正常）')
        for ln in dl:
            print('   ' + ln[:80])

    print('\n※ 対象外にしてよい画像は 01_記録/掲載台帳_対象外.txt（理由を1行添える）。作品なら、その場で登録＋予約公開まで入れる。')


if __name__ == '__main__':
    main()
