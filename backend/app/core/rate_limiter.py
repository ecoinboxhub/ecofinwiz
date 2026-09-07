import time
from typing import Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import get_settings
from app.database.redis import get_redis
from app.shared.logger import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()

    def _get_client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    def _get_user_id(self, request: Request) -> Optional[str]:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None
        try:
            from jose import jwt
            token = auth_header.split(" ")[1]
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=[self.settings.algorithm],
                options={"verify_aud": False},
            )
            return str(payload.get("sub"))
        except Exception:
            return None

    def _is_exempt(self, path: str) -> bool:
        for exempt in self.settings.rate_limit_exempt_path_list:
            if path == exempt or path.startswith(exempt.rstrip("*")):
                return True
        return False

    async def dispatch(self, request: Request, call_next):
        if not self.settings.rate_limit_active:
            return await call_next(request)

        if self._is_exempt(request.url.path):
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        user_id = self._get_user_id(request)

        if user_id:
            max_requests = self.settings.rate_limit_auth_requests
            window = self.settings.rate_limit_auth_window_seconds
            key = f"ratelimit:user:{user_id}"
        else:
            max_requests = self.settings.rate_limit_requests
            window = self.settings.rate_limit_window_seconds
            key = f"ratelimit:ip:{client_ip}"

        redis = await get_redis()
        now = int(time.time())
        window_start = now - window

        try:
            await redis.zremrangebyscore(key, 0, window_start)
            current_count = await redis.zcard(key)

            if current_count >= max_requests:
                reset_time = window_start + window
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": "RATE_LIMITED",
                            "message": "Too many requests. Please try again later.",
                        }
                    },
                    headers={
                        "Retry-After": str(window),
                        "X-RateLimit-Limit": str(max_requests),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(reset_time),
                    },
                )

            await redis.zadd(key, {str(now): now})
            await redis.expire(key, window)

            remaining = max_requests - current_count - 1
            reset_time = window_start + window

            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(max_requests)
            response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
            response.headers["X-RateLimit-Reset"] = str(reset_time)
            return response

        except Exception as e:
            logger.warning(f"Rate limiter unavailable (Redis?): {e}")
            return await call_next(request)