import io
import os
import random

import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

from common import get_closet, show_title
from messages import WAITING_MESSAGES
from outfit import CATEGORIES, Outfit, arrange
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

with st.container(key="sticky_top"):  # タイトルは管理画面と同じく画面上部に固定
    show_title()

# --- 天気 ---
st.header("今日の天気")
city = st.selectbox("地域", list(CITIES))
lat, lon = CITIES[city]
weather = get_today_weather(lat, lon, city)
if weather:
    # スマホでも2x2で収まるよう、2列を2段に分ける（スタイルは style.py の .st-key-weather_grid）
    with st.container(key="weather_grid"):
        c1, c2 = st.columns(2)
        c1.metric("天候", weather["current_weather"])
        c2.metric("気温(最高/最低)", f"{weather['max_temp']}/{weather['min_temp']}℃")
        c3, c4 = st.columns(2)
        c3.metric("湿度", f"{weather['humidity']}%")
        c4.metric("降水確率", f"{weather['precip_prob']}%")
else:
    st.warning("天気を取得できませんでした。")

# --- 提案 ---
# ボタンは画面下部に固定（スクロールしても常に押せる）。スタイルは style.py の .st-key-suggest_bar
with st.container(key="suggest_bar"):
    clicked = st.button(
        "✨ 今日の服装を提案してもらう",
        type="primary",
        width="stretch",
        disabled=not (closet_ids and weather),
    )
if not closet_ids:
    st.info("提案には服の登録が必要です。「クローゼット管理」から登録してください。")

if clicked:
    st.header("今日の服装の提案")
    images = [Image.open(io.BytesIO(closet.read(i))) for i in closet_ids]
    names = "\n".join(f"- 画像{i + 1}" for i in range(len(closet_ids)))
    prompt = f"""
あなたはファッションスタイリストです。添付の画像は私が持っている服です。
{names}

今日の天気（{weather['city']}）:
- 天候: {weather['current_weather']}
- 気温: 最高{weather['max_temp']}℃ / 最低{weather['min_temp']}℃（現在{weather['current_temp']}℃）
- 湿度: {weather['humidity']}%
- 降水確率: {weather['precip_prob']}%

持っている服の中から、今日快適に過ごせる組み合わせを1つ提案してください。
・使う服は上記の画像番号で指定する（category は {" / ".join(CATEGORIES)} のいずれか）
・同じ種類は1点まで（小物は複数可）。暑くて羽織りが不要など、着ない種類は含めない
・理由は気温・湿度・降水確率の観点で書く。画面には画像が並んで表示されるので、note・reason・advice に「画像1」「服15」のような番号は書かず、服は「デニムジャケット」のように特徴で呼ぶ
・羽織りものや傘など、持ち物のアドバイスも書く
手持ちの服に適したものがなければ、items を空にして、その旨を reason に正直に書いてください。
"""
    with st.spinner(random.choice(WAITING_MESSAGES)):
        try:
            client = genai.Client(vertexai=True, project=project, location=location)
            response = client.models.generate_content(
                model=MODEL,
                contents=[*images, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", response_schema=Outfit
                ),
            )
            outfit = Outfit.model_validate_json(response.text)
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            outfit = None

    if outfit:
        items = arrange(outfit, len(closet_ids))
        if items:
            # 上に着るものから順に、服の画像と説明を並べる（スタイルは style.py の .st-key-outfit_list）
            with st.container(key="outfit_list"):
                for item in items:
                    img_col, text_col = st.columns([1, 2], vertical_alignment="center")
                    img_col.image(closet.read(closet_ids[item.image_number - 1]), width="stretch")
                    text_col.markdown(f"**{item.category}**  \n{item.note}")
        else:
            st.info("今日の天気に合う服が見つかりませんでした。")
        st.markdown(f"**理由**  \n{outfit.reason}")
        st.markdown(f"**持ち物**  \n{outfit.advice}")

# 固定ボタンに本文の末尾が隠れないための余白
st.markdown('<div style="height:4.5rem"></div>', unsafe_allow_html=True)
