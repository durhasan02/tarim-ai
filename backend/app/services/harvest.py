import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.field import Field
from app.models.harvest import Harvest
from app.models.sale import Sale
from app.schemas.harvest import HarvestCreate, SaleCreate


async def create_harvest(db: AsyncSession, user_id: uuid.UUID, data: HarvestCreate) -> Harvest:
    # Dekar başına verim hesapla
    area = await db.scalar(
        select(Field.area_decare).where(Field.id == data.field_id, Field.user_id == user_id)
    )
    yield_per_decare = None
    if area and float(area) > 0:
        yield_per_decare = round(data.total_amount / float(area), 2)

    harvest = Harvest(
        **data.model_dump(),
        yield_per_decare=yield_per_decare,
    )
    db.add(harvest)
    await db.flush()
    await db.refresh(harvest)
    return harvest


async def get_user_harvests(db: AsyncSession, user_id: uuid.UUID) -> list[Harvest]:
    result = await db.execute(
        select(Harvest)
        .join(Field, Harvest.field_id == Field.id)
        .where(Field.user_id == user_id)
        .order_by(Harvest.harvest_date.desc())
    )
    return result.scalars().all()


async def create_sale(db: AsyncSession, user_id: uuid.UUID, data: SaleCreate) -> Sale:
    total_revenue = None
    if data.unit_price and data.amount:
        total_revenue = round(data.unit_price * data.amount, 2)

    sale = Sale(
        user_id=user_id,
        total_revenue=total_revenue,
        **data.model_dump(),
    )
    db.add(sale)
    await db.flush()
    await db.refresh(sale)
    return sale


async def get_sales_summary(db: AsyncSession, user_id: uuid.UUID) -> dict:
    total_revenue = await db.scalar(
        select(func.sum(Sale.total_revenue)).where(Sale.user_id == user_id)
    )
    total_sales = await db.scalar(
        select(func.count(Sale.id)).where(Sale.user_id == user_id)
    )
    return {
        "total_revenue": float(total_revenue) if total_revenue else 0.0,
        "total_sales": total_sales or 0,
    }
