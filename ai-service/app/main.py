import io
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Model singleton'ları import sırasında yükleniyor
    from app.disease_detector import detector
    from app.irrigation_optimizer import optimizer
    yield


app = FastAPI(
    title="Tarım AI Servisi",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    from app.disease_detector import detector
    from app.irrigation_optimizer import optimizer
    return {
        "status": "ok",
        "disease_model": "onnx" if detector.session else "demo",
        "irrigation_model": "ml" if optimizer.pipeline else "rule_based",
    }


@app.post("/disease-detection")
async def detect_disease(
    image: UploadFile = File(...),
    field_id: str | None = Form(None),
):
    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Sadece resim dosyaları kabul edilir",
        )

    # 10MB limit
    contents = await image.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Dosya 10MB'dan büyük olamaz",
        )

    from app.disease_detector import detector
    result = detector.predict(contents)

    return {
        "status": "success",
        "data": {**result, "field_id": field_id},
    }


@app.post("/irrigation/recommendation")
async def irrigation_recommendation(body: dict):
    """
    Body:
        temperature: float
        humidity: float
        rain_forecast: float
        wind_speed: float
        soil_type: str  (clay/sandy/loamy/silty)
        crop_type: str
        days_since_irrigation: float
        planting_date: str (YYYY-MM-DD, opsiyonel)
    """
    from app.irrigation_optimizer import optimizer
    result = optimizer.recommend(body)
    return {"status": "success", "data": result}
