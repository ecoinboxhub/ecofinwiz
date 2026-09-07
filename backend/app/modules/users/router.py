from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.modules.auth.dependencies import get_current_user
from app.models import User
from app.modules.users.schemas import (
    UpdatePreferencesRequest,
    UpdateProfileRequest,
    UserPreferencesResponse,
    UserProfileResponse,
    UserProgressResponse,
    UserStatsResponse,
)
from app.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return UserProfileResponse.model_validate(current_user)


@router.patch("/me", response_model=UserProfileResponse)
async def update_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    user = await service.update_profile(
        current_user,
        full_name=body.full_name,
        avatar_url=body.avatar_url,
        persona_type=body.persona_type,
    )
    return UserProfileResponse.model_validate(user)


@router.get("/me/preferences", response_model=UserPreferencesResponse)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    prefs = await service.get_preferences(current_user)
    return UserPreferencesResponse.model_validate(prefs)


@router.patch("/me/preferences", response_model=UserPreferencesResponse)
async def update_preferences(
    body: UpdatePreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    prefs = await service.update_preferences(
        current_user,
        currency=body.currency,
        language=body.language,
        notification_push=body.notification_push,
        notification_email=body.notification_email,
        notification_daily_tip=body.notification_daily_tip,
        notification_budget_alert=body.notification_budget_alert,
    )
    return UserPreferencesResponse.model_validate(prefs)


@router.get("/me/progress", response_model=UserProgressResponse)
async def get_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    progress = await service.get_progress(current_user)
    return UserProgressResponse(**progress)


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_stats(current_user: User = Depends(get_current_user)):
    return UserStatsResponse(
        streak_days=0,
        total_badges=0,
        member_since=current_user.created_at,
    )


@router.get("/me/notifications")
async def get_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    skip = (page - 1) * per_page
    notifications = await service.get_notifications(current_user, skip=skip, limit=per_page)
    return {"items": notifications, "page": page, "per_page": per_page}


@router.patch("/me/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = UserService(db)
    notif = await svc.mark_notification_read(notification_id, current_user)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"id": str(notif.id), "is_read": True}


@router.post("/me/notifications/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = UserService(db)
    count = await svc.mark_all_notifications_read(current_user)
    return {"marked_read": count}
