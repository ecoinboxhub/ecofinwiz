"""Add content & learning tables, update badges

Revision ID: 002
Revises: 001
Create Date: 2026-06-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- badge_rules ---
    op.create_table(
        "badge_rules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("key", sa.String(100), unique=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("icon_url", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Update user_badges: add badge_key, content_ref; migrate data; drop badge_type ---
    op.add_column("user_badges",
        sa.Column("badge_key", sa.String(100), nullable=True)
    )
    op.add_column("user_badges",
        sa.Column("content_ref", sa.String(255), nullable=True)
    )

    op.execute("UPDATE user_badges SET badge_key = badge_type")

    op.alter_column("user_badges", "badge_key", nullable=False)

    op.drop_index("idx_user_badges_type", table_name="user_badges")
    op.drop_column("user_badges", "badge_type")

    op.create_index("idx_user_badges_key", "user_badges",
                    ["user_id", "badge_key", "content_ref"], unique=True)

    # --- bookmarks ---
    op.create_table(
        "bookmarks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("content_type", sa.String(50), nullable=False),
        sa.Column("content_id", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_bookmarks_user", "bookmarks", ["user_id", "content_type", "content_id"], unique=True)

    # --- forum_topics ---
    op.create_table(
        "forum_topics",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("category", sa.String(100), nullable=False, index=True),
        sa.Column("tags", JSONB, nullable=True),
        sa.Column("is_pinned", sa.Boolean, server_default=sa.text("false")),
        sa.Column("is_locked", sa.Boolean, server_default=sa.text("false")),
        sa.Column("view_count", sa.Integer, server_default=sa.text("0")),
        sa.Column("reply_count", sa.Integer, server_default=sa.text("0")),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_forum_topics_category_activity", "forum_topics", ["category", "last_activity_at"])

    # --- forum_replies ---
    op.create_table(
        "forum_replies",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("topic_id", UUID(as_uuid=True), sa.ForeignKey("forum_topics.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("is_solution", sa.Boolean, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("forum_replies")
    op.drop_table("forum_topics")
    op.drop_table("bookmarks")

    op.drop_index("idx_user_badges_key", table_name="user_badges")
    op.add_column("user_badges",
        sa.Column("badge_type", sa.String(50), nullable=True)
    )
    op.execute("UPDATE user_badges SET badge_type = badge_key")
    op.alter_column("user_badges", "badge_type", nullable=False)
    op.create_index("idx_user_badges_type", "user_badges", ["user_id", "badge_type"], unique=True)
    op.drop_column("user_badges", "content_ref")
    op.drop_column("user_badges", "badge_key")

    op.drop_table("badge_rules")
