"""画面全体の見た目（Instagram風: 白基調・細い枠線・グラデーションのアクセント）"""

import streamlit as st

# Instagram のロゴ色を意識したグラデーション
_GRADIENT = "linear-gradient(45deg, #feda75, #fa7e1e 25%, #d62976 55%, #962fbf 80%, #4f5bd5)"

_CSS = f"""
<style>
:root {{ --ig-border: #dbdbdb; --ig-sub: #737373; }}

.stApp {{ background: #fafafa; }}
.block-container {{ max-width: 640px; padding-top: 2.5rem; }}

/* タイトル: ロゴのようなグラデーション文字 */
h1 {{
  font-size: 2rem !important; font-weight: 800 !important; letter-spacing: -0.02em;
  background: {_GRADIENT}; -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent; width: fit-content; padding-bottom: 0.2rem;
}}
h2, h3 {{ font-weight: 700 !important; font-size: 1.1rem !important; }}
[data-testid="stCaptionContainer"] {{ color: var(--ig-sub); }}

/* ボタン: 細い枠線の丸角。主ボタンはグラデーション */
.stButton > button, .stDownloadButton > button {{
  border-radius: 8px; border: 1px solid var(--ig-border); background: #fff;
  font-weight: 600; transition: transform .1s;
}}
.stButton > button:active {{ transform: scale(.97); }}
.stButton > button[kind="primary"] {{
  background: {_GRADIENT}; border: 0; color: #fff;
}}
.stButton > button[kind="tertiary"] {{ border: 0; background: transparent; color: var(--ig-sub); }}

/* カード: 天気の指標やアップロード欄を投稿カードのように */
[data-testid="stMetric"], [data-testid="stFileUploader"] section {{
  background: #fff; border: 1px solid var(--ig-border); border-radius: 12px; padding: .7rem .9rem;
}}
[data-testid="stMetricLabel"] {{ color: var(--ig-sub); }}
[data-testid="stAlert"] {{ border-radius: 12px; }}

/* Streamlit は幅640px未満(スマホ)だと列を縦1列に積むため、グリッドは横並びを維持する */
.st-key-closet_grid [data-testid="stHorizontalBlock"],
.st-key-weather_grid [data-testid="stHorizontalBlock"] {{ flex-wrap: nowrap; }}
.st-key-closet_grid [data-testid="stColumn"],
.st-key-weather_grid [data-testid="stColumn"] {{ min-width: 0; width: auto; flex: 1 1 0; }}
.st-key-weather_grid [data-testid="stMetricValue"] {{ font-size: 1.5rem; }}

/* 画面切り替えのタブ: Instagramの下部タブのように画面最下部に固定（スマホでも横2つ） */
:root {{ --nav-h: 3.4rem; }}
.st-key-bottom_nav {{
  position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); z-index: 1000;
  width: min(100%, 640px); box-sizing: border-box; height: calc(var(--nav-h) + env(safe-area-inset-bottom));
  padding-bottom: env(safe-area-inset-bottom); background: #fff; border-top: 1px solid var(--ig-border);
}}
.st-key-bottom_nav [data-testid="stHorizontalBlock"] {{ flex-wrap: nowrap; gap: 0; }}
.st-key-bottom_nav [data-testid="stColumn"] {{ min-width: 0; width: auto; flex: 1 1 0; }}
.st-key-bottom_nav a {{
  justify-content: center; height: var(--nav-h); border-radius: 0; font-weight: 600; color: var(--ig-sub);
}}
.st-key-bottom_nav a[aria-current="page"] {{ color: #262626; background: transparent; box-shadow: inset 0 2px 0 #262626; }}
/* サイドバーは使わないので、開閉ボタンも出さない */
[data-testid="stSidebar"], [data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] {{ display: none; }}

/* 提案ボタン: タブのすぐ上に固定（スマホの親指で押しやすい位置）。本文が隠れないよう下に余白を足す */
.block-container {{ padding-bottom: 6rem; }}
.st-key-suggest_bar {{
  position: fixed; bottom: calc(var(--nav-h) + env(safe-area-inset-bottom)); left: 50%;
  transform: translateX(-50%); z-index: 999;
  width: min(100%, 640px); box-sizing: border-box; padding: .6rem 1rem;
  background: rgba(255, 255, 255, .96); border-top: 1px solid var(--ig-border);
}}
.st-key-suggest_bar .stButton > button {{ min-height: 3rem; font-size: 1rem; }}

/* 服の一覧: プロフィール画面のような正方形グリッド(隙間は細く) */
.st-key-closet_grid [data-testid="stHorizontalBlock"] {{ gap: 3px; }}
.st-key-closet_grid [data-testid="stVerticalBlock"] {{ gap: 0; }}
.st-key-closet_grid img {{ aspect-ratio: 1 / 1; object-fit: cover; border-radius: 2px; }}
.st-key-closet_grid [data-testid="stImageCaption"] {{ display: none; }}
.st-key-closet_grid .stButton > button {{ min-height: 1.8rem; padding: 0; font-size: .8rem; }}

/* 登録枚数: プロフィールの「投稿 N」風 */
.closet-stat {{ display: flex; align-items: baseline; gap: .4rem; padding: .6rem 0 1rem; border-bottom: 1px solid var(--ig-border); margin-bottom: 3px; }}
.closet-stat b {{ font-size: 1.4rem; }}
.closet-stat span {{ color: var(--ig-sub); }}
</style>
"""


def apply_style() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
