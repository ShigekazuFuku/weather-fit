# 📝 WeatherFit 開発作業ログ

## 📅 2026-09-28 (作業日 #1)

### 🎯 今日のゴール
- 開発環境の確認と計画書の作成
- Step 1: Gemini API との疎通確認・服の画像認識テスト
- Step 2: 無料天気API（Open-Meteo）による気象データ取得テスト
- Git環境の整備（安全対策）と GitHub `dev` ブランチへのプッシュ

---

### 🛠️ 実施したこと

#### 1. 開発計画の策定
- 初心者でも挫折せず動くものを最速で作るため、5つのステップに分割したロードマップを作成。
- [PROJECT_PLAN.md](PROJECT_PLAN.md) に計画を整理。

#### 2. Step 1: Gemini API 疎通 & 服の画像認識
- **環境確認**: `google-genai` (v2.25.0), `pillow`, `python-dotenv` の導入確認。
- **疎通テスト ([step1_test.py](step1_test.py))**:
  - 推奨モデル `gemini-3.8-flash` を使用し、AIからの挨拶メッセージ取得に成功。
- **画像認識テスト ([step1_image_test.py](step1_image_test.py))**:
  - `images/sample.jpg`（ネイビーの半袖ボタンダウンシャツ）を読み込ませて分析を実行。
  - **認識結果**:
    - 種類: 半袖ボタンダウンシャツ
    - 色: ネイビー（無地）
    - 特徴: ボタンダウンカラー、胸ポケット、ホワイトボタン、オックスフォード系
    - 適した季節・気温: 初夏〜夏（23℃〜30℃以上）
    - コーディネート提案: グレースラックスやベージュチノ、白インナー羽織りなど

#### 3. Step 2: 天気データの取得
- **スクリプト作成 ([step2_weather_test.py](step2_weather_test.py))**:
  - 登録不要・無料で使える Open-Meteo API を利用。
  - 今日の東京の「天候・現在気温・最高/最低気温・湿度・降水確率」のリアルタイム取得に成功。

#### 4. Git 環境の整備 & GitHub へのプッシュ
- **セキュリティ対策**:
  - 設定が書かれた `.env` や仮想環境 `venv/` を除外する [.gitignore](.gitignore) を作成。
  - テンプレート用の [.env.example](.env.example) を用意。
- **Git 操作**:
  - 開発用ブランチ `dev` を作成。
  - コミット: `feat: Step 1 (Gemini API/画像認識) および Step 2 (天気情報取得) のテストスクリプトを実装` (`ebf733d`)
  - リモートリポジトリ（`https://github.com/ShigekazuFuku/weather-fit.git`）の `dev` ブランチへ Push 完了。

---

## 📅 2026-10-04 (作業日 #2)

- [app.py](app.py)（Streamlit）を作成。Step 3 と Step 4 をまとめて実装:
  - 服の写真を複数アップロード → `closet/` フォルダに保存（`.gitignore` 済み）
  - 地域を選んで Open-Meteo から天気取得（step2 の関数を再利用）
  - 全ての服の画像 + 天気を Gemini に渡して服装を提案
- [requirements.txt](requirements.txt) を追加。
- ⚠️ 未検証: この環境に streamlit 未インストールのため構文チェックのみ。実機で要動作確認。
- 実行方法: `pip install -r requirements.txt` → `streamlit run app.py`
- ✅ 動作確認済み（Vertex AI 経由で服装提案が表示されることを確認）。

#### Gemini の呼び出しを AI Studio から Vertex AI（Google Cloud）へ変更
- 経緯: AI Studio のプリペイド残高切れ（402 RESOURCE_EXHAUSTED）。Google Cloud のクレジットを使うため Vertex AI に切り替えた。
- `app.py` / `step1_test.py` / `step1_image_test.py`: `genai.Client(vertexai=True, project=..., location=...)` に変更。`GEMINI_API_KEY` は不要になった。
- `.env` に `GOOGLE_CLOUD_PROJECT`（必須）と `GOOGLE_CLOUD_LOCATION`（省略時 `global`）を設定する。
- 認証は ADC（`gcloud auth application-default login`）。事前に `gcloud services enable aiplatform.googleapis.com --project=<プロジェクトID>` が必要。
- ハマりどころ:
  - ADC の請求先が別プロジェクトになっていた → `gcloud auth application-default set-quota-project <プロジェクトID>` で修正。
  - `~/.bashrc` の `GOOGLE_CLOUD_PROJECT` が `.env` より優先されていた → `load_dotenv(override=True)` で `.env` を優先。

#### Step 5 準備: Cloud Run 用ファイルの追加（作業日 #2 続き）
- [Dockerfile](Dockerfile)（python:3.12-slim、`PORT` 環境変数で Streamlit を起動）と [.dockerignore](.dockerignore)（`.env` / `closet/` / `images/` 等を除外）を追加。
- ⚠️ 未検証: Docker ビルドとデプロイは未実施（コマンドを書いただけ）。
- デプロイ手順（`<プロジェクトID>` は自分のものに置き換える）:
  1. `gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com --project=<プロジェクトID>`
  2. `gcloud run deploy weather-fit --source . --region asia-northeast1 --project=<プロジェクトID> --set-env-vars GOOGLE_CLOUD_PROJECT=<プロジェクトID>,GOOGLE_CLOUD_LOCATION=global --max-instances 1 --allow-unauthenticated`
     （`--max-instances 1` は同時に動くインスタンスを1台に制限し、大量アクセス時の課金に頭打ちを作る）
  3. 実行用サービスアカウントに「Vertex AI ユーザー（`roles/aiplatform.user`）」権限が必要（ローカルの ADC の代わりになる）。
  4. 発行された URL をスマホ/ブラウザで開いて動作確認。
- 注意点:
  - Cloud Run のディスクは一時的なため、`closet/` にアップロードした服はインスタンス再起動で消える（永続化するなら Cloud Storage 化が必要）。
  - `--allow-unauthenticated` は URL を知る人が誰でも使える設定（Gemini の課金が発生しうる）。認証は付けない方針とし、代わりに以下の課金対策を行った。
- 課金対策（2026-10-04）:
  - 予算アラートを作成済み: 月 1,000 円、50% / 90% / 100% 到達時に請求アカウント管理者へメール通知（`gcloud billing budgets create`）。通知のみで自動停止はしない。
  - 同時インスタンス数の上限は `--max-instances 1`（デプロイ時に指定）。
  - 使わなくなったら `gcloud run services delete weather-fit --region asia-northeast1` で削除する。

### 🗺️ 現在地と次のタスク

- [x] **Step 1: Python から Gemini API を呼び出す（画像認識・特徴抽出）**
- [x] **Step 2: 今日の天気（気温・降水確率）を取得する**
- [x] **Step 3: Web画面（Streamlit）を作る**（動作確認済み）
- [x] **Step 4: 天気 × クローゼットを組み合わせて服装を提案させる**（動作確認済み）
- [x] **Step 5: Google Cloud（Cloud Run）にデプロイする**（動作確認済み）

#### Step 5 完了: Cloud Run へデプロイ（2026-10-04）
- 実施内容: API 有効化 → 実行用サービスアカウント（Compute Engine 既定）へ `roles/aiplatform.user` 付与 → `gcloud run deploy weather-fit --source .`（`asia-northeast1`、`--max-instances 1`、認証なし）。
- ブラウザから画面表示と Gemini による服装提案まで動作確認済み。
- 公開 URL は認証なしで誰でも使えるため、このログには記載しない（Cloud Console の Cloud Run 画面か `gcloud run services describe weather-fit --region asia-northeast1` で確認できる）。URL を SNS 等に載せないこと。
- 全5ステップ完了。

#### デプロイ後の片付けと Git 整理（2026-10-04）
- Git:
  - `dev` を `main` にマージ（`main` は GitHub 作成時の Initial commit のみで履歴が別だったため `--allow-unrelated-histories` を使用。`LICENSE` / `README.md` も `main` に含まれる）。`dev` / `main` とも GitHub に push 済み。
  - このリポジトリのリモート名は `origin` ではなく **`upstream`**（`git push upstream dev`）。
- Google Cloud の後片付け（動作確認後、課金リスクをなくすため）:
  - Cloud Run サービス `weather-fit` を削除（公開 URL は停止）。
  - Artifact Registry のリポジトリ `cloud-run-source-deploy`（Cloud Run が自動作成、約187MB）を削除。
  - 残っているもの: 予算アラート、有効化済み API、`roles/aiplatform.user` の付与、Cloud Build がソースを置く Cloud Storage バケット（小容量、未確認・未削除）。
- 再デプロイしたいときは上記「Step 5 準備」の手順 2 を実行すれば Artifact Registry も自動で作り直される。

#### 次回やること候補（余裕があれば）：
1. **公開範囲の見直し**: 再デプロイして審査員に見せる場合はアプリ側パスワード等の認証を検討。
2. **改善**: `closet/` の Cloud Storage 化（再起動で写真が消える問題の解消）、見た目の調整。

#### ユーザーごとの服画像の保存（2026-10-05）
- 要件: ユーザーごとに服の画像を記憶、追加・削除できる。**他ユーザーの画像が見えるのは絶対NG**。
- 実装: `closet_store.py`（保存処理）＋ `app.py`（Googleログイン `st.login`、追加・削除UI）。
  - ユーザーID＝ログインID(`sub`)のSHA-256。メールアドレスは保存しない。保存先は必ず `ユーザーID/` 配下。
  - 画像IDはサーバー生成のuuid＋拡張子のみ受け付ける（`../` 等は拒否）。公開URLは発行しない。
  - 本番は非公開 Cloud Storage（`CLOSET_BUCKET`）、開発時はローカル。`LOCAL_DEV=1` は手元専用で**本番では絶対に設定しない**。
- 設計上の注意: アプリは1つのサービスアカウントで全ユーザーの画像を読み書きできるため、ユーザー分離は**コードの正しさ**で守っている。`closet_store.py` を変更したら必ず分離を再確認すること。
- Google Cloud の設定（`<プロジェクトID>` は自分のものに置き換える）:
  1. バケット作成（東京、均一アクセス制御、公開アクセス禁止）
  2. 専用サービスアカウント `weather-fit-runner` を作成。権限は「Vertex AI利用(プロジェクト)」と「バケット内オブジェクト管理(バケット単位)」「Secret読み取り(その秘密のみ)」だけ
  3. Google Auth Platform で同意画面とOAuthクライアントを作成（サポートメールはGoogleグループ）。リダイレクトURIは `https://weather-fit-<プロジェクト番号>.asia-northeast1.run.app/oauth2callback`（この形式のURLから開くこと）
  4. `secrets.toml`（`[auth]` 設定）を Secret Manager に保存し、`--set-secrets /app/.streamlit/secrets.toml=...` でマウント
  5. `gcloud run deploy weather-fit --source . --service-account ... --set-env-vars ...,CLOSET_BUCKET=... --set-secrets ... --max-instances 1 --allow-unauthenticated`
- 動作確認: ログイン、追加、再読込後も残る、削除、提案、別アカウントから画像が見えないことを確認済み。
- 公開前のTODO: OAuth同意画面を「テスト中」から「本番環境に公開」へ（審査員に使ってもらう場合）。

#### 画像管理画面の分離（2026-10-05）
- `st.navigation` で「服装提案」と「クローゼット管理」の2画面に分割（`app.py` が入口、`common.py` にログイン・クローゼット取得、`views/` に各画面）。
- 管理画面は服の画像を3列で表示し、登録・削除ができる。提案画面には登録枚数と管理画面へのリンクのみ表示。
- Dockerfile に `common.py` と `views/` のCOPYを追加（追加し忘れるとCloud Runで起動しない）。
- 確認: Streamlit の AppTest で両画面が例外なく描画され、管理画面が3列になることを確認。実ブラウザ・本番での確認は未実施。

#### Instagram風の見た目（2026-10-05）
- `style.py` に共通CSS（白基調・細い枠線・グラデーションのタイトルと主ボタン・正方形の服グリッド）、`.streamlit/config.toml` で light テーマ固定。
- Cloud Run は Secret を `/app/.streamlit/` に重ねてマウントし config.toml が隠れうるため、Dockerfile でも `STREAMLIT_THEME_BASE=light` を環境変数で指定。
- スマホ幅では Streamlit が列を縦積みにするため、服グリッド(3列)と天気(2x2)だけ CSS で横並びを維持。
- 全体に `font-family` を `[class*="st-"]` で指定するとアイコンフォントが壊れる（`upload` 等の文字が出る）ので指定しない。
- ローカル確認のダミー画像は `closet/` のコピーを一時フォルダに取り込んで使用（旧形式のため。元フォルダは未変更）。

#### スマホ優先のナビゲーション変更（2026-10-05）
- サイドバーは廃止（スマホで邪魔なため）。`st.navigation(position="top")` もスマホ幅ではサイドバーに畳まれるので使わず、`position="hidden"` ＋ タイトル下の自前タブ(`st.page_link`)にした。
- 提案ボタンは画面下部に固定（`.st-key-suggest_bar`）。提案結果はボタンの上の本文側に表示される。
- ログアウトボタンは管理画面の末尾へ移動。

- 画面切り替えタブも画面最下部に固定（Instagramの下部タブ風）。提案ボタンはそのすぐ上に固定。タイトル下の説明文は削除。

- アップロード欄を「📷 写真をアップロード」ボタン1つに変更。写真を選ぶと自動で保存される（別の保存ボタンは廃止）。ボタン文言は Streamlit が "Upload" 固定のため CSS で差し替え。

#### おすすめコーデの画像表示（2026-10-05）
- Gemini に文章ではなく JSON（`outfit.py` の `Outfit`: 画像番号・種類・説明・理由・持ち物）を返させ、服の画像を「アウター→トップス→ボトムス→シューズ→小物」の順にカードで表示。
- 存在しない画像番号・重複はコード側(`arrange`)で除外し、並び順もコードで保証。
- 確認は偽のGemini応答で実施（実際のGeminiでの動作は未確認）。

- 「タイトル + クローゼット管理 + アップロードボタン」をスクロールしても画面上部に固定（`.st-key-sticky_top`、position: sticky）。タイトル表示は `common.show_title()` に移し、各画面の sticky_top コンテナ内で呼ぶ。
- アップロードボタンと「N枚の服」の間の隙間を詰めた。
