import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stock import StockItem, StockMovement
from app.schemas.stock import StockItemCreate, StockItemUpdate, StockMoveCreate


def _to_response(item: StockItem) -> dict:
    return {
        "id": item.id,
        "user_id": item.user_id,
        "name": item.name,
        "category": item.category,
        "quantity": float(item.quantity),
        "unit": item.unit,
        "critical_level": float(item.critical_level) if item.critical_level else None,
        "purchase_price": float(item.purchase_price) if item.purchase_price else None,
        "purchase_date": item.purchase_date,
        "expiry_date": item.expiry_date,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
        "is_critical": (
            item.critical_level is not None and float(item.quantity) <= float(item.critical_level)
        ),
    }


async def get_user_stock(db: AsyncSession, user_id: uuid.UUID) -> list[dict]:
    result = await db.execute(
        select(StockItem).where(StockItem.user_id == user_id).order_by(StockItem.name)
    )
    return [_to_response(i) for i in result.scalars().all()]


async def get_stock_item(db: AsyncSession, item_id: uuid.UUID, user_id: uuid.UUID) -> Optional[StockItem]:
    result = await db.execute(
        select(StockItem).where(StockItem.id == item_id, StockItem.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_stock_item(db: AsyncSession, user_id: uuid.UUID, data: StockItemCreate) -> dict:
    item = StockItem(user_id=user_id, **data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return _to_response(item)


async def update_stock_item(
    db: AsyncSession, item_id: uuid.UUID, user_id: uuid.UUID, data: StockItemUpdate
) -> Optional[dict]:
    item = await get_stock_item(db, item_id, user_id)
    if not item:
        return None
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(item, key, value)
    await db.flush()
    await db.refresh(item)
    return _to_response(item)


async def move_stock(
    db: AsyncSession, item_id: uuid.UUID, user_id: uuid.UUID, data: StockMoveCreate
) -> Optional[dict]:
    item = await get_stock_item(db, item_id, user_id)
    if not item:
        return None

    if data.movement_type == "out":
        item.quantity = float(item.quantity) - data.quantity
    else:
        item.quantity = float(item.quantity) + data.quantity

    movement = StockMovement(
        stock_item_id=item_id,
        movement_type=data.movement_type,
        quantity=data.quantity,
        reason=data.reason,
        planting_id=data.planting_id,
    )
    db.add(movement)
    await db.flush()
    await db.refresh(item)
    return _to_response(item)


async def get_critical_stock(db: AsyncSession, user_id: uuid.UUID) -> list[dict]:
    result = await db.execute(
        select(StockItem).where(
            StockItem.user_id == user_id,
            StockItem.critical_level.isnot(None),
            StockItem.quantity <= StockItem.critical_level,
        )
    )
    return [_to_response(i) for i in result.scalars().all()]
