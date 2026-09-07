from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class PlanResponse(BaseModel):
    key: str
    name: str
    price_monthly: float
    ai_chats_per_month: int | None
    max_savings_goals: int | None
    max_invoices_per_month: int | None
    max_team_members: int
    ad_free: bool
    ai_provider: str
    business_plan_enabled: bool


class SubscriptionResponse(BaseModel):
    id: UUID
    user_id: UUID
    plan: str
    status: str
    provider: str
    provider_ref: str | None
    current_period_start: datetime
    current_period_end: datetime | None
    auto_renew: bool
    created_at: datetime


class UsageResponse(BaseModel):
    ai_chats: dict
    invoices_created: dict
    savings_goals_created: dict


class UpgradeRequest(BaseModel):
    plan: str


class UpgradeResponse(BaseModel):
    subscription: SubscriptionResponse
    checkout_url: str | None
    message: str
