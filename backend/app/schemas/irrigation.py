import uuid
from datetime import datetime

from pydantic import BaseModel


class IrrigationCreate(BaseModel):
    field_id: uuid.UUID
    planting_id: uuid.UUID | None = None
    irrigation_date: datetime
    duration_minutes: int | None = None
    water_amount_liters: float | None = None
    method: str | None = None  # drip, sprinkler, flood, manual
    notes: str | None = None


class IrrigationResponse(BaseModel):
    id: uuid.UUID
    field_id: uuid.UUID
    planting_id: uuid.UUID | None
    irrigation_date: datetime
    duration_minutes: int | None
    water_amount_liters: float | None
    method: str | None
    ai_recommended: bool
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
