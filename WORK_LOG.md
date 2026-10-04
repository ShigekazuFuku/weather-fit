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

#### ユーザーごとのクローゼットと Cloud Storage 永続化（2026-10-04）
- [storage.py](storage.py) を追加。ユーザー名+パスワード（PBKDF2 ハッシュ）でログインし、画像は `users/<ユーザー名>/closet/` 配下にのみ保存・取得する（他ユーザーの画像は見えない）。
- `CLOSET_BUCKET` 環境変数があれば Cloud Storage、無ければローカル `closet/`（開発用）に保存。再デプロイしても画像・アカウントは残る。
- ⚠️ 未検証: ローカル保存での単体テストのみ。Cloud Storage 実機と Streamlit 画面は未確認。
- デプロイ手順（`<プロジェクトID>` / `<バケット名>` は置き換える）:
  1. `gcloud storage buckets create gs://<バケット名> --location=asia-northeast1 --project=<プロジェクトID> --uniform-bucket-level-access`（公開設定にしないこと）
  2. 実行用サービスアカウントにバケットへの `roles/storage.objectAdmin` を付与
  3. `gcloud run deploy` に `--set-env-vars ...,CLOSET_BUCKET=<バケット名>` を追加
- 注意: 認証は簡易（アカウント作成は誰でも可、パスワード再設定なし）。`--max-instances 1` のままなら ID 競合は起きにくい。
