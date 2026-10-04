import streamlit as st

from closet_store import ClosetError
from common import get_closet

COLUMNS = 3  # 服の画像を並べる列数

closet = get_closet()

st.subheader("👗 クローゼット管理")

# --- 登録 ---
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
uploaded = st.file_uploader(
    "服の写真を選択（複数可）",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}",
)
if uploaded and st.button("クローゼットに保存"):
    saved = 0
    for f in uploaded:
        try:
            closet.add(f.getvalue())
            saved += 1
        except ClosetError as e:
            st.error(f"{f.name}: {e}")
    if saved:
        st.session_state.uploader_key += 1  # アップロード欄をリセット
        st.session_state.flash = f"{saved} 枚を保存しました"
        st.rerun()
if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

# --- 一覧（3列） ---
closet_ids = closet.list_ids()
st.write(f"登録済み: {len(closet_ids)} 枚")
# Streamlit は幅640px未満(スマホ)だと列を縦1列に積むため、一覧部分だけ横並びを維持する
st.markdown(
    """
<style>
.st-key-closet_grid [data-testid="stHorizontalBlock"] { flex-wrap: nowrap; gap: 0.5rem; }
.st-key-closet_grid [data-testid="stColumn"] { min-width: 0; width: auto; flex: 1 1 0; }
</style>
""",
    unsafe_allow_html=True,
)
if closet_ids:
    with st.container(key="closet_grid"):
        # 3枚ずつ1行にする（最後の行が余っても幅がそろうよう、列は常に COLUMNS 個作る）
        for start in range(0, len(closet_ids), COLUMNS):
            cols = st.columns(COLUMNS)
            for col, i in zip(cols, range(start, min(start + COLUMNS, len(closet_ids)))):
                image_id = closet_ids[i]
                with col:
                    st.image(closet.read(image_id), caption=f"服 {i + 1}", width="stretch")
                    if st.button("削除", key=f"del_{image_id}", width="stretch"):
                        closet.delete(image_id)
                        st.rerun()
