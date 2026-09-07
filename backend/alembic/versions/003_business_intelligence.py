"""Add business tools & intelligence layer tables

Revision ID: 003
Revises: 002
Create Date: 2026-06-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Rebuild user_lessons with string content_id ---
    op.drop_table("user_lessons")
    op.create_table(
        "user_lessons",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("content_type", sa.String(50), nullable=False, server_default="lesson"),
        sa.Column("content_id", sa.String(255), nullable=False),
        sa.Column("completed", sa.Boolean, server_default=sa.text("false")),
        sa.Column("score", sa.DECIMAL(5, 2), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_user_lessons_user_content", "user_lessons", ["user_id", "content_type", "content_id"], unique=True)
    op.create_index("idx_user_lessons_completed", "user_lessons", ["user_id", "completed"])

    # --- invoices ---
    op.create_table(
        "invoices",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("number", sa.String(50), nullable=False),
        sa.Column("client_name", sa.String(255), nullable=False),
        sa.Column("client_email", sa.String(255), nullable=True),
        sa.Column("client_address", sa.Text, nullable=True),
        sa.Column("items", JSONB, nullable=False, server_default="[]"),
        sa.Column("subtotal", sa.DECIMAL(12, 2), nullable=False),
        sa.Column("tax_rate", sa.DECIMAL(5, 2), server_default=sa.text("0")),
        sa.Column("tax_amount", sa.DECIMAL(12, 2), server_default=sa.text("0")),
        sa.Column("total", sa.DECIMAL(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="NGN"),
        sa.Column("status", sa.String(20), server_default="draft"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_invoices_user_status", "invoices", ["user_id", "status"])

    # --- documents ---
    op.create_table(
        "documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("filename", sa.String(512), nullable=False),
        sa.Column("original_filename", sa.String(512), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("size_bytes", sa.Integer, server_default=sa.text("0")),
        sa.Column("storage_path", sa.String(1024), nullable=False),
        sa.Column("category", sa.String(50), server_default="general"),
        sa.Column("tags", JSONB, nullable=True),
        sa.Column("is_indexed", sa.Boolean, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_documents_user_category", "documents", ["user_id", "category"])

    # --- Check constraints ---
    op.create_check_constraint("ck_invoice_status", "invoices",
                                sa.text("status IN ('draft','sent','paid','overdue','cancelled')"))


def downgrade() -> None:
    op.drop_table("documents")
    op.drop_table("invoices")
    op.drop_table("user_lessons")

    op.create_table(
        "user_lessons",
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("lesson_id", UUID(as_uuid=True), primary_key=True),
        sa.Column("is_completed", sa.Boolean, server_default=sa.text("false")),
        sa.Column("quiz_score", sa.DECIMAL(5, 2), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
