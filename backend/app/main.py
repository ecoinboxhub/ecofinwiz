from contextlib import asynccontextmanager

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from app.config import get_settings
from app.core.exceptions import AppException
from app.core.rate_limiter import RateLimitMiddleware
from app.database.redis import close_redis
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.finance.router import router as finance_router
from app.modules.ai.router import router as ai_router
from app.modules.content.router import router as content_router
from app.modules.business.router import router as business_router
from app.modules.intelligence.router import router as intelligence_router
from app.modules.admin.router import router as admin_router
from app.modules.subscriptions.router import router as subscriptions_router
from app.modules.subscriptions.webhook import router as webhook_router
from app.modules.ads.router import router as ads_router
from app.modules.calculators.router import router as calculators_router
from app.modules.markets.router import router as markets_router
from app.shared.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.app_env,
            release=settings.app_version,
            traces_sample_rate=0.25,
            profiles_sample_rate=0.10,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                RedisIntegration(),
                LoggingIntegration(level=None, event_level=None),
            ],
            before_send=filter_sentry_events,
        )
        logger.info("Sentry initialized")
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    logger.info("Shutting down...")
    await close_redis()


def filter_sentry_events(event, hint):
    """Filter out expected/benign errors from Sentry."""
    if "exc_info" in hint:
        exc_type, exc_value, _ = hint["exc_info"]
        # Filter out common expected errors
        if exc_type.__name__ in ("NotFoundError", "UnauthorizedError", "RateLimitedError"):
            return None
    # Filter 404, 401, 429 from HTTP exceptions
    if event.get("request", {}).get("url"):
        pass  # Could filter by URL pattern here
    return event


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

# Add Sentry ASGI middleware for request context (must be after other middleware)
if settings.sentry_dsn:
    app.add_middleware(SentryAsgiMiddleware)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.detail["message"],
                "details": exc.details,
            }
        },
    )


app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(finance_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(content_router, prefix="/api/v1")
app.include_router(business_router, prefix="/api/v1")
app.include_router(intelligence_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(subscriptions_router, prefix="/api/v1")
app.include_router(webhook_router, prefix="/api/v1")
app.include_router(ads_router, prefix="/api/v1")
app.include_router(calculators_router, prefix="/api/v1")
app.include_router(markets_router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "version": settings.app_version, "env": settings.app_env}
