#!/usr/bin/env python3
"""NFCアクキーから来た人が RUN の★オーナーモードへ行けるようにする。

    python3 tools/patch_tap_runowner.py          # 当てる
    python3 tools/patch_tap_runowner.py --check  # 当たるかだけ見る（書かない）

■ なぜ要るか（2026-09-22）
    ユーザーがユルクレイジーのアクキーで実機確認して見つけた。
    「読み込み先のページに run へのリンクがない」

    経路を追うとこうなっていた。

        アクキーのタグ → /n/yurucrazy → /tap/yurucrazy.html?nfc=1
                                          ボタンは3つだけ
                                          （作家さんのSNS / グッズ / ほかのキャラ）
                                          RUN へのリンクが無い

    ★オーナーモードが開く唯一の入口は run.html?owner=<トークン> で、
    トークンを付けていたのは**旧ルートの /api/go?c= のほう**だった。
    実際に出回っているタグは /n/ のほう（スキャン54回 対 15回）なので、
    **かざしてもオーナーモードにならない状態が続いていた。**

    公式Xの発表文と、9/21に作家さん9名へ送った案内は
    「アクキーをかざして開くと、そのキャラで二段ジャンプができ」と書いてある。
    実装をこちらに合わせる。

■ 何をするか
    ① api/n.js が行き先に &owner=<トークン> を足す（このファイルの対象外・手で直す）
    ② TAPページに、owner が付いているときだけ出るボタンを足す（ここ）

    トークンはここでは検証しない。検証は run-score.js が記録の登録時にやるので、
    偽のトークンでは★オーナーの順位表に入らない。

■ 対象
    RUN にキャラがいて、かつ TAP ページがあるものだけ。
    ⚠️ PUTTI と MOSSUN はアクキーがあるが RUN にキャラがいない → ボタンを出さない。
    ⚠️ だんなは /n/danna が characters/danna.html へ行く。あちらは既に実装済みなので触らない。

■ トークンが外に出ないこと
    TAPのシェアは location.origin + location.pathname だけを使っていて
    クエリを捨てているので、?owner= がXやLINEに流れることはない。
"""
import sys, os, re, glob

# RUN にいるキャラ（run.html の CHARS のキー）∩ tap/*.html
TARGETS = ['sue', 'gmc', 'ufoo', 'kagechiyo', 'yurucrazy',
           'dogooooo', 'inkumo', 'blockma', 'mony']

CSS = """  .runbtn {
    pointer-events:auto; display:none; margin-top:14px;
    background:linear-gradient(135deg,#FFE27A,#E0A800); color:#111; font-weight:900;
    text-decoration:none; padding:14px 28px; border-radius:30px;
    font-size:clamp(14px,3.5vmin,18px); box-shadow:0 6px 0 rgba(0,0,0,.25);
    transition:transform .12s;
  }
  .runbtn.on { display:inline-block; }
  .runbtn:active { transform:scale(.96); }
"""

BTN = ('    <a class="runbtn" id="runOwner" href="#" rel="noopener">'
       '🎮 RUN で走る（★オーナー特典つき）</a>\n')

JS = """<script>
// NFCアクキーから来た人だけ、RUNの★オーナーモードへ行けるボタンを出す。
// トークンは /n/<キー> のリダイレクト（api/n.js）が付ける。ここでは検証しない。
// 検証は run-score.js が記録の登録時にやるので、偽のトークンでは順位表に入らない。
// ⚠️ シェアのURLは location.pathname だけを使っているので、トークンは外に出ない。
(function(){
  var o = new URLSearchParams(location.search).get("owner");
  var a = document.getElementById("runOwner");
  if(!o || !a) return;
  var key = (location.pathname.split("/").pop() || "").replace(/\\.html$/, "");
  if(!key) return;
  a.href = "/run.html?char=" + encodeURIComponent(key)
         + "&owner=" + encodeURIComponent(o) + "&utm_source=nfc";
  a.classList.add("on");
  a.addEventListener("pointerdown", function(e){ e.stopPropagation(); });
  a.addEventListener("click", function(){
    if(window.cmEvent) cmEvent("tap_run_owner", { character: key });
  });
})();
</script>
"""


def patch(path):
    s = open(path, encoding='utf-8').read()
    if 'id="runOwner"' in s:
        return None                                  # すでに当たっている
    out = s

    # ① CSS を .buy:active の直後に入れる
    m = re.search(r'^  \.buy:active \{[^\n]*\n', out, re.M)
    if not m:
        return f'✗ {path}: .buy:active が見つからない'
    out = out[:m.end()] + CSS + out[m.end():]

    # ② ボタンを .buy のアンカーの直後に入れる
    m = re.search(r'^    <a class="buy" id="buy"[^\n]*\n', out, re.M)
    if not m:
        return f'✗ {path}: .buy のアンカーが見つからない'
    out = out[:m.end()] + BTN + out[m.end():]

    # ③ スクリプトを </body> の直前に入れる
    m = re.search(r'\n</body>', out)
    if not m:
        return f'✗ {path}: </body> が見つからない'
    out = out[:m.start()] + '\n' + JS + out[m.start():]

    return ('OK', path, out)


def main():
    check = '--check' in sys.argv
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    done, skip, err = [], [], []
    for k in TARGETS:
        p = f'tap/{k}.html'
        if not os.path.exists(p):
            err.append(f'✗ {p}: ファイルが無い')
            continue
        r = patch(p)
        if r is None:
            skip.append(p)
        elif isinstance(r, str):
            err.append(r)
        else:
            done.append(p)
            if not check:
                open(p, 'w', encoding='utf-8').write(r[2])

    print(f'当てた {len(done)} ／ すでに当たっていた {len(skip)} ／ 失敗 {len(err)}')
    for p in done:
        print(f'  ✓ {p}')
    for p in skip:
        print(f'  - {p}（そのまま）')
    for e in err:
        print(f'  {e}')
    if check:
        print('※ --check なので書いていません')
    print('\n⚠️ PUTTI と MOSSUN はアクキーがあるが RUN にキャラがいないので対象外。')
    print('⚠️ だんなは /n/danna が characters/danna.html へ行く（あちらは実装済み）。')
    return 1 if err else 0


if __name__ == '__main__':
    sys.exit(main())
