from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database.postgres import get_db
from app.models import Subscription, User
from app.services.analytics_service import get_analytics
from app.services.payment_service import get_paystack_service, get_flutterwave_service
from app.shared.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/subscriptions/webhook", tags=["Webhooks"])


async def _activate_subscription(db: AsyncSession, email: str, plan: str, provider: str, provider_ref: str) -> dict:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.plan = plan
    sub_result = await db.execute(select(Subscription).where(Subscription.user_id == user.id))
    sub = sub_result.scalar_one_or_none()
    if not sub:
        sub = Subscription(user_id=user.id)
        db.add(sub)

    sub.plan = plan
    sub.status = "active"
    sub.provider = provider
    sub.provider_ref = provider_ref
    sub.current_period_start = datetime.now(timezone.utc)
    sub.current_period_end = datetime.now(timezone.utc) + timedelta(days=30)
    sub.auto_renew = True
    await db.commit()
    await db.refresh(sub)
    await db.refresh(user)

    analytics = get_analytics()
    await analytics.track_subscription(user.id, plan, provider)
    logger.info("Subscription activated: %s -> %s via %s (%s)", email, plan, provider, provider_ref)
    return {"status": "success", "plan": plan, "user_id": str(user.id)}


@router.post("/paystack")
async def paystack_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.body()
    signature = request.headers.get("x-paystack-signature", "")

    paystack = get_paystack_service()
    if not paystack.verify_webhook(body, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    import json
    payload = json.loads(body)
    event = payload.get("event", "")

    if event == "charge.success":
        data = payload.get("data", {})
        metadata = data.get("metadata", {})
        email = data.get("customer", {}).get("email", "")
        plan_code = metadata.get("plan_code", "")
        reference = data.get("reference", "")

        if not email or not plan_code:
            logger.warning("Paystack webhook missing email/plan_code")
            return {"status": "ignored"}

        return await _activate_subscription(db, email, plan_code, "paystack", reference)

    if event == "subscription.create":
        logger.info("Paystack subscription.create: %s", payload.get("data", {}).get("subscription_code"))
        return {"status": "received"}

    if event in ("invoice.payment_failed", "subscription.disable"):
        data = payload.get("data", {})
        sub_code = data.get("subscription_code", "")
        logger.warning("Paystack subscription issue: %s for %s", event, sub_code)
        return {"status": "noted"}

    logger.debug("Paystack unhandled event: %s", event)
    return {"status": "ignored"}


@router.post("/flutterwave")
async def flutterwave_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.body()
    signature = request.headers.get("verif-hash", "")

    if not signature:
        raise HTTPException(status_code=400, detail="Missing verif-hash header")

    flw = get_flutterwave_service()
    if not flw.verify_webhook(body, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    import json
    payload = json.loads(body)
    event = payload.get("event", "")
    data = payload.get("data", {})

    if event == "charge.completed" and data.get("status") == "successful":
        customer = data.get("customer", {})
        email = customer.get("email", "")
        meta = data.get("meta", {})
        plan_code = meta.get("plan_code", "")
        tx_ref = data.get("tx_ref", "")

        if not email or not plan_code:
            logger.warning("Flutterwave webhook missing email/plan_code")
            return {"status": "ignored"}

        return await _activate_subscription(db, email, plan_code, "flutterwave", tx_ref)

    logger.debug("Flutterwave unhandled event: %s", event)
    return {"status": "ignored"}
