import uuid
from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import (
    Boolean, CheckConstraint, Column, Date, DateTime, DECIMAL, ForeignKey,
    Index, Integer, String, Text, func, JSON, text,
)
from typing import Any
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    persona_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    plan: Mapped[str] = mapped_column(String(20), default="free")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    oauth_accounts = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    savings_goals = relationship("SavingsGoal", back_populates="user", cascade="all, delete-orphan")
    ai_conversations = relationship("AIConversation", back_populates="user", cascade="all, delete-orphan")
    business_plans = relationship("BusinessPlan", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    device_tokens = relationship("DeviceToken", back_populates="user", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_users_created_at", "created_at"),
    )


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False)

    user = relationship("User", back_populates="oauth_accounts")

    __table_args__ = (
        Index("idx_oauth_provider", "provider", "provider_id", unique=True),
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="refresh_tokens")

    __table_args__ = (
        Index("idx_refresh_tokens_expires", "expires_at"),
    )


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    currency: Mapped[str] = mapped_column(String(3), default="NGN")
    language: Mapped[str] = mapped_column(String(10), default="en")
    notification_push: Mapped[bool] = mapped_column(Boolean, default=True)
    notification_email: Mapped[bool] = mapped_column(Boolean, default=False)
    notification_daily_tip: Mapped[bool] = mapped_column(Boolean, default=True)
    notification_budget_alert: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="preferences")


class OnboardingAnswer(Base):
    __tablename__ = "onboarding_answers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    step: Mapped[str] = mapped_column(String(50), nullable=False)
    answers: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    monthly_limit: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2), nullable=True)
    percentage_limit: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), nullable=True)
    is_adaptive: Mapped[bool] = mapped_column(Boolean, default=False)
    start_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="budgets")
    transactions = relationship("Transaction", back_populates="budget")

    __table_args__ = (
        Index("idx_budgets_active", "user_id", "start_date", postgresql_where=text("end_date IS NULL OR end_date >= CURRENT_DATE")),
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    __table_args__ = (
        Index("idx_categories_user_name", "user_id", "name", unique=True),
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    budget_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("budgets.id", ondelete="SET NULL"), nullable=True)
    type: Mapped[str] = mapped_column(String(10), nullable=False)
    amount: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    transaction_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="transactions")
    budget = relationship("Budget", back_populates="transactions")

    __table_args__ = (
        CheckConstraint("type IN ('income', 'expense')", name="ck_transaction_type"),
        Index("idx_transactions_user_date", "user_id", "transaction_date"),
        Index("idx_transactions_user_category", "user_id", "category"),
        Index("idx_transactions_user_type", "user_id", "type"),
    )


class SavingsGoal(Base):
    __tablename__ = "savings_goals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_amount: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    current_amount: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0)
    target_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="savings_goals")
    contributions = relationship("SavingsContribution", back_populates="goal", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_savings_goals_completed", "user_id", "is_completed"),
    )


class SavingsContribution(Base):
    __tablename__ = "savings_contributions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("savings_goals.id", ondelete="CASCADE"), index=True)
    amount: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contributed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    goal = relationship("SavingsGoal", back_populates="contributions")


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="ai_conversations")
    messages = relationship("AIMessage", back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("type IN ('advisor', 'mentor', 'investment')", name="ck_conversation_type"),
        Index("idx_ai_conversations_user", "user_id", "updated_at"),
    )


class AIMessage(Base):
    __tablename__ = "ai_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_conversations.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    extra_data: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, nullable=True)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("AIConversation", back_populates="messages")

    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name="ck_message_role"),
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_message_rating"),
        Index("idx_ai_messages_conversation", "conversation_id", "created_at"),
    )


class BusinessPlan(Base):
    __tablename__ = "business_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="business_plans")

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'completed')", name="ck_business_plan_status"),
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    priority: Mapped[str] = mapped_column(String(10), default="medium")
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    assigned_to: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="tasks")

    __table_args__ = (
        CheckConstraint("status IN ('pending', 'in_progress', 'completed')", name="ck_task_status"),
        CheckConstraint("priority IN ('low', 'medium', 'high')", name="ck_task_priority"),
        Index("idx_tasks_user_status", "user_id", "status"),
    )


class UserLesson(Base):
    __tablename__ = "user_lessons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    content_type: Mapped[str] = mapped_column(String(50), default="lesson")
    content_id: Mapped[str] = mapped_column(String(255), nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    score: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_user_lessons_user_content", "user_id", "content_type", "content_id", unique=True),
        Index("idx_user_lessons_completed", "user_id", "completed"),
    )


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    number: Mapped[str] = mapped_column(String(50), nullable=False)
    client_name: Mapped[str] = mapped_column(String(255), nullable=False)
    client_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    client_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    items: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)
    subtotal: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    tax_rate: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0)
    tax_amount: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0)
    total: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="NGN")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="invoices")

    __table_args__ = (
        CheckConstraint("status IN ('draft','sent','paid','overdue','cancelled')", name="ck_invoice_status"),
        Index("idx_invoices_user_status", "user_id", "status"),
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="general")
    tags: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    is_indexed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="documents")

    __table_args__ = (
        Index("idx_documents_user_category", "user_id", "category"),
    )


class BadgeRule(Base):
    __tablename__ = "badge_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserBadge(Base):
    __tablename__ = "user_badges"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    badge_key: Mapped[str] = mapped_column(String(100), nullable=False)
    content_ref: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_user_badges_key", "user_id", "badge_key", "content_ref", unique=True),
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index("idx_notifications_user", "user_id", "is_read", "created_at"),
    )


class DeviceToken(Base):
    __tablename__ = "device_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    platform: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="device_tokens")


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content_id: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_bookmarks_user", "user_id", "content_type", "content_id", unique=True),
    )


class ForumTopic(Base):
    __tablename__ = "forum_topics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tags: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    reply_count: Mapped[int] = mapped_column(Integer, default=0)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    replies = relationship("ForumReply", back_populates="topic", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_forum_topics_category_activity", "category", "last_activity_at"),
    )


class ForumReply(Base):
    __tablename__ = "forum_replies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("forum_topics.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_solution: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    topic = relationship("ForumTopic", back_populates="replies")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    plan: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    provider: Mapped[str] = mapped_column(String(50), default="manual")
    provider_ref: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="subscription")

    __table_args__ = (
        CheckConstraint("status IN ('active', 'canceled', 'expired', 'trialing')", name="ck_subscription_status"),
        CheckConstraint("plan IN ('free', 'pro', 'business')", name="ck_subscription_plan"),
    )


class UsageQuota(Base):
    __tablename__ = "usage_quotas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    month: Mapped[str] = mapped_column(String(7), nullable=False)
    ai_chats: Mapped[int] = mapped_column(Integer, default=0)
    invoices_created: Mapped[int] = mapped_column(Integer, default=0)
    savings_goals_created: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_usage_quotas_user_month", "user_id", "month", unique=True),
    )


class AdCampaign(Base):
    __tablename__ = "ad_campaigns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    advertiser_name: Mapped[str] = mapped_column(String(255), nullable=False)
    image_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    target_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    cpm: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    budget: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0)
    spent: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0)
    impressions_bought: Mapped[int] = mapped_column(Integer, default=0)
    impressions_served: Mapped[int] = mapped_column(Integer, default=0)
    target_pages: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_ad_campaigns_active", "is_active", "start_date"),
    )


class AdImpression(Base):
    __tablename__ = "ad_impressions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ad_campaigns.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    amount_earned: Mapped[float] = mapped_column(DECIMAL(10, 6), default=0)
    served_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    read_time_minutes: Mapped[int] = mapped_column(Integer, default=5)
    tags: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_articles_published", "is_published", "created_at"),
    )


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    tags: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    comments_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    comments = relationship("BlogComment", back_populates="post", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_blog_posts_published", "is_published", "created_at"),
    )


class BlogComment(Base):
    __tablename__ = "blog_comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("blog_posts.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    author_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    post = relationship("BlogPost", back_populates="comments")


class NewsArticle(Base):
    __tablename__ = "news"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    is_breaking: Mapped[bool] = mapped_column(Boolean, default=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    published_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_news_published", "is_published", "published_date"),
    )


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), default="beginner")
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    duration_hours: Mapped[float] = mapped_column(DECIMAL(5, 2), default=1.0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    lessons: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    enrolled_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_courses_published", "is_published", "created_at"),
    )
