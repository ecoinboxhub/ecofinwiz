from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.modules.auth.dependencies import get_current_user
from app.models import User
from app.modules.ads.service import AdService
from app.modules.ads.schemas import AdResponse, ImpressionRequest, ImpressionResponse

router = APIRouter(prefix="/ads", tags=["Ads"])


def get_ad_svc(db: AsyncSession = Depends(get_db)) -> AdService:
    return AdService(db)


@router.get("/{page_context}", response_model=list[AdResponse])
async def get_ads(
    page_context: str,
    user: User = Depends(get_current_user),
    svc: AdService = Depends(get_ad_svc),
):
    return await svc.get_ads_for_user(user, page_context)


@router.post("/impression", response_model=ImpressionResponse)
async def record_impression(
    req: ImpressionRequest,
    user: User = Depends(get_current_user),
    svc: AdService = Depends(get_ad_svc),
):
    impression = await svc.record_impression(req.campaign_id, user.id)
    return impression
