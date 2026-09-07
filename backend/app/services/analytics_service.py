"""
Product analytics service for user behavior tracking.

Supports PostHog (self-hostable, GDPR-compliant) as the primary provider.
Tracks key events: signup, login, budget_create, ai_chat, course_complete, etc.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

import httpx

from app.config import get_settings
from app.shared.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class PostHogService:
    """PostHog product analytics (self-hosted or cloud)."""

    def __init__(self):
        self.api_key = settings.posthog_api_key
        self.host = settings.posthog_host or "https://app.posthog.com"

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def capture(
        self,
        distinct_id: str,
        event: str,
        properties: Optional[dict] = None,
    ) -> bool:
        if not self.is_configured:
            return False

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    f"{self.host}/capture",
                    json={
                        "api_key": self.api_key,
                        "event": event,
                        "distinct_id": str(distinct_id),
                        "properties": {
                            "$lib": "finwize-backend",
                            "$lib_version": settings.app_version,
                            "env": settings.app_env,
                            **(properties or {}),
                        },
                    },
                )
                return resp.status_code == 200
        except Exception as e:
            logger.debug("PostHog capture error: %s", e)
            return False

    async def identify(self, distinct_id: str, properties: dict) -> bool:
        if not self.is_configured:
            return False
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    f"{self.host}/identify",
                    json={
                        "api_key": self.api_key,
                        "distinct_id": str(distinct_id),
                        "properties": properties,
                    },
                )
                return resp.status_code == 200
        except Exception:
            return False

    async def track_pageview(self, distinct_id: str, path: str, title: str = "") -> bool:
        return await self.capture(distinct_id, "$pageview", {
            "$current_url": path,
            "$title": title,
        })

    async def track_signup(self, user_id: UUID, method: str = "email", persona: str = "") -> bool:
        return await self.capture(str(user_id), "user_signed_up", {
            "method": method,
            "persona": persona,
        })

    async def track_login(self, user_id: UUID, method: str = "email") -> bool:
        return await self.capture(str(user_id), "user_logged_in", {"method": method})

    async def track_ai_chat(self, user_id: UUID, advisor: str, message_count: int) -> bool:
        return await self.capture(str(user_id), "ai_chat", {
            "advisor": advisor,
            "message_count": message_count,
        })

    async def track_budget_created(self, user_id: UUID, category: str, amount: float) -> bool:
        return await self.capture(str(user_id), "budget_created", {
            "category": category,
            "amount": amount,
        })

    async def track_savings_goal(self, user_id: UUID, target_amount: float) -> bool:
        return await self.capture(str(user_id), "savings_goal_created", {
            "target_amount": target_amount,
        })

    async def track_course_completed(self, user_id: UUID, course_id: str, course_title: str) -> bool:
        return await self.capture(str(user_id), "course_completed", {
            "course_id": course_id,
            "course_title": course_title,
        })

    async def track_business_plan(self, user_id: UUID, industry: str) -> bool:
        return await self.capture(str(user_id), "business_plan_generated", {
            "industry": industry,
        })

    async def track_subscription(self, user_id: UUID, plan: str, provider: str) -> bool:
        return await self.capture(str(user_id), "subscription_upgraded", {
            "plan": plan,
            "provider": provider,
        })


_analytics: Optional[PostHogService] = None


def get_analytics() -> PostHogService:
    global _analytics
    if _analytics is None:
        _analytics = PostHogService()
    return _analytics
