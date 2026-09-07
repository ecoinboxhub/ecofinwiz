from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class PlatformStats(BaseModel):
    total_users: int
    active_users: int
    total_transactions: int
    total_invoices: float
    total_business_plans: int
    total_forum_topics: int
    total_courses: int
    total_articles: int
    total_ai_conversations: int


class UserGrowthPoint(BaseModel):
    date: str
    count: int


class EngagementMetrics(BaseModel):
    total_lessons_completed: int
    total_quiz_attempts: int
    total_bookmarks: int
    total_forum_replies: int
    total_ai_messages: int


class AdminUserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    persona_type: Optional[str] = None
    onboarding_completed: bool
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime


class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    persona_type: Optional[str] = None


class AdminNotificationCreate(BaseModel):
    user_ids: list[UUID]
    title: str
    body: Optional[str] = None
    type: str = "admin"
    data: Optional[dict] = None


class AnalyticsSummary(BaseModel):
    period: str
    new_users: int
    active_users: int
    transactions_count: int
    transactions_volume: float
    top_categories: list[dict]
