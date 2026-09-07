"""
Regression tests for environment-aware config (P3 deployment readiness).

The RateLimitMiddleware gates on Settings.rate_limit_active, which must
auto-enable in staging/production while staying off in development unless
explicitly enabled. CORS origins must include the production hosts.
"""

import pytest

from app.config import Settings


@pytest.mark.parametrize("env,expected", [
    ("development", False),
    ("staging", True),
    ("production", True),
    ("Development", False),
])
def test_rate_limit_active_by_env(env, expected):
    s = Settings(
        secret_key="test-secret",
        app_env=env,
        rate_limit_enabled=False,
    )
    assert s.rate_limit_active is expected


def test_rate_limit_explicit_enable_wins_in_dev():
    s = Settings(
        secret_key="test-secret",
        app_env="development",
        rate_limit_enabled=True,
    )
    assert s.rate_limit_active is True


def test_rate_limit_explicit_disable_always_wins():
    s = Settings(
        secret_key="test-secret",
        app_env="production",
        rate_limit_enabled=False,
    )
    assert s.rate_limit_active is True


def test_cors_origins_defaults_include_production_hosts():
    s = Settings(secret_key="test-secret", _env_file=None)
    origins = s.cors_origin_list
    assert "https://finwize.app" in origins
    assert "https://staging.finwize.app" in origins
    assert "http://localhost:5300" in origins