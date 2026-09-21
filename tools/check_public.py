#!/usr/bin/env python3
"""公開ファイルに、外に出してはいけないものが混ざっていないか調べる。

    python3 tools/check_public.py          # 見つかったら 1 を返す
    python3 tools/check_public.py --staged # git に add したぶんだけ調べる

■ なぜ作ったか
    2026-09-21、characters/pins.html のコメントに、
    作家さんとのやり取りの状態がそのまま書いてあるのが見つかった。
    「morryさんはピンズの案内に未返信」「ちゅいさんの新イラスト・本人が用意中」など。
    HTMLとJSのコメントは View Source で誰でも読める。画面に出ないだけ。
    2026-09-18 の発売から3日間、公開されていた。

    人が気をつける話にしない。**push する前に、これを通す。**

■ 何を見るか
    HTMLコメント（<!-- -->）と、JS/CSS の行コメント（//）とブロックコメント（/* */）だけ。
    本文に書いてある言葉は対象外（作品説明に「待ち」が出ることはある）。
"""
import sys, re, os, glob, subprocess

# 🔴 交渉・検討の状態。作家さんが読んで気持ちのいいものではない
NEGOTIATION = ['未返信', '返事待ち', '承諾待ち', '打診', '交渉', '一任', '渋', '断られ',
               '却下', 'NGだった', 'もめ', 'クレーム', '本人が用意中', '返事が来るまで']
# 🔴 社内の段取り。外から見て意味がないうえ、未公開のものの存在を漏らす
INTERNAL = ['非公開ページ', 'トップ未リンク', '仮ページ', '見せて詰めて', '公開前', 'まだ公開しない',
            '社内', '内緒', '関係者のみ']
# 🔴 出てはいけない値
SECRET = [r'APPLY_KEY\s*=\s*[\'"]', r'sk_live_', r'sk_test_', r'whsec_',
          r'BLOB_READ_WRITE_TOKEN', r'UPSTASH_\w+_TOKEN', r'\?owner=[0-9a-f]{8,}']

# 見ないもの（配らないファイル）
SKIP_DIRS = ('node_modules', '.git', '.vercel', 'tools', 'api')


def comments(text, path):
    """コメントだけを (行番号, 中身) で返す。"""
    out = []
    for m in re.finditer(r'<!--(.*?)(?:-->|$)', text, re.S):
        out.append((text[:m.start()].count('\n') + 1, m.group(1)))
    for m in re.finditer(r'/\*(.*?)(?:\*/|$)', text, re.S):
        out.append((text[:m.start()].count('\n') + 1, m.group(1)))
    for m in re.finditer(r'^[^\S\n]*//(.*)$', text, re.M):
        out.append((text[:m.start()].count('\n') + 1, m.group(1)))
    return out


def targets(staged):
    if staged:
        r = subprocess.run(['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
                           capture_output=True, text=True)
        files = [f for f in r.stdout.split('\n') if f.strip()]
    else:
        files = glob.glob('**/*.html', recursive=True) + glob.glob('**/*.js', recursive=True) \
              + glob.glob('**/*.css', recursive=True)
    return [f for f in files
            if os.path.isfile(f)
            and f.rsplit('.', 1)[-1] in ('html', 'js', 'css')
            and not any(f.startswith(d + '/') or ('/' + d + '/') in f for d in SKIP_DIRS)]


def main():
    staged = '--staged' in sys.argv
    hits = []
    for f in sorted(set(targets(staged))):
        try:
            s = open(f, encoding='utf-8').read()
        except Exception:
            continue
        for pat in SECRET:                      # 本文もコメントも問わず探す
            for m in re.finditer(pat, s):
                hits.append(('鍵', f, s[:m.start()].count('\n') + 1, m.group(0)[:60]))
        for line, body in comments(s, f):
            for w in NEGOTIATION:
                if w in body:
                    hits.append(('やり取り', f, line, body.strip().replace('\n', ' ')[:90]))
                    break
            else:
                for w in INTERNAL:
                    if w in body:
                        hits.append(('社内事情', f, line, body.strip().replace('\n', ' ')[:90]))
                        break

    if not hits:
        print(f'OK  {len(set(targets(staged)))} ファイルを見て、出てはいけないものは見つかりませんでした')
        return 0

    print(f'🔴 {len(hits)} 件あります。push する前に直してください。\n')
    for kind, f, line, body in hits:
        print(f'  [{kind}] {f}:{line}')
        print(f'      {body}')
    print('\n  HTMLとJSのコメントは View Source で誰でも読めます。画面に出ないだけです。')
    print('  作家さんとのやり取りの状態は 01_記録/ 側に書いてください。')
    return 1


if __name__ == '__main__':
    sys.exit(main())
