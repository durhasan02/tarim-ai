import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Planting(Base):
    __tablename__ = "plantings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    crop_type: Mapped[str] = mapped_column(String(100), nullable=False)
    planting_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_harvest_date: Mapped[date | None] = mapped_column(Date)
    actual_harvest_date: Mapped[date | None] = mapped_column(Date)
    seed_amount: Mapped[float | None] = mapped_column(Numeric(10, 2))
    seed_unit: Mapped[str | None] = mapped_column(String(20))    # kg, adet
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, harvested, failed
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # İlişkiler
    field: Mapped["Field"] = relationship(back_populates="plantings")  # noqa: F821
    user: Mapped["User"] = relationship(back_populates="plantings")  # noqa: F821
    irrigation_logs: Mapped[list["IrrigationLog"]] = relationship(back_populates="planting")  # noqa: F821
    health_reports: Mapped[list["HealthReport"]] = relationship(back_populates="planting")  # noqa: F821
    harvests: Mapped[list["Harvest"]] = relationship(back_populates="planting")  # noqa: F821
    stock_movements: Mapped[list["StockMovement"]] = relationship(back_populates="planting")  # noqa: F821
