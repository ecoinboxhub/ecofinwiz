import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class UpdateProfileRequest(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=255)
    avatar_url: str | None = None
    persona_type: str | None = Field(None, pattern="^(freelancer|sme|student|worker)?$")


class UpdatePreferencesRequest(BaseModel):
    currency: str | None = None
    language: str | None = None
    notification_push: bool | None = None
    notification_email: bool | None = None
    notification_daily_tip: bool | None = None
    notification_budget_alert: bool | None = None


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    avatar_url: str | None = None
    persona_type: str | None = None
    onboarding_completed: bool = False
    is_email_verified: bool = False
    is_admin: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserPreferencesResponse(BaseModel):
    currency: str = "NGN"
    language: str = "en"
    notification_push: bool = True
    notification_email: bool = False
    notification_daily_tip: bool = True
    notification_budget_alert: bool = True

    model_config = {"from_attributes": True}


class UserProgressResponse(BaseModel):
    lessons_completed: int = 0
    courses_completed: int = 0
    badges: list[str] = []
    current_streak: int = 0
    total_saved: float = 0
    active_goals: int = 0

    model_config = {"from_attributes": True}


class UserStatsResponse(BaseModel):
    streak_days: int = 0
    total_badges: int = 0
    member_since: datetime | None = None

    model_config = {"from_attributes": True}
