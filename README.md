# Threads 自動投稿ボット

Claude AI（claude-opus-4-6）がコンテンツを自動生成し、Threads に定期投稿するツールです。

---

## ファイル構成

```
.
├── threads_bot.py        # 投稿のメインロジック
├── content_generator.py  # Claude API でコンテンツ生成
├── scheduler.py          # 定期実行スケジューラー
├── .env.example          # 環境変数テンプレート
├── requirements.txt      # 依存パッケージ
└── README.md             # このファイル
```

---

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. Threads API アクセストークンの取得

#### Step 1: Meta Developer アプリを作成
1. [Meta for Developers](https://developers.facebook.com/) にアクセスしてログイン
2. 「マイアプリ」→「アプリを作成」をクリック
3. 「その他」→「なし」を選択してアプリを作成

#### Step 2: Threads API を有効化
1. アプリダッシュボードの左メニューから「Threads API」を追加
2. 「設定」→「基本設定」でアプリ ID とアプリシークレットを控えておく

#### Step 3: 短期アクセストークンを取得
ブラウザで以下の URL にアクセスし、アカウントを認証します（`{APP_ID}` と `{REDIRECT_URI}` を置き換えてください）:

```
https://threads.net/oauth/authorize
  ?client_id={APP_ID}
  &redirect_uri={REDIRECT_URI}
  &scope=threads_basic,threads_content_publish
  &response_type=code
```

認証後にリダイレクトされた URL から `code=` の値をコピーし、以下のリクエストでトークンと交換します:

```bash
curl -X POST "https://graph.threads.net/oauth/access_token" \
  -d "client_id={APP_ID}" \
  -d "client_secret={APP_SECRET}" \
  -d "grant_type=authorization_code" \
  -d "redirect_uri={REDIRECT_URI}" \
  -d "code={CODE}"
```

#### Step 4: 長期トークンに交換（60日有効）

```bash
curl "https://graph.threads.net/access_token
  ?grant_type=th_exchange_token
  &client_secret={APP_SECRET}
  &access_token={SHORT_LIVED_TOKEN}"
```

レスポンスの `access_token` を控えておきます。

#### Step 5: ユーザー ID を取得

```bash
curl "https://graph.threads.net/v1.0/me?fields=id,username&access_token={ACCESS_TOKEN}"
```

レスポンスの `id` がユーザー ID です。

---

### 3. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を編集して取得した値を設定します:

```
THREADS_ACCESS_TOKEN=取得した長期トークン
THREADS_USER_ID=取得したユーザーID
ANTHROPIC_API_KEY=AnthropicのAPIキー
POST_TOPIC=テクノロジー
POST_TONE=カジュアル
POST_INTERVAL_HOURS=6
```

---

## 使い方

### API 接続テスト（投稿しない）

```bash
python threads_bot.py --test
```

### 1回だけ投稿（動作確認）

```bash
python threads_bot.py
```

### 内容確認のみ（実際には投稿しない）

```bash
python threads_bot.py --dry-run
```

### 定期投稿を開始

```bash
python scheduler.py
```

起動直後に1回投稿し、その後 `POST_INTERVAL_HOURS` の間隔で自動投稿し続けます。

---

## 注意事項

- Threads API の投稿レート制限: **1日250件** まで
- アクセストークンは60日で失効します。失効前に再取得が必要です
- `.env` ファイルは絶対に Git にコミットしないでください
