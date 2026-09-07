# EcoFinwize — Software Requirements Specification (SWR)

> **Version**: 1.1
> **Status**: Implemented (v1.1 — All content migrated to PostgreSQL, MongoDB eliminated)
> **Last Updated**: July 14, 2026

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
                         Clients
               ┌──────────┐  ┌──────────┐
               │  React   │  │  Flutter │
               │  Web App │  │  Mobile  │
               │  (23 pg) │  │ (19 scr) │
               └────┬─────┘  └────┬─────┘
                    │              │
                    └──────┬───────┘
                           │ HTTPS / REST (JSON)
                      ┌────▼──────┐
                      │  FastAPI   │
                      │  Backend   │
                      │ (141 routes)│
                      └────┬──────┘
                           │
           ┌───────────────┼───────────────────┐
           │               │                   │
     ┌─────▼───┐     ┌────▼────┐    ┌─────────▼──┐
     │PostgreSQL│     │Pinecone │    │   Redis    │
     │ (async)  │     │Vector DB│    │ (caching)  │
     │ 33 models│     │1536 dim │    │            │
     └──────────┘     └─────────┘    └────────────┘
```

### 1.2 Module Architecture (Backend) — Actual

```
backend/
└── app/
    ├── main.py                    # FastAPI entry point (11 routers)
    ├── config.py                  # Pydantic Settings v2 + .env
    ├── models.py                  # 33 SQLAlchemy models
    ├── database/
    │   ├── postgres.py            # SQLAlchemy async engine + get_db
    │   └── redis.py               # Redis client + get_redis
    ├── core/
    │   ├── security.py            # JWT (HS256), bcrypt hashing
    │   ├── exceptions.py          # AppException, NotFound, Conflict, etc.
    │   └── pagination.py          # PaginationParams + PaginatedResponse
    ├── shared/
    │   ├── logger.py              # StreamHandler logger
    │   └── utils.py               # Placeholder
    ├── modules/
    │   ├── auth/                  # JWT + Google OAuth + password reset
    │   │   ├── router.py          # 7 endpoints
    │   │   ├── service.py         # Register, login, google, refresh, logout, forgot/reset password
    │   │   ├── schemas.py         # Request/response models
    │   │   └── dependencies.py    # get_current_user, get_current_admin
    │   ├── users/                 # Profile, preferences, progress, notifications
    │   │   ├── router.py          # 9 endpoints
    │   │   ├── service.py         # CRUD, progress, stats
    │   │   └── schemas.py
    │   ├── finance/               # Budget, transactions, savings, categories
    │   │   ├── router.py          # 19 endpoints
    │   │   ├── service.py         # Full CRUD, adaptive budget, summaries
    │   │   └── schemas.py
    │   ├── ai/                    # Advisor (Kemi), Mentor (Chidi)
    │   │   ├── router.py          # 14 endpoints
    │   │   ├── service.py         # Chat orchestrator, context, guardrails
    │   │   ├── schemas.py
    │   │   ├── providers.py       # OpenAICompatibleProvider
    │   │   ├── prompts.py         # System prompts
    │   │   ├── guardrails.py      # PII, harmful content, output filter
    │   │   └── context.py         # ContextAssembler
    │   ├── content/               # Courses, articles, blog, news, forum, badges
    │   │   ├── router.py          # 22 endpoints
    │   │   ├── service.py
    │   │   └── schemas.py
    │   ├── business/              # Business plans, tasks, invoices
    │   │   ├── router.py          # 14 endpoints
    │   │   ├── service.py
    │   │   └── schemas.py
    │   ├── intelligence/          # RAG, documents, recommendations, tips
    │   │   ├── router.py          # 10 endpoints
    │   │   ├── service.py
    │   │   ├── schemas.py
    │   │   └── rag.py             # Pinecone client, chunking, embedding
    │   ├── admin/                 # Dashboard, users, notifications, analytics
    │   │   ├── router.py          # 7 endpoints
    │   │   ├── service.py
    │   │   ├── schemas.py
    │   │   ├── ad_service.py
    │   │   └── ad_schemas.py
    │   ├── subscriptions/         # Plans, quotas, upgrade
    │   │   ├── router.py          # 4 endpoints
    │   │   ├── service.py
    │   │   └── schemas.py
    │   └── ads/                   # Ad serving engine
    │       ├── router.py          # 3 endpoints
    │       ├── service.py
    │       └── schemas.py
    ├── alembic/                   # 4 migrations (001-004)
    └── scripts/
        └── seed.py                # Demo user with sample data
```

### 1.3 Frontend Architecture (React) — Actual

```
frontend/src/
├── api/
│   └── client.ts                  # Axios instance + JWT refresh interceptor
├── context/
│   └── AuthContext.tsx            # Auth state (React Context API)
├── components/
│   ├── Layout.tsx                 # Header + 5-tab bottom nav + AdBanner + Outlet
│   ├── ProtectedRoute.tsx         # Auth guard + admin-only guard
│   └── AdBanner.tsx               # Contextual ad display for free tier
├── pages/                         # 23 pages (incl. ForgotPassword, ResetPassword, PaymentCallback)
│   ├── Landing.tsx                # Marketing hero, features, stats, CTA
│   ├── Login.tsx                  # Email + password login
│   ├── Register.tsx               # Registration form
│   ├── Dashboard.tsx              # Budget summary, recent txns, savings, tip, actions
│   ├── Budget.tsx                 # Budget list + CRUD with progress bars
│   ├── Transactions.tsx           # Transaction list with filters
│   ├── Savings.tsx                # Goals list + create/contribute
│   ├── Advisor.tsx                # Kemi AI chat (SSE streaming)
│   ├── Mentor.tsx                 # Chidi AI mentor chat
│   ├── Learning.tsx               # Courses, lessons, progress
│   ├── Articles.tsx               # Investment education articles
│   ├── Blog.tsx                   # Blog with comments
│   ├── News.tsx                   # News feed with categories
│   ├── Forum.tsx                  # Topics with replies, solutions
│   ├── BusinessTasks.tsx          # Task CRUD with status/priority
│   ├── Invoices.tsx               # Invoice list + create
│   ├── BusinessPlan.tsx           # AI business plan generator
│   ├── Profile.tsx                # User info, progress, stats
│   ├── Pricing.tsx                # Subscription plans display
│   ├── Notifications.tsx          # Notification list + mark read
│   └── Admin.tsx                  # Admin dashboard
├── App.tsx                        # 24 routes defined with React Router (incl. ForgotPassword, ResetPassword, PaymentCallback)
├── main.tsx                       # BrowserRouter + AuthProvider
└── index.css                      # Tailwind directives + custom styles
```

### 1.4 Mobile Architecture (Flutter) — Actual

```
mobile/lib/
├── main.dart                      # AuthGate -> LandingScreen or MainShell
├── config/
│   └── theme.dart                 # Brand colors (Sky Blue, Gold, Orange, Rose) - Material 3
├── services/
│   └── api_service.dart           # Singleton HTTP client with SharedPreferences token
├── providers/
│   ├── auth_provider.dart         # ChangeNotifier: login/register/logout/checkAuth
│   └── data_provider.dart         # Generic data state
├── screens/                       # 18 screens
│   ├── landing_screen.dart
│   ├── login_screen.dart
│   ├── register_screen.dart
│   ├── dashboard_screen.dart      # IndexedStack with 5-tab navigation
│   ├── budget_screen.dart
│   ├── transactions_screen.dart
│   ├── savings_screen.dart
│   ├── advisor_screen.dart        # Kemi AI chat
│   ├── mentor_screen.dart         # Chidi mentor chat
│   ├── learning_screen.dart
│   ├── articles_screen.dart
│   ├── news_screen.dart
│   ├── forum_screen.dart
│   ├── tasks_screen.dart
│   ├── invoices_screen.dart
│   ├── business_plan_screen.dart
│   ├── profile_screen.dart
│   ├── notifications_screen.dart
│   └── admin_screen.dart
└── widgets/
    ├── ad_banner.dart             # Ad display + embedded PricingScreen
    └── chat_bubble.dart           # Reusable chat UI widget
```

---

## 2. Technology Stack — Implemented

### 2.1 Backend

| Component | Technology | Notes |
|-----------|------------|-------|
| Framework | FastAPI (Python 3.12.10) | Async, auto OpenAPI docs |
| ASGI Server | Uvicorn | Dev mode with --reload |
| ORM | SQLAlchemy 2.0 (async) | 28 models, async session |
| Migrations | Alembic | 4 migrations applied (001-004) |
| Validation | Pydantic v2 | Built into FastAPI |
| Auth | python-jose + passlib | HS256 JWT, bcrypt hashing |
| PostgreSQL | asyncpg via SQLAlchemy | Running locally (v18) |
| MongoDB | Motor (async) | 6 collections |
| Redis | redis-py (async) | Caching, session management |
| Vector DB | pinecone-client | Configured, requires API key |
| AI Clients | openai + httpx | OpenRouter + Groq APIs |
| Testing | pytest + httpx | 26/28 smoke tests pass |

### 2.2 Frontend

| Component | Technology | Notes |
|-----------|------------|-------|
| Framework | React 19 + TypeScript 6 | 0 build errors |
| Build | Vite 8 | Fast dev startup |
| Routing | React Router v6 | 21 routes, protected routing |
| State | React Context API | AuthContext provider |
| API Client | Axios | Bearer token injection, 401 refresh interceptor |
| Styling | Tailwind CSS 3.4 | Custom brand palette (sky, gold, orange, rose) |
| Charts | Recharts 2 | Dashboard spending visualization |
| Icons | Lucide React | Tree-shakeable icons |
| Build Output | dist/ | 733 kB JS + 26 kB CSS (212 kB gzipped) |

### 2.3 Mobile

| Component | Technology | Notes |
|-----------|------------|-------|
| Framework | Flutter 3.22.0 (Dart 3.4) | Material 3 |
| State | Provider (ChangeNotifier) | Auth + data providers |
| Navigation | Navigator.push | Imperative routing |
| HTTP | http package | Singleton with token header |
| Local Storage | SharedPreferences | Token persistence |
| APK Size | split-per-abi | arm64-v8a: 7.1 MB, armeabi-v7a: 6.6 MB, x86_64: 7.3 MB |
| Additional Deps | shimmer, connectivity_plus, intl | Loading states, connectivity, formatting |

---

## 3. API Design

### 3.1 API Conventions

- **Base URL**: `http://localhost:8100/api/v1` (dev), `https://api.finwize.com/v1` (prod)
- **Format**: JSON (request/response)
- **Auth**: Bearer JWT token in `Authorization` header
- **Errors**: Consistent `{ "error": { "code": "...", "message": "..." } }` format
- **Pagination**: `?page=1&page_size=20` query params, `{ "items": [...], "total": N, "page": 1, "page_size": 20 }` response

### 3.2 Error Code Taxonomy

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTH_INVALID_CREDENTIALS` | 401 | Email or password incorrect |
| `AUTH_TOKEN_EXPIRED` | 401 | Access token expired, refresh required |
| `AUTH_TOKEN_INVALID` | 401 | Token malformed or revoked |
| `AUTH_EMAIL_NOT_VERIFIED` | 403 | Email verification required |
| `VALIDATION_ERROR` | 422 | Request body failed Pydantic validation |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource does not exist |
| `RESOURCE_CONFLICT` | 409 | Duplicate resource (e.g., duplicate email) |
| `RATE_LIMITED` | 429 | Too many requests (scaffolded, not enforced) |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

### 3.3 API Endpoints (v1) — Actual Implementation (141 Routes)

#### Auth (`/api/v1/auth`) — 7 endpoints

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| POST | /auth/register | Email/password registration | ✅ |
| POST | /auth/login | Email/password login | ✅ |
| POST | /auth/google | Google OAuth token verification | ✅ |
| POST | /auth/refresh | Refresh access token | ✅ |
| POST | /auth/logout | Invalidate refresh token | ✅ |
| POST | /auth/forgot-password | Send password reset email | ✅ |
| POST | /auth/reset-password | Reset password with JWT token | ✅ |

#### Users (`/api/v1/users`) — 9 endpoints

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| GET | /users/me | Get current user profile | ✅ |
| PATCH | /users/me | Update profile | ✅ |
| GET | /users/me/preferences | Get notification/locale preferences | ✅ |
| PATCH | /users/me/preferences | Update preferences | ✅ |
| GET | /users/me/progress | Get learning + savings progress | ✅ |
| GET | /users/me/stats | Get user stats (streak, badges, totals) | ✅ |
| GET | /users/me/notifications | List notifications (paginated) | ✅ |
| PATCH | /users/me/notifications/{id}/read | Mark single notification read | ✅ |
| POST | /users/me/notifications/read-all | Mark all notifications read | ✅ |

#### Finance (`/api/v1/finance`) — 19 endpoints

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| GET | /finance/budgets | List budgets (with spent/remaining) | ✅ |
| GET | /finance/budgets/summary | Aggregate budget summary | ✅ |
| POST | /finance/budgets | Create budget | ✅ |
| GET | /finance/budgets/{id} | Get budget detail | ✅ |
| PATCH | /finance/budgets/{id} | Update budget | ✅ |
| DELETE | /finance/budgets/{id} | Delete budget | ✅ |
| GET | /finance/budgets/adaptive/calculate | Get adaptive budget suggestion | ✅ |
| GET | /finance/transactions | List transactions (filterable, paginated) | ✅ |
| POST | /finance/transactions | Add transaction | ✅ |
| PATCH | /finance/transactions/{id} | Update transaction | ✅ |
| DELETE | /finance/transactions/{id} | Delete transaction | ✅ |
| GET | /finance/transactions/summary | Spending summary (by category/period) | ✅ |
| GET | /finance/categories | List user categories | ✅ |
| POST | /finance/categories | Create custom category | ✅ |
| DELETE | /finance/categories/{id} | Delete category | ✅ |
| GET | /finance/savings-goals | List savings goals (with progress) | ✅ |
| POST | /finance/savings-goals | Create savings goal | ✅ |
| GET | /finance/savings-goals/{id} | Get goal detail | ✅ |
| PATCH | /finance/savings-goals/{id} | Update goal | ✅ |
| DELETE | /finance/savings-goals/{id} | Delete goal | ✅ |
| POST | /finance/savings-goals/{id}/contribute | Add contribution to goal | ✅ |

#### AI (`/api/v1/ai`) — 16 endpoints

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| POST | /ai/advisor/chat | Chat with Kemi (SSE streaming) | ✅ |
| POST | /ai/advisor/chat/groq | Chat via Groq Llama (SSE streaming) | ✅ |
| POST | /ai/advisor/chat/sync | Non-streaming advisor chat | ✅ |
| POST | /ai/mentor/chat | Chat with Chidi (SSE streaming) | ✅ |
| POST | /ai/mentor/chat/sync | Non-streaming mentor chat | ✅ |
| POST | /ai/investment/chat | Chat with Musa (SSE streaming) | ✅ |
| POST | /ai/investment/chat/sync | Non-streaming investment chat | ✅ |
| GET | /ai/investment/conversations | List investment conversations | ✅ |
| POST | /ai/advisor/feedback | Submit 1-5 star rating | ✅ |
| POST | /ai/advisor/report | Report inappropriate response | ✅ |
| GET | /ai/advisor/conversations | List advisor conversations | ✅ |
| GET | /ai/mentor/conversations | List mentor conversations | ✅ |
| GET | /ai/advisor/conversations/{id} | Get conversation with messages | ✅ |
| GET | /ai/mentor/conversations/{id} | Get mentor conversation detail | ✅ |
| PATCH | /ai/advisor/conversations/{id}/archive | Archive conversation | ✅ |
| DELETE | /ai/advisor/conversations/{id} | Delete conversation | ✅ |
| DELETE | /ai/mentor/conversations/{id} | Delete mentor conversation | ✅ |

#### Content (`/api/v1`) — 43 endpoints (no `/content/` prefix — routes defined directly on router)

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| GET | /courses | List courses (filterable) | ✅ |
| POST | /courses | Create course (admin) | ✅ |
| GET | /courses/{course_id} | Get course detail with lessons | ✅ |
| PATCH | /courses/{course_id} | Update course (admin) | ✅ |
| DELETE | /courses/{course_id} | Delete course (admin) | ✅ |
| POST | /courses/{course_id}/enroll | Enroll user in course | ✅ |
| GET | /courses/{course_id}/lessons/{lesson_id} | Get lesson content | ✅ |
| POST | /courses/{course_id}/lessons/{lesson_id}/complete | Mark lesson complete | ✅ |
| POST | /courses/{course_id}/lessons/{lesson_id}/quiz | Submit quiz (auto-graded) | ✅ |
| GET | /courses/{course_id}/progress | Get user's course progress | ✅ |
| POST | /articles | Create article (admin) | ✅ |
| GET | /articles | List articles (filtered) | ✅ |
| GET | /articles/{article_id} | Get article by ID | ✅ |
| GET | /articles/slug/{slug} | Get article by slug | ✅ |
| PATCH | /articles/{article_id} | Update article (admin) | ✅ |
| DELETE | /articles/{article_id} | Delete article (admin) | ✅ |
| POST | /blog | Create blog post (admin) | ✅ |
| GET | /blog | List blog posts | ✅ |
| GET | /blog/{post_id} | Get blog post with content | ✅ |
| GET | /blog/slug/{slug} | Get blog post by slug | ✅ |
| PATCH | /blog/{post_id} | Update blog post (admin) | ✅ |
| DELETE | /blog/{post_id} | Delete blog post (admin) | ✅ |
| POST | /blog/{post_id}/comments | Add comment to blog | ✅ |
| GET | /blog/{post_id}/comments | List blog comments | ✅ |
| DELETE | /blog/comments/{comment_id} | Delete blog comment (admin) | ✅ |
| POST | /news | Create news item (admin) | ✅ |
| GET | /news | List news (filtered by category/region) | ✅ |
| GET | /news/{news_id} | Get news detail | ✅ |
| GET | /news/slug/{slug} | Get news by slug | ✅ |
| PATCH | /news/{news_id} | Update news (admin) | ✅ |
| DELETE | /news/{news_id} | Delete news (admin) | ✅ |
| POST | /forum/topics | Create forum topic | ✅ |
| GET | /forum/topics | List forum topics | ✅ |
| GET | /forum/topics/{topic_id} | Get topic with replies | ✅ |
| PATCH | /forum/topics/{topic_id} | Update topic | ✅ |
| DELETE | /forum/topics/{topic_id} | Delete topic | ✅ |
| POST | /forum/topics/{topic_id}/replies | Reply to topic | ✅ |
| POST | /forum/replies/{reply_id}/mark-solution | Mark reply as solution | ✅ |
| GET | /forum/categories | List forum categories | ✅ |
| POST | /bookmarks | Toggle bookmark (add/remove) | ✅ |
| GET | /bookmarks | List user bookmarks | ✅ |
| DELETE | /bookmarks/{bookmark_id} | Remove bookmark | ✅ |
| GET | /badges | List available badges | ✅ |

#### Business (`/api/v1`) — 15 endpoints (routes defined directly, no `/business/` prefix)

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| POST | /business-plans/generate | AI-generate business plan | ✅ |
| GET | /business-plans | List user's plans | ✅ |
| GET | /business-plans/{plan_id} | Get plan detail | ✅ |
| DELETE | /business-plans/{plan_id} | Delete plan | ✅ |
| POST | /tasks | Create task | ✅ |
| GET | /tasks | List tasks (filtered) | ✅ |
| GET | /tasks/{task_id} | Get task detail | ✅ |
| PATCH | /tasks/{task_id} | Update task | ✅ |
| DELETE | /tasks/{task_id} | Delete task | ✅ |
| POST | /invoices | Create invoice (auto-numbered) | ✅ |
| GET | /invoices | List invoices | ✅ |
| GET | /invoices/{invoice_id} | Get invoice with line items | ✅ |
| PATCH | /invoices/{invoice_id} | Update invoice | ✅ |
| POST | /invoices/{invoice_id}/mark-paid | Mark invoice as paid | ✅ |
| DELETE | /invoices/{invoice_id} | Delete invoice | ✅ |

#### Intelligence (`/api/v1/intelligence`) — 11 endpoints

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| POST | /intelligence/documents/upload | Upload document (auto-index) | ✅ |
| GET | /intelligence/documents | List uploaded documents | ✅ |
| GET | /intelligence/documents/{doc_id} | Get document metadata | ✅ |
| GET | /intelligence/documents/{doc_id}/download | Download document file | ✅ |
| PATCH | /intelligence/documents/{doc_id} | Update document metadata | ✅ |
| DELETE | /intelligence/documents/{doc_id} | Delete document | ✅ |
| POST | /intelligence/rag/query | Query RAG knowledge base | ✅ |
| GET | /intelligence/rag/status | Get RAG connection status | ✅ |
| GET | /intelligence/recommendations | Get personalized recommendations | ✅ |
| GET | /intelligence/tips/daily | Get daily personalized tip | ✅ |
| GET | /intelligence/tips | List all tips | ✅ |

#### Admin (`/api/v1/admin`) — 12 endpoints

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| GET | /admin/stats | Platform overview stats | ✅ |
| GET | /admin/stats/users/growth | User growth metrics | ✅ |
| GET | /admin/stats/engagement | Engagement metrics | ✅ |
| GET | /admin/users | List all users (paginated) | ✅ |
| GET | /admin/users/{id} | Get user detail | ✅ |
| PATCH | /admin/users/{id} | Update user (suspend, change role) | ✅ |
| POST | /admin/notifications/send | Broadcast notification to all users | ✅ |
| GET | /admin/analytics/summary | Aggregate analytics | ✅ |
| GET | /admin/ads/campaigns | List ad campaigns | ✅ |
| POST | /admin/ads/campaigns | Create ad campaign | ✅ |
| PATCH | /admin/ads/campaigns/{campaign_id} | Update ad campaign | ✅ |
| GET | /admin/ads/stats | Ad campaign stats | ✅ |

#### Subscriptions (`/api/v1/subscriptions`) — 4 endpoints

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| GET | /subscriptions/plans | List available plans | ✅ |
| GET | /subscriptions/my | Get current user's subscription | ✅ |
| GET | /subscriptions/my/usage | Get current usage vs quota | ✅ |
| POST | /subscriptions/upgrade | Upgrade subscription plan (Paystack/Flutterwave) | ✅ |

#### Ads (`/api/v1/ads`) — 2 endpoints (ad campaign CRUD moved to admin module)

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| GET | /ads/{page_context} | Get ad for page context | ✅ |
| POST | /ads/impression | Track ad impression | ✅ |

#### System — 1 endpoint

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| GET | /api/v1/health | Health check | ✅ |

### 3.4 API Mismatches Fixed (Integration Phase)

The following frontend-to-backend path mismatches were identified and fixed during integration:

| Frontend Called | Backend Expects | Fix Applied |
|-----------------|----------------|-------------|
| `PUT /finance/budgets/{id}` | `PATCH /finance/budgets/{id}` | Frontend PUT -> PATCH |
| `/finance/savings` | `/finance/savings-goals` | Frontend path updated (4 occurrences) |
| `/finance/savings/{id}/contribute` | `/finance/savings-goals/{id}/contribute` | Frontend path updated |
| `/intelligence/daily-tip` | `/intelligence/tips/daily` | Frontend path updated (2 occurrences) |
| `/users/progress` | `/users/me/progress` | Frontend path updated (2 occurrences) |
| `/users/notifications` | `/users/me/notifications` | Frontend path updated (2 occurrences) |
| `/users/notifications/{id}/read` | `/users/me/notifications/{id}/read` | Frontend path updated |
| `/users/notifications/read-all` | `/users/me/notifications/read-all` | Frontend path updated (2 occurrences) |
| `/admin/notifications/broadcast` | `/admin/notifications/send` | Frontend path updated |
| `/business/business-plans/generate` | `/business-plans/generate` | Frontend path corrected (SWR had wrong `/business/` prefix) |
| *(missing)* | `/finance/budgets/summary` | **New endpoint implemented** |

---

## 4. Database Schema

### 4.1 PostgreSQL — 28 Models (26 Tables + 2 Code Models)

The following tables are implemented via SQLAlchemy models with 4 Alembic migrations:

| Table | Purpose | Migration |
|-------|---------|-----------|
| `users` | User accounts, auth, persona, role | 001 |
| `oauth_accounts` | Google OAuth provider links | 001 |
| `refresh_tokens` | JWT refresh token store (hashed) | 001 |
| `user_preferences` | Notification/locale/theme preferences | 001 |
| `onboarding_answers` | Onboarding questionnaire data | 001 |
| `budgets` | Budget records (per-category limits) | 001 |
| `transactions` | Income/expense records | 001 |
| `categories` | Custom transaction categories | 001 |
| `savings_goals` | Savings targets with deadlines | 001 |
| `savings_contributions` | Goal contribution records | 001 |
| `ai_conversations` | Advisor and mentor conversation metadata | 001 |
| `ai_messages` | Individual chat messages in conversations | 001 |
| `business_plans` | Generated business plans (JSON) | 003 |
| `tasks` | SME task management | 003 |
| `invoices` | Invoice records with line items | 003 |
| `notifications` | In-app notification records | 001 |
| `user_lessons` | Lesson completion tracking | 003 |
| `user_badges` | Earned achievement badges | 002 |
| `badge_rules` | Badge definition criteria | 002 |
| `forum_topics` | Community forum topics (with pin/lock) | 002 |
| `forum_replies` | Forum topic replies (with solution flag) | 002 |
| `bookmarks` | User content bookmarks (polymorphic) | 002 |
| `recommendation_log` | Recommendation history | 003 |
| `daily_tips` | Personalized daily tip rotation | 003 |
| `knowledge_documents` | RAG document metadata | 003 |
| `device_tokens` | Push notification device tokens | 001 |

**Code models (not separate tables)**:
- `Subscription` — Plan definition with feature limits (mapped to `users.subscription_plan` column)
- `UsageQuota` — Per-user usage tracking against plan limits

### 4.2 MongoDB — DEPRECATED (All Content Migrated to PostgreSQL)

All content previously stored in MongoDB (courses, articles, blog posts, blog comments, news, recommendations) was migrated to PostgreSQL as of **Migration 005 (MongoDB→PG content)**. The MongoDB dependency (`motor`) has been removed from requirements. All 33 models now live in PostgreSQL.

| Former MongoDB Collection | PostgreSQL Table | Migration |
|--------------------------|-----------------|-----------|
| `courses` | `courses` | 005 |
| `articles` | `articles` | 005 |
| `news` | `news` | 005 |
| `blog_posts` | `blog_posts` | 005 |
| `blog_comments` | `blog_comments` | 005 |
| `recommendations` | `recommendation_log` | 003 (was already PG) |

### 4.3 Pinecone Vector Index (Configured, Requires API Key)

```
Index:     finwize-knowledge
Dimension: 384 (or 1536 depending on embedding model)
Metric:    cosine
```

---

## 5. AI Architecture

### 5.1 AI Models

| AI Feature | Primary Model | Fallback Model | Streaming |
|------------|---------------|----------------|-----------|
| Kemi Advisor | OpenRouter GPT-4o-mini | Groq Llama-3.3-70b | ✅ SSE |
| Chidi Mentor | OpenRouter GPT-4o-mini | Groq Llama-3.3-70b | ✅ SSE |
| Musa Investment | OpenRouter GPT-4o-mini | Groq Llama-3.3-70b | ✅ SSE |
| Business Plan | Groq Llama-3.3-70b | OpenRouter GPT-4o-mini | ❌ (synchronous) |
| RAG Query | OpenAI-compatible embedding | N/A | ❌ |

### 5.2 AI Guardrails (Implemented)

| Guardrail | Approach | Status |
|-----------|----------|--------|
| PII Redaction | Regex-based masking (email, phone, SSN) before LLM call | ✅ |
| Harmful Content Detection | Blacklist-based detection of harmful financial advice patterns | ✅ |
| Output Filtering | LLM response scanned for prohibited content after generation | ✅ |
| Context Assembly | User profile + budget + goals + learning history injected into prompt | ✅ |
| Source Citations | RAG responses include source document references | ✅ |
| Response Rating | 1-5 star feedback + report inappropriate button per response | ✅ |

### 5.3 AI Evaluation Framework

| Layer | Method | Threshold |
|-------|--------|-----------|
| 1. Automated Safety | PII filter, harmful content detection | Block on match |
| 2. RAG Relevance | Cosine similarity score | > 0.75 |
| 3. User Ratings | 1-5 star feedback | < 3 stars -> human review |
| 4. Human Evaluation | 100 random conversations/month | Accuracy + helpfulness + safety |

---

## 6. Security Architecture

### 6.1 Authentication Flow

```
Registration:
  POST /auth/register -> bcrypt hash password -> INSERT user
                      -> flush user (get user.id)
                      -> INSERT user_preferences with user_id
                      -> Generate JWT (access + refresh)
                      -> Return tokens + user profile

Login:
  POST /auth/login -> lookup user by email -> verify password
                   -> check is_active -> generate JWT tokens
                   -> store refresh token hash
                   -> Return tokens + user profile

Token Refresh:
  POST /auth/refresh -> validate refresh token -> check hash in DB
                      -> delete old refresh token
                      -> generate new access + refresh tokens
                      -> Return new tokens
```

### 6.2 Security Measures

| Layer | Measure | Status |
|-------|---------|--------|
| Transport | TLS 1.3, HSTS | ⬜ Requires deployment |
| Auth | bcrypt (passlib), JWT HS256 (python-jose), refresh rotation | ✅ Implemented |
| API | CORS whitelist (configurable origins) | ✅ Configured (localhost:5300) |
| PII | PII masking in logs, PII redaction before AI calls | ✅ Partial (no AES-256 at rest) |
| AI | Input sanitization, harmful content guardrails | ✅ Implemented |
| DB | Parameterized queries (SQLAlchemy ORM) | ✅ Implemented |
| Secrets | .env file (python-dotenv / Pydantic Settings) | ✅ Implemented |
| Rate Limiting | `RateLimited` exception exists | ⬜ Not enforced |

---

## 7. Deployment & Infrastructure

### 7.1 Development Environment

| Service | Host | Port | Status |
|---------|------|------|--------|
| FastAPI Backend | localhost | 8100 | ✅ Running (--reload) |
| React Frontend | localhost | 5300 | ✅ Running (Vite dev) |
| PostgreSQL | localhost | 5432 | ✅ Running (v18) |
| Redis | localhost | 6379 | ✅ Running |
| Flutter Mobile | emulator-5554 | — | ✅ APK installed on Pixel_10 (Android 14) |

### 7.2 Docker Services (docker-compose.yml)

| Service | Image | Port | Status |
|---------|-------|------|--------|
| api | finwize-api (local build) | 8100 | ✅ Configured |
| postgres | postgres:18-alpine | 5432 | ✅ Configured |
| redis | redis:7-alpine | 6379 | ✅ Configured |

### 7.3 CI/CD Pipeline (GitHub Actions)

| Job | Trigger | Action |
|-----|---------|--------|
| lint | PR + push to main | ruff check on app/ |
| test | PR + push to main | pytest with PostgreSQL service container |
| build | Push to main | Docker image build + push to Docker Hub |

### 7.4 Known Gaps for Production Deployment

| Area | Issue | Fix Required | Priority |
|------|-------|-------------|----------|
| CORS | Only allows localhost:5300 | Add Vercel/Render domain | Critical |
| Frontend API URL | `VITE_API_URL` env not set for prod | Configure in Vercel | Critical |
| Flutter API URL | Hardcoded to `10.0.2.2:8100` | Build flavors for prod | Critical |
| API Keys | OpenRouter/Groq keys not in `.env` | Add API keys | High |
| API Keys | Pinecone key not in `.env` | Add API key | High |
| Rate Limiting | `RateLimited` exception, middleware implemented | Enforce via Redis | Medium |
| Email | SendGrid configured (403 on unverified sender) | Verify sender identity | Medium |
| PDF Generation | Business plan JSON-only | Add PDF library (ReportLab) | Low |
| Monitoring | No Sentry/PostHog integration | Add monitoring tools | Low |
| Offline-first | No Service Worker or cache | Implement SW + sync queue | Medium |
| Frontend tests | 0% coverage | Add React Testing Library | Low |

---

## 8. Testing Strategy

| Layer | Type | Tool | Coverage | Status |
|-------|------|------|----------|--------|
| Backend | Integration | pytest + httpx | 65 passing + 8 skipped (0 failures) | ✅ |
| Backend | Local Smoke | pytest | 29/29 passing | ✅ |
| Frontend | Build | tsc + vite | 0 TypeScript errors, 864 kB JS + 29 kB CSS | ✅ |
| Mobile | Build | flutter build apk --split-per-abi | 3 split APKs built | ✅ |
| Mobile | Analysis | dart analyze | Clean (no warnings) | ✅ |
| API | Verified | curl manual + automated | All 141 endpoints responsive | ✅ |
| API | Auth Flow | pytest | Register -> Login -> Refresh -> Logout + Forgot/Reset password | ✅ |
| Frontend | Unit | Not implemented | — | ⬜ |
| Mobile | Widget | Not implemented | — | ⬜ |
| E2E | Cross-surface | Not implemented | — | ⬜ |
| Load | Performance | Not implemented | — | ⬜ |

---

## 9. Key Metrics Summary

| Metric | Value |
|--------|-------|
| Backend routes | 141 |
| Database models | 33 SQLAlchemy (33 tables) |
| MongoDB | Eliminated — all content migrated to PostgreSQL |
| Alembic migrations | 5 (001, 002, 003, 004, 005) |
| Backend modules | 11 (auth, users, finance, ai, content, business, intelligence, admin, subscriptions, ads) |
| React pages | 23 (incl. ForgotPassword, ResetPassword, PaymentCallback) |
| Flutter screens | 19 (incl. admin screen) |
| Frontend build size | 864 kB JS + 29 kB CSS (245 kB gzipped) |
| APK sizes | arm64-v8a: 7.1 MB, armeabi-v7a: 6.6 MB, x86_64: 7.3 MB |
| Python version | 3.12.10 |
| Flutter version | 3.22.0 |
| PostgreSQL version | 18 |
| Backend tests | 65 passing + 8 skipped (integration), 29 passing (local smoke) |

---

## 10. Glossary

| Term | Definition |
|------|------------|
| RAG | Retrieval-Augmented Generation — AI grounded in retrieved documents |
| Persona | User archetype (Freelancer, SME, Student, Worker, Investor) |
| Adaptive Budget | Budget that adjusts based on actual income (percentage-based limits) |
| Streak | Consecutive days of app usage / learning activity |
| JWT | JSON Web Token — stateless authentication mechanism |
| SSE | Server-Sent Events — streaming AI responses over HTTP |
| Kemi | AI Financial Advisor persona (name means "mine" in Yoruba) |
| Chidi | AI Business Mentor persona (name means "God exists" in Igbo) |
| CPM | Cost Per Mille — ad revenue per 1,000 impressions |
| MoSCoW | Prioritization framework: Must have, Should have, Could have, Won't have |
