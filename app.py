import os
import streamlit as st
from PIL import Image
# from dotenv import load_dotenv # .env からのAPIキー読み込みは不要になります
import requests

import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part

# ----------------------------------------------------
# 1. Google Cloud (Vertex AI) 設定
# ----------------------------------------------------
# 環境変数からプロジェクトIDとロケーションを読み込む
# GCP_PROJECT_ID と GCP_LOCATION を設定してください
# 例: export GCP_PROJECT_ID="your-gcp-project-id"
# 例: export GCP_LOCATION="asia-northeast1"

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_LOCATION = os.getenv("GCP_LOCATION")
VERTEX_AI_MODEL_NAME = "gemini-1.5-flash-001" # Vertex AIで利用可能なモデル名

if not GCP_PROJECT_ID or not GCP_LOCATION:
    st.error("❌ エラー: 環境変数 GCP_PROJECT_ID または GCP_LOCATION が設定されていません。")
    st.info("コマンドラインで `export GCP_PROJECT_ID='your-project-id'` および `export GCP_LOCATION='your-region'` を実行してください。")
    st.stop() # 環境変数が設定されていない場合は停止

# Vertex AI の初期化
try:
    vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)
    st.success(f"✅ Vertex AI をプロジェクト '{GCP_PROJECT_ID}'、ロケーション '{GCP_LOCATION}' で初期化しました。")
except Exception as e:
    st.error(f"❌ Vertex AI の初期化に失敗しました: {e}")
    st.info("`gcloud auth application-default login` を実行して認証情報を設定しているか確認してください。")
    st.stop() # 初期化に失敗した場合は停止

# 3. WMO天気コード（数値）を日本語の天気に変換するマップ
WEATHER_CODES = {
    0: "☀️ 快晴", 1: "🌤️ 主に晴れ", 2: "⛅ 一部曇り", 3: "☁️ 曇り",
    45: "🌫️ 霧", 48: "🌫️ 霧氷",
    51: "🌦️ 弱い霧雨", 53: "🌦️ 霧雨", 55: "🌧️ 濃い霧雨",
    61: "🌧️ 弱い雨", 63: "🌧️ 雨", 65: "🌧️ 強い雨",
    71: "🌨️ 弱い雪", 73: "🌨️ 雪", 75: "❄️ 強い雪",
    80: "🌦️ にわか雨", 81: "🌧️ 強いにわか雨", 82: "⛈️ 非常に激しいにわか雨",
    95: "⛈️ 雷雨",
}

# 4. Open-Meteo API を使って指定した場所の今日の天気を取得する関数
def get_today_weather(latitude=35.6895, longitude=139.6917, city_name="東京"):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "relative_humidity_2m", "weather_code"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_probability_max", "weather_code"],
        "timezone": "Asia/Tokyo"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        current_temp = data["current"]["temperature_2m"]
        current_humidity = data["current"]["relative_humidity_2m"]
        current_weather_code = data["current"]["weather_code"]
        current_weather = WEATHER_CODES.get(current_weather_code, "不明")

        max_temp = data["daily"]["temperature_2m_max"][0]
        min_temp = data["daily"]["temperature_2m_min"][0]
        precip_prob = data["daily"]["precipitation_probability_max"][0]

        weather_info = {
            "city": city_name,
            "current_weather": current_weather,
            "current_temp": current_temp,
            "humidity": current_humidity,
            "max_temp": max_temp,
            "min_temp": min_temp,
            "precip_prob": precip_prob
        }
        return weather_info

    except requests.exceptions.RequestException as e:
        st.error(f"天気情報の取得に失敗しました: {e}")
        return None

# 5. Streamlit アプリケーションの構築
st.set_page_config(page_title="WeatherFit", layout="centered")
st.title("👕 WeatherFit - AI服装アドバイザー")
st.write("今日の天気とあなたの服から、最適なコーディネートを提案します。")

# 天気情報セクション
with st.expander("今日の天気情報 (東京)", expanded=True):
    st.subheader("現在の東京の天気")
    weather_data = get_today_weather()
    if weather_data:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("現在の気温", f"{weather_data['current_temp']} ℃", delta=None)
            st.metric("今日の最高気温", f"{weather_data['max_temp']} ℃", delta=None)
        with col2:
            st.metric("天候", weather_data['current_weather'], delta=None)
            st.metric("今日の最低気温", f"{weather_data['min_temp']} ℃", delta=None)
        with col3:
            st.metric("湿度", f"{weather_data['humidity']} %", delta=None)
            st.metric("降水確率", f"{weather_data['precip_prob']} %", delta=None)
    else:
        st.warning("天気情報を取得できませんでした。")

st.subheader("👚 服の画像をアップロード")
uploaded_file = st.file_uploader("ここに服の画像をドラッグ＆ドロップ、またはクリックして選択してください。", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた服", use_column_width=True)
    st.write("")

    if st.button("この服をGeminiに分析してもらう"):
        try:
            with st.spinner("Geminiが画像を分析中... しばらくお待ちください。"):
                # Vertex AI のモデルをロード
                model = GenerativeModel(VERTEX_AI_MODEL_NAME)
                
                # 画像を Vertex AI の Part オブジェクトに変換
                image_part = Part.from_image(image)

                prompt = """
                添付された服の画像を見て、以下の項目を整理して教えてください：
                1. 服の種類（カテゴリ）: 例（半袖シャツ、Tシャツ、セーターなど）
                2. 色・柄:
                3. 特徴（襟の形、ボタン、ポケットなど）:
                4. 適した季節・気温感:
                5. コーディネートのワンポイントアドバイス:
                """
                response = model.generate_content([prompt, image_part]) # prompt と image_part を渡す
                st.success("分析が完了しました！")
                st.markdown("---")
                st.subheader("Geminiによる服の分析結果")
                st.write(response.text)
                st.markdown("---")

        except Exception as e:
            st.error(f"Geminiによる分析中にエラーが発生しました: {e}")
            st.info("Vertex AI の設定、認証情報、またはモデルの利用可能状況を確認してください。")
else:
    st.info("画像をアップロードしてください。")

st.markdown("---")
st.caption("Powered by Google Gemini (Vertex AI) & Open-Meteo API")

