import os
from dotenv import load_dotenv
from google import genai

# 1. .env ファイルから環境変数（GEMINI_API_KEY）を読み込む
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ エラー: .env ファイルに GEMINI_API_KEY が見つかりませんでした。")
    print("   .env に GEMINI_API_KEY=あなたのキー を記述してください。")
    exit(1)

print("🔑 APIキーの読み込みに成功しました。")
print("🤖 Gemini API に接続してテストメッセージを送信しています...")

# 2. Gemini クライアントの準備
client = genai.Client(api_key=api_key)

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
