# CHARAMARL 開発引き継ぎ

キャラクターIPのセレクトショップ（プレオープン中）。このファイルは別PC・別環境で開発を続けるための引き継ぎメモ。

## URL

| ページ | URL |
|---|---|
| 本番トップ | https://charamarl.vercel.app |
| クリエイター応募 | /apply.html |
| ログイン / マイページ | /login.html → /mypage.html |
| アーティスト用ダッシュボード | /stats.html |
| 応募管理（要キー） | /apply-admin.html?key=APPLY_KEY（キーはVercel環境変数を参照） |

関連リポ: [dinorenny-colortap](https://github.com/recorder11c-cmd/dinorenny-colortap)（COLOR TAP。本番 dinorenny-colortap.vercel.app）

## 技術構成

- **フロント**: 素のHTML/CSS/JS（ビルドなし）。デザイントークンは各ファイルの`:root`（オレンジ#FF8A00 / パープル#A855F7、M PLUS Rounded 1c）
- **API**: `api/*.js` = Vercel Serverless Functions（Node、CommonJS）
  - `api/react.js` — ♥いいね/🔖保存の全体集計（Upstash Redis）
  - `api/apply.js` — クリエイター応募の保存/一覧/削除（GET・DELETEはAPPLY_KEYで保護）
  - `api/auth.js` — 会員登録/ログイン（scryptハッシュ、セッション60日httpOnlyクッキー）、コレクション同期
  - `api/checkout.js` — Stripe Checkout
- **データ**: Upstash Redis（Vercel Storage連携、無料枠）
- **環境変数**（Vercelに設定済み・値はダッシュボード参照）: `KV_REST_API_URL` `KV_REST_API_TOKEN` `STRIPE_PK` `STRIPE_SK` `APPLY_KEY`

## 開発の流れ

```bash
git clone https://github.com/recorder11c-cmd/charamarl.git
cd charamarl
npx serve -l 3002 .        # ローカル確認（APIはローカルでは動かない。フロントのみ）
git push origin main        # → Vercelが自動デプロイ
```

- 自動デプロイが数分たっても反映されない場合（稀にwebhook取りこぼしあり）:
  `npx vercel login`（recorder11cアカウント）→ `npx vercel link` → `npx vercel --prod --yes`
- `vercel env pull`は機密値を空で返すため、Redisの直接操作は不可。データ操作は各APIの管理エンドポイント経由で行う
- APIの動作確認は本番に対してcurlで行う（テストデータは各APIの削除機能で後始末）

## 実装済み機能（2026-07-12時点）

- トップ: ヒーローカルーセル / 注目アーティスト（+Nは実データ自動計算）/ DISCOVER（カテゴリ絞り込み・検索・おすすめ順/人気順ソート）/ アートポップアップ（♥/🔖、サーバー集計）/ TRENDINGランキング（ベース値+実カウントで動的描画）/ 通知ベル（`NEWS`配列にお知らせ追加）/ クリエイター登録CTA
- 会員: ニックネーム+パスワード登録 → ♥/🔖コレクションがアカウント同期（端末間引き継ぎ）→ マイページ
- 決済: Stripe単独（プレ期間中の方針）

## 本稼働前チェックリスト（重要）

1. **Vercel Hobby→Proへ切替**（Hobbyは商用利用が規約違反。$20/月）
2. Stripe Connect化（他アーティスト出店の自動分配）
3. 特定商取引法に基づく表記・プライバシーポリシーのページ追加
4. 独自ドメインの検討
5. Upstash Redis無料枠の使用量確認

## キャラクター・素材

- SUE / PUTTI / MOSSUN = DinoRenny、レコマル(GMC) = MARUさん（準備中扱い・Buyなし）
- ギャラリーアートID: roar / worldcup / 90s / nodino / costume / ahoyoung（`img/gallery/`）
- 作品追加はDISCOVERの`.pin`マークアップ＋`ARTWORKS`(index.html)＋`stats.html`のリストに追記
