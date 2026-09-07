"""
Integration tests — requires live PostgreSQL, MongoDB, and Redis.

Run with live DBs:
    pytest tests/test_integration.py -v -m integration

Run smoke tests only (mocked):
    pytest tests/ -v -m "not integration"

Run all tests:
    pytest tests/ -v
"""

import os
import uuid
from datetime import date, datetime, timezone

import pytest

pytestmark = pytest.mark.integration


# =====================================================================
# Health
# =====================================================================

class TestHealth:
    def test_health_endpoint(self, integration_client):
        resp = integration_client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data


# =====================================================================
# Auth
# =====================================================================

class TestAuth:
    def test_register_and_login(self, integration_client, db_available):
        if not db_available:
            pytest.skip("Databases not available")
        suffix = uuid.uuid4().hex[:8]
        email = f"inttest_{suffix}@finwize.app"
        password = "StrongPass123!"
        name = "Integration Tester"

        # Register
        resp = integration_client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": name},
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["user"]["email"] == email
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]

        # Login
        resp = integration_client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["user"]["email"] == email
        assert "access_token" in data["tokens"]

        # Refresh
        refresh_token = data["tokens"]["refresh_token"]
        resp = integration_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert resp.status_code == 200, resp.text
        assert "access_token" in resp.json()

        # Logout
        resp = integration_client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
        )
        assert resp.status_code == 204

    def test_register_duplicate_email(self, integration_client, db_available):
        if not db_available:
            pytest.skip("Databases not available")
        resp = integration_client.post(
            "/api/v1/auth/register",
            json={"email": "dupe@finwize.app", "password": "StrongPass123!", "full_name": "Dupe"},
        )
        if resp.status_code == 201:
            resp = integration_client.post(
                "/api/v1/auth/register",
                json={"email": "dupe@finwize.app", "password": "StrongPass123!", "full_name": "Dupe"},
            )
        assert resp.status_code == 409

    def test_login_wrong_password(self, integration_client, db_available):
        if not db_available:
            pytest.skip("Databases not available")
        resp = integration_client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@finwize.app", "password": "wrong"},
        )
        assert resp.status_code == 401


# =====================================================================
# Users
# =====================================================================

class TestUsers:
    def test_get_profile(self, db_available, integration_client, auth_headers):
        resp = integration_client.get("/api/v1/users/me", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "email" in data
        assert "full_name" in data

    def test_update_profile(self, db_available, integration_client, auth_headers):
        resp = integration_client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"full_name": "Updated Name", "persona_type": "freelancer"},
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["full_name"] == "Updated Name"

    def test_get_preferences(self, db_available, integration_client, auth_headers):
        resp = integration_client.get("/api/v1/users/me/preferences", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "currency" in data

    def test_update_preferences(self, db_available, integration_client, auth_headers):
        resp = integration_client.patch(
            "/api/v1/users/me/preferences",
            headers=auth_headers,
            json={"currency": "USD", "language": "fr"},
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["currency"] == "USD"

    def test_get_progress(self, db_available, integration_client, auth_headers):
        resp = integration_client.get("/api/v1/users/me/progress", headers=auth_headers)
        assert resp.status_code == 200, resp.text

    def test_get_notifications(self, db_available, integration_client, auth_headers):
        resp = integration_client.get("/api/v1/users/me/notifications", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        assert "items" in resp.json()

    def test_mark_notifications_read(self, db_available, integration_client, auth_headers):
        resp = integration_client.post("/api/v1/users/me/notifications/read-all", headers=auth_headers)
        assert resp.status_code == 200, resp.text

    def test_get_stats(self, db_available, integration_client, auth_headers):
        resp = integration_client.get("/api/v1/users/me/stats", headers=auth_headers)
        assert resp.status_code == 200, resp.text


# =====================================================================
# Finance: Budgets
# =====================================================================

class TestBudgets:
    def test_create_and_list_budgets(self, db_available, integration_client, auth_headers):
        resp = integration_client.post(
            "/api/v1/finance/budgets",
            headers=auth_headers,
            json={"name": "Monthly Food", "category": "Food", "monthly_limit": 50000},
        )
        assert resp.status_code == 201, resp.text
        budget = resp.json()
        assert budget["name"] == "Monthly Food"
        assert budget["monthly_limit"] == 50000.0
        budget_id = budget["id"]

        resp = integration_client.get("/api/v1/finance/budgets", headers=auth_headers)
        assert resp.status_code == 200
        ids = [b["id"] for b in resp.json()]
        assert budget_id in ids

    def test_budget_summary(self, db_available, integration_client, auth_headers):
        resp = integration_client.get("/api/v1/finance/budgets/summary", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "total_budget" in data
        assert "total_spent" in data

    def test_update_and_delete_budget(self, db_available, integration_client, auth_headers):
        resp = integration_client.post(
            "/api/v1/finance/budgets",
            headers=auth_headers,
            json={"name": "Temp Budget", "category": "Misc", "monthly_limit": 10000},
        )
        assert resp.status_code == 201
        b_id = resp.json()["id"]

        resp = integration_client.patch(
            f"/api/v1/finance/budgets/{b_id}",
            headers=auth_headers,
            json={"name": "Updated Budget", "monthly_limit": 20000},
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["name"] == "Updated Budget"

        resp = integration_client.delete(f"/api/v1/finance/budgets/{b_id}", headers=auth_headers)
        assert resp.status_code == 204


# =====================================================================
# Finance: Categories
# =====================================================================

class TestCategories:
    def test_create_and_list_categories(self, db_available, integration_client, auth_headers):
        resp = integration_client.post(
            "/api/v1/finance/categories",
            headers=auth_headers,
            json={"name": "Test Cat", "icon": "shopping-cart", "type": "expense"},
        )
        assert resp.status_code == 201, resp.text
        cat_id = resp.json()["id"]

        resp = integration_client.get("/api/v1/finance/categories", headers=auth_headers)
        assert resp.status_code == 200
        ids = [c["id"] for c in resp.json() if "id" in c]
        assert cat_id in ids

        resp = integration_client.delete(f"/api/v1/finance/categories/{cat_id}", headers=auth_headers)
        assert resp.status_code == 204


# =====================================================================
# Finance: Transactions
# =====================================================================

class TestTransactions:
    def test_create_and_list_transactions(self, db_available, integration_client, auth_headers):
        resp = integration_client.post(
            "/api/v1/finance/transactions",
            headers=auth_headers,
            json={
                "amount": 15000,
                "type": "expense",
                "category": "Food",
                "description": "Lunch meeting",
            },
        )
        assert resp.status_code == 201, resp.text
        txn = resp.json()
        txn_id = txn["id"]

        resp = integration_client.get("/api/v1/finance/transactions", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) >= 1

        resp = integration_client.get(
            f"/api/v1/finance/transactions?type=expense",
            headers=auth_headers,
        )
        assert resp.status_code == 200

    def test_update_and_delete_transaction(self, db_available, integration_client, auth_headers):
        resp = integration_client.post(
            "/api/v1/finance/transactions",
            headers=auth_headers,
            json={"amount": 5000, "type": "expense", "category": "Transport"},
        )
        assert resp.status_code == 201
        txn_id = resp.json()["id"]

        resp = integration_client.patch(
            f"/api/v1/finance/transactions/{txn_id}",
            headers=auth_headers,
            json={"amount": 6000, "description": "Updated"},
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["amount"] == 6000.0

        resp = integration_client.delete(f"/api/v1/finance/transactions/{txn_id}", headers=auth_headers)
        assert resp.status_code == 204

    def test_spending_summary(self, db_available, integration_client, auth_headers):
        resp = integration_client.get("/api/v1/finance/transactions/summary", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "categories" in data


# =====================================================================
# Finance: Savings Goals
# =====================================================================

class TestSavingsGoals:
    def test_create_and_list_goals(self, db_available, integration_client, auth_headers):
        resp = integration_client.post(
            "/api/v1/finance/savings-goals",
            headers=auth_headers,
            json={"name": "Emergency Fund", "target_amount": 500000},
        )
        # Free tier quota: first goal should succeed
        if resp.status_code == 403:
            pytest.skip("Quota exceeded for free tier")
        assert resp.status_code == 201, resp.text
        goal_id = resp.json()["id"]

        resp = integration_client.get("/api/v1/finance/savings-goals", headers=auth_headers)
        assert resp.status_code == 200
        ids = [g["id"] for g in resp.json()]
        assert goal_id in ids

        # Contribute
        resp = integration_client.post(
            f"/api/v1/finance/savings-goals/{goal_id}/contribute",
            headers=auth_headers,
            json={"amount": 25000},
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["current_amount"] >= 25000

        # Delete
        resp = integration_client.delete(f"/api/v1/finance/savings-goals/{goal_id}", headers=auth_headers)
        assert resp.status_code == 204

    def test_adaptive_budget_calculation(self, db_available, integration_client, auth_headers):
        resp = integration_client.get(
            "/api/v1/finance/budgets/adaptive/calculate",
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text


# =====================================================================
# Business: Tasks
# =====================================================================

class TestTasks:
    def test_create_and_list_tasks(self, db_available, integration_client, auth_headers):
        resp = integration_client.post(
            "/api/v1/tasks",
            headers=auth_headers,
            json={"title": "Review budget", "priority": "high", "status": "pending"},
        )
        assert resp.status_code == 201, resp.text
        task_id = resp.json()["id"]

        resp = integration_client.get("/api/v1/tasks", headers=auth_headers)
        assert resp.status_code == 200
        ids = [t["id"] for t in resp.json()]
        assert task_id in ids

        resp = integration_client.patch(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
            json={"status": "completed"},
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == "completed"

        resp = integration_client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
        assert resp.status_code == 204


# =====================================================================
# Business: Invoices
# =====================================================================

class TestInvoices:
    def test_create_and_list_invoices(self, db_available, integration_client, auth_headers):
        resp = integration_client.post(
            "/api/v1/invoices",
            headers=auth_headers,
            json={
                "client_name": "Acme Corp",
                "client_email": "billing@acme.com",
                "items": [{"description": "Consulting", "quantity": 10, "unit_price": 50000}],
                "subtotal": 500000,
                "total": 575000,
                "tax_rate": 15,
                "tax_amount": 75000,
            },
        )
        # Free tier may block invoice creation
        if resp.status_code == 403:
            pytest.skip("Invoice quota exceeded for free tier")
        assert resp.status_code == 201, resp.text
        inv_id = resp.json()["id"]

        # List
        resp = integration_client.get("/api/v1/invoices", headers=auth_headers)
        assert resp.status_code == 200

        # Mark paid
        resp = integration_client.post(
            f"/api/v1/invoices/{inv_id}/mark-paid",
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == "paid"

        # Delete
        resp = integration_client.delete(f"/api/v1/invoices/{inv_id}", headers=auth_headers)
        assert resp.status_code == 204


# =====================================================================
# Business: Plans
# =====================================================================

class TestBusinessPlans:
    def test_generate_and_list_plans(self, db_available, integration_client, auth_headers):
        resp = integration_client.post(
            "/api/v1/business-plans/generate",
            headers=auth_headers,
            json={"business_name": "TestBiz", "industry": "Tech", "description": "A test plan"},
        )
        # AI-dependent; may fall back or fail without API key
        if resp.status_code in (503, 502, 500):
            pytest.skip(f"AI generation unavailable: {resp.status_code}")
        assert resp.status_code == 201, resp.text
        plan_id = resp.json()["id"]

        resp = integration_client.get("/api/v1/business-plans", headers=auth_headers)
        assert resp.status_code == 200

        resp = integration_client.delete(f"/api/v1/business-plans/{plan_id}", headers=auth_headers)
        assert resp.status_code == 204


# =====================================================================
# Content: Courses
# =====================================================================

class TestCourses:
    def test_create_and_list_courses(self, db_available, mongo_available, integration_client, auth_headers):
        if not mongo_available:
            pytest.skip("MongoDB not available")
        resp = integration_client.post(
            "/api/v1/courses",
            headers=auth_headers,
            json={
                "title": "Test Course",
                "description": "Integration test course",
                "category": "Finance",
                "difficulty": "beginner",
                "lessons": [
                    {"title": "Lesson 1", "content": "Content 1", "order": 1},
                ],
            },
        )
        assert resp.status_code == 201, resp.text
        course_id = resp.json()["id"]

        resp = integration_client.get("/api/v1/courses", headers=auth_headers)
        assert resp.status_code == 200

        resp = integration_client.get(f"/api/v1/courses/{course_id}", headers=auth_headers)
        assert resp.status_code == 200

        resp = integration_client.post(
            f"/api/v1/courses/{course_id}/enroll",
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text

    def test_course_lesson_flow(self, db_available, mongo_available, integration_client, auth_headers):
        if not mongo_available:
            pytest.skip("MongoDB not available")
        resp = integration_client.post(
            "/api/v1/courses",
            headers=auth_headers,
            json={
                "title": "Lesson Flow Course",
                "description": "Test lesson flow",
                "category": "Finance",
                "difficulty": "beginner",
                "lessons": [
                    {"id": "l1", "title": "Lesson 1", "content": "Content 1", "order": 1},
                ],
            },
        )
        assert resp.status_code == 201
        course_id = resp.json()["id"]

        resp = integration_client.get(
            f"/api/v1/courses/{course_id}/lessons/l1",
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text

        resp = integration_client.post(
            f"/api/v1/courses/{course_id}/lessons/l1/complete",
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text

        resp = integration_client.get(
            f"/api/v1/courses/{course_id}/progress",
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text


# =====================================================================
# Content: Articles
# =====================================================================

class TestArticles:
    def test_create_and_list_articles(self, db_available, mongo_available, integration_client, auth_headers):
        if not mongo_available:
            pytest.skip("MongoDB not available")
        resp = integration_client.post(
            "/api/v1/articles",
            headers=auth_headers,
            json={
                "title": "Test Article",
                "content": "Article content here",
                "category": "Investing",
                "summary": "A summary",
            },
        )
        assert resp.status_code == 201, resp.text
        article_id = resp.json()["id"]

        resp = integration_client.get("/api/v1/articles", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1


# =====================================================================
# Content: Blog
# =====================================================================

class TestBlog:
    def test_create_and_list_blog(self, db_available, mongo_available, integration_client, auth_headers):
        if not mongo_available:
            pytest.skip("MongoDB not available")
        resp = integration_client.post(
            "/api/v1/blog",
            headers=auth_headers,
            json={
                "title": "Test Blog Post",
                "content": "Blog content here",
                "category": "Finance Tips",
                "summary": "A blog summary",
            },
        )
        assert resp.status_code == 201, resp.text

        resp = integration_client.get("/api/v1/blog", headers=auth_headers)
        assert resp.status_code == 200


# =====================================================================
# Content: Forum
# =====================================================================

class TestForum:
    def test_create_forum_topic_and_reply(self, db_available, mongo_available, integration_client, auth_headers):
        if not mongo_available:
            pytest.skip("MongoDB not available")
        resp = integration_client.post(
            "/api/v1/forum/topics",
            headers=auth_headers,
            json={"title": "Test Topic", "content": "Topic content", "category": "General"},
        )
        assert resp.status_code == 201, resp.text
        topic_id = resp.json()["id"]

        resp = integration_client.get("/api/v1/forum/topics", headers=auth_headers)
        assert resp.status_code == 200

        resp = integration_client.post(
            f"/api/v1/forum/topics/{topic_id}/replies",
            headers=auth_headers,
            json={"content": "A test reply"},
        )
        assert resp.status_code == 201, resp.text
        reply_id = resp.json()["id"]

        resp = integration_client.post(
            f"/api/v1/forum/replies/{reply_id}/mark-solution",
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text


# =====================================================================
# Content: Bookmarks
# =====================================================================

class TestBookmarks:
    def test_create_and_list_bookmarks(self, db_available, mongo_available, integration_client, auth_headers):
        if not mongo_available:
            pytest.skip("MongoDB not available")
        resp = integration_client.post(
            "/api/v1/bookmarks",
            headers=auth_headers,
            json={"content_type": "article", "content_id": "test-article-123"},
        )
        assert resp.status_code == 201, resp.text
        bm_id = resp.json()["id"]

        resp = integration_client.get("/api/v1/bookmarks", headers=auth_headers)
        assert resp.status_code == 200

        resp = integration_client.delete(f"/api/v1/bookmarks/{bm_id}", headers=auth_headers)
        assert resp.status_code == 204


# =====================================================================
# Content: Badges
# =====================================================================

class TestBadges:
    def test_list_badges(self, db_available, mongo_available, integration_client, auth_headers):
        if not mongo_available:
            pytest.skip("MongoDB not available")
        resp = integration_client.get("/api/v1/badges", headers=auth_headers)
        assert resp.status_code == 200, resp.text


# =====================================================================
# News
# =====================================================================

class TestNews:
    def test_create_and_list_news(self, db_available, mongo_available, integration_client, auth_headers):
        if not mongo_available:
            pytest.skip("MongoDB not available")
        resp = integration_client.post(
            "/api/v1/news",
            headers=auth_headers,
            json={
                "title": "Test News",
                "content": "News content",
                "category": "Markets",
                "summary": "News summary",
                "source": "Test",
            },
        )
        assert resp.status_code == 201, resp.text

        resp = integration_client.get("/api/v1/news", headers=auth_headers)
        assert resp.status_code == 200


# =====================================================================
# Subscriptions
# =====================================================================

class TestSubscriptions:
    def test_plans(self, db_available, integration_client):
        resp = integration_client.get("/api/v1/subscriptions/plans")
        assert resp.status_code == 200
        plans = resp.json()
        assert len(plans) >= 3

    def test_my_subscription(self, db_available, integration_client, auth_headers):
        resp = integration_client.get("/api/v1/subscriptions/my", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        assert resp.json()["plan"] in ("free", "pro", "business")

    def test_usage(self, db_available, integration_client, auth_headers):
        resp = integration_client.get("/api/v1/subscriptions/my/usage", headers=auth_headers)
        assert resp.status_code == 200, resp.text


# =====================================================================
# Intelligence
# =====================================================================

class TestIntelligence:
    def test_daily_tip(self, db_available, integration_client, auth_headers):
        resp = integration_client.get("/api/v1/tips/daily", headers=auth_headers)
        assert resp.status_code == 200, resp.text

    def test_recommendations(self, db_available, mongo_available, integration_client, auth_headers):
        if not mongo_available:
            pytest.skip("MongoDB not available")
        resp = integration_client.get("/api/v1/recommendations", headers=auth_headers)
        assert resp.status_code == 200, resp.text

    def test_rag_status(self, db_available, integration_client, auth_headers):
        resp = integration_client.get("/api/v1/rag/status", headers=auth_headers)
        assert resp.status_code == 200, resp.text

    def test_list_documents(self, db_available, integration_client, auth_headers):
        resp = integration_client.get("/api/v1/documents", headers=auth_headers)
        assert resp.status_code == 200, resp.text


# =====================================================================
# Ads
# =====================================================================

class TestAds:
    def test_get_ads(self, db_available, integration_client, auth_headers):
        resp = integration_client.get("/api/v1/ads/dashboard", headers=auth_headers)
        # Ads may be empty, but route should work
        assert resp.status_code in (200, 404), resp.text


# =====================================================================
# Admin
# =====================================================================

class TestAdmin:
    def test_admin_endpoints_require_admin(self, db_available, integration_client, auth_headers):
        resp = integration_client.get("/api/v1/admin/stats", headers=auth_headers)
        # Non-admin user should get 403
        assert resp.status_code == 403, resp.text

    def test_admin_stats_with_admin(self, db_available, mongo_available, integration_client, admin_headers):
        if not mongo_available:
            pytest.skip("MongoDB not available")
        resp = integration_client.get("/api/v1/admin/stats", headers=admin_headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "total_users" in data

    def test_admin_users(self, db_available, integration_client, admin_headers):
        resp = integration_client.get("/api/v1/admin/users", headers=admin_headers)
        assert resp.status_code == 200, resp.text
        assert "items" in resp.json()

    def test_admin_analytics(self, db_available, integration_client, admin_headers):
        resp = integration_client.get("/api/v1/admin/analytics/summary", headers=admin_headers)
        assert resp.status_code == 200, resp.text

    def test_admin_user_growth(self, db_available, integration_client, admin_headers):
        resp = integration_client.get("/api/v1/admin/stats/users/growth", headers=admin_headers)
        assert resp.status_code == 200, resp.text

    def test_admin_engagement(self, db_available, integration_client, admin_headers):
        resp = integration_client.get("/api/v1/admin/stats/engagement", headers=admin_headers)
        assert resp.status_code == 200, resp.text


# =====================================================================
# AI (sync only — streaming tested separately)
# =====================================================================

class TestAI:
    def test_advisor_chat_sync(self, db_available, integration_client, auth_headers):
        resp = integration_client.post(
            "/api/v1/ai/advisor/chat/sync",
            headers=auth_headers,
            json={"message": "What is compound interest?"},
        )
        # Without API keys, may return 503
        assert resp.status_code in (200, 503, 400, 403), resp.text

    def test_mentor_chat_sync(self, db_available, integration_client, auth_headers):
        resp = integration_client.post(
            "/api/v1/ai/mentor/chat/sync",
            headers=auth_headers,
            json={"message": "How do I start a business?"},
        )
        assert resp.status_code in (200, 503, 400, 403), resp.text

    def test_conversations(self, db_available, integration_client, auth_headers):
        resp = integration_client.get("/api/v1/ai/advisor/conversations", headers=auth_headers)
        assert resp.status_code == 200, resp.text

        resp = integration_client.get("/api/v1/ai/mentor/conversations", headers=auth_headers)
        assert resp.status_code == 200, resp.text


# =====================================================================
# Unauthenticated access
# =====================================================================

class TestUnauthenticated:
    def test_health_public(self, db_available, integration_client):
        resp = integration_client.get("/api/v1/health")
        assert resp.status_code == 200

    def test_protected_route_rejects_unauthenticated(self, db_available, integration_client):
        resp = integration_client.get("/api/v1/finance/budgets")
        assert resp.status_code in (401, 403, 422)
