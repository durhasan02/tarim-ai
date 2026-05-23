"""
Sulama optimizasyonu modülü.
scikit-learn pipeline (pkl) ile çalışır; model yoksa kural tabanlı fallback kullanır.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from app.config import IRRIGATION_MODEL_PATH

SOIL_MAP = {"clay": 0, "sandy": 1, "loamy": 2, "silty": 3}
CROP_MAP = {
    "Buğday": 0, "Mısır": 1, "Domates": 2, "Patates": 3,
    "Biber": 4, "Pamuk": 5, "Ayçiçeği": 6, "Arpa": 7,
    "Çeltik": 8, "Soğan": 9,
}
STAGE_MAP = {"seedling": 0, "vegetative": 1, "flowering": 2, "fruiting": 3, "maturity": 4}


def _growth_stage(planting_date_str: str | None) -> str:
    if not planting_date_str:
        return "vegetative"
    try:
        from datetime import date
        pd = date.fromisoformat(planting_date_str)
        days = (date.today() - pd).days
        if days < 20:
            return "seedling"
        elif days < 60:
            return "vegetative"
        elif days < 90:
            return "flowering"
        elif days < 120:
            return "fruiting"
        return "maturity"
    except Exception:
        return "vegetative"


def _rule_based(features: dict) -> float:
    """Model yokken basit kural tabanlı sulama tahmini."""
    temp = features["temperature"]
    humidity = features["humidity"]
    rain = features["rain_forecast"]
    days = features["days_since_irrigation"]

    base = 300  # litre/dekar
    if temp > 35:
        base *= 1.4
    elif temp > 28:
        base *= 1.2
    if humidity > 70:
        base *= 0.85
    if rain > 10:
        base *= max(0, 1 - rain / 30)
    if days < 2:
        base *= 0.5

    soil = features.get("soil_type", "loamy")
    soil_factor = {"clay": 0.8, "loamy": 1.0, "sandy": 1.3, "silty": 0.9}
    return max(0, base * soil_factor.get(soil, 1.0))


class IrrigationOptimizer:
    def __init__(self):
        self.pipeline = None
        self._load_model()

    def _load_model(self):
        if not Path(IRRIGATION_MODEL_PATH).exists():
            print(f"⚠️  Sulama modeli bulunamadı: {IRRIGATION_MODEL_PATH}")
            print("   Kural tabanlı mod etkin. Gerçek model için train.py çalıştırın.")
            return
        try:
            import joblib
            self.pipeline = joblib.load(IRRIGATION_MODEL_PATH)
            print(f"✓ Sulama modeli yüklendi: {IRRIGATION_MODEL_PATH}")
        except Exception as e:
            print(f"Sulama modeli yüklenemedi: {e}")

    def recommend(self, features: dict) -> dict:
        soil_enc = SOIL_MAP.get(features.get("soil_type", "loamy"), 2)
        crop_enc = CROP_MAP.get(features.get("crop_type", "Domates"), 2)
        stage = _growth_stage(features.get("planting_date"))
        stage_enc = STAGE_MAP.get(stage, 1)
        days = features.get("days_since_irrigation", 3)

        if self.pipeline is not None:
            X = np.array([[
                features.get("temperature", 25),
                features.get("humidity", 60),
                features.get("rain_forecast", 0),
                features.get("wind_speed", 10),
                soil_enc, crop_enc, days, stage_enc,
            ]], dtype=np.float32)
            water_amount = float(max(0, self.pipeline.predict(X)[0]))
            model_used = "ml"
        else:
            water_amount = _rule_based({**features, "days_since_irrigation": days})
            model_used = "rule_based"

        # Zamanlama kararı
        rain = features.get("rain_forecast", 0)
        if water_amount < 50:
            timing = "Sulama gerekmez"
            when = "not_needed"
        elif rain > 15:
            timing = f"Yağış bekleniyor ({rain}mm). Sulama 24 saat ertelenebilir."
            when = "delay_24h"
        elif features.get("temperature", 25) > 35:
            timing = "Şimdi sulayın — yüksek sıcaklık nedeniyle sabah erken veya akşam önerilir."
            when = "now"
        else:
            timing = "Bugün içinde sulayabilirsiniz."
            when = "today"

        reason_parts = []
        if features.get("temperature", 25) > 30:
            reason_parts.append(f"yüksek sıcaklık ({features['temperature']}°C)")
        if features.get("humidity", 60) < 40:
            reason_parts.append("düşük nem")
        if days > 4:
            reason_parts.append(f"son sulamadan {days} gün geçti")
        reason = "Sulama önerisi: " + (", ".join(reason_parts) or "standart periyot") + "."

        return {
            "water_amount_liters_per_decare": round(water_amount, 1),
            "timing": timing,
            "when": when,
            "growth_stage": stage,
            "reason": reason,
            "model_used": model_used,
        }


optimizer = IrrigationOptimizer()
