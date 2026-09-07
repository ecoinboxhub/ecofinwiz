from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Subscription, UsageQuota


PLANS = {
    "free": {
        "ai_chats_per_month": 200,
        "max_savings_goals": 1,
        "max_invoices_per_month": 0,
        "max_team_members": 0,
        "ad_free": False,
        "ai_provider": "openrouter",
        "business_plan_enabled": False,
    },
    "pro": {
        "ai_chats_per_month": None,
        "max_savings_goals": None,
        "max_invoices_per_month": 20,
        "max_team_members": 0,
        "ad_free": True,
        "ai_provider": "openrouter",
        "business_plan_enabled": True,
    },
    "business": {
        "ai_chats_per_month": None,
        "max_savings_goals": None,
        "max_invoices_per_month": None,
        "max_team_members": 5,
        "ad_free": True,
        "ai_provider": "groq",
        "business_plan_enabled": True,
    },
}


def current_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


class SubscriptionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_quota(self, user_id: UUID, month: str | None = None) -> UsageQuota:
        month = month or current_month()
        result = await self.db.execute(
            select(UsageQuota).where(
                UsageQuota.user_id == user_id,
                UsageQuota.month == month,
            )
        )
        quota = result.scalar_one_or_none()
        if not quota:
            quota = UsageQuota(user_id=user_id, month=month)
            self.db.add(quota)
            await self.db.commit()
            await self.db.refresh(quota)
        return quota

    async def check_quota(self, user: User, feature: str) -> bool:
        plan_config = PLANS.get(user.plan, PLANS["free"])
        limit = plan_config.get(f"{feature}_per_month")

        if limit is None:
            return True

        quota = await self.get_or_create_quota(user.id)
        current = getattr(quota, feature, 0)
        return current < limit

    async def increment_usage(self, user_id: UUID, feature: str) -> UsageQuota:
        quota = await self.get_or_create_quota(user_id)
        setattr(quota, feature, getattr(quota, feature, 0) + 1)
        await self.db.commit()
        await self.db.refresh(quota)
        return quota

    def get_plan_config(self, plan: str) -> dict:
        return PLANS.get(plan, PLANS["free"])

    def get_upgrade_plan(self, current_plan: str) -> str | None:
        if current_plan == "free":
            return "pro"
        if current_plan == "pro":
            return "business"
        return None

    async def get_usage_summary(self, user_id: UUID) -> dict:
        plan = PLANS.get("free")
        quota = await self.get_or_create_quota(user_id)
        summary = {}
        for feature in ["ai_chats", "invoices_created", "savings_goals_created"]:
            limit = plan.get(f"{feature}_per_month")
            used = getattr(quota, feature, 0)
            summary[feature] = {
                "used": used,
                "limit": limit,
                "remaining": None if limit is None else max(0, limit - used),
            }
        return summary

    async def get_or_create_subscription(self, user: User) -> Subscription:
        result = await self.db.execute(
            select(Subscription).where(Subscription.user_id == user.id)
        )
        sub = result.scalar_one_or_none()
        if not sub:
            sub = Subscription(
                user_id=user.id,
                plan=user.plan or "free",
                status="active",
                provider="manual",
            )
            self.db.add(sub)
            await self.db.commit()
            await self.db.refresh(sub)
        return sub

    async def upgrade(self, user: User, new_plan: str) -> Subscription:
        if new_plan not in PLANS:
            raise ValueError(f"Invalid plan: {new_plan}")

        sub = await self.get_or_create_subscription(user)
        sub.plan = new_plan
        user.plan = new_plan
        await self.db.commit()
        await self.db.refresh(sub)
        await self.db.refresh(user)
        return sub
