from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AdCampaign, AdImpression, User


async def list_ad_campaigns(db: AsyncSession) -> list[AdCampaign]:
    result = await db.execute(select(AdCampaign).order_by(AdCampaign.created_at.desc()))
    return list(result.scalars().all())


async def create_ad_campaign(data: dict, db: AsyncSession) -> AdCampaign:
    campaign = AdCampaign(**data)
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


async def update_ad_campaign(campaign_id, data: dict, db: AsyncSession) -> AdCampaign:
    result = await db.execute(select(AdCampaign).where(AdCampaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Campaign not found")
    for key, val in data.items():
        if val is not None:
            setattr(campaign, key, val)
    await db.commit()
    await db.refresh(campaign)
    return campaign


async def get_ad_stats(db: AsyncSession) -> dict:
    total = (await db.execute(select(func.count(AdCampaign.id)))).scalar() or 0
    active = (await db.execute(
        select(func.count(AdCampaign.id)).where(AdCampaign.is_active.is_(True))
    )).scalar() or 0
    impressions = (await db.execute(select(func.count(AdImpression.id)))).scalar() or 0
    revenue = (await db.execute(
        select(func.coalesce(func.sum(AdCampaign.spent), 0))
    )).scalar() or 0
    return {
        "total_campaigns": total,
        "active_campaigns": active,
        "total_impressions": impressions,
        "total_revenue": float(revenue),
        "ctr": 0.0,
    }
