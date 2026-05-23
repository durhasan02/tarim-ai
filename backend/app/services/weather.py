import httpx

from app.core.config import settings


async def get_weather(lat: float, lon: float) -> dict:
    if not settings.OPENWEATHERMAP_API_KEY:
        return _mock_weather()

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": settings.OPENWEATHERMAP_API_KEY,
        "units": "metric",
        "lang": "tr",
        "cnt": 40,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        raw = resp.json()

    return _parse_weather(raw)


def _parse_weather(raw: dict) -> dict:
    forecasts = []
    alerts = []

    for item in raw.get("list", [])[:8]:  # 24 saatlik (3h * 8)
        temp = item["main"]["temp"]
        rain = item.get("rain", {}).get("3h", 0)
        wind = item["wind"]["speed"] * 3.6  # m/s → km/h
        desc = item["weather"][0]["description"]

        forecasts.append({
            "time": item["dt_txt"],
            "temp": round(temp, 1),
            "humidity": item["main"]["humidity"],
            "rain_mm": round(rain, 1),
            "wind_kmh": round(wind, 1),
            "description": desc,
        })

        # Uyarı kuralları
        if temp > 38:
            alerts.append({"type": "heat", "message": f"Yüksek sıcaklık uyarısı: {temp}°C"})
        if wind > 50:
            alerts.append({"type": "wind", "message": f"Kuvvetli rüzgar uyarısı: {round(wind)}km/h"})
        if rain > 20:
            alerts.append({"type": "rain", "message": f"Yoğun yağış uyarısı: {rain}mm"})

    return {"forecasts": forecasts, "alerts": alerts, "city": raw.get("city", {}).get("name", "")}


def _mock_weather() -> dict:
    return {
        "forecasts": [
            {"time": "Demo", "temp": 22, "humidity": 55, "rain_mm": 0, "wind_kmh": 12, "description": "Açık"},
        ],
        "alerts": [],
        "city": "Demo (API anahtarı yok)",
    }
