import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class IrrigationLog(Base):
    __tablename__ = "irrigation_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    planting_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("plantings.id"))
    field_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False)
    irrigation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    water_amount_liters: Mapped[float | None] = mapped_column(Numeric(10, 2))
    method: Mapped[str | None] = mapped_column(String(50))  # drip, sprinkler, flood, manual
    ai_recommended: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # İlişkiler
    planting: Mapped["Planting | None"] = relationship(back_populates="irrigation_logs")  # noqa: F821
    field: Mapped["Field"] = relationship(back_populates="irrigation_logs")  # noqa: F821
