import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class HealthReport(Base):
    __tablename__ = "health_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    planting_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("plantings.id"))
    field_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    detected_disease: Mapped[str | None] = mapped_column(String(255))
    disease_severity: Mapped[str | None] = mapped_column(String(20))   # low, medium, high
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 4))
    treatment_suggestion: Mapped[str | None] = mapped_column(Text)
    ai_model_version: Mapped[str | None] = mapped_column(String(50))
    reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # İlişkiler
    planting: Mapped["Planting | None"] = relationship(back_populates="health_reports")  # noqa: F821
    field: Mapped["Field"] = relationship(back_populates="health_reports")  # noqa: F821
