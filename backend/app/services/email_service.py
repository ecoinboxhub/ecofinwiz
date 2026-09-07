"""
Email notification service for password reset, email verification, and alerts.

Supports SendGrid and Mailgun as providers with automatic fallback.
"""

from dataclasses import dataclass
from typing import Optional

import httpx

from app.config import get_settings
from app.shared.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


@dataclass
class EmailResult:
    success: bool
    provider: str
    message_id: Optional[str] = None
    error: Optional[str] = None


class EmailService:
    def __init__(self):
        self.sendgrid_key = settings.sendgrid_api_key
        self.mailgun_key = settings.mailgun_api_key
        self.mailgun_domain = settings.mailgun_domain
        self.from_email = settings.email_from_address or "noreply@finwize.app"
        self.from_name = settings.email_from_name or "EcoFinwize"
        self.frontend_url = settings.frontend_url or "http://localhost:5300"

    async def send(self, to: str, subject: str, html: str) -> EmailResult:
        if self.sendgrid_key:
            return await self._send_sendgrid(to, subject, html)
        if self.mailgun_key and self.mailgun_domain:
            return await self._send_mailgun(to, subject, html)
        logger.warning("Email service: no provider configured (SendGrid or Mailgun)")
        return EmailResult(success=False, provider="none", error="No email provider configured")

    async def _send_sendgrid(self, to: str, subject: str, html: str) -> EmailResult:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={
                        "Authorization": f"Bearer {self.sendgrid_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "personalizations": [{"to": [{"email": to}]}],
                        "from": {"email": self.from_email, "name": self.from_name},
                        "subject": subject,
                        "content": [{"type": "text/html", "value": html}],
                    },
                )
                if resp.status_code == 202:
                    return EmailResult(success=True, provider="sendgrid", message_id=resp.headers.get("X-Message-Id"))
                logger.error("SendGrid error %d: %s", resp.status_code, resp.text[:200])
                return EmailResult(success=False, provider="sendgrid", error=f"HTTP {resp.status_code}")
        except httpx.TimeoutException:
            logger.error("SendGrid: timeout sending to %s", to)
            return EmailResult(success=False, provider="sendgrid", error="timeout")
        except Exception as e:
            logger.error("SendGrid error: %s", e)
            return EmailResult(success=False, provider="sendgrid", error=str(e))

    async def _send_mailgun(self, to: str, subject: str, html: str) -> EmailResult:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages",
                    auth=("api", self.mailgun_key),
                    data={
                        "from": f"{self.from_name} <{self.from_email}>",
                        "to": to,
                        "subject": subject,
                        "html": html,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return EmailResult(success=True, provider="mailgun", message_id=data.get("id"))
                logger.error("Mailgun error %d: %s", resp.status_code, resp.text[:200])
                return EmailResult(success=False, provider="mailgun", error=f"HTTP {resp.status_code}")
        except Exception as e:
            logger.error("Mailgun error: %s", e)
            return EmailResult(success=False, provider="mailgun", error=str(e))

    async def send_verification(self, email: str, token: str) -> EmailResult:
        link = f"{self.frontend_url}/verify-email?token={token}"
        html = f"""
        <div style="font-family:sans-serif;max-width:480px;margin:0 auto;">
            <h2 style="color:#0284C7;">Welcome to EcoFinwize!</h2>
            <p>Click below to verify your email address:</p>
            <a href="{link}" style="display:inline-block;padding:12px 28px;background:#0284C7;
                color:white;text-decoration:none;border-radius:6px;font-weight:bold;">Verify Email</a>
            <p style="margin-top:24px;font-size:12px;color:#666;">
                If you didn't create an account, ignore this email.<br>
                EcoFinwize - AI-Powered Financial Guidance
            </p>
        </div>"""
        return await self.send(email, "Verify your EcoFinwize account", html)

    async def send_password_reset(self, email: str, token: str) -> EmailResult:
        link = f"{self.frontend_url}/reset-password?token={token}"
        html = f"""
        <div style="font-family:sans-serif;max-width:480px;margin:0 auto;">
            <h2 style="color:#0284C7;">Reset your EcoFinwize password</h2>
            <p>Click below to reset your password. This link expires in 1 hour.</p>
            <a href="{link}" style="display:inline-block;padding:12px 28px;background:#0284C7;
                color:white;text-decoration:none;border-radius:6px;font-weight:bold;">Reset Password</a>
            <p style="margin-top:24px;font-size:12px;color:#666;">
                If you didn't request this, ignore this email.<br>
                EcoFinwize - AI-Powered Financial Guidance
            </p>
        </div>"""
        return await self.send(email, "Reset your EcoFinwize password", html)

    async def send_welcome(self, email: str, name: str) -> EmailResult:
        html = f"""
        <div style="font-family:sans-serif;max-width:480px;margin:0 auto;">
            <h2 style="color:#0284C7;">Hi {name}, welcome to EcoFinwize!</h2>
            <p>Your AI-powered financial guidance platform is ready.</p>
            <ul>
                <li>Chat with Kemi, your AI financial advisor</li>
                <li>Create adaptive budgets for irregular income</li>
                <li>Learn with micro-lessons and earn badges</li>
            </ul>
            <a href="{self.frontend_url}/dashboard"
               style="display:inline-block;padding:12px 28px;background:#0284C7;
                      color:white;text-decoration:none;border-radius:6px;">Go to Dashboard</a>
        </div>"""
        return await self.send(email, "Welcome to EcoFinwize!", html)

    async def send_budget_alert(self, email: str, category: str, spent: float, limit: float) -> EmailResult:
        pct = round((spent / limit) * 100) if limit > 0 else 0
        html = f"""
        <div style="font-family:sans-serif;max-width:480px;margin:0 auto;">
            <h3 style="color:#F97316;">Budget Alert: {category}</h3>
            <p>You've used <strong>{pct}%</strong> of your {category} budget.</p>
            <p>Spent: ₦{spent:,.2f} / ₦{limit:,.2f}</p>
            <a href="{self.frontend_url}/budgets" style="color:#0284C7;">View Budget</a>
        </div>"""
        return await self.send(email, f"Budget Alert: {category} at {pct}%", html)


_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
