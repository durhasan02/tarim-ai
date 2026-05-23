import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Harvest(Base):
    __tablename__ = "harvests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    planting_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("plantings.id"), nullable=False)
    field_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False)
    harvest_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(20))       # kg, ton, adet
    yield_per_decare: Mapped[float | None] = mapped_column(Numeric(10, 2))
    quality_grade: Mapped[str | None] = mapped_column(String(10))  # A, B, C
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # İlişkiler
    planting: Mapped["Planting"] = relationship(back_populates="harvests")  # noqa: F821
    field: Mapped["Field"] = relationship(back_populates="harvests")  # noqa: F821
    sales: Mapped[list["Sale"]] = relationship(back_populates="harvest", cascade="all, delete-orphan")  # noqa: F821
