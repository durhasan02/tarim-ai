import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class HarvestCreate(BaseModel):
    planting_id: uuid.UUID
    field_id: uuid.UUID
    harvest_date: date
    total_amount: float
    unit: str | None = Field(None, max_length=20)
    quality_grade: str | None = Field(None, max_length=10)
    notes: str | None = None


class HarvestResponse(BaseModel):
    id: uuid.UUID
    planting_id: uuid.UUID
    field_id: uuid.UUID
    harvest_date: date
    total_amount: float
    unit: str | None
    yield_per_decare: float | None
    quality_grade: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SaleCreate(BaseModel):
    harvest_id: uuid.UUID
    sale_date: date
    amount: float
    unit: str | None = None
    unit_price: float | None = None
    buyer_name: str | None = Field(None, max_length=255)
    notes: str | None = None


class SaleResponse(BaseModel):
    id: uuid.UUID
    harvest_id: uuid.UUID
    user_id: uuid.UUID
    sale_date: date
    amount: float
    unit: str | None
    unit_price: float | None
    total_revenue: float | None
    buyer_name: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
