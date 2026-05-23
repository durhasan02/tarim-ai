from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DB
from app.schemas.common import APIResponse
from app.services import weather as weather_service
from app.services.field import get_user_fields
from app.services.harvest import get_sales_summary
from app.services.planting import get_user_plantings
from app.services.stock import get_critical_stock

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=APIResponse[dict])
async def summary(current_user: CurrentUser, db: DB):
    fields = await get_user_fields(db, current_user.id)
    plantings = await get_user_plantings(db, current_user.id)
    active_plantings = [p for p in plantings if p.status == "active"]
    sales = await get_sales_summary(db, current_user.id)
    critical_stock = await get_critical_stock(db, current_user.id)

    return {
        "status": "success",
        "data": {
            "total_fields": len(fields),
            "total_area_decare": round(sum(f["area_decare"] or 0 for f in fields), 2),
            "active_plantings": len(active_plantings),
            "total_revenue": sales["total_revenue"],
            "critical_stock_count": len(critical_stock),
        },
    }


@router.get("/weather", response_model=APIResponse[dict])
async def weather(
    lat: float = Query(39.9, description="Enlem"),
    lon: float = Query(32.8, description="Boylam"),
):
    data = await weather_service.get_weather(lat, lon)
    return {"status": "success", "data": data}


@router.get("/tasks", response_model=APIResponse[dict])
async def upcoming_tasks(current_user: CurrentUser, db: DB):
    from datetime import date, timedelta
    from sqlalchemy import select
    from app.models.planting import Planting

    today = date.today()
    next_week = today + timedelta(days=7)

    result = await db.execute(
        select(Planting).where(
            Planting.user_id == current_user.id,
            Planting.status == "active",
            Planting.expected_harvest_date <= next_week,
            Planting.expected_harvest_date >= today,
        ).order_by(Planting.expected_harvest_date)
    )
    upcoming = result.scalars().all()

    tasks = [
        {
            "type": "harvest",
            "planting_id": str(p.id),
            "crop_type": p.crop_type,
            "date": str(p.expected_harvest_date),
            "message": f"{p.crop_type} hasadı yaklaşıyor",
        }
        for p in upcoming
    ]

    return {"status": "success", "data": {"tasks": tasks}}
