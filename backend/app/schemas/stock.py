import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class StockItemCreate(BaseModel):
    name: str = Field(max_length=255)
    category: str | None = None  # fertilizer, pesticide, herbicide, equipment
    quantity: float
    unit: str | None = Field(None, max_length=20)
    critical_level: float | None = None
    purchase_price: float | None = None
    purchase_date: date | None = None
    expiry_date: date | None = None


class StockItemUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    category: str | None = None
    quantity: float | None = None
    unit: str | None = None
    critical_level: float | None = None
    purchase_price: float | None = None
    expiry_date: date | None = None


class StockMoveCreate(BaseModel):
    movement_type: str  # in, out
    quantity: float
    reason: str | None = None  # purchase, use, waste
    planting_id: uuid.UUID | None = None


class StockItemResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    category: str | None
    quantity: float
    unit: str | None
    critical_level: float | None
    purchase_price: float | None
    purchase_date: date | None
    expiry_date: date | None
    created_at: datetime
    updated_at: datetime
    is_critical: bool = False

    model_config = {"from_attributes": True}
