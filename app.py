import io
import os

import streamlit as st
from dotenv import load_dotenv
from google import genai
from PIL import Image

from step2_weather_test import get_today_weather
from storage import Store, normalize_username

MODEL = "gemini-3.8-flash"

# 地域の選択肢（緯度, 経度）
CITIES = {
    "東京": (35.6895, 139.6917),
    "大阪": (34.6937, 135.5023),
    "名古屋": (35.1815, 136.9066),
    "札幌": (43.0618, 141.3545),
    "福岡": (33.5902, 130.4017),
}

load_dotenv(override=True)  # シェルの環境変数（~/.bashrc 等）より .env を優先する
# Vertex AI（Google Cloud）経由で Gemini を呼ぶ。課金は Google Cloud のクレジットが対象
project = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")

st.title("👕 WeatherFit")
st.caption("持っている服と今日の天気から、快適な服装を提案します")

if not project:
    st.error(".env に GOOGLE_CLOUD_PROJECT（GoogleCloudのプロジェクトID）を設定してください。")
    st.stop()

@st.cache_resource
def get_store() -> Store:
    return Store()


store = get_store()

# --- 0. ログイン（ユーザーごとにクローゼットを分けるため） ---
user = st.session_state.get("user")
if not user:
    st.header("ログイン")
    tab_login, tab_register = st.tabs(["ログイン", "新規登録"])
    with tab_login:
        with st.form("login"):
            name = st.text_input("ユーザー名")
            pw = st.text_input("パスワード", type="password")
            if st.form_submit_button("ログイン"):
                uname = normalize_username(name)
                if uname and store.verify(uname, pw):
                    st.session_state["user"] = uname
                    st.rerun()
                else:
                    st.error("ユーザー名またはパスワードが違います。")
    with tab_register:
        with st.form("register"):
            name = st.text_input("ユーザー名（英数字・_・-、3〜32文字）")
            pw = st.text_input("パスワード（8文字以上）", type="password")
            if st.form_submit_button("登録"):
                uname = normalize_username(name)
                if not uname:
                    st.error("ユーザー名は英数字・_・-の3〜32文字にしてください。")
                elif len(pw) < 8:
                    st.error("パスワードは8文字以上にしてください。")
                elif store.register(uname, pw):
                    st.session_state["user"] = uname
                    st.rerun()
                else:
                    st.error("そのユーザー名は既に使われています。")
    st.stop()

st.sidebar.write(f"ログイン中: {user}")
if st.sidebar.button("ログアウト"):
    del st.session_state["user"]
    st.rerun()

# --- 1. クローゼット登録 ---
st.header("1. クローゼットに服を登録")
uploaded = st.file_uploader(
    "服の写真を選択（複数可）", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)
if uploaded and st.button("クローゼットに保存"):
    for f in uploaded:
        store.save_image(user, f.name, f.getvalue())
    st.success(f"{len(uploaded)} 枚を保存しました")

closet_names = store.list_images(user)
st.write(f"登録済み: {len(closet_names)} 枚")
closet_images = [(n, store.load_image(user, n)) for n in closet_names]
if closet_images:
    cols = st.columns(4)
    for i, (n, data) in enumerate(closet_images):
        cols[i % 4].image(data, caption=n, use_container_width=True)
        if cols[i % 4].button("削除", key=f"del_{n}"):
            store.delete_image(user, n)
            st.rerun()

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
if st.button("提案してもらう", type="primary", disabled=not (closet_images and weather)):
    images = [Image.open(io.BytesIO(d)) for _, d in closet_images]
    names = "\n".join(f"- 画像{i + 1}: {n}" for i, (n, _) in enumerate(closet_images))
    prompt = f"""
あなたはファッションスタイリストです。添付の画像は私が持っている服です。
{names}

今日の天気（{weather['city']}）:
- 天候: {weather['current_weather']}
- 気温: 最高{weather['max_temp']}℃ / 最低{weather['min_temp']}℃（現在{weather['current_temp']}℃）
- 湿度: {weather['humidity']}%
- 降水確率: {weather['precip_prob']}%

持っている服の中から、今日快適に過ごせる組み合わせを提案してください。
・どの画像の服を着るか（画像番号とファイル名、服の種類）
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
