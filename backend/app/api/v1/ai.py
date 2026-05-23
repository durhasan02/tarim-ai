"""
Ana backend'den AI servisine proxy/gateway endpoint'leri.
Frontend sadece :8000'e konuşur; AI servisi arka planda :8001'de çalışır.
"""

import uuid

import httpx
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status

from app.api.deps import CurrentUser, DB
from app.core.config import settings
from app.models.health import HealthReport
from app.services.planting import get_planting

router = APIRouter(prefix="/ai", tags=["ai"])

AI_URL = settings.AI_SERVICE_URL


async def _ai_post(path: str, **kwargs) -> dict:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{AI_URL}{path}", **kwargs)
            resp.raise_for_status()
            return resp.json()
    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI servisi şu an erişilemiyor",
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))


@router.post("/disease-detection")
async def disease_detection(
    current_user: CurrentUser,
    db: DB,
    image: UploadFile = File(...),
    field_id: str | None = Form(None),
    planting_id: str | None = Form(None),
):
    contents = await image.read()

    result = await _ai_post(
        "/disease-detection",
        files={"image": (image.filename, contents, image.content_type)},
        data={"field_id": field_id or ""},
    )

    ai_data = result.get("data", {})

    # Sonucu DB'ye kaydet
    if field_id:
        try:
            fid = uuid.UUID(field_id)
            pid = uuid.UUID(planting_id) if planting_id else None

            # Fotoğrafı media'ya kaydet (basit versiyon)
            import os
            media_path = f"media/health/{uuid.uuid4()}{os.path.splitext(image.filename or '.jpg')[1]}"
            os.makedirs(os.path.dirname(media_path), exist_ok=True)
            with open(media_path, "wb") as f:
                f.write(contents)

            report = HealthReport(
                field_id=fid,
                planting_id=pid,
                image_url=f"/{media_path}",
                detected_disease=ai_data.get("detected_disease"),
                disease_severity=ai_data.get("severity"),
                confidence_score=ai_data.get("confidence"),
                treatment_suggestion=ai_data.get("treatment"),
                ai_model_version=ai_data.get("model_version", "1.0.0"),
            )
            db.add(report)
        except Exception:
            pass  # Kayıt başarısız olsa da sonuç döndür

    return {"status": "success", "data": ai_data}


@router.get("/irrigation/recommendation")
async def irrigation_recommendation(
    current_user: CurrentUser,
    db: DB,
    field_id: uuid.UUID = Query(...),
    planting_id: uuid.UUID | None = Query(None),
):
    from app.services.field import get_field
    from app.services.weather import get_weather

    field = await get_field(db, field_id, current_user.id)
    if not field:
        raise HTTPException(status_code=404, detail="Tarla bulunamadı")

    planting = None
    if planting_id:
        planting = await get_planting(db, planting_id, current_user.id)

    # Hava durumu (Türkiye merkezi koordinat — idealde tarladan alınmalı)
    weather = await get_weather(39.0, 35.0)
    forecast = weather.get("forecasts", [{}])[0] if weather.get("forecasts") else {}

    payload = {
        "temperature": forecast.get("temp", 25),
        "humidity": forecast.get("humidity", 60),
        "rain_forecast": forecast.get("rain_mm", 0),
        "wind_speed": forecast.get("wind_kmh", 10),
        "soil_type": field.get("soil_type") or "loamy",
        "crop_type": planting.crop_type if planting else "Domates",
        "days_since_irrigation": 3,
        "planting_date": str(planting.planting_date) if planting else None,
    }

    result = await _ai_post("/irrigation/recommendation", json=payload)
    return {"status": "success", "data": result.get("data", {})}
