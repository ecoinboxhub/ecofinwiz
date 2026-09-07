"""
Payment gateway service for subscription billing.

Supports Paystack (primary - Nigeria) and Flutterwave (secondary - broader Africa).
Handles plan upgrade/downgrade, invoice generation, and webhook verification.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

import httpx

from app.config import get_settings
from app.shared.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


PLAN_PRICES = {
    "pro_monthly": {"amount": 499, "currency": "NGN", "interval": "monthly"},
    "pro_yearly": {"amount": 4990, "currency": "NGN", "interval": "yearly"},
    "business_monthly": {"amount": 1999, "currency": "NGN", "interval": "monthly"},
    "business_yearly": {"amount": 19990, "currency": "NGN", "interval": "yearly"},
}


@dataclass
class PaymentResult:
    success: bool
    provider: str
    transaction_id: Optional[str] = None
    authorization_url: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None


@dataclass
class VerifyResult:
    success: bool
    status: str
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    customer_email: Optional[str] = None
    plan: Optional[str] = None
    error: Optional[str] = None


class PaystackService:
    """Paystack payment gateway (primary - Nigeria, Ghana, South Africa)."""

    def __init__(self):
        self.secret_key = settings.paystack_secret_key
        self.public_key = settings.paystack_public_key
        self.base_url = "https://api.paystack.co"

    @property
    def is_configured(self) -> bool:
        return bool(self.secret_key and self.secret_key.startswith("sk_"))

    async def initialize_transaction(
        self, email: str, amount_kobo: int, plan_code: str, metadata: Optional[dict] = None
    ) -> PaymentResult:
        if not self.is_configured:
            return PaymentResult(success=False, provider="paystack", error="Paystack not configured")

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.base_url}/transaction/initialize",
                    headers={
                        "Authorization": f"Bearer {self.secret_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "email": email,
                        "amount": amount_kobo,
                        "currency": "NGN",
                        "metadata": {"plan_code": plan_code, **(metadata or {})},
                        "callback_url": f"{settings.frontend_url}/subscriptions/callback",
                    },
                )
                data = resp.json()
                if resp.status_code == 200 and data.get("status"):
                    return PaymentResult(
                        success=True,
                        provider="paystack",
                        transaction_id=data["data"]["reference"],
                        authorization_url=data["data"]["authorization_url"],
                        status="pending",
                    )
                logger.error("Paystack init error %d: %s", resp.status_code, data)
                return PaymentResult(
                    success=False, provider="paystack",
                    error=data.get("message", f"HTTP {resp.status_code}"),
                )
        except Exception as e:
            logger.error("Paystack init exception: %s", e)
            return PaymentResult(success=False, provider="paystack", error=str(e))

    async def verify_transaction(self, reference: str) -> VerifyResult:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.base_url}/transaction/verify/{reference}",
                    headers={"Authorization": f"Bearer {self.secret_key}"},
                )
                data = resp.json()
                if resp.status_code == 200 and data.get("status"):
                    tx = data["data"]
                    return VerifyResult(
                        success=tx["status"] == "success",
                        status=tx["status"],
                        amount=Decimal(tx["amount"]) / 100,
                        currency=tx["currency"],
                        customer_email=tx["customer"]["email"],
                        plan=tx["metadata"].get("plan_code") if tx.get("metadata") else None,
                    )
                return VerifyResult(success=False, status="failed", error=data.get("message", "Verification failed"))
        except Exception as e:
            logger.error("Paystack verify exception: %s", e)
            return VerifyResult(success=False, status="error", error=str(e))

    async def create_subscription(self, email: str, plan_code: str, authorization_code: str) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{self.base_url}/subscription",
                    headers={"Authorization": f"Bearer {self.secret_key}"},
                    json={
                        "customer": email,
                        "plan": plan_code,
                        "authorization": authorization_code,
                    },
                )
                data = resp.json()
                if resp.status_code == 201 and data.get("status"):
                    return data["data"]["subscription_code"]
                logger.error("Paystack subscription error: %s", data)
                return None
        except Exception as e:
            logger.error("Paystack subscription exception: %s", e)
            return None

    async def list_plans(self) -> list[dict]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.base_url}/plan",
                    headers={"Authorization": f"Bearer {self.secret_key}"},
                )
                data = resp.json()
                if resp.status_code == 200 and data.get("status"):
                    return [{"code": p["plan_code"], "name": p["name"], "amount": p["amount"] / 100}
                            for p in data["data"]]
                return []
        except Exception:
            return []

    def verify_webhook(self, body: bytes, signature: str) -> bool:
        import hashlib, hmac
        expected = hmac.new(
            self.secret_key.encode(), body, hashlib.sha512
        ).hexdigest()
        return hmac.compare_digest(expected, signature)


class FlutterwaveService:
    """Flutterwave payment gateway (secondary - 30+ African countries)."""

    def __init__(self):
        self.secret_key = settings.flutterwave_secret_key
        self.public_key = settings.flutterwave_public_key
        self.base_url = "https://api.flutterwave.com/v3"

    @property
    def is_configured(self) -> bool:
        return bool(self.secret_key and self.secret_key.startswith("FLWSECK"))

    async def initialize_transaction(
        self, email: str, amount: int, currency: str, plan_code: str
    ) -> PaymentResult:
        if not self.is_configured:
            return PaymentResult(success=False, provider="flutterwave", error="Flutterwave not configured")

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.base_url}/payments",
                    headers={
                        "Authorization": f"Bearer {self.secret_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "tx_ref": f"finwize-{datetime.now(timezone.utc).timestamp():.0f}",
                        "amount": amount,
                        "currency": currency,
                        "redirect_url": f"{settings.frontend_url}/subscriptions/callback",
                        "customer": {"email": email},
                        "meta": {"plan_code": plan_code},
                        "customizations": {
                            "title": "EcoFinwize Subscription",
                            "description": f"Upgrade to {plan_code.replace('_', ' ').title()}",
                        },
                    },
                )
                data = resp.json()
                if resp.status_code == 200 and data.get("status") == "success":
                    return PaymentResult(
                        success=True,
                        provider="flutterwave",
                        transaction_id=data["data"]["tx_ref"],
                        authorization_url=data["data"]["link"],
                        status="pending",
                    )
                logger.error("Flutterwave init error %d: %s", resp.status_code, data)
                return PaymentResult(
                    success=False, provider="flutterwave",
                    error=data.get("message", f"HTTP {resp.status_code}"),
                )
        except Exception as e:
            logger.error("Flutterwave init exception: %s", e)
            return PaymentResult(success=False, provider="flutterwave", error=str(e))

    async def verify_transaction(self, transaction_id: str) -> VerifyResult:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.base_url}/transactions/{transaction_id}/verify",
                    headers={"Authorization": f"Bearer {self.secret_key}"},
                )
                data = resp.json()
                if resp.status_code == 200 and data.get("status") == "success":
                    tx = data["data"]
                    return VerifyResult(
                        success=tx["status"] == "successful",
                        status=tx["status"],
                        amount=Decimal(str(tx["amount"])),
                        currency=tx["currency"],
                        customer_email=tx["customer"]["email"],
                        plan=tx.get("meta", {}).get("plan_code"),
                    )
                return VerifyResult(success=False, status="failed", error=data.get("message", "Verification failed"))
        except Exception as e:
            logger.error("Flutterwave verify exception: %s", e)
            return VerifyResult(success=False, status="error", error=str(e))

    def verify_webhook(self, body: bytes, signature: str) -> bool:
        import hashlib
        expected = hashlib.sha256(
            (self.secret_key + body.decode()).encode()
        ).hexdigest()
        return expected == signature


def get_plan_amount(plan: str, interval: str = "monthly") -> tuple[int, str]:
    key = f"{plan}_{interval}"
    config = PLAN_PRICES.get(key, PLAN_PRICES["pro_monthly"])
    return config["amount"], config["currency"]


def get_paystack_service() -> PaystackService:
    return PaystackService()


def get_flutterwave_service() -> FlutterwaveService:
    return FlutterwaveService()
