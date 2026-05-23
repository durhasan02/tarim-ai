import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class PlantingCreate(BaseModel):
    field_id: uuid.UUID
    crop_type: str = Field(max_length=100)
    planting_date: date
    expected_harvest_date: date | None = None
    seed_amount: float | None = None
    seed_unit: str | None = Field(None, max_length=20)
    notes: str | None = None


class PlantingUpdate(BaseModel):
    crop_type: str | None = Field(None, max_length=100)
    expected_harvest_date: date | None = None
    actual_harvest_date: date | None = None
    seed_amount: float | None = None
    seed_unit: str | None = None
    status: str | None = None  # active, harvested, failed
    notes: str | None = None


class PlantingResponse(BaseModel):
    id: uuid.UUID
    field_id: uuid.UUID
    user_id: uuid.UUID
    crop_type: str
    planting_date: date
    expected_harvest_date: date | None
    actual_harvest_date: date | None
    seed_amount: float | None
    seed_unit: str | None
    status: str
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
