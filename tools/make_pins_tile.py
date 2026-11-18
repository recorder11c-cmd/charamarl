# -*- coding: utf-8 -*-
# ピンズ12種を1枚に並べるだけ（絵は加工しない。既存の img/pins/*.png を縮小して置く）
from PIL import Image
SRC = "/Users/KCL/charamarl/img/pins/"
OUT = "/Users/KCL/charamarl/img/t/pins/"
KEYS = ["sue", "mossun", "putti", "yurucrazy", "danna", "inkumo", "mony", "kg_kagechiyo", "kg_kimi", "kg_shigure", "kg_promu", "kg_muchiko"]

def sheet(cols, rows, cell, pin, pad, bg, top=0):
    W, H = cols * cell + pad * 2, rows * cell + pad * 2 + top
    im = Image.new("RGBA", (W, H), bg)
    for i, k in enumerate(KEYS):
        p = Image.open(SRC + k + ".png").convert("RGBA")
        p.thumbnail((pin, pin), Image.LANCZOS)
        x = pad + (i % cols) * cell + (cell - p.width) // 2
        y = top + pad + (i // cols) * cell + (cell - p.height) // 2
        im.alpha_composite(p, (x, y))
    return im

# グッズタブのタイル・NEW DROP の小さい絵（地は生成り）
a = sheet(4, 3, 146, 128, 8, (255, 253, 245, 255), top=92)  # 上は「販売中」の札が重なるので空ける
a.convert("RGB").save(OUT + "pins_all.webp", "WEBP", quality=88)
# HERO の大きい絵（地は透明）
b = sheet(3, 4, 196, 176, 8, (0, 0, 0, 0))  # 縦長（PCで左右の文字とカードに重ならない幅）
b.save(OUT + "pins_all_nobg.webp", "WEBP", quality=90)
print(a.size, b.size)
