import os

import streamlit as st
from dotenv import load_dotenv

from common import require_login
from style import apply_style

load_dotenv(override=True)  # シェルの環境変数（~/.bashrc 等）より .env を優先する

st.set_page_config(page_title="WeatherFit", page_icon="👕")
apply_style()
st.title("👕 WeatherFit")

if not os.getenv("GOOGLE_CLOUD_PROJECT"):
    st.error(".env に GOOGLE_CLOUD_PROJECT（GoogleCloudのプロジェクトID）を設定してください。")
    st.stop()

require_login()  # ユーザーごとにクローゼットを分けるため、全画面でログイン必須

# 画面の切り替え。サイドバーは使わない（スマホだと top 指定でもサイドバーに畳まれてしまう）。
# Streamlit 標準のメニューは隠し、画面下部に固定の自前タブ(ページリンク)を置く
suggest_page = st.Page("views/suggest.py", title="服装提案", icon="👕", default=True)
manage_page = st.Page("views/manage.py", title="クローゼット管理", icon="👗")
pg = st.navigation([suggest_page, manage_page], position="hidden")

with st.container(key="bottom_nav"):
    c1, c2 = st.columns(2)
    c1.page_link(suggest_page, width="stretch")
    c2.page_link(manage_page, width="stretch")

pg.run()
