import os
from PIL import Image
from dotenv import load_dotenv
from google import genai

# 1. .env から Google Cloud のプロジェクト設定を読み込み（Vertex AI 経由で呼ぶ）
load_dotenv(override=True)
project = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")

if not project:
    print("❌ エラー: .env ファイルに GOOGLE_CLOUD_PROJECT が見つかりませんでした。")
    exit(1)

# 2. 画像ファイルを開く
image_path = "images/sample.jpg"
if not os.path.exists(image_path):
    print(f"❌ エラー: 画像ファイル {image_path} が見つかりません。")
    exit(1)

print(f"🖼️ 画像 [{image_path}] を読み込みました。")
image = Image.open(image_path)

# 3. Gemini クライアントの初期化
client = genai.Client(vertexai=True, project=project, location=location)

# 4. 画像と質問を Gemini に送る
print("🤖 Gemini に画像を見せて分析してもらっています...")

prompt = """
添付された服の画像を見て、以下の項目を整理して教えてください：
1. 服の種類（カテゴリ）: 例（半袖シャツ、Tシャツ、セーターなど）
2. 色・柄:
3. 特徴（襟の形、ボタン、ポケットなど）:
4. 適した季節・気温感:
5. コーディネートのワンポイントアドバイス:
"""

try:
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=[image, prompt],
    )

    print("\n--- [Gemini の服分析結果] ---")
    print(response.text)
    print("-----------------------------\n")
    print("🎉 成功！ 服の画像を Gemini に認識させることができました！")

except Exception as e:
    print(f"\n❌ エラーが発生しました: {e}")
