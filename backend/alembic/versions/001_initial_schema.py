"""Initial schema - tüm tablolar

Revision ID: 001
Revises:
Create Date: 2026-04-05

"""
from typing import Sequence, Union

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostGIS extension
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255)),
        sa.Column("phone", sa.String(20)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # fields
    op.create_table(
        "fields",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("geometry", geoalchemy2.types.Geometry("POLYGON", srid=4326), nullable=False),
        sa.Column("area_decare", sa.Numeric(10, 2)),
        sa.Column("soil_type", sa.String(50)),
        sa.Column("irrigation_source", sa.String(50)),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_fields_user_id", "fields", ["user_id"])
    op.execute("CREATE INDEX IF NOT EXISTS idx_fields_geometry ON fields USING GIST(geometry)")

    # plantings
    op.create_table(
        "plantings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("field_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fields.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("crop_type", sa.String(100), nullable=False),
        sa.Column("planting_date", sa.Date, nullable=False),
        sa.Column("expected_harvest_date", sa.Date),
        sa.Column("actual_harvest_date", sa.Date),
        sa.Column("seed_amount", sa.Numeric(10, 2)),
        sa.Column("seed_unit", sa.String(20)),
        sa.Column("status", sa.String(20), server_default="active"),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # irrigation_logs
    op.create_table(
        "irrigation_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("planting_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("plantings.id")),
        sa.Column("field_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fields.id"), nullable=False),
        sa.Column("irrigation_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_minutes", sa.Integer),
        sa.Column("water_amount_liters", sa.Numeric(10, 2)),
        sa.Column("method", sa.String(50)),
        sa.Column("ai_recommended", sa.Boolean, server_default="false"),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # stock_items
    op.create_table(
        "stock_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(50)),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit", sa.String(20)),
        sa.Column("critical_level", sa.Numeric(10, 2)),
        sa.Column("purchase_price", sa.Numeric(10, 2)),
        sa.Column("purchase_date", sa.Date),
        sa.Column("expiry_date", sa.Date),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # stock_movements
    op.create_table(
        "stock_movements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("stock_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stock_items.id"), nullable=False),
        sa.Column("movement_type", sa.String(20), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("reason", sa.String(255)),
        sa.Column("planting_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("plantings.id")),
        sa.Column("movement_date", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # health_reports
    op.create_table(
        "health_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("planting_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("plantings.id")),
        sa.Column("field_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fields.id"), nullable=False),
        sa.Column("image_url", sa.String(500), nullable=False),
        sa.Column("detected_disease", sa.String(255)),
        sa.Column("disease_severity", sa.String(20)),
        sa.Column("confidence_score", sa.Numeric(5, 4)),
        sa.Column("treatment_suggestion", sa.Text),
        sa.Column("ai_model_version", sa.String(50)),
        sa.Column("reported_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # harvests
    op.create_table(
        "harvests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("planting_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("plantings.id"), nullable=False),
        sa.Column("field_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fields.id"), nullable=False),
        sa.Column("harvest_date", sa.Date, nullable=False),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit", sa.String(20)),
        sa.Column("yield_per_decare", sa.Numeric(10, 2)),
        sa.Column("quality_grade", sa.String(10)),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # sales
    op.create_table(
        "sales",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("harvest_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("harvests.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("sale_date", sa.Date, nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit", sa.String(20)),
        sa.Column("unit_price", sa.Numeric(10, 2)),
        sa.Column("total_revenue", sa.Numeric(12, 2)),
        sa.Column("buyer_name", sa.String(255)),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # weather_cache
    op.create_table(
        "weather_cache",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("latitude", sa.Numeric(10, 7)),
        sa.Column("longitude", sa.Numeric(10, 7)),
        sa.Column("forecast_data", postgresql.JSONB),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("weather_cache")
    op.drop_table("sales")
    op.drop_table("harvests")
    op.drop_table("health_reports")
    op.drop_table("stock_movements")
    op.drop_table("stock_items")
    op.drop_table("irrigation_logs")
    op.drop_table("plantings")
    op.drop_index("idx_fields_geometry", table_name="fields")
    op.drop_index("ix_fields_user_id", table_name="fields")
    op.drop_table("fields")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
