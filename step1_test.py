import os
from dotenv import load_dotenv
from google import genai

# 1. .env ファイルから環境変数（GOOGLE_CLOUD_PROJECT）を読み込む（Vertex AI 経由で呼ぶ）
load_dotenv(override=True)

project = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")

if not project:
    print("❌ エラー: .env ファイルに GOOGLE_CLOUD_PROJECT が見つかりませんでした。")
    print("   .env に GOOGLE_CLOUD_PROJECT=プロジェクトID を記述してください。")
    exit(1)

print("🔑 プロジェクト設定の読み込みに成功しました。")
print("🤖 Vertex AI 経由で Gemini に接続してテストメッセージを送信しています...")

# 2. Gemini クライアントの準備
client = genai.Client(vertexai=True, project=project, location=location)

try:
    # 3. Gemini にメッセージを送ってみる（推奨モデル gemini-3.8-flash を使用）
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="こんにちは！今日の服装を提案するAIアシスタントとして、明るく短い挨拶をしてください。",
    )

    # 4. 結果を表示
    print("\n--- [Gemini からの返答] ---")
    print(response.text)
    print("---------------------------\n")
    print("🎉 成功！ Gemini API と正常に通信できました。")

except Exception as e:
    print(f"\n❌ 通信エラーが発生しました: {e}")
