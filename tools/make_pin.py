#!/usr/bin/env python3
"""ピンズ（直径25mm・金属フレーム＋ドーム加工）のモック画像を作る。

    python3 tools/make_pin.py <透過PNG> <出力名> [--bg=RRGGBB] [--face]

    --face  顔まわりを大きく切り出す（顔アップ版）。既定は全身
    --bg    地の色を指定。省略するとキャラの主要色の補色から自動で決める
    --flat  入稿用（1200×1200・背景は四隅まで・リムとグロスなし）。既定は画面用のモック

■ なぜ補色を自動で選ぶか
    既存のユルクレイジー（黄色いキャラ＋桃色の地）と同じ考え方。
    同系色だとキャラが地に沈み、25mmでは何が描いてあるか分からなくなる。

■ 25mmで見えるかどうかが唯一の基準
    画面では細部まで見えるが、実物は1円玉より少し大きいだけ。
    顔アップ版を必ず一緒に作って、並べて判断する。
"""
import sys, os, colorsys
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

SIZE = 1000
RING = 0.045          # 金属フレームの太さ（直径に対する割合）

# 入稿仕様（~/Downloads/ピンズ入稿/00_入稿ガイド.png を実測した値）
FLAT_SIZE = 1200      # 正方形・PNG または JPG
SAFE = 0.82           # セーフ円の直径比。顔・目・文字はこの内側に入れる
                      # 仕上がりの丸い切り抜きは正方形いっぱい。外周はドームのカーブで歪む


def bbox_alpha(im, thr=12):
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.where(a > thr)
    return xs.min(), ys.min(), xs.max(), ys.max()


def main_hue(im):
    """不透明な画素のうち、彩度のある色から代表の色相を拾う。"""
    a = np.asarray(im.resize((160, 160), Image.LANCZOS)).astype(float) / 255
    rgb, alpha = a[:, :, :3], a[:, :, 3]
    m = alpha > .6
    if not m.any():
        return 0.58
    px = rgb[m]
    hsv = np.array([colorsys.rgb_to_hsv(*p) for p in px])
    vivid = hsv[(hsv[:, 1] > .25) & (hsv[:, 2] > .2)]
    if len(vivid) < 10:
        return 0.58
    # 色相は環状なのでベクトル平均で出す（単純平均だと赤が緑になる）
    ang = vivid[:, 0] * 2 * np.pi
    return (np.arctan2(np.sin(ang).mean(), np.cos(ang).mean()) / (2 * np.pi)) % 1.0


def auto_bg(im):
    h = (main_hue(im) + 0.5) % 1.0          # 補色
    r, g, b = colorsys.hsv_to_rgb(h, 0.34, 0.95)
    return int(r * 255), int(g * 255), int(b * 255)


def dome(base):
    """ドーム加工の見え方。上に寄せた広いハイライトと、下の内側の影。"""
    out = base.copy()
    d = ImageDraw.Draw(out, 'RGBA')
    # 下側の落ち込み
    sh = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([SIZE * .06, SIZE * .18, SIZE * .94, SIZE * 1.06],
                               fill=(20, 14, 30, 60))
    out = Image.alpha_composite(out, sh.filter(ImageFilter.GaussianBlur(SIZE * .07)))
    # 上側のつや
    gl = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(gl).ellipse([SIZE * .13, SIZE * .05, SIZE * .87, SIZE * .52],
                               fill=(255, 255, 255, 96))
    out = Image.alpha_composite(out, gl.filter(ImageFilter.GaussianBlur(SIZE * .055)))
    return out


def ring(img):
    """金属フレーム。単色だと平board に見えるので、明暗を上下でつける。"""
    w = int(SIZE * RING)
    d = ImageDraw.Draw(img, 'RGBA')
    for i in range(w):
        t = i / max(1, w - 1)
        v = int(150 + 85 * (1 - t) ** 1.6)          # 外側ほど明るい
        d.ellipse([i, i, SIZE - 1 - i, SIZE - 1 - i], outline=(v, v, v + 4, 255), width=1)
    d.ellipse([w, w, SIZE - 1 - w, SIZE - 1 - w], outline=(255, 255, 255, 120), width=2)
    return img


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    face = '--face' in sys.argv
    flat = '--flat' in sys.argv
    bgarg = next((a[5:] for a in sys.argv[1:] if a.startswith('--bg=')), None)
    if len(args) < 2:
        raise SystemExit('使い方: python3 tools/make_pin.py <透過PNG> <出力名> [--bg=RRGGBB] [--face]')
    src, out = os.path.expanduser(args[0]), args[1]

    im = Image.open(src).convert('RGBA')
    x0, y0, x1, y1 = bbox_alpha(im)
    im = im.crop((x0, y0, x1 + 1, y1 + 1))

    bg = tuple(int(bgarg[i:i + 2], 16) for i in (0, 2, 4)) if bgarg else auto_bg(im)

    S = FLAT_SIZE if flat else SIZE
    if flat:
        # 背景は四隅まで塗る。白い余白を残すと、そのまま白く印刷される
        canvas = Image.new('RGBA', (S, S), bg + (255,))
    else:
        canvas = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        disc = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(disc).ellipse([0, 0, S - 1, S - 1], fill=bg + (255,))
        canvas = Image.alpha_composite(canvas, disc)

    if face:
        # 頭は上にあるが、耳やしっぽで横幅が出る。上1/3の不透明画素の重心を
        # 中心にして切ると、顔が真ん中に来る。単純に画像の中央で切ると外れる。
        a = np.asarray(im)[:, :, 3]
        h, w = a.shape
        top = a[:max(1, h // 3)]
        cx = int(np.where(top > 12)[1].mean()) if (top > 12).any() else w // 2
        s = min(w, int(h * .62))
        left = min(max(0, cx - s // 2), max(0, w - s))
        im = im.crop((left, 0, left + s, min(h, s)))
        # 入稿ではセーフ円の内側に顔を収める。モックは見栄え優先で少し大きく
        scale = (S * SAFE * 0.98 if flat else S * 0.80) / max(im.size)
    else:
        scale = (S * SAFE * 0.90 if flat else S * 0.74) / max(im.size)

    im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    layer = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    layer.paste(im, ((S - im.width) // 2, (S - im.height) // 2), im)
    canvas = Image.alpha_composite(canvas, layer)

    if flat:
        canvas.convert('RGB').save(out, quality=95)
    else:
        # 円の外をくり抜く（キャラがはみ出しても円に収まる）
        mask = Image.new('L', (S, S), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, S - 1, S - 1], fill=255)
        canvas.putalpha(Image.fromarray(
            np.minimum(np.asarray(canvas)[:, :, 3], np.asarray(mask))))
        ring(dome(canvas)).save(out)
    kind = ('入稿' if flat else 'モック') + '／' + ('顔アップ' if face else '全身')
    print(f'{out}  {S}x{S}  地の色 #{bg[0]:02X}{bg[1]:02X}{bg[2]:02X}  {kind}')


if __name__ == '__main__':
    main()
