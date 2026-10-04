import io
import os

import streamlit as st
from google import genai
from PIL import Image

from common import get_closet
from step2_weather_test import get_today_weather

MODEL = "gemini-3.8-flash"

# 地域の選択肢（緯度, 経度）
CITIES = {
    "東京": (35.6895, 139.6917),
    "大阪": (34.6937, 135.5023),
    "名古屋": (35.1815, 136.9066),
    "札幌": (43.0618, 141.3545),
    "福岡": (33.5902, 130.4017),
}

project = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
closet = get_closet()
closet_ids = closet.list_ids()

# --- 1. クローゼット ---
st.header("1. クローゼット")
st.write(f"登録済み: {len(closet_ids)} 枚")
st.page_link("views/manage.py", label="服の登録・削除はこちら（クローゼット管理）", icon="👗")

# --- 2. 天気 ---
st.header("2. 今日の天気")
city = st.selectbox("地域", list(CITIES))
lat, lon = CITIES[city]
weather = get_today_weather(lat, lon, city)
if weather:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("天候", weather["current_weather"])
    c2.metric("気温(最高/最低)", f"{weather['max_temp']}/{weather['min_temp']}℃")
    c3.metric("湿度", f"{weather['humidity']}%")
    c4.metric("降水確率", f"{weather['precip_prob']}%")
else:
    st.warning("天気を取得できませんでした。")

# --- 3. 提案 ---
st.header("3. 今日の服装を提案")
if st.button("提案してもらう", type="primary", disabled=not (closet_ids and weather)):
    images = [Image.open(io.BytesIO(closet.read(i))) for i in closet_ids]
    names = "\n".join(f"- 画像{i + 1}: 服 {i + 1}" for i in range(len(closet_ids)))
    prompt = f"""
あなたはファッションスタイリストです。添付の画像は私が持っている服です。
{names}

今日の天気（{weather['city']}）:
- 天候: {weather['current_weather']}
- 気温: 最高{weather['max_temp']}℃ / 最低{weather['min_temp']}℃（現在{weather['current_temp']}℃）
- 湿度: {weather['humidity']}%
- 降水確率: {weather['precip_prob']}%

持っている服の中から、今日快適に過ごせる組み合わせを提案してください。
・どの画像の服を着るか（画像番号、服の種類）
・そう選んだ理由（気温・湿度・降水確率の観点で）
・羽織りものや傘など、持ち物のアドバイス
手持ちの服に適したものがなければ、その旨も正直に伝えてください。
"""
    with st.spinner("Gemini が考え中..."):
        try:
            client = genai.Client(vertexai=True, project=project, location=location)
            response = client.models.generate_content(
                model=MODEL, contents=[*images, prompt]
            )
            st.markdown(response.text)
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
