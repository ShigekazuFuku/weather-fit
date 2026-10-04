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
    reason: str = Field(description="そう選んだ理由（気温・湿度・降水確率の観点で）")
    advice: str = Field(description="羽織りものや傘など、持ち物のアドバイス")


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
