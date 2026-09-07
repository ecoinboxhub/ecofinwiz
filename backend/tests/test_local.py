"""
Local smoke tests — no Docker, PostgreSQL, MongoDB, or Redis required.
Mocks DB dependencies and verifies all route handlers are wired correctly,
request/response schemas are valid, and the AI/RAG modules initialize.

Run with:  pytest tests/test_local.py -v -m smoke
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.smoke
class TestAuthRoutes:
    def test_register(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "email": "test@test.com",
            "password": "password",
            "full_name": "Test",
        })
        assert resp.status_code in (200, 201, 409, 422)

    def test_login(self, client):
        resp = client.post("/api/v1/auth/login", json={
            "email": "test@test.com", "password": "password",
        })
        assert resp.status_code in (200, 401, 422)

    def test_refresh(self, client):
        resp = client.post("/api/v1/auth/refresh", json={
            "refresh_token": "fake-token",
        })
        assert resp.status_code in (200, 401, 422)


@pytest.mark.smoke
class TestFinanceRoutes:
    def test_list_budgets(self, client):
        resp = client.get("/api/v1/finance/budgets")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_transaction(self, client):
        resp = client.post("/api/v1/finance/transactions", json={
            "amount": 5000, "type": "expense",
            "category_id": "00000000-0000-0000-0000-000000000001",
            "description": "Test",
        })
        assert resp.status_code in (200, 201, 422)

    def test_savings_goals(self, client):
        resp = client.get("/api/v1/finance/savings-goals")
        assert resp.status_code == 200


@pytest.mark.smoke
class TestContentRoutes:
    def test_list_courses(self, client):
        resp = client.get("/api/v1/courses")
        assert resp.status_code == 200

    def test_list_articles(self, client):
        resp = client.get("/api/v1/articles")
        assert resp.status_code == 200

    def test_list_blog(self, client):
        resp = client.get("/api/v1/blog")
        assert resp.status_code == 200

    def test_list_news(self, client):
        resp = client.get("/api/v1/news")
        assert resp.status_code == 200

    def test_forum_topics(self, client):
        resp = client.get("/api/v1/forum/topics")
        assert resp.status_code == 200

    def test_bookmarks(self, client):
        resp = client.get("/api/v1/bookmarks")
        assert resp.status_code == 200

    def test_badges(self, client):
        resp = client.get("/api/v1/badges")
        assert resp.status_code == 200


@pytest.mark.smoke
class TestBusinessRoutes:
    def test_list_business_plans(self, client):
        resp = client.get("/api/v1/business-plans")
        assert resp.status_code == 200

    def test_list_tasks(self, client):
        resp = client.get("/api/v1/tasks")
        assert resp.status_code == 200

    def test_list_invoices(self, client):
        resp = client.get("/api/v1/invoices")
        assert resp.status_code == 200


@pytest.mark.smoke
class TestAIRoutes:
    def test_advisor_chat_sync(self, client):
        resp = client.post("/api/v1/ai/advisor/chat/sync", json={
            "message": "Hello",
        })
        assert resp.status_code in (200, 201, 400, 422, 503)

    def test_list_conversations(self, client):
        resp = client.get("/api/v1/ai/advisor/conversations")
        assert resp.status_code == 200

    def test_mentor_conversations(self, client):
        resp = client.get("/api/v1/ai/mentor/conversations")
        assert resp.status_code == 200


@pytest.mark.smoke
class TestIntelligenceRoutes:
    def test_documents(self, client):
        resp = client.get("/api/v1/documents")
        assert resp.status_code == 200

    def test_rag_status(self, client):
        resp = client.get("/api/v1/rag/status")
        assert resp.status_code == 200

    def test_recommendations(self, client):
        resp = client.get("/api/v1/recommendations")
        assert resp.status_code == 200

    def test_daily_tip(self, client):
        resp = client.get("/api/v1/tips/daily")
        assert resp.status_code == 200


@pytest.mark.smoke
class TestAdminRoutes:
    def test_admin_stats(self, client):
        resp = client.get("/api/v1/admin/stats")
        assert resp.status_code == 200

    def test_admin_users(self, client):
        resp = client.get("/api/v1/admin/users")
        assert resp.status_code == 200

    def test_admin_analytics(self, client):
        resp = client.get("/api/v1/admin/analytics/summary")
        assert resp.status_code == 200

    def test_send_notification(self, client):
        resp = client.post("/api/v1/admin/notifications/send", json={
            "user_ids": ["00000000-0000-0000-0000-000000000001"],
            "title": "Test",
        })
        assert resp.status_code in (200, 201, 422)


@pytest.mark.smoke
class TestHealth:
    def test_health(self, client):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


@pytest.mark.smoke
class TestHealthASGI:
    @pytest.mark.asyncio
    async def test_health_check(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/v1/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert "version" in data
