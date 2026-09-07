"""Initial database tables

Revision ID: 001
Revises:
Create Date: 2026-06-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("avatar_url", sa.String(512), nullable=True),
        sa.Column("persona_type", sa.String(50), nullable=True),
        sa.Column("onboarding_completed", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("is_admin", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_users_email", "users", ["email"])
    op.create_index("idx_users_persona_type", "users", ["persona_type"])
    op.create_index("idx_users_created_at", "users", ["created_at"])

    op.create_table(
        "oauth_accounts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("provider_id", sa.String(255), nullable=False),
    )
    op.create_index("idx_oauth_provider", "oauth_accounts", ["provider", "provider_id"], unique=True)

    op.create_table(
        "refresh_tokens",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_refresh_tokens_expires", "refresh_tokens", ["expires_at"])

    op.create_table(
        "user_preferences",
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("currency", sa.String(3), server_default=sa.text("'NGN'")),
        sa.Column("language", sa.String(10), server_default=sa.text("'en'")),
        sa.Column("notification_push", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("notification_email", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("notification_daily_tip", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("notification_budget_alert", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "onboarding_answers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("step", sa.String(50), nullable=False),
        sa.Column("answers", JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_onboarding_answers_user_id", "onboarding_answers", ["user_id"])

    op.create_table(
        "budgets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("monthly_limit", sa.DECIMAL(12, 2), nullable=True),
        sa.Column("percentage_limit", sa.DECIMAL(5, 2), nullable=True),
        sa.Column("is_adaptive", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_budgets_user_id", "budgets", ["user_id"])

    op.create_table(
        "categories",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("type", sa.String(10), nullable=True),
    )
    op.create_index("idx_categories_user_name", "categories", ["user_id", "name"], unique=True)

    op.create_table(
        "transactions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("budget_id", UUID(as_uuid=True), sa.ForeignKey("budgets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("type", sa.String(10), nullable=False),
        sa.Column("amount", sa.DECIMAL(12, 2), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("transaction_date", sa.Date, nullable=False),
        sa.Column("is_recurring", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("type IN ('income', 'expense')", name="ck_transaction_type"),
    )
    op.create_index("idx_transactions_user_date", "transactions", ["user_id", "transaction_date"])
    op.create_index("idx_transactions_user_category", "transactions", ["user_id", "category"])
    op.create_index("idx_transactions_user_type", "transactions", ["user_id", "type"])

    op.create_table(
        "savings_goals",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("target_amount", sa.DECIMAL(12, 2), nullable=False),
        sa.Column("current_amount", sa.DECIMAL(12, 2), server_default=sa.text("0")),
        sa.Column("target_date", sa.Date, nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("is_completed", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_savings_goals_user_id", "savings_goals", ["user_id"])
    op.create_index("idx_savings_goals_completed", "savings_goals", ["user_id", "is_completed"])

    op.create_table(
        "savings_contributions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("goal_id", UUID(as_uuid=True), sa.ForeignKey("savings_goals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.DECIMAL(12, 2), nullable=False),
        sa.Column("note", sa.Text, nullable=True),
        sa.Column("contributed_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_savings_contributions_goal_id", "savings_contributions", ["goal_id"])

    op.create_table(
        "ai_conversations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("is_archived", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("type IN ('advisor', 'mentor')", name="ck_conversation_type"),
    )
    op.create_index("idx_ai_conversations_user", "ai_conversations", ["user_id", "updated_at"])

    op.create_table(
        "ai_messages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("conversation_id", UUID(as_uuid=True), sa.ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("rating", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name="ck_message_role"),
        sa.CheckConstraint("rating BETWEEN 1 AND 5", name="ck_message_rating"),
    )
    op.create_index("idx_ai_messages_conversation", "ai_messages", ["conversation_id", "created_at"])

    op.create_table(
        "business_plans",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", JSONB, nullable=False),
        sa.Column("status", sa.String(20), server_default=sa.text("'draft'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("status IN ('draft', 'completed')", name="ck_business_plan_status"),
    )
    op.create_index("idx_business_plans_user_id", "business_plans", ["user_id"])

    op.create_table(
        "tasks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), server_default=sa.text("'pending'")),
        sa.Column("priority", sa.String(10), server_default=sa.text("'medium'")),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("assigned_to", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("status IN ('pending', 'in_progress', 'completed')", name="ck_task_status"),
        sa.CheckConstraint("priority IN ('low', 'medium', 'high')", name="ck_task_priority"),
    )
    op.create_index("idx_tasks_user_status", "tasks", ["user_id", "status"])

    op.create_table(
        "user_lessons",
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("lesson_id", UUID(as_uuid=True), primary_key=True),
        sa.Column("is_completed", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("quiz_score", sa.DECIMAL(5, 2), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_user_lessons_completed", "user_lessons", ["user_id", "is_completed"])

    op.create_table(
        "user_badges",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("badge_type", sa.String(50), nullable=False),
        sa.Column("earned_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_user_badges_user_id", "user_badges", ["user_id"])
    op.create_index("idx_user_badges_type", "user_badges", ["user_id", "badge_type"], unique=True)

    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("data", JSONB, nullable=True),
        sa.Column("is_read", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_notifications_user", "notifications", ["user_id", "is_read", "created_at"])

    op.create_table(
        "device_tokens",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token", sa.String(512), nullable=False, unique=True),
        sa.Column("platform", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_device_tokens_user_id", "device_tokens", ["user_id"])


def downgrade() -> None:
    op.drop_table("device_tokens")
    op.drop_table("notifications")
    op.drop_table("user_badges")
    op.drop_table("user_lessons")
    op.drop_table("tasks")
    op.drop_table("business_plans")
    op.drop_table("ai_messages")
    op.drop_table("ai_conversations")
    op.drop_table("savings_contributions")
    op.drop_table("savings_goals")
    op.drop_table("transactions")
    op.drop_table("categories")
    op.drop_table("budgets")
    op.drop_table("onboarding_answers")
    op.drop_table("user_preferences")
    op.drop_table("refresh_tokens")
    op.drop_table("oauth_accounts")
    op.drop_table("users")
