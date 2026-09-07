"""Add subscriptions, usage quotas, ad campaigns tables + plan column on users

Revision ID: 004
Revises: 003
Create Date: 2026-06-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Add plan column to users ---
    op.add_column("users", sa.Column("plan", sa.String(20), server_default="free", nullable=False))

    # --- subscriptions ---
    op.create_table(
        "subscriptions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("plan", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), server_default="active"),
        sa.Column("provider", sa.String(50), server_default="manual"),
        sa.Column("provider_ref", sa.String(255), nullable=True),
        sa.Column("current_period_start", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("auto_renew", sa.Boolean, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_check_constraint("ck_subscription_status", "subscriptions",
                                sa.text("status IN ('active', 'canceled', 'expired', 'trialing')"))
    op.create_check_constraint("ck_subscription_plan", "subscriptions",
                                sa.text("plan IN ('free', 'pro', 'business')"))

    # --- usage_quotas ---
    op.create_table(
        "usage_quotas",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("month", sa.String(7), nullable=False),
        sa.Column("ai_chats", sa.Integer, server_default=sa.text("0")),
        sa.Column("invoices_created", sa.Integer, server_default=sa.text("0")),
        sa.Column("savings_goals_created", sa.Integer, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_usage_quotas_user_month", "usage_quotas", ["user_id", "month"], unique=True)

    # --- ad_campaigns ---
    op.create_table(
        "ad_campaigns",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("advertiser_name", sa.String(255), nullable=False),
        sa.Column("image_url", sa.String(1024), nullable=False),
        sa.Column("target_url", sa.String(1024), nullable=False),
        sa.Column("cpm", sa.DECIMAL(10, 2), nullable=False),
        sa.Column("budget", sa.DECIMAL(12, 2), server_default=sa.text("0")),
        sa.Column("spent", sa.DECIMAL(12, 2), server_default=sa.text("0")),
        sa.Column("impressions_bought", sa.Integer, server_default=sa.text("0")),
        sa.Column("impressions_served", sa.Integer, server_default=sa.text("0")),
        sa.Column("target_pages", JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_ad_campaigns_active", "ad_campaigns", ["is_active", "start_date"])

    # --- ad_impressions ---
    op.create_table(
        "ad_impressions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("campaign_id", UUID(as_uuid=True), sa.ForeignKey("ad_campaigns.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", UUID(as_uuid=True), nullable=True),
        sa.Column("amount_earned", sa.DECIMAL(10, 6), server_default=sa.text("0")),
        sa.Column("served_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("ad_impressions")
    op.drop_table("ad_campaigns")
    op.drop_table("usage_quotas")
    op.drop_table("subscriptions")
    op.drop_column("users", "plan")
