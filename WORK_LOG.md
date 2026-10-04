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
  - APIキーが書かれた `.env` や仮想環境 `venv/` を除外する [.gitignore](.gitignore) を作成。
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

### 🗺️ 現在地と次のタスク

- [x] **Step 1: Python から Gemini API を呼び出す（画像認識・特徴抽出）**
- [x] **Step 2: 今日の天気（気温・降水確率）を取得する**
- [x] **Step 3: Web画面（Streamlit）を作る**（動作確認待ち）
- [x] **Step 4: 天気 × クローゼットを組み合わせて服装を提案させる**（動作確認待ち）
- [ ] **Step 5: Google Cloud（Cloud Run）にデプロイする**

#### 次回やること候補：
1. **「服 × 天気」の組み合わせ推論ロジックの実装（Step 4 のコア部分）**:
   - `images/sample.jpg` と 今日の天気データを Gemini に渡し、「今日の天気でこの服を着ていくのは適切か？」「羽織りものは必要か？」をアドバイスさせる。
2. **Streamlit による Web 画面の作成（Step 3）**:
   - ブラウザから写真をアップロードして、ボタンを押すと服装アドバイスが表示される画面を作る。
