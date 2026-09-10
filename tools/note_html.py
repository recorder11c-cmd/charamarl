#!/usr/bin/env python3
"""
note 貼り付け用HTMLを作る

note の編集画面は「リッチテキストの貼り付け」に対応している。
見出し・引用・画像を含んだHTMLをブラウザで開いて ⌘A → ⌘C → note に ⌘V すると、
書式を保ったまま入る。noteの画面で見出しを付け直す作業が要らなくなる。

■ 使い方
    python3 tools/note_html.py 原稿.md 出力.html

■ 原稿の書き方（Markdownの一部だけ使う）
    ## 見出し           → <h2>
    > 引用              → <blockquote>（連続行はひとつの引用にまとまる）
    [[img:パス]]        → <img>（画像はbase64で埋め込むので単体で完結する）
    それ以外の行        → <p>
    空行                → 段落の区切り
    ---                 → 無視（原稿の区切り用）

■ 注意
  - **タイトルは原稿に入れない。**note のタイトル欄に別途入れる
  - 画像が貼り付けで落ちることがある。その場合は本文だけ貼って画像は手で入れる
  - 貼ったあと note 側で直すこと:
      ・引用の「出典を入力」は空欄でよい（本人インタビューなので出典なし）
      ・画像のクレジットが「CHARAMARLより」になっていたら **作家名に直す**
        （他作家の作品に自社名が付いたままになるのを防ぐ）
"""
import sys, os, base64, html, re

def img_tag(path):
    p = os.path.expanduser(path.strip())
    if not os.path.exists(p):
        raise SystemExit(f'画像が見つかりません: {p}')
    ext = 'png' if p.lower().endswith('.png') else 'jpeg'
    b64 = base64.b64encode(open(p, 'rb').read()).decode()
    alt = html.escape(os.path.basename(p))
    return f'<img src="data:image/{ext};base64,{b64}" alt="{alt}">'

def linkify(s):
    return re.sub(r'(https?://[^\s<）」]+)', r'<a href="\1">\1</a>', s)

def convert(md):
    out, quote, para = [], [], []
    def flush_para():
        if para:
            out.append('<p>' + '<br>'.join(linkify(html.escape(x)) for x in para) + '</p>')
            para.clear()
    def flush_quote():
        if quote:
            inner = ''.join(f'<p>{linkify(html.escape(x))}</p>' for x in quote)
            out.append(f'<blockquote>{inner}</blockquote>')
            quote.clear()
    for raw in md.split('\n'):
        line = raw.rstrip()
        if line.strip() in ('---', ''):
            flush_quote(); flush_para(); continue
        m = re.match(r'\[\[img:(.+?)\]\]', line.strip())
        if m:
            flush_quote(); flush_para(); out.append(img_tag(m.group(1))); continue
        if line.startswith('## '):
            flush_quote(); flush_para(); out.append(f'<h2>{html.escape(line[3:].strip())}</h2>'); continue
        if line.startswith('> '):
            flush_para(); quote.append(line[2:].strip()); continue
        flush_quote(); para.append(line.strip())
    flush_quote(); flush_para()
    return '\n'.join(out)

CSS = """body{font-family:"Hiragino Sans","Yu Gothic",sans-serif;max-width:660px;margin:0 auto;
 padding:28px 22px 80px;line-height:1.9;color:#1a1a1a;font-size:16px;}
h2{font-size:22px;font-weight:800;margin:44px 0 14px;line-height:1.5;}
p{margin:0 0 22px;}
blockquote{margin:0 0 22px;padding:2px 0 2px 18px;border-left:4px solid #ccc;color:#444;}
blockquote p{margin:0 0 6px;}
img{width:100%;height:auto;display:block;margin:26px 0;}
a{color:#0a66c2;}"""

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('使い方: python3 tools/note_html.py 原稿.md 出力.html')
    src, dst = sys.argv[1], os.path.expanduser(sys.argv[2])
    body = convert(open(os.path.expanduser(src), encoding='utf-8').read())
    open(dst, 'w', encoding='utf-8').write(
        f'<!doctype html><html lang="ja"><head><meta charset="utf-8">'
        f'<title>note 貼り付け用</title><style>{CSS}</style></head><body>\n{body}\n</body></html>')
    print(f'{dst}  {round(os.path.getsize(dst)/1024)} KB')
    print('→ ブラウザで開いて ⌘A → ⌘C → note に ⌘V')
