#!/usr/bin/env python3
"""2026-11-27 の追加ぶんの絵を置く（1回きり。縮小だけ・切らない・色を変えない）。
    python3 tools/canvas_add_20261127.py
・トサカマミ「moni」     → img/canvas/a/tosakamami_moni.jpg（1200px）＋ 一覧用 600px
・DinoRenny「鹿児島」    → img/canvas/dino_kagoshima.jpg（1080px・届いた大きさのまま）＋ 一覧用 600px
characters/canvas.json への1行追加もここで行う（もう在れば何もしない）。"""
import json, os
from PIL import Image
R = '/Users/KCL/Library/Mobile Documents/com~apple~CloudDocs/CHARAMARL/00_受け取り/'

# トサカマミ「moni」
src = Image.open(R + 'charamarl_incoming/tosakamami_moni_ufo_1920.png')
assert src.size == (1920, 1920) and src.getchannel('A').getextrema() == (255, 255), '透明な部分がある'
rgb = src.convert('RGB')
os.makedirs('img/canvas/a', exist_ok=True); os.makedirs('img/t/canvas/a', exist_ok=True)
rgb.resize((1200, 1200), Image.LANCZOS).save('img/canvas/a/tosakamami_moni.jpg', quality=90)
rgb.resize((600, 600), Image.LANCZOS).save('img/t/canvas/a/tosakamami_moni.webp', quality=82)

works = json.load(open('characters/canvas.json', encoding='utf-8'))
if not any(w['key'] == 'tosakamami_moni' for w in works):
    works.append({'no': 'CV30', 'key': 'tosakamami_moni', 'artist': 'トサカマミ', 'slug': 'tosakamami', 'aid': 'tosakamami',
                  'title': 'moni', 'gid': 'g790db8ff45a3',
                  'img': 'img/canvas/a/tosakamami_moni.jpg', 'thumb': 'img/t/canvas/a/tosakamami_moni.webp'})
    open('characters/canvas.json', 'w', encoding='utf-8').write(
        '[\n' + ',\n'.join(' ' + json.dumps(w, ensure_ascii=False) for w in works) + '\n]\n')

# DinoRenny「鹿児島」
k = Image.open(R + '8.png')
assert k.size == (1080, 1080), k.size
k = k.convert('RGB')
k.save('img/canvas/dino_kagoshima.jpg', quality=92)
k.resize((600, 600), Image.LANCZOS).save('img/t/canvas/dino_kagoshima.webp', quality=82)
print(len(works), '点', [w['no'] for w in works][-2:])
