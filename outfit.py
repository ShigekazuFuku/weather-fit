"""おすすめコーディネートの形式（Geminiの返答）と、表示用の並べ替え。

Gemini には文章ではなく「どの画像番号を、どの種類の服として使うか」を JSON で返させる。
こうすると画面側で、該当する服の画像を並べて表示できる。
"""

from typing import Literal

from pydantic import BaseModel, Field

# 上に着るものから順（表示もこの順番）
CATEGORIES = ["アウター", "トップス", "ボトムス", "シューズ", "小物"]
Category = Literal["アウター", "トップス", "ボトムス", "シューズ", "小物"]


class OutfitItem(BaseModel):
    image_number: int = Field(description="使う服の画像番号（1始まり）")
    category: Category
    note: str = Field(description="その服の特徴を15字程度で（例: 白×青のスニーカー）")


class Outfit(BaseModel):
    items: list[OutfitItem] = Field(description="今日着る服。同じ種類は1点まで（小物は複数可）")
    reason: list[str] = Field(
        description="そう選んだ理由（気温・湿度・降水確率の観点で）。1項目1文30字程度で、ちょうど3項目"
    )
    advice: list[str] = Field(
        description="羽織りものや傘など、持ち物のアドバイス。1項目1文30字程度で、ちょうど3項目"
    )


def arrange(outfit: Outfit, image_count: int) -> list[OutfitItem]:
    """表示用に整える: 存在しない画像番号・同じ画像の重複を除き、上に着る順に並べる"""
    seen = set()
    valid = []
    for item in outfit.items:
        if not 1 <= item.image_number <= image_count or item.image_number in seen:
            continue
        seen.add(item.image_number)
        valid.append(item)
    return sorted(valid, key=lambda it: CATEGORIES.index(it.category))  # sorted は安定ソート


MAX_BULLETS = 3  # 理由・持ち物は、それぞれ最大この行数まで表示する


def bullets(lines: list[str]) -> str:
    """箇条書き（最大 MAX_BULLETS 行）の Markdown にする。空行は除く"""
    return "\n".join(f"- {line.strip()}" for line in [l for l in lines if l.strip()][:MAX_BULLETS])
