import os
from unittest.mock import AsyncMock, MagicMock

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-smoke-tests")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.database.postgres import get_db
from app.modules.auth.dependencies import get_current_user


# ── Smoke-test fixtures (mocked DB) ─────────────────────────────────


@pytest.fixture
def mock_db():
    session = AsyncMock()
    execute_result = MagicMock()
    execute_result.scalar.return_value = None
    execute_result.scalar_one_or_none.return_value = None
    execute_result.all.return_value = []
    execute_result.first.return_value = None
    session.execute.return_value = execute_result
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()

    added = []

    def _track_add(obj):
        added.append(obj)

    def _apply_defaults():
        for obj in added:
            for col in obj.__mapper__.columns:
                val = getattr(obj, col.key)
                if val is not None:
                    continue
                if col.default is not None:
                    if col.default.is_scalar:
                        setattr(obj, col.key, col.default.arg)
                    elif col.default.is_callable:
                        try:
                            setattr(obj, col.key, col.default.arg())
                        except TypeError:
                            try:
                                setattr(obj, col.key, col.default.arg(ctx=None))
                            except TypeError:
                                pass
                elif col.server_default is not None:
                    from datetime import datetime, timezone
                    setattr(obj, col.key, datetime.now(timezone.utc))

    session.add = MagicMock(side_effect=_track_add)
    session.flush = AsyncMock(side_effect=_apply_defaults)
    session.delete = AsyncMock()
    return session


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = "00000000-0000-0000-0000-000000000001"
    user.email = "test@finwize.app"
    user.full_name = "Test User"
    user.is_active = True
    user.is_admin = True
    user.avatar_url = None
    user.persona_type = "student"
    user.onboarding_completed = True
    user.plan = "free"
    user.created_at = None
    user.updated_at = None
    return user


@pytest.fixture(autouse=True)
def override_deps_smoke(request, mock_db, mock_user):
    """Override FastAPI dependencies for smoke tests. Skips for integration."""
    is_integration = any(
        mark.name == "integration" for mark in request.node.iter_markers()
    )
    if not is_integration:
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    if not is_integration:
        app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


# ── Integration-test fixtures (live DB) ──────────────────────────────


def check_db_connectivity():
    """Quick check if databases are reachable. Returns True if all OK."""
    pg_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://finwize:finwize@localhost:5432/finwize",
    )
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        import asyncio

        async def _try():
            engine = create_async_engine(pg_url, pool_size=1, max_overflow=0)
            try:
                async with engine.connect():
                    return True
            except Exception:
                return False
            finally:
                await engine.dispose()

        return asyncio.run(_try())
    except Exception:
        return False


def pytest_configure(config):
    """Add custom marker for external API tests."""
    config.addinivalue_line("markers", "external: marks tests that need external API keys")


@pytest.fixture(scope="session")
def db_available():
    """Session-level fixture to check DB connectivity once."""
    return check_db_connectivity()


def check_mongo_connectivity():
    """Quick check if MongoDB is reachable."""
    url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    try:
        from pymongo import MongoClient

        client = MongoClient(url, serverSelectionTimeoutMS=3000)
        client.admin.command("ping", serverSelectionTimeoutMS=3000)
        client.close()
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def mongo_available():
    """Session-level fixture to check MongoDB connectivity once."""
    return check_mongo_connectivity()


@pytest.fixture
def integration_client():
    """Creates a test client (dependencies NOT overridden -> live DB)."""
    app.dependency_overrides.clear()
    with TestClient(app) as client:
        yield client


@pytest.fixture
def auth_headers(integration_client, db_available):
    """Register a test user and return Authorization headers."""
    if not db_available:
        pytest.skip("Databases not available")

    import random
    import string

    suffix = "".join(random.choices(string.ascii_lowercase, k=8))
    email = f"test_{suffix}@finwize.integration"
    password = "TestPass123!"

    resp = integration_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Integration Tester"},
    )
    if resp.status_code == 201:
        data = resp.json()
        token = data["tokens"]["access_token"]
    elif resp.status_code == 409:
        resp2 = integration_client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        data = resp2.json()
        token = data["tokens"]["access_token"]
    else:
        pytest.skip(f"Could not authenticate: {resp.status_code} {resp.text[:200]}")

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(integration_client, db_available):
    """Return admin auth headers. Registers a user and promotes to admin."""
    if not db_available:
        pytest.skip("Databases not available")

    import asyncio
    import random
    import string

    suffix = "".join(random.choices(string.ascii_lowercase, k=8))
    email = f"admin_{suffix}@finwize.integration"
    password = "AdminPass123!"

    resp = integration_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Admin Tester"},
    )
    if resp.status_code not in (201, 409):
        pytest.skip(f"Could not register admin: {resp.status_code}")
    if resp.status_code == 201:
        token = resp.json()["tokens"]["access_token"]
    else:
        resp2 = integration_client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        if resp2.status_code != 200:
            pytest.skip(f"Could not login admin: {resp2.status_code}")
        token = resp2.json()["tokens"]["access_token"]

    # Promote user to admin directly via DB
    from sqlalchemy.ext.asyncio import create_async_engine
    from app.models import User
    from sqlalchemy import update

    pg_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://finwize:finwize@localhost:5432/finwize",
    )

    async def _promote():
        engine = create_async_engine(pg_url)
        async with engine.begin() as conn:
            await conn.execute(
                update(User).where(User.email == email).values(is_admin=True)
            )
        await engine.dispose()

    asyncio.run(_promote())

    return {"Authorization": f"Bearer {token}"}
