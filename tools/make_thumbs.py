#!/usr/bin/env python3
"""一覧表示用のサムネイル(WebP 600px)を img/t/ に作る。

トップページのピンは画面上240px幅で表示されるのに、元画像は600〜2000pxある。
そのままだと1枚1〜2MBになるので、表示用だけ小さいWebPに差し替える。
元画像は消さない（ライトボックス・商品ページ・印刷用はそのまま使う）。

  python3 tools/make_thumbs.py          # 更新があったものだけ作る
  python3 tools/make_thumbs.py --all    # 全部作り直す
"""
import os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'img', 't')
MAX = 600
QUALITY = 82
# 一覧に出ないもの＝作らない（モックは営業資料用、tは出力先自身）
SKIP_DIRS = {os.path.join('img', 't'), os.path.join('img', 'mock')}
SRC_DIRS = [os.path.join('img'), os.path.join('tap', 'art')]
EXTS = ('.png', '.jpg', '.jpeg')


def sources():
    for base in SRC_DIRS:
        for dirpath, _dirnames, filenames in os.walk(os.path.join(ROOT, base)):
            rel_dir = os.path.relpath(dirpath, ROOT)
            if any(rel_dir == s or rel_dir.startswith(s + os.sep) for s in SKIP_DIRS):
                continue
            for fn in filenames:
                if fn.lower().endswith(EXTS):
                    yield os.path.join(dirpath, fn)


def main():
    force = '--all' in sys.argv
    made = skipped = 0
    saved_before = saved_after = 0
    for src in sorted(sources()):
        rel = os.path.relpath(src, ROOT)
        # img/gallery/x.png -> img/t/gallery/x.webp ／ tap/art/x.png -> img/t/tap/art/x.webp
        key = rel[len('img' + os.sep):] if rel.startswith('img' + os.sep) else rel
        dst = os.path.join(OUT_DIR, os.path.splitext(key)[0] + '.webp')
        if not force and os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
            skipped += 1
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        im = Image.open(src)
        im = im.convert('RGBA') if im.mode in ('RGBA', 'LA', 'P') else im.convert('RGB')
        im.thumbnail((MAX, MAX), Image.LANCZOS)
        im.save(dst, 'WEBP', quality=QUALITY, method=6)
        saved_before += os.path.getsize(src)
        saved_after += os.path.getsize(dst)
        made += 1
    print(f'作成 {made} 件 / 変更なし {skipped} 件')
    if made:
        print(f'{saved_before // 1024:,}KB → {saved_after // 1024:,}KB '
              f'（{100 - saved_after * 100 // saved_before}%減）')


if __name__ == '__main__':
    main()
