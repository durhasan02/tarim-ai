"""
Bitki hastalığı tespiti modülü.

- ONNX modeli varsa gerçek inference yapar
- Yoksa demo modu ile çalışır (geliştirme ortamı için)
"""

import io
import json
import os
import random
from pathlib import Path

import numpy as np
from PIL import Image

from app.config import DISEASE_MODEL_PATH, MODEL_VERSION

# PlantVillage 38 sınıfı ve Türkçe karşılıkları
DISEASE_LABELS = [
    "Elma — Elma Karaleke",
    "Elma — Siyah Çürüklük",
    "Elma — Sedir Elma Pası",
    "Elma — Sağlıklı",
    "Yaban Mersini — Sağlıklı",
    "Kiraz — Toz Mildiyösü",
    "Kiraz — Sağlıklı",
    "Mısır — Gri Yaprak Lekesi",
    "Mısır — Ortak Pas",
    "Mısır — Kuzey Yaprak Yanıklığı",
    "Mısır — Sağlıklı",
    "Üzüm — Siyah Çürüklük",
    "Üzüm — Esca (Siyah Kızılcık)",
    "Üzüm — Yaprak Yanıklığı",
    "Üzüm — Sağlıklı",
    "Portakal — Citrus Greening",
    "Şeftali — Bakteriyel Leke",
    "Şeftali — Sağlıklı",
    "Biber — Bakteriyel Leke",
    "Biber — Sağlıklı",
    "Patates — Erken Yanıklık",
    "Patates — Geç Yanıklık",
    "Patates — Sağlıklı",
    "Ahududu — Sağlıklı",
    "Soya — Sağlıklı",
    "Kabak — Toz Mildiyösü",
    "Çilek — Yaprak Yanıklığı",
    "Çilek — Sağlıklı",
    "Domates — Bakteriyel Leke",
    "Domates — Erken Yanıklık",
    "Domates — Geç Yanıklık",
    "Domates — Yaprak Küfü",
    "Domates — Septoria Yaprak Lekesi",
    "Domates — Örümcek Akarı",
    "Domates — Hedef Leke",
    "Domates — Sarı Yaprak Kıvrılma Virüsü",
    "Domates — Mozaik Virüsü",
    "Domates — Sağlıklı",
]

TREATMENTS = {
    "Sağlıklı": "Herhangi bir müdahale gerekmemektedir. Düzenli takibi sürdürün.",
    "Erken Yanıklık": "Mankozeb veya klorotalonil bazlı fungisit uygulayın. Alt yaprakları temizleyin.",
    "Geç Yanıklık": "Metalaxyl içerikli fungisit uygulayın. Sulama sıklığını azaltın, havalanmayı artırın.",
    "Bakteriyel Leke": "Bakır bazlı bakterisit uygulayın. Hasta bitkileri uzaklaştırın.",
    "Toz Mildiyösü": "Kükürt bazlı fungisit veya bikarbonat solüsyonu uygulayın.",
    "Yaprak Yanıklığı": "Etkilenen yaprakları budayın. Captan veya thiram bazlı fungisit kullanın.",
    "Pas": "Tebukonazol içerikli fungisit uygulayın. Bitki artıklarını imha edin.",
    "Virüs": "Vektör böcekleri kontrol edin. Hasta bitkileri imha edin, ilaç etkisi sınırlıdır.",
    "Örümcek Akarı": "Abamektin veya spiromesifen bazlı akarisit uygulayın. Yaprak altlarını ıslatın.",
    "default": "Yerel tarım danışmanınıza başvurun. Örnek göndererek laboratuvar analizi yaptırın.",
}


def _get_treatment(disease_name: str) -> str:
    for key, treatment in TREATMENTS.items():
        if key in disease_name:
            return treatment
    return TREATMENTS["default"]


def _get_severity(confidence: float) -> str:
    if confidence > 0.85:
        return "high"
    elif confidence > 0.65:
        return "medium"
    return "low"


class DiseaseDetector:
    def __init__(self):
        self.session = None
        self.labels = DISEASE_LABELS
        self._load_model()

    def _load_model(self):
        if not Path(DISEASE_MODEL_PATH).exists():
            print(f"⚠️  ONNX model bulunamadı: {DISEASE_MODEL_PATH}")
            print("   Demo modda çalışılacak. Gerçek model için train.py çalıştırın.")
            return

        try:
            import onnxruntime as ort
            self.session = ort.InferenceSession(
                DISEASE_MODEL_PATH,
                providers=["CPUExecutionProvider"],
            )

            # Metadata varsa label'ları güncelle
            meta_path = DISEASE_MODEL_PATH.replace(".onnx", "_meta.json")
            if Path(meta_path).exists():
                with open(meta_path, encoding="utf-8") as f:
                    meta = json.load(f)
                self.labels = meta.get("labels", self.labels)

            print(f"✓ ONNX model yüklendi: {DISEASE_MODEL_PATH}")
        except Exception as e:
            print(f"Model yüklenemedi: {e} — demo modda devam ediliyor.")

    def _preprocess(self, image_bytes: bytes) -> np.ndarray:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize((224, 224), Image.BILINEAR)
        arr = np.array(img, dtype=np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        arr = (arr - mean) / std
        return arr.transpose(2, 0, 1)[np.newaxis, :]  # (1, 3, 224, 224)

    def predict(self, image_bytes: bytes) -> dict:
        if self.session is None:
            return self._demo_predict()

        inp = self._preprocess(image_bytes).astype(np.float32)
        logits = self.session.run(["logits"], {"image": inp})[0][0]

        # Softmax
        exp = np.exp(logits - logits.max())
        probs = exp / exp.sum()

        top_idx = int(probs.argmax())
        confidence = float(probs[top_idx])
        disease_name = self.labels[top_idx] if top_idx < len(self.labels) else "Bilinmiyor"

        # Top-3 benzer hastalıklar
        top3_idx = probs.argsort()[-3:][::-1]
        similar = [
            self.labels[i] for i in top3_idx[1:]
            if i < len(self.labels)
        ]

        return {
            "detected_disease": disease_name,
            "severity": _get_severity(confidence),
            "confidence": round(confidence, 4),
            "treatment": _get_treatment(disease_name),
            "similar_diseases": similar,
            "model_version": MODEL_VERSION,
        }

    def _demo_predict(self) -> dict:
        """Model yokken demo yanıt üret (geliştirme ortamı için)."""
        diseases = [
            ("Domates — Geç Yanıklık", 0.923),
            ("Domates — Erken Yanıklık", 0.871),
            ("Patates — Geç Yanıklık", 0.845),
            ("Domates — Sağlıklı", 0.962),
            ("Biber — Bakteriyel Leke", 0.788),
        ]
        disease_name, base_conf = random.choice(diseases)
        confidence = round(base_conf + random.uniform(-0.05, 0.05), 4)

        return {
            "detected_disease": disease_name,
            "severity": _get_severity(confidence),
            "confidence": confidence,
            "treatment": _get_treatment(disease_name),
            "similar_diseases": random.sample(
                [d for d, _ in diseases if d != disease_name], 2
            ),
            "model_version": "demo",
            "demo_mode": True,
        }


# Singleton
detector = DiseaseDetector()
