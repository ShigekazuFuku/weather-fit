import requests

# WMO天気コード（数値）を日本語の天気に変換するマップ
WEATHER_CODES = {
    0: "☀️ 快晴",
    1: "🌤️ 主に晴れ",
    2: "⛅ 一部曇り",
    3: "☁️ 曇り",
    45: "🌫️ 霧",
    48: "🌫️ 霧氷",
    51: "🌦️ 弱い霧雨",
    53: "🌦️ 霧雨",
    55: "🌧️ 濃い霧雨",
    61: "🌧️ 弱い雨",
    63: "🌧️ 雨",
    65: "🌧️ 強い雨",
    71: "🌨️ 弱い雪",
    73: "🌨️ 雪",
    75: "❄️ 強い雪",
    80: "🌦️ にわか雨",
    81: "🌧️ 強いにわか雨",
    82: "⛈️ 非常に激しいにわか雨",
    95: "⛈️ 雷雨",
}

def get_today_weather(latitude=35.6895, longitude=139.6917, city_name="東京"):
    """
    Open-Meteo API を使って指定した場所の今日の天気を取得する関数
    (APIキー登録不要で利用可能)
    """
    print(f"🌍 [{city_name}] の天気情報を取得しています...")

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "relative_humidity_2m", "weather_code"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_probability_max", "weather_code"],
        "timezone": "Asia/Tokyo"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # 現在のデータ
        current_temp = data["current"]["temperature_2m"]
        current_humidity = data["current"]["relative_humidity_2m"]
        current_weather_code = data["current"]["weather_code"]
        current_weather = WEATHER_CODES.get(current_weather_code, "不明")

        # 今日の1日の予報データ
        max_temp = data["daily"]["temperature_2m_max"][0]
        min_temp = data["daily"]["temperature_2m_min"][0]
        precip_prob = data["daily"]["precipitation_probability_max"][0]

        weather_info = {
            "city": city_name,
            "current_weather": current_weather,
            "current_temp": current_temp,
            "humidity": current_humidity,
            "max_temp": max_temp,
            "min_temp": min_temp,
            "precip_prob": precip_prob
        }

        return weather_info

    except Exception as e:
        print(f"❌ 天気情報の取得に失敗しました: {e}")
        return None

if __name__ == "__main__":
    # 東京の天気を取得
    weather = get_today_weather(latitude=35.6895, longitude=139.6917, city_name="東京")

    if weather:
        print("\n--- [今日の天気予報（東京）] ---")
        print(f"天候　　: {weather['current_weather']}")
        print(f"現在気温: {weather['current_temp']} ℃")
        print(f"最高気温: {weather['max_temp']} ℃")
        print(f"最低気温: {weather['min_temp']} ℃")
        print(f"湿度　　: {weather['humidity']} %")
        print(f"降水確率: {weather['precip_prob']} %")
        print("--------------------------------\n")
        print("🎉 成功！ 天気データを正常に取得できました。")
