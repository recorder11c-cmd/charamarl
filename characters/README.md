# 商品（キャラ）ページの作り方・更新方法

商品ページは **`characters/characters.json` を編集 → ビルド** で生成します。
HTMLを直接いじる必要はありません。

## 1. 設定を編集

`characters/characters.json` の `characters` 配列に、キャラごとの設定を書きます。

| 項目 | 内容 | 例 |
|------|------|-----|
| `id` | ファイル名・画像名のキー | `"sue"` → `characters/sue.html` / `img/colors_nobg/sue_*.png` |
| `name` | **商品名**（表示名） | `"SUE"` |
| `creator` | **by** の後ろ（作者） | `"DinoRenny (@dino_renny)"` |
| `tags` | タグ配列 | `["DinoRenny","アクキー","50mm","両面印刷"]` |
| `desc` | **詳細**文（`<br>`で改行可） | `"ライブドローイングから…<br>6色展開…"` |
| `productLabel` | 下部バーの商品名 | `"SUE アクリルキーホルダー 50mm"` |
| `price` | 価格（数値） | `1200` |
| `colortap` | COLOR TAP のURL | `"https://dinorenny-colortap.vercel.app/sue.html"` |

> **商品画像**は `id` から自動参照されます（`img/colors_nobg/<id>_<色>.png`）。
> 画像は別途 `recolor_character.py`（dinorenny-colortapリポジトリ）で6色生成して
> `img/colors_nobg/` に置いてください。

## 2. ビルド（生成）

```bash
python3 tools/build_characters.py
```

→ `characters/<id>.html` が全キャラ分、再生成されます。
（既存ページは上書き。常に characters.json が正＝単一の情報源）

## 3. 新キャラを追加する手順まとめ

1. 画像を用意：`recolor_character.py` で6色生成 → `img/colors_nobg/<id>_*.png`
2. `characters.json` に1ブロック追記（id / name / creator / desc など）
3. `python3 tools/build_characters.py` 実行
4. トップ（`index.html`）のフィードに載せる場合は、index 側の商品ピンも追加（別管理）
5. commit & push → Vercel自動デプロイ

---

※ 生成ページには「6色カラー選択・カート・今すぐ購入・COLOR TAPリンク」が
　自動で入ります（テンプレートは `tools/build_characters.py` 内）。
