import streamlit as st

from closet_store import ClosetError
from common import get_closet, show_logout_button, show_title

COLUMNS = 3  # 服の画像を並べる列数

closet = get_closet()

# --- 登録 ---
# 「タイトル + 見出し + アップロードボタン」は、一覧をスクロールしても画面上部に残す
# （固定の仕組みは style.py の .st-key-sticky_top）
# ボタンは「写真をアップロード」1つだけ。写真を選んだ時点で自動保存する
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
with st.container(key="sticky_top"):
    show_title()
    st.subheader("👗 クローゼット管理")
    with st.container(key="uploader_wrap"):
        uploaded = st.file_uploader(
            "服の写真を選択（複数可）",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.uploader_key}",
            label_visibility="collapsed",
        )
if uploaded:
    saved, errors = 0, []
    for f in uploaded:
        try:
            closet.add(f.getvalue())
            saved += 1
        except ClosetError as e:
            errors.append(f"{f.name}: {e}")
    st.session_state.uploader_key += 1  # アップロード欄をリセット（再保存を防ぐ）
    st.session_state.flash = (saved, errors)
    st.rerun()
if "flash" in st.session_state:
    saved, errors = st.session_state.pop("flash")
    if saved:
        st.success(f"{saved} 枚を保存しました")
    for msg in errors:
        st.error(msg)

# --- 一覧（3列） ---
closet_ids = closet.list_ids()
st.markdown(
    f'<div class="closet-stat"><b>{len(closet_ids)}</b><span>枚の服</span></div>',
    unsafe_allow_html=True,
)
if closet_ids:
    # 一覧のスタイル（スマホでも横3列を保つ等）は style.py の .st-key-closet_grid
    with st.container(key="closet_grid"):
        # 3枚ずつ1行にする（最後の行が余っても幅がそろうよう、列は常に COLUMNS 個作る）
        for start in range(0, len(closet_ids), COLUMNS):
            cols = st.columns(COLUMNS)
            for col, i in zip(cols, range(start, min(start + COLUMNS, len(closet_ids)))):
                image_id = closet_ids[i]
                with col:
                    st.image(closet.read(image_id), caption=f"服 {i + 1}", width="stretch")
                    if st.button("🗑 削除", key=f"del_{image_id}", type="tertiary", width="stretch"):
                        closet.delete(image_id)
                        st.rerun()

# --- アカウント ---
show_logout_button()
