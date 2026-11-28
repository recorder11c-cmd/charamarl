#!/usr/bin/env python3
"""グッズを作る前に、作家さんへ見せる「形の案」の絵を作る。

    python3 tools/make_goods_plan.py <設定.json>

絵には手を入れない。やるのは「縮小する」「線と説明を重ねる」「丸く切り取る範囲を示す」だけ。
色・形は変えない。足りない所を描き足さない。

■ アクリルキーホルダー（acrykey）
    透過PNGから、切り抜く線の案と、半透明の所の扱いの案を並べる。
    shape   fit   = 絵のかたちに沿う（くぼみは工具が入る丸みまで埋める）
            round = まるくまとめる（とがった先のあいだも埋める。折れにくい）
    white   all   = 絵のある所すべてに白を敷く（紙に刷ったように色が出る）
            solid = 不透明な所だけ白を敷く（半透明の所はアクリルが透ける）
    市松もようは「透明なアクリル」を表す。色の出方は目安で、実物とは違う。

■ ピンズ（pin）
    絵の上に、丸く切り抜かれる円（赤）と、顔・目を入れる円（緑・直径の82%）を重ねて、
    切り取ったあとの丸を横に並べる。

設定の書き方は、このファイルの末尾の例を見る。
"""
import sys, os, json
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

FONT_B = '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc'
FONT_R = '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
RED, GREEN, INK, SUB = (226, 28, 72), (16, 150, 90), (34, 30, 44), (110, 106, 120)

ART = 1500            # 絵の長い辺をこの画素数に縮めて作業する
MARGIN_MM = 2.5       # 絵の端から切り抜く線までの余白
TAB_R_MM = 3.5        # 金具の穴まわりの出っぱり（半径）
HOLE_R_MM = 1.5       # 金具の穴（半径）
SAFE = 0.82           # ピンズ：顔・目・文字を入れる円（tools/make_pin.py と同じ値）


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def disk(r):
    r = max(1, int(round(r)))
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def checker(w, h, s=26):
    yy, xx = np.mgrid[0:h, 0:w]
    c = ((xx // s + yy // s) % 2).astype(np.float32)
    g = 236 - 22 * c
    return np.dstack([g, g, g])


def acry_panel(src, mm=70, shape='fit', white='all'):
    """アクキー1案ぶんの絵（RGB）と、仕上がりの大きさ（mm）を返す。"""
    im = Image.open(os.path.expanduser(src)).convert('RGBA')
    a0 = np.asarray(im)[:, :, 3]
    ys, xs = np.where(a0 > 20)
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    k = ART / max(im.size)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    ppm = ART / (mm - 2 * MARGIN_MM)                    # 1mm あたりの画素
    pad = int(ppm * (MARGIN_MM + TAB_R_MM * 2 + 16))    # まるめる計算で端に当たらない余白
    W, H = im.width + pad * 2, im.height + pad * 2
    art = np.zeros((H, W, 4), np.float32)
    art[pad:pad + im.height, pad:pad + im.width] = np.asarray(im, np.float32)
    rgb, al = art[:, :, :3], art[:, :, 3] / 255.0

    # 切り抜く形：絵のある所を余白ぶん太らせ、くぼみを埋める
    m = (al > 20 / 255).astype(np.uint8)
    body = cv2.dilate(m, disk(ppm * MARGIN_MM))
    body = cv2.morphologyEx(body, cv2.MORPH_CLOSE, disk(ppm * (3 if shape == 'fit' else 14)))
    cs, _ = cv2.findContours(body, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    body = np.zeros_like(body); cv2.drawContours(body, cs, -1, 1, -1)
    # 金具の穴：形の重心の真上（下げたときに傾きにくい）
    cx = int(np.where(body)[1].mean())
    top = int(np.where(body[:, cx])[0].min())
    tc = (cx, int(top - ppm * 1.0))
    cv2.circle(body, tc, int(ppm * TAB_R_MM), 1, -1)
    body = cv2.morphologyEx(body, cv2.MORPH_CLOSE, disk(ppm * 2.2))
    body = (cv2.GaussianBlur(body.astype(np.float32), (0, 0), ppm * 0.35) > 0.5).astype(np.uint8)
    hole = np.zeros_like(body); cv2.circle(hole, tc, int(ppm * HOLE_R_MM), 1, -1)
    plate = cv2.GaussianBlur((body & (1 - hole)).astype(np.float32), (0, 0), 1.2)[:, :, None]

    # 下地：市松（＝透明）。アクリルの板は、ほんの少し白く見せる
    out = checker(W, H)
    out = out * (1 - 0.30 * plate) + 255 * 0.30 * plate
    # 白を敷く所
    if white == 'all':
        wm = (al > 20 / 255).astype(np.float32)
    else:
        wm = cv2.morphologyEx((al >= 230 / 255).astype(np.uint8), cv2.MORPH_OPEN, disk(2)).astype(np.float32)
    wm = cv2.GaussianBlur(wm, (0, 0), 1.0)[:, :, None]
    on_white = rgb * al[:, :, None] + 255 * (1 - al[:, :, None])      # 白の上に刷った色
    on_clear = rgb * al[:, :, None] + out * (1 - al[:, :, None])      # 透明の上に刷った色
    out = on_white * wm + on_clear * (1 - wm)

    out = np.clip(out, 0, 255).astype(np.uint8)
    for msk in (body, hole):
        cs, _ = cv2.findContours(msk, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.polylines(out, cs, True, RED, 5, cv2.LINE_AA)
    ys, xs = np.where(body)
    size_mm = ((xs.max() - xs.min()) / ppm, (ys.max() - ys.min()) / ppm)
    e = int(ppm * 3)
    box = (max(0, xs.min() - e), max(0, ys.min() - e), min(W, xs.max() + e), min(H, ys.max() + e))
    return Image.fromarray(out).crop(box), size_mm


def sheet(title, panels, notes, out, width=2000):
    """panels = [(絵, 見出し, 説明の行のリスト)]。横に並べて1枚にする。"""
    n, gap, side = len(panels), 50, 70
    pw = (width - side * 2 - gap * (n - 1)) // n
    ims = []
    for im, _, _ in panels:
        k = pw / im.width
        ims.append(im.resize((pw, round(im.height * k)), Image.LANCZOS))
    ph = max(i.height for i in ims)
    f_t, f_h, f_c, f_n = font(52, True), font(40, True), font(30), font(28)
    cap_h = 70 + 44 * max(len(c) for _, _, c in panels)
    top = 150
    H = top + cap_h + ph + 50 + 44 * len(notes) + 60
    S = Image.new('RGB', (width, H), (255, 255, 255))
    d = ImageDraw.Draw(S)
    d.text((side, 56), title, font=f_t, fill=INK)
    for i, (im, (_, head, cap)) in enumerate(zip(ims, panels)):
        x = side + i * (pw + gap)
        d.text((x, top), head, font=f_h, fill=RED)
        for j, line in enumerate(cap):
            d.text((x, top + 62 + 44 * j), line, font=f_c, fill=INK)
        S.paste(im, (x, top + cap_h + (ph - im.height) // 2))
    y = top + cap_h + ph + 50
    for j, line in enumerate(notes):
        d.text((side, y + 44 * j), line, font=f_n, fill=SUB)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    S.save(out, quality=92)
    return S.size


def pin_panel(src, c, view=None):
    """c=(中心x, 中心y, 直径)。絵に円を重ねた図と、切り取ったあとの丸を返す。"""
    im = Image.open(os.path.expanduser(src)).convert('RGB')
    cx, cy, dia = c
    r = dia / 2
    # 切り取ったあとの丸（絵の外に出たぶんは、絵のいちばん近い色ではなく、そのまま「絵が無い」と分かる灰色）
    S = 900
    crop = Image.new('RGB', (dia, dia), (200, 200, 200))
    crop.paste(im, (int(-(cx - r)), int(-(cy - r))))
    crop = crop.resize((S, S), Image.LANCZOS)
    msk = Image.new('L', (S * 2, S * 2), 0)
    ImageDraw.Draw(msk).ellipse([0, 0, S * 2 - 1, S * 2 - 1], fill=255)
    res = Image.new('RGB', (S, S), (255, 255, 255))
    res.paste(crop, (0, 0), msk.resize((S, S), Image.LANCZOS))
    # 絵に円を重ねた図（円の外は少し暗く）
    g = np.asarray(im).astype(np.float32)
    yy, xx = np.mgrid[0:im.height, 0:im.width]
    outside = ((xx - cx) ** 2 + (yy - cy) ** 2 > r * r)[:, :, None]
    g = np.where(outside, g * 0.45 + 255 * 0.12, g).astype(np.uint8).copy()
    cv2.circle(g, (int(cx), int(cy)), int(r), RED, 7, cv2.LINE_AA)
    cv2.circle(g, (int(cx), int(cy)), int(r * SAFE), GREEN, 5, cv2.LINE_AA)
    guide = Image.fromarray(g)
    if view:
        guide = guide.crop(tuple(view))
    return guide, res


def pin_sheet(title, src, rows, notes, out, width=2000):
    """rows = [(見出し, 説明の行, (cx, cy, 直径))]。1案を1段に。"""
    side, gap, top = 70, 60, 150
    f_t, f_h, f_c, f_n = font(52, True), font(40, True), font(30), font(28)
    gh = 860
    blocks = []
    for head, cap, c in rows:
        guide, res = pin_panel(src, c)
        guide = guide.resize((round(guide.width * gh / guide.height), gh), Image.LANCZOS)
        res = res.resize((gh - 120, gh - 120), Image.LANCZOS)
        blocks.append((head, cap, guide, res))
    bh = 70 + 44 * max(len(b[1]) for b in blocks) + gh + 70
    H = top + bh * len(blocks) + 44 * len(notes) + 60
    S = Image.new('RGB', (width, H), (255, 255, 255))
    d = ImageDraw.Draw(S)
    d.text((side, 56), title, font=f_t, fill=INK)
    for i, (head, cap, guide, res) in enumerate(blocks):
        y = top + bh * i
        d.text((side, y), head, font=f_h, fill=RED)
        for j, line in enumerate(cap):
            d.text((side, y + 62 + 44 * j), line, font=f_c, fill=INK)
        y2 = y + 70 + 44 * max(len(b[1]) for b in blocks)
        S.paste(guide, (side, y2))
        x2 = side + guide.width + gap
        d.text((x2, y2 + gh // 2 - 30), '→', font=font(70, True), fill=SUB)
        S.paste(res, (x2 + 130, y2 + 60))
    y = top + bh * len(blocks)
    for j, line in enumerate(notes):
        d.text((side, y + 44 * j), line, font=f_n, fill=SUB)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    S.save(out, quality=92)
    return S.size


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    cfg_path = os.path.expanduser(sys.argv[1])
    cfg = json.load(open(cfg_path, encoding='utf-8'))
    base = os.path.dirname(cfg_path)
    P = lambda p: p if os.path.isabs(os.path.expanduser(p)) else os.path.join(base, p)
    for job in cfg['jobs']:
        out = P(job['out'])
        if job['kind'] == 'acrykey':
            panels = []
            for p in job['panels']:
                im, mmsize = acry_panel(P(job['src']), job.get('mm', 70), p.get('shape', 'fit'), p.get('white', 'all'))
                panels.append((im, p['head'], p.get('cap', [])))
                print('  %s shape=%s white=%s  仕上がり 約%.0f×%.0fmm（穴の出っぱり込み）' % (
                    os.path.basename(out), p.get('shape', 'fit'), p.get('white', 'all'), mmsize[0], mmsize[1]))
            size = sheet(job['title'], panels, job.get('notes', []), out)
        elif job['kind'] == 'pin':
            size = pin_sheet(job['title'], P(job['src']), [(r['head'], r.get('cap', []), tuple(r['c'])) for r in job['rows']],
                             job.get('notes', []), out)
        else:
            raise SystemExit('kind は acrykey か pin: ' + str(job.get('kind')))
        print('OK', out, size)


if __name__ == '__main__':
    main()

# 設定の例（パスは、設定ファイルのある所から見た場所）
# {"jobs": [
#   {"kind": "acrykey", "src": "元データ/a.png", "out": "1_アクキー.jpg", "mm": 70, "title": "…",
#    "panels": [{"head": "案1", "cap": ["…"], "shape": "fit", "white": "all"},
#               {"head": "案2", "cap": ["…"], "shape": "fit", "white": "solid"}],
#    "notes": ["赤い線＝切り抜く形", "…"]},
#   {"kind": "pin", "src": "元データ/a_背景つき.jpg", "out": "3_ピンズ.jpg", "title": "…",
#    "rows": [{"head": "案1 顔アップ", "cap": ["…"], "c": [600, 560, 700]}], "notes": ["…"]}
# ]}
