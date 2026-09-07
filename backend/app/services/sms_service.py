"""
SMS notification service for African markets.

Supports AfricasTalking (primary - 17+ African countries) and Twilio (global).
Used for budget alerts, transaction confirmations, and account notifications.
"""

from dataclasses import dataclass
from typing import Optional

import httpx

from app.config import get_settings
from app.shared.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


@dataclass
class SMSResult:
    success: bool
    provider: str
    message_id: Optional[str] = None
    error: Optional[str] = None


class AfricasTalkingService:
    """AfricasTalking SMS (primary - Nigeria, Kenya, Ghana, Uganda, etc.)."""

    def __init__(self):
        self.api_key = settings.africas_talking_api_key
        self.username = settings.africas_talking_username or "finwize"
        self.from_number = settings.sms_from_number or "FINWIZE"
        self.base_url = "https://api.africastalking.com/version1/messaging"

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def send(self, to: str, message: str) -> SMSResult:
        if not self.is_configured:
            return SMSResult(success=False, provider="africastalking", error="AfricasTalking not configured")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{self.base_url}",
                    headers={
                        "ApiKey": self.api_key,
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Accept": "application/json",
                    },
                    data={
                        "username": self.username,
                        "to": to,
                        "message": message,
                        "from": self.from_number,
                    },
                )
                data = resp.json()
                if resp.status_code == 201 and data.get("SMSMessageData", {}).get("Recipients"):
                    recipient = data["SMSMessageData"]["Recipients"][0]
                    status = recipient.get("status", "")
                    if status in ("Success", "Sent"):
                        return SMSResult(success=True, provider="africastalking", message_id=recipient.get("messageId"))
                    return SMSResult(success=False, provider="africastalking", error=status)
                logger.error("AfricasTalking error %d: %s", resp.status_code, data)
                return SMSResult(success=False, provider="africastalking", error=data.get("message", f"HTTP {resp.status_code}"))
        except Exception as e:
            logger.error("AfricasTalking exception: %s", e)
            return SMSResult(success=False, provider="africastalking", error=str(e))


class TwilioSMSService:
    """Twilio SMS (global fallback)."""

    def __init__(self):
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.from_number = settings.twilio_from_number

    @property
    def is_configured(self) -> bool:
        return bool(self.account_sid and self.auth_token)

    async def send(self, to: str, message: str) -> SMSResult:
        if not self.is_configured:
            return SMSResult(success=False, provider="twilio", error="Twilio not configured")

        try:
            auth = httpx.BasicAuth(self.account_sid, self.auth_token)
            async with httpx.AsyncClient(timeout=10.0, auth=auth) as client:
                resp = await client.post(
                    f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json",
                    data={"To": to, "From": self.from_number, "Body": message},
                )
                data = resp.json()
                if resp.status_code == 201:
                    return SMSResult(success=True, provider="twilio", message_id=data.get("sid"))
                logger.error("Twilio error %d: %s", resp.status_code, data.get("message"))
                return SMSResult(success=False, provider="twilio", error=data.get("message", f"HTTP {resp.status_code}"))
        except Exception as e:
            logger.error("Twilio exception: %s", e)
            return SMSResult(success=False, provider="twilio", error=str(e))


def send_sms(to: str, message: str) -> SMSResult:
    """Send SMS with automatic provider fallback."""
    import asyncio

    at = AfricasTalkingService()
    if at.is_configured:
        return asyncio.run(at.send(to, message))

    twilio = TwilioSMSService()
    if twilio.is_configured:
        return asyncio.run(twilio.send(to, message))

    return SMSResult(success=False, provider="none", error="No SMS provider configured")
