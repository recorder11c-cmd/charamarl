#!/usr/bin/env python3
"""
CHARAMARL 週次の作家別集計

前回のベースラインと比べて、作家ごとの送客・♥・保存・作品数の増減を出す。
実行するたびに新しいベースラインを保存するので、毎週同じ形で比較できる。

■ 使い方
    python3 tools/weekly_stats.py          # 集計して差分を表示＋新しいベースラインを保存
    python3 tools/weekly_stats.py --dry    # 表示だけ（保存しない）

■ 保存先
    ~/Downloads/charamarl_baseline_YYYYMMDD.json
    いちばん新しいものを自動で前回分として読む。

■ 何を見るか
  - **送客が最重要**。作家にとっての実利はこれ（自分のショップ/SNSへ何人行ったか）
  - ♥は参考。送客と比例しない（実測で確認済み）
  - **1〜2点の作家が動いているか**を必ず見る。ここが伸びていれば並び順の修正が効いている

■ 注意
  - 作家へ数字を伝えるときは**全部出す。0人なら0人と書く。**ごまかさない
  - 他の作家の数字は出さない（平均と順位までにする）
"""
import json, urllib.request, collections, datetime, glob, os, sys

BASE_DIR = os.path.expanduser('~/Downloads')
API = 'https://charamarl.com/api'

def fetch(url):
    return json.load(urllib.request.urlopen(url))

def collect():
    works = fetch(f'{API}/gallery')['list']
    out = fetch(f'{API}/out?counts=1')
    agg = collections.defaultdict(lambda: {'works': 0, 'likes': 0, 'saves': 0, 'out': 0})
    for w in works:
        a = w.get('artist') or '(不明)'
        agg[a]['works'] += 1
        agg[a]['out'] += int(out.get(w['id']) or 0)
        try:
            r = fetch(f"{API}/react?id={w['id']}")
            agg[a]['likes'] += r.get('likes', 0)
            agg[a]['saves'] += r.get('saves', 0)
        except Exception:
            pass
    return dict(agg)

def latest_baseline():
    files = sorted(glob.glob(f'{BASE_DIR}/charamarl_baseline_*.json'))
    if not files:
        return None, None
    return files[-1], json.load(open(files[-1], encoding='utf-8'))

if __name__ == '__main__':
    dry = '--dry' in sys.argv
    today = datetime.date.today()
    path, prev = latest_baseline()
    cur = collect()

    tot = sum(v['out'] for v in cur.values())
    artists = [a for a in cur if a != 'CHARAMARL']
    print(f'■ {today:%Y-%m-%d} 時点')
    print(f'  作家 {len(artists)}組 / 作品 {sum(v["works"] for v in cur.values())}点')
    print(f'  送客 合計 {tot}人 / 1組あたり平均 {tot/len(artists):.1f}人')

    if prev:
        pb = prev['artists']
        pt = sum(v['out'] for v in pb.values())
        days = (today - datetime.date.fromisoformat(prev['measured_at'])).days
        print(f'\n■ 前回（{prev["measured_at"]} / {days}日前）との差   送客 {pt} → {tot}  ({tot-pt:+d})')
        if days: print(f'  1日あたり {(tot-pt)/days:.1f}人')
        rows = []
        for a, v in cur.items():
            b = pb.get(a)
            if not b: rows.append((v['out'], 0, v['out'], 0, v['works'], a, True)); continue
            rows.append((v['out'] - b['out'], b['out'], v['out'], b['works'], v['works'], a, False))
        rows.sort(key=lambda r: (r[6], r[0]), reverse=True)   # 新規を先頭に、次に増加順
        moved = [r for r in rows if r[0] or r[6]]
        print(f'\n{"差":>4} {"前":>4} {"今":>4} {"点":>4}  作家')
        for d, b, n, wb, wn, a, new in moved:
            tag = ' ★新規' if new else (f'（作品 {wb}→{wn}）' if wn != wb else '')
            print(f'{d:>+4} {b:>4} {n:>4} {wn:>4}  {a}{tag}')
        print(f'\n動いた作家 {len(moved)}組 / {len(rows)}組')
        few = [r for r in moved if r[4] <= 2 and not r[6]]
        print(f'うち作品1〜2点の作家 {len(few)}組  ← ここが動いていれば並び順の修正が効いている')

    if not dry:
        outp = f'{BASE_DIR}/charamarl_baseline_{today:%Y%m%d}.json'
        json.dump({'measured_at': str(today),
                   'note': '週次集計。tools/weekly_stats.py で自動生成。',
                   'artists': cur}, open(outp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'\n保存: {outp}')
    else:
        print('\n(--dry のため保存していません)')
