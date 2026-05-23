import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.planting import Planting
from app.models.irrigation import IrrigationLog
from app.schemas.planting import PlantingCreate, PlantingUpdate
from app.schemas.irrigation import IrrigationCreate


async def get_user_plantings(db: AsyncSession, user_id: uuid.UUID, field_id: uuid.UUID | None = None) -> list[Planting]:
    q = select(Planting).where(Planting.user_id == user_id)
    if field_id:
        q = q.where(Planting.field_id == field_id)
    result = await db.execute(q.order_by(Planting.planting_date.desc()))
    return result.scalars().all()


async def get_planting(db: AsyncSession, planting_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Planting]:
    result = await db.execute(
        select(Planting).where(Planting.id == planting_id, Planting.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_planting(db: AsyncSession, user_id: uuid.UUID, data: PlantingCreate) -> Planting:
    planting = Planting(user_id=user_id, **data.model_dump())
    db.add(planting)
    await db.flush()
    await db.refresh(planting)
    return planting


async def update_planting(
    db: AsyncSession, planting_id: uuid.UUID, user_id: uuid.UUID, data: PlantingUpdate
) -> Optional[Planting]:
    planting = await get_planting(db, planting_id, user_id)
    if not planting:
        return None
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(planting, key, value)
    await db.flush()
    await db.refresh(planting)
    return planting


async def get_irrigation_logs(db: AsyncSession, planting_id: uuid.UUID) -> list[IrrigationLog]:
    result = await db.execute(
        select(IrrigationLog)
        .where(IrrigationLog.planting_id == planting_id)
        .order_by(IrrigationLog.irrigation_date.desc())
    )
    return result.scalars().all()


async def add_irrigation_log(
    db: AsyncSession, planting_id: uuid.UUID, data: IrrigationCreate
) -> IrrigationLog:
    log = IrrigationLog(planting_id=planting_id, **data.model_dump())
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log
