#!/usr/bin/env python3
"""CHARAMARL RUN 週間ランキングのカード画像を作る（1200×1200・Xにそのまま貼れる）

    python3 tools/make_rank.py --week=last [出力先] [--title=先週の1位]

    例) python3 tools/make_rank.py --week=last ~/Downloads/CHARAMARL/03_画像/charamarl_run_rank

■ なぜ画像を作るか
    この投稿の中身は「数字」なのに、run.html のリンクカード（og_run.png）は
    数字をひとつも見せない。しかも同じ絵が公開告知で何度も流れている。
    順位表そのものを画像にすれば、タップしなくても10キャラ分が読めて、
    自分の名前を見つけた人が反応できる。

■ 毎週月曜の定例向け
    差し替わるのは数字と名前だけ。--week を変えれば同じ体裁で出る。

■ 名前の扱い
    🔴 ランキング名は自己申告。画像にもそのまま載せるが、
    「◯◯さん（本人）」と断定する文言は入れない。@ も付けない。
"""
import sys, os, json, html, subprocess, urllib.request
from datetime import date, timedelta
from PIL import Image

KEY = os.environ.get('CHARAMARL_KEY', 'f51472ede46274ebf97b56d0')
API = 'https://charamarl.com/api/run-score'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
W, H = 1200, 1200
OUT_DEFAULT = os.path.expanduser('~/Downloads/CHARAMARL/03_画像/charamarl_run_rank')

# run.html の CHARS と同じ並び・同じ表記
CHARS = [('SUE', 'SUE'), ('GMC', 'レコマル'), ('UFOO', 'う〜ほ〜'), ('KAGECHIYO', 'カゲチヨ'),
         ('YURUCRAZY', 'ユルクレイジー'), ('DOGOOOOO', 'ドグー'), ('INKUMO', 'インクモ'),
         ('DANNA', 'だんな'), ('BLOCKMA', 'ぶろっくま'), ('MONY', 'モニィ')]


def top1(cid, week):
    """そのキャラの、その週の1位を返す。登録が無ければ None。"""
    url = f'{API}?week={week}&key={KEY}&char={cid}'
    try:
        d = json.load(urllib.request.urlopen(url))
    except Exception:
        return None
    rows = d.get('top') or d.get('list') or []
    return rows[0] if rows else None


def week_label(week):
    """見出しに出す期間。week=last は先週の月〜日。"""
    if week != 'last':
        return week
    today = date.today()
    mon = today - timedelta(days=today.weekday())       # 今週の月曜
    s, e = mon - timedelta(days=7), mon - timedelta(days=1)
    return f'{s.month}/{s.day}〜{e.month}/{e.day}'


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    week = next((a[7:] for a in sys.argv[1:] if a.startswith('--week=')), 'last')
    title = next((a[8:] for a in sys.argv[1:] if a.startswith('--title=')), '先週の1位')
    outdir = os.path.expanduser(args[0]) if args else OUT_DEFAULT

    rows = []
    for cid, jp in CHARS:
        t = top1(cid, week)
        rows.append((jp, (t or {}).get('name'), (t or {}).get('score')))

    scored = [r for r in rows if r[2] is not None]
    best = max(scored, key=lambda r: r[2]) if scored else None

    tr = ''
    for jp, name, score in rows:
        if score is None:
            tr += (f'<tr class="none"><td class="c">{html.escape(jp)}</td>'
                   f'<td class="n" colspan="2">まだ登録がありません</td></tr>')
            continue
        crown = ' top' if best and (jp, name, score) == best else ''
        tr += (f'<tr class="{crown.strip()}"><td class="c">{html.escape(jp)}</td>'
               f'<td class="n">{html.escape(str(name))}</td>'
               f'<td class="s">{score:,}</td></tr>')

    doc = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:#18171D;
 font-family:"Hiragino Sans","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif}}
.stripe{{height:8px;background:linear-gradient(90deg,#FF8A00 0%,#FF4D8D 52%,#8E4ED9 100%)}}
.wrap{{padding:44px 56px 0}}
h1{{color:#fff;font-size:52px;font-weight:800;letter-spacing:.01em}}
h1 b{{color:#FFD400}}
.sub{{color:#9B96A6;font-size:26px;font-weight:600;margin-top:10px}}
table{{width:100%;border-collapse:collapse;margin-top:30px}}
td{{padding:15px 0;border-bottom:1px solid #2C2A34;font-variant-numeric:tabular-nums}}
.c{{color:#fff;font-size:33px;font-weight:700;width:38%}}
.n{{color:#CFC9DA;font-size:30px;font-weight:600}}
.s{{color:#fff;font-size:34px;font-weight:800;text-align:right;width:24%}}
tr.top .c,tr.top .n,tr.top .s{{color:#FFD400}}
tr.none .n{{color:#6E687C;font-size:24px;font-weight:600}}
tr.none .c{{color:#6E687C}}
.foot{{position:absolute;left:56px;right:56px;bottom:34px;display:flex;
 align-items:baseline;gap:18px}}
.foot .m{{color:#9B96A6;font-size:24px;font-weight:600;flex:1}}
.foot .u{{color:#8E8998;font-size:24px;font-weight:700;letter-spacing:.02em}}
</style></head><body>
<div class="stripe"></div>
<div class="wrap">
  <h1>CHARAMARL <b>RUN</b></h1>
  <div class="sub">{html.escape(title)}　{week_label(week)}</div>
  <table>{tr}</table>
</div>
<div class="foot">
  <div class="m">月曜0時にリセット。今週の1位はまだ空いています</div>
  <div class="u">charamarl.com/run.html</div>
</div>
</body></html>'''

    os.makedirs(outdir, exist_ok=True)
    base = os.path.join(outdir, f'run_rank_{date.today():%Y%m%d}')
    tmp = base + '.html'
    open(tmp, 'w', encoding='utf-8').write(doc)
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars',
                    '--force-device-scale-factor=1', f'--window-size={W},{H}',
                    '--virtual-time-budget=8000', f'--screenshot={base}.png', tmp],
                   check=True, capture_output=True)
    Image.open(base + '.png').convert('RGB').save(base + '.jpg', quality=92, optimize=True)
    os.remove(base + '.png'); os.remove(tmp)
    print(f'{base}.jpg')
    for jp, name, score in rows:
        print(f'  {jp:<12}{(name or "—"):<16}{("" if score is None else f"{score:,}"):>9}')


if __name__ == '__main__':
    main()
