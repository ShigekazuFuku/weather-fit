import os

import streamlit as st

from closet_store import Closet, make_backend, user_id_from_subject


def require_login() -> None:
    """ログイン必須。未ログインならログインボタンを出して処理を止める"""
    if os.getenv("LOCAL_DEV") == "1":
        return  # 手元での開発用。本番(Cloud Run)では絶対に設定しないこと
    if not st.user.is_logged_in:
        st.info("ご自身の服の写真を保存するため、ログインしてください。")
        st.button("Googleでログイン", on_click=st.login)
        st.stop()


def show_logout_button() -> None:
    """ログアウトボタン（ローカル開発時は不要なので出さない）"""
    if os.getenv("LOCAL_DEV") != "1":
        st.button("ログアウト", on_click=st.logout)


@st.cache_resource
def _get_backend():
    return make_backend()


def get_closet() -> Closet:
    """ログイン中のユーザー専用のクローゼット(他人の領域には触れない)"""
    if os.getenv("LOCAL_DEV") == "1":
        user_id = user_id_from_subject("local-dev-user")
    else:
        user_id = user_id_from_subject(st.user.sub)
    return Closet(_get_backend(), user_id)
