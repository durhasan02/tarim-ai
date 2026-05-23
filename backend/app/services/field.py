import json
import uuid
from typing import Optional

from geoalchemy2.functions import ST_Area, ST_AsGeoJSON, ST_GeomFromGeoJSON, ST_Transform
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.field import Field
from app.models.planting import Planting
from app.models.harvest import Harvest
from app.schemas.field import FieldCreate, FieldUpdate


async def get_user_fields(db: AsyncSession, user_id: uuid.UUID) -> list[dict]:
    result = await db.execute(
        select(
            Field.id,
            Field.user_id,
            Field.name,
            ST_AsGeoJSON(Field.geometry).label("geometry_json"),
            Field.area_decare,
            Field.soil_type,
            Field.irrigation_source,
            Field.notes,
            Field.created_at,
        ).where(Field.user_id == user_id).order_by(Field.created_at.desc())
    )
    rows = result.all()
    fields = []
    for row in rows:
        fields.append({
            "id": row.id,
            "user_id": row.user_id,
            "name": row.name,
            "geometry": json.loads(row.geometry_json),
            "area_decare": float(row.area_decare) if row.area_decare else None,
            "soil_type": row.soil_type,
            "irrigation_source": row.irrigation_source,
            "notes": row.notes,
            "created_at": row.created_at,
        })
    return fields


async def get_field(db: AsyncSession, field_id: uuid.UUID, user_id: uuid.UUID) -> Optional[dict]:
    result = await db.execute(
        select(
            Field.id,
            Field.user_id,
            Field.name,
            ST_AsGeoJSON(Field.geometry).label("geometry_json"),
            Field.area_decare,
            Field.soil_type,
            Field.irrigation_source,
            Field.notes,
            Field.created_at,
        ).where(Field.id == field_id, Field.user_id == user_id)
    )
    row = result.first()
    if not row:
        return None
    return {
        "id": row.id,
        "user_id": row.user_id,
        "name": row.name,
        "geometry": json.loads(row.geometry_json),
        "area_decare": float(row.area_decare) if row.area_decare else None,
        "soil_type": row.soil_type,
        "irrigation_source": row.irrigation_source,
        "notes": row.notes,
        "created_at": row.created_at,
    }


async def create_field(db: AsyncSession, user_id: uuid.UUID, data: FieldCreate) -> dict:
    geom_json = json.dumps(data.geometry)
    geom = ST_GeomFromGeoJSON(geom_json)

    # Metrekareden dekara çevir (1 dekar = 1000 m²)
    area_m2 = await db.scalar(
        select(ST_Area(ST_Transform(geom, 3857)))
    )
    area_decare = round(area_m2 / 1000, 2) if area_m2 else None

    field = Field(
        user_id=user_id,
        name=data.name,
        geometry=geom_json,
        area_decare=area_decare,
        soil_type=data.soil_type,
        irrigation_source=data.irrigation_source,
        notes=data.notes,
    )
    db.add(field)
    await db.flush()

    return await get_field(db, field.id, user_id)


async def update_field(
    db: AsyncSession, field_id: uuid.UUID, user_id: uuid.UUID, data: FieldUpdate
) -> Optional[dict]:
    result = await db.execute(
        select(Field).where(Field.id == field_id, Field.user_id == user_id)
    )
    field = result.scalar_one_or_none()
    if not field:
        return None

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(field, key, value)

    await db.flush()
    return await get_field(db, field_id, user_id)


async def delete_field(db: AsyncSession, field_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(Field).where(Field.id == field_id, Field.user_id == user_id)
    )
    field = result.scalar_one_or_none()
    if not field:
        return False
    await db.delete(field)
    await db.flush()
    return True


async def get_field_stats(db: AsyncSession, field_id: uuid.UUID, user_id: uuid.UUID) -> Optional[dict]:
    # Önce tarlanın bu kullanıcıya ait olduğunu doğrula
    field_exists = await db.scalar(
        select(Field.id).where(Field.id == field_id, Field.user_id == user_id)
    )
    if not field_exists:
        return None

    total_plantings = await db.scalar(
        select(func.count(Planting.id)).where(Planting.field_id == field_id)
    )
    active_plantings = await db.scalar(
        select(func.count(Planting.id)).where(
            Planting.field_id == field_id, Planting.status == "active"
        )
    )
    total_harvests = await db.scalar(
        select(func.count(Harvest.id)).where(Harvest.field_id == field_id)
    )
    last_harvest = await db.scalar(
        select(func.max(Harvest.harvest_date)).where(Harvest.field_id == field_id)
    )

    return {
        "field_id": field_id,
        "total_plantings": total_plantings or 0,
        "active_plantings": active_plantings or 0,
        "total_harvests": total_harvests or 0,
        "last_harvest_date": str(last_harvest) if last_harvest else None,
    }
