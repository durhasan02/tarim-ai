"""
Sulama optimizasyonu — Gradient Boosting Regressor eğitimi.

Gerçek veri yokken sentetik veri ile başlar.
Gerçek veri hazır olduğunda CSV yolu verin: --data-csv irrigation_data.csv

CSV beklentisi (sütunlar):
    temperature, humidity, rain_forecast, wind_speed,
    soil_type, crop_type, days_since_irrigation, growth_stage,
    water_needed_liters_per_decare  ← hedef değişken

Kullanım:
    python train.py                          # sentetik veri
    python train.py --data-csv mydata.csv    # gerçek veri
"""

import argparse
import json
import os

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# ── Kodlama haritaları ────────────────────────────────────────────────────
SOIL_MAP = {"clay": 0, "sandy": 1, "loamy": 2, "silty": 3}
CROP_MAP = {
    "Buğday": 0, "Mısır": 1, "Domates": 2, "Patates": 3,
    "Biber": 4, "Pamuk": 5, "Ayçiçeği": 6, "Arpa": 7,
    "Çeltik": 8, "Soğan": 9,
}
STAGE_MAP = {"seedling": 0, "vegetative": 1, "flowering": 2, "fruiting": 3, "maturity": 4}

# Model kayıt yolu
MODEL_OUTPUT = os.path.join(os.path.dirname(__file__), "../../ai-service/models/irrigation_model.pkl")
META_OUTPUT = os.path.join(os.path.dirname(__file__), "../../ai-service/models/irrigation_meta.json")


def encode_features(rows: list[dict]) -> np.ndarray:
    X = []
    for r in rows:
        X.append([
            r["temperature"],
            r["humidity"],
            r["rain_forecast"],
            r["wind_speed"],
            SOIL_MAP.get(r["soil_type"], 2),
            CROP_MAP.get(r["crop_type"], 2),
            r["days_since_irrigation"],
            STAGE_MAP.get(r["growth_stage"], 1),
        ])
    return np.array(X, dtype=np.float32)


def generate_synthetic_data(n: int = 5000) -> tuple[np.ndarray, np.ndarray]:
    """FAO-56 Penman-Monteith ilhamıyla sentetik sulama verisi üretir."""
    rng = np.random.default_rng(42)
    rows, targets = [], []

    for _ in range(n):
        temp = rng.uniform(10, 42)
        humidity = rng.uniform(20, 95)
        rain = rng.uniform(0, 30)
        wind = rng.uniform(0, 60)
        soil = rng.choice(list(SOIL_MAP.keys()))
        crop = rng.choice(list(CROP_MAP.keys()))
        days = rng.integers(0, 10)
        stage = rng.choice(list(STAGE_MAP.keys()))

        # Basit fizik tabanlı hedef (gerçek modelde FAO verisiyle değiştirilir)
        et0 = 0.0023 * (temp + 17.8) * (42 - humidity / 3) * 0.5
        kc = {"seedling": 0.6, "vegetative": 1.0, "flowering": 1.15, "fruiting": 1.1, "maturity": 0.8}[stage]
        etc = et0 * kc
        pe = max(0, rain * 0.75)
        soil_factor = {"clay": 0.8, "loamy": 1.0, "sandy": 1.3, "silty": 0.9}[soil]
        base = max(0, (etc - pe / days if days > 0 else etc) * 1000 * soil_factor)

        # Gürültü ekle
        water = max(0, base + rng.normal(0, 50))
        if rain > 15:
            water = 0  # Yağmur yeterliyse sulama gerekmez

        rows.append({
            "temperature": temp, "humidity": humidity, "rain_forecast": rain,
            "wind_speed": wind, "soil_type": soil, "crop_type": crop,
            "days_since_irrigation": float(days), "growth_stage": stage,
        })
        targets.append(water)

    return encode_features(rows), np.array(targets, dtype=np.float32)


def train(args):
    if args.data_csv and os.path.exists(args.data_csv):
        import csv
        rows, targets = [], []
        with open(args.data_csv, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                targets.append(float(row.pop("water_needed_liters_per_decare")))
                row["days_since_irrigation"] = float(row["days_since_irrigation"])
                rows.append(row)
        X = encode_features(rows)
        y = np.array(targets)
        print(f"Gerçek veri yüklendi: {len(y)} örnek")
    else:
        print("Sentetik veri üretiliyor...")
        X, y = generate_synthetic_data(5000)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", GradientBoostingRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=5,
            min_samples_split=10,
            random_state=42,
        )),
    ])

    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    print(f"MAE: {mae:.2f} litre/dekar | R²: {r2:.4f}")

    os.makedirs(os.path.dirname(MODEL_OUTPUT), exist_ok=True)
    joblib.dump(pipeline, MODEL_OUTPUT)

    meta = {
        "soil_map": SOIL_MAP,
        "crop_map": CROP_MAP,
        "stage_map": STAGE_MAP,
        "features": ["temperature", "humidity", "rain_forecast", "wind_speed",
                     "soil_type", "crop_type", "days_since_irrigation", "growth_stage"],
        "mae": round(mae, 2),
        "r2": round(r2, 4),
    }
    with open(META_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"Model kaydedildi: {MODEL_OUTPUT}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-csv", default=None)
    args = parser.parse_args()
    train(args)
