from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.modules.auth.dependencies import get_current_user
from app.models import User
from app.modules.subscriptions.service import SubscriptionService, PLANS
from app.modules.subscriptions.schemas import (
    PlanResponse, SubscriptionResponse, UsageResponse,
    UpgradeRequest, UpgradeResponse,
)
from app.services.analytics_service import get_analytics
from app.services.payment_service import get_paystack_service, get_flutterwave_service, get_plan_amount

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


def get_sub_svc(db: AsyncSession = Depends(get_db)) -> SubscriptionService:
    return SubscriptionService(db)


def _to_sub_response(sub) -> SubscriptionResponse:
    return SubscriptionResponse(
        id=sub.id,
        user_id=sub.user_id,
        plan=sub.plan,
        status=sub.status,
        provider=sub.provider,
        provider_ref=sub.provider_ref,
        current_period_start=sub.current_period_start,
        current_period_end=sub.current_period_end,
        auto_renew=sub.auto_renew,
        created_at=sub.created_at,
    )


@router.get("/plans")
async def list_plans():
    return [
        PlanResponse(
            key=key,
            name={"free": "Free", "pro": "EcoFinwize Pro", "business": "EcoFinwize Business"}[key],
            price_monthly={"free": 0, "pro": 4.0, "business": 12.0}[key],
            **cfg,
        )
        for key, cfg in PLANS.items()
    ]


@router.get("/my", response_model=SubscriptionResponse)
async def my_subscription(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = SubscriptionService(db)
    sub = await svc.get_or_create_subscription(user)
    return _to_sub_response(sub)


@router.get("/my/usage", response_model=UsageResponse)
async def my_usage(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = SubscriptionService(db)
    summary = await svc.get_usage_summary(user.id)
    return UsageResponse(**summary)


@router.post("/upgrade", response_model=UpgradeResponse)
async def upgrade(
    req: UpgradeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if req.plan == user.plan:
        raise HTTPException(status_code=400, detail=f"Already on {req.plan} plan")

    svc = SubscriptionService(db)

    if req.plan == "free":
        sub = await svc.upgrade(user, "free")
        return UpgradeResponse(subscription=_to_sub_response(sub), checkout_url=None, message="Downgraded to Free plan")

    amount, currency = get_plan_amount(req.plan)

    paystack = get_paystack_service()
    if paystack.is_configured:
        result = await paystack.initialize_transaction(
            email=user.email,
            amount_kobo=amount,
            plan_code=req.plan,
            metadata={"user_id": str(user.id)},
        )
        if result.success:
            analytics = get_analytics()
            await analytics.track_subscription(user.id, req.plan, "paystack")
            sub = await svc.get_or_create_subscription(user)
            return UpgradeResponse(
                subscription=_to_sub_response(sub),
                checkout_url=result.authorization_url,
                message="Redirect to payment to complete upgrade",
            )

    flw = get_flutterwave_service()
    if flw.is_configured:
        result = await flw.initialize_transaction(
            email=user.email,
            amount=amount,
            currency=currency,
            plan_code=req.plan,
        )
        if result.success:
            analytics = get_analytics()
            await analytics.track_subscription(user.id, req.plan, "flutterwave")
            sub = await svc.get_or_create_subscription(user)
            return UpgradeResponse(
                subscription=_to_sub_response(sub),
                checkout_url=result.authorization_url,
                message="Redirect to payment to complete upgrade",
            )

    sub = await svc.upgrade(user, req.plan)
    return UpgradeResponse(
        subscription=_to_sub_response(sub),
        checkout_url=None,
        message=f"No payment provider configured — plan activated manually.",
    )
