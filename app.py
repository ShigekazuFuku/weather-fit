import os

import streamlit as st
from dotenv import load_dotenv

from common import require_login
from style import apply_style

load_dotenv(override=True)  # シェルの環境変数（~/.bashrc 等）より .env を優先する

st.set_page_config(page_title="WeatherFit", page_icon="👕")
apply_style()
st.title("👕 WeatherFit")
st.caption("持っている服と今日の天気から、快適な服装を提案します")

if not os.getenv("GOOGLE_CLOUD_PROJECT"):
    st.error(".env に GOOGLE_CLOUD_PROJECT（GoogleCloudのプロジェクトID）を設定してください。")
    st.stop()

require_login()  # ユーザーごとにクローゼットを分けるため、全画面でログイン必須

# 画面の切り替え（サイドバーに表示される）
pg = st.navigation(
    [
        st.Page("views/suggest.py", title="服装提案", icon="👕", default=True),
        st.Page("views/manage.py", title="クローゼット管理", icon="👗"),
    ]
)
pg.run()
