from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AdCampaign, AdImpression, User
from app.modules.subscriptions.service import PLANS


def _eligible_campaign_conditions(now: datetime) -> list:
    """Eligibility filter for serving an ad campaign at time `now`.

    A campaign is eligible when it is active, has started, still has
    impressions left, and has no end date (runs indefinitely) OR its end
    date is still in the future. Note the end-date rule is an OR — a
    campaign cannot be both unexpired and expired at once.
    """
    return [
        AdCampaign.is_active.is_(True),
        AdCampaign.start_date <= now,
        or_(
            AdCampaign.end_date.is_(None),
            AdCampaign.end_date >= now,
        ),
        AdCampaign.impressions_bought > AdCampaign.impressions_served,
    ]


class AdService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_ads_for_user(self, user: User, page_context: str | None = None) -> list[dict]:
        plan_config = PLANS.get(user.plan, PLANS["free"])
        if plan_config.get("ad_free"):
            return []

        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(AdCampaign)
            .where(*_eligible_campaign_conditions(now))
            .order_by(func.random())
            .limit(2)
        )
        campaigns = result.scalars().all()
        return [
            {
                "id": str(c.id),
                "image_url": c.image_url,
                "target_url": c.target_url,
                "sponsor_name": c.advertiser_name,
                "label": "Sponsored",
            }
            for c in campaigns
        ]

    async def record_impression(self, campaign_id: UUID, user_id: UUID | None = None) -> AdImpression:
        result = await self.db.execute(
            select(AdCampaign).where(AdCampaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        if not campaign:
            raise ValueError("Campaign not found")

        cpm = campaign.cpm
        amount_earned = cpm / 1000.0

        impression = AdImpression(
            campaign_id=campaign_id,
            user_id=user_id,
            amount_earned=amount_earned,
        )
        campaign.impressions_served += 1
        campaign.spent += amount_earned
        self.db.add(impression)
        await self.db.commit()
        await self.db.refresh(impression)
        return impression
