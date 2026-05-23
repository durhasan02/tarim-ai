import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Field(Base):
    __tablename__ = "fields"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    geometry: Mapped[object] = mapped_column(Geometry("POLYGON", srid=4326), nullable=False)
    area_decare: Mapped[float | None] = mapped_column(Numeric(10, 2))
    soil_type: Mapped[str | None] = mapped_column(String(50))       # clay, sandy, loamy, silty
    irrigation_source: Mapped[str | None] = mapped_column(String(50))  # rain, drip, sprinkler, flood
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # İlişkiler
    user: Mapped["User"] = relationship(back_populates="fields")  # noqa: F821
    plantings: Mapped[list["Planting"]] = relationship(back_populates="field", cascade="all, delete-orphan")  # noqa: F821
    irrigation_logs: Mapped[list["IrrigationLog"]] = relationship(back_populates="field")  # noqa: F821
    health_reports: Mapped[list["HealthReport"]] = relationship(back_populates="field")  # noqa: F821
    harvests: Mapped[list["Harvest"]] = relationship(back_populates="field")  # noqa: F821
