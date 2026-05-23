import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FieldCreate(BaseModel):
    name: str = Field(max_length=255)
    geometry: dict[str, Any]  # GeoJSON Polygon
    soil_type: str | None = None      # clay, sandy, loamy, silty
    irrigation_source: str | None = None  # rain, drip, sprinkler, flood
    notes: str | None = None


class FieldUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    soil_type: str | None = None
    irrigation_source: str | None = None
    notes: str | None = None


class FieldResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    geometry: dict[str, Any]
    area_decare: float | None
    soil_type: str | None
    irrigation_source: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FieldStats(BaseModel):
    field_id: uuid.UUID
    total_plantings: int
    active_plantings: int
    total_harvests: int
    last_harvest_date: str | None
