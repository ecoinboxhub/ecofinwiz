from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.modules.auth.dependencies import get_current_user
from app.models import User
from app.modules.admin import service
from app.modules.admin.schemas import (
    AdminUserResponse, AdminUserUpdate,
    AdminNotificationCreate,
    AnalyticsSummary,
)
from app.modules.admin.ad_schemas import (
    AdCampaignCreate, AdCampaignUpdate, AdCampaignResponse, AdStatsResponse,
)
from app.modules.admin import ad_service

router = APIRouter()


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# =====================================================================
# DASHBOARD
# =====================================================================

@router.get("/admin/stats", tags=["Admin"])
async def platform_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return await service.get_platform_stats(db)


@router.get("/admin/stats/users/growth", tags=["Admin"])
async def user_growth(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return await service.get_user_growth(db, days)


@router.get("/admin/stats/engagement", tags=["Admin"])
async def engagement_metrics(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return await service.get_engagement_metrics(db)


# =====================================================================
# USER MANAGEMENT
# =====================================================================

@router.get("/admin/users", tags=["Admin"])
async def list_users(
    is_active: Optional[bool] = Query(None),
    is_admin: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    users, total = await service.list_all_users(db, skip, limit, is_active, is_admin, search)
    return {
        "items": [AdminUserResponse(
            id=u.id, email=u.email, full_name=u.full_name,
            avatar_url=u.avatar_url, persona_type=u.persona_type,
            onboarding_completed=u.onboarding_completed,
            is_active=u.is_active, is_admin=u.is_admin,
            created_at=u.created_at, updated_at=u.updated_at,
        ) for u in users],
        "total": total,
    }


@router.get("/admin/users/{user_id}", tags=["Admin"])
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    u = await service.get_user_detail(user_id, db)
    return AdminUserResponse(
        id=u.id, email=u.email, full_name=u.full_name,
        avatar_url=u.avatar_url, persona_type=u.persona_type,
        onboarding_completed=u.onboarding_completed,
        is_active=u.is_active, is_admin=u.is_admin,
        created_at=u.created_at, updated_at=u.updated_at,
    )


@router.patch("/admin/users/{user_id}", tags=["Admin"])
async def update_user(
    user_id: UUID,
    data: AdminUserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    u = await service.update_user(user_id, data, db)
    return AdminUserResponse(
        id=u.id, email=u.email, full_name=u.full_name,
        avatar_url=u.avatar_url, persona_type=u.persona_type,
        onboarding_completed=u.onboarding_completed,
        is_active=u.is_active, is_admin=u.is_admin,
        created_at=u.created_at, updated_at=u.updated_at,
    )


# =====================================================================
# NOTIFICATIONS (Admin)
# =====================================================================

@router.post("/admin/notifications/send", status_code=201, tags=["Admin"])
async def send_notification(
    data: AdminNotificationCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    count = await service.send_admin_notification(data, db)
    return {"sent": count}


# =====================================================================
# ANALYTICS
# =====================================================================

@router.get("/admin/analytics/summary", tags=["Admin"])
async def analytics_summary(
    period_days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return await service.get_analytics_summary(db, period_days)


# =====================================================================
# AD CAMPAIGNS (Admin)
# =====================================================================

@router.get("/admin/ads/campaigns", response_model=list[AdCampaignResponse], tags=["Admin"])
async def list_ad_campaigns(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    campaigns = await ad_service.list_ad_campaigns(db)
    return [AdCampaignResponse(
        id=c.id, advertiser_name=c.advertiser_name,
        image_url=c.image_url, target_url=c.target_url,
        cpm=float(c.cpm), budget=float(c.budget),
        spent=float(c.spent), impressions_bought=c.impressions_bought,
        impressions_served=c.impressions_served,
        target_pages=c.target_pages,
        is_active=c.is_active, start_date=c.start_date,
        end_date=c.end_date, created_at=c.created_at,
    ) for c in campaigns]


@router.post("/admin/ads/campaigns", response_model=AdCampaignResponse, status_code=201, tags=["Admin"])
async def create_ad_campaign(
    data: AdCampaignCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    c = await ad_service.create_ad_campaign(data.model_dump(), db)
    return AdCampaignResponse(
        id=c.id, advertiser_name=c.advertiser_name,
        image_url=c.image_url, target_url=c.target_url,
        cpm=float(c.cpm), budget=float(c.budget),
        spent=float(c.spent), impressions_bought=c.impressions_bought,
        impressions_served=c.impressions_served,
        target_pages=c.target_pages,
        is_active=c.is_active, start_date=c.start_date,
        end_date=c.end_date, created_at=c.created_at,
    )


@router.patch("/admin/ads/campaigns/{campaign_id}", response_model=AdCampaignResponse, tags=["Admin"])
async def update_ad_campaign(
    campaign_id: UUID,
    data: AdCampaignUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    c = await ad_service.update_ad_campaign(campaign_id, data.model_dump(exclude_unset=True), db)
    return AdCampaignResponse(
        id=c.id, advertiser_name=c.advertiser_name,
        image_url=c.image_url, target_url=c.target_url,
        cpm=float(c.cpm), budget=float(c.budget),
        spent=float(c.spent), impressions_bought=c.impressions_bought,
        impressions_served=c.impressions_served,
        target_pages=c.target_pages,
        is_active=c.is_active, start_date=c.start_date,
        end_date=c.end_date, created_at=c.created_at,
    )


@router.get("/admin/ads/stats", response_model=AdStatsResponse, tags=["Admin"])
async def ad_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return await ad_service.get_ad_stats(db)
