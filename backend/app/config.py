from pydantic_settings import BaseSettings
from pydantic import model_validator
from functools import lru_cache
import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    app_name: str = "EcoFinwize"
    app_version: str = "0.1.0"
    app_debug: bool = True
    app_env: str = "development"

    secret_key: str
    access_token_expire_minutes: int = 1440
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"

    google_client_id: str = ""
    google_client_secret: str = ""

    database_url: str = "postgresql+asyncpg://finwize:finwize@localhost:5432/finwize"
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "finwize"
    redis_url: str = "redis://localhost:6379/0"

    pinecone_api_key: str = ""
    pinecone_environment: str = "us-east-1-aws"
    pinecone_index_name: str = "finwize-knowledge"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    sentry_dsn: str = ""

    cors_origins: str = (
        "http://localhost:5300,http://localhost:3000,"
        "https://finwize.app,https://www.finwize.app,"
        "https://staging.finwize.app,https://admin.finwize.app"
    )

    sendgrid_api_key: str = ""
    mailgun_api_key: str = ""
    mailgun_domain: str = ""
    email_from_address: str = "noreply@finwize.app"
    email_from_name: str = "EcoFinwize"

    africas_talking_api_key: str = ""
    africas_talking_username: str = "finwize"
    sms_from_number: str = "FINWIZE"
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""

    paystack_secret_key: str = ""
    paystack_public_key: str = ""
    flutterwave_secret_key: str = ""
    flutterwave_public_key: str = ""
    flutterwave_encryption_key: str = ""

    posthog_api_key: str = ""
    posthog_host: str = "https://app.posthog.com"

    s3_bucket_name: str = ""
    s3_region: str = "eu-west-1"
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_endpoint_url: str = ""
    s3_use_path_style: bool = False
    local_storage_dir: str = ""

    newsapi_key: str = ""
    exchange_rate_api_key: str = ""
    jina_embedding_api_key: str = ""

    frontend_url: str = "http://localhost:5300"

    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    rate_limit_auth_requests: int = 200
    rate_limit_auth_window_seconds: int = 60
    rate_limit_exempt_paths: str = "/api/v1/health,/docs,/redoc,/openapi.json,/api/v1/auth/login,/api/v1/auth/register"

    @property
    def rate_limit_exempt_path_list(self) -> list[str]:
        return [p.strip() for p in self.rate_limit_exempt_paths.split(",")]

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def rate_limit_active(self) -> bool:
        """Rate limiting is auto-enabled in staging/production.

        An explicit RATE_LIMIT_ENABLED=true still wins everywhere (including
        local development); an explicit false always disables it. This lets the
        same settings object serve all environments without code changes.
        """
        if self.app_env.lower() in ("staging", "production"):
            return True
        return self.rate_limit_enabled

    @model_validator(mode="after")
    def validate_cors_origins(self) -> "Settings":
        """Validate CORS origins format on startup."""
        if not self.cors_origins:
            return self

        origin_pattern = re.compile(
            r"^https?://"
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
            r"localhost|"
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
            r"(?::\d+)?"
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        valid_origins = []
        for origin in self.cors_origin_list:
            if origin_pattern.match(origin):
                valid_origins.append(origin)
            else:
                logger.warning(
                    "Invalid CORS origin format (ignored): %s. Expected format: http(s)://host[:port]",
                    origin,
                )

        if len(valid_origins) != len(self.cors_origin_list):
            self.cors_origins = ",".join(valid_origins)

        return self

    @model_validator(mode="after")
    def validate_api_keys(self) -> "Settings":
        """Validate required API keys based on environment."""
        is_prod = self.app_env.lower() in ("staging", "production")

        # AI: At least one LLM provider required
        has_openrouter = bool(self.openrouter_api_key and self.openrouter_api_key != "your-openrouter-api-key")
        has_groq = bool(self.groq_api_key and self.groq_api_key != "your-groq-api-key")
        if not has_openrouter and not has_groq:
            if is_prod:
                raise ValueError(
                    "Production requires at least one LLM provider: OPENROUTER_API_KEY or GROQ_API_KEY"
                )
            else:
                logger.warning("No LLM provider configured (OPENROUTER_API_KEY or GROQ_API_KEY). AI features will be unavailable.")

        # Pinecone: Required for RAG, warn if missing
        if self.pinecone_api_key and self.pinecone_api_key != "your-pinecone-api-key":
            if not self.pinecone_index_name:
                logger.warning("PINECONE_API_KEY set but PINECONE_INDEX_NAME is empty")
        elif is_prod:
            logger.warning("PINECONE_API_KEY not configured. RAG features will use local embeddings fallback.")

        # Paystack: Required for payments in production
        if is_prod:
            if not self.paystack_secret_key or not self.paystack_secret_key.startswith("sk_"):
                raise ValueError("Production requires valid PAYSTACK_SECRET_KEY (must start with 'sk_')")
            if not self.paystack_public_key or not self.paystack_public_key.startswith("pk_"):
                raise ValueError("Production requires valid PAYSTACK_PUBLIC_KEY (must start with 'pk_')")
        else:
            if self.paystack_secret_key and not self.paystack_secret_key.startswith("sk_"):
                logger.warning("PAYSTACK_SECRET_KEY should start with 'sk_' (got: %s...)", self.paystack_secret_key[:10])
            if self.paystack_public_key and not self.paystack_public_key.startswith("pk_"):
                logger.warning("PAYSTACK_PUBLIC_KEY should start with 'pk_' (got: %s...)", self.paystack_public_key[:10])

        # Flutterwave: Optional, validate format if present
        if self.flutterwave_secret_key and not self.flutterwave_secret_key.startswith("FLWSECK_"):
            logger.warning("FLUTTERWAVE_SECRET_KEY should start with 'FLWSECK_'")
        if self.flutterwave_public_key and not self.flutterwave_public_key.startswith("FLWPUBK_"):
            logger.warning("FLUTTERWAVE_PUBLIC_KEY should start with 'FLWPUBK_'")

        # OpenRouter format check
        if has_openrouter and not self.openrouter_api_key.startswith("sk-"):
            logger.warning("OPENROUTER_API_KEY should start with 'sk-'")

        # Groq format check
        if has_groq and not self.groq_api_key.startswith("gsk_"):
            logger.warning("GROQ_API_KEY should start with 'gsk_'")

        # Pinecone format check
        if self.pinecone_api_key and not self.pinecone_api_key.startswith("pcsk_"):
            logger.warning("PINECONE_API_KEY should start with 'pcsk_'")

        return self

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,
            dotenv_settings,
            env_settings,
            file_secret_settings,
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
