# EcoFinwize — Production Deployment & Implementation Guide

> **Purpose**: Step-by-step guide to take EcoFinwize v1.0 from local development to a live, production-ready platform.
> **Status**: All features built. This guide covers Phases 10+ (Pilot, Launch, Post-Launch).
> **Last Updated**: June 27, 2026

---

## Table of Contents

1. [Critical Path (Blocking Launch)](#1-critical-path-blocking-launch)
   - 1.1 Backend Production Deployment
   - 1.2 CORS Configuration
   - 1.3 Frontend Environment Setup
   - 1.4 Flutter Production Build
   - 1.5 API Key Provisioning
2. [High Priority](#2-high-priority)
   - 2.1 Email Service Integration
   - 2.2 Rate Limiting Middleware
   - 2.3 Load Testing
3. [Medium Priority](#3-medium-priority)
   - 3.1 Error Monitoring (Sentry)
   - 3.2 Offline Resilience
   - 3.3 Database Backups
4. [Nice to Have](#4-nice-to-have)
   - 4.1 Frontend Tests
   - 4.2 Flutter Tests
   - 4.3 PDF Export
   - 4.4 WCAG Accessibility Audit
   - 4.5 Dark Mode
5. [Post-Launch Roadmap](#5-post-launch-roadmap)

---

## 1. Critical Path (Blocking Launch)

### 1.1 Backend Production Deployment

**Target**: FastAPI backend running on Railway (or Render) with PostgreSQL, MongoDB, and Redis.

#### Step 1.1.1: Create accounts
- Sign up at [railway.app](https://railway.app) or [render.com](https://render.com)
- Install Railway CLI: `npm i -g @railway/cli`

#### Step 1.1.2: Provision production databases

**Railway (easiest — all-in-one):**
```bash
railway login
railway init
# Add PostgreSQL, MongoDB, and Redis plugins via dashboard or CLI:
railway add postgres
railway add mongodb
railway add redis
```

**Render (alternative):**
- Create a PostgreSQL instance (Render Dashboard -> New -> PostgreSQL)
- Create a Redis instance (Render Dashboard -> New -> Redis)
- For MongoDB, use MongoDB Atlas free tier (M0): https://www.mongodb.com/atlas

#### Step 1.1.3: Prepare backend for production

**File: `backend/Dockerfile`** — already exists and is production-ready:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Remove `--reload` from the production CMD (already correct in Dockerfile).

#### Step 1.1.4: Create `backend/.env.production`

```
APP_NAME=EcoFinwize
APP_VERSION=1.0.0
APP_DEBUG=false
APP_ENV=production

SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(32))">
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256

# Railway auto-provides these as DATABASE_URL, MONGO_URL, REDIS_URL
# For Render/Atlas, use the connection strings from the dashboard:
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/finwize?sslmode=require
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/finwize
MONGODB_DB_NAME=finwize
REDIS_URL=rediss://:password@host:6379

PINECONE_API_KEY=<see section 1.5>
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=finwize-knowledge

OPENROUTER_API_KEY=<see section 1.5>
OPENROUTER_MODEL=openai/gpt-4o-mini

GROQ_API_KEY=<see section 1.5>
GROQ_MODEL=llama-3.3-70b-versatile

SENTRY_DSN=<see section 3.1>

CORS_ORIGINS=https://finwize.vercel.app,https://www.finwize.app
```

#### Step 1.1.5: Deploy

**Railway:**
```bash
railway up                    # Deploys backend/
railway domain                # Get public URL (e.g., finwize.up.railway.app)
```

**Render:**
- Connect GitHub repo -> Select backend/ -> Build command: `pip install -r requirements.txt` -> Start command: `uvicorn app.main:app --host 0.0.0.0 --port 8100`

#### Step 1.1.6: Run production migrations

```bash
# After deployment, run migrations against the production DB:
railway run alembic upgrade head

# Verify health endpoint:
curl https://finwize.up.railway.app/api/v1/health
# Expected: {"status":"ok","version":"1.0.0","env":"production"}
```

#### Step 1.1.7: Seed demo data (optional)

```bash
railway run python -m app.scripts.seed
```

---

### 1.2 CORS Configuration

**Problem**: `CORS_ORIGINS=http://localhost:5300,http://localhost:3000` blocks all production frontends.

**Fix**: Update `CORS_ORIGINS` in the production environment to include your deployed frontend URLs.

**File: `backend/app/config.py`** — already reads from env var:
```python
cors_origins: str = "http://localhost:5300,http://localhost:3000"
```

**Production env value:**
```
CORS_ORIGINS=https://finwize.vercel.app,https://www.finwize.app,https://finwize.up.railway.app
```

**Verification:**
```bash
curl -H "Origin: https://finwize.vercel.app" \
  -H "Access-Control-Request-Method: GET" \
  -X OPTIONS https://finwize.up.railway.app/api/v1/health \
  -I
# Expected: Access-Control-Allow-Origin: https://finwize.vercel.app
```

---

### 1.3 Frontend Environment Setup

**Target**: Deploy React app to Vercel.

#### Step 1.3.1: Create `.env.production` in `frontend/`

```
VITE_API_URL=https://finwize.up.railway.app/api/v1
```

**File: `frontend/src/api/client.ts`** — already reads from env:
```typescript
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8100/api/v1";
```

#### Step 1.3.2: Deploy to Vercel

```bash
npm install -g vercel
vercel login

cd frontend
vercel --prod

# Set the environment variable:
vercel env add VITE_API_URL production
# Enter: https://finwize.up.railway.app/api/v1

# Redeploy:
vercel --prod
```

**Alternative — GitHub + Vercel auto-deploy:**
- Push `frontend/` to GitHub
- Connect repo in Vercel dashboard
- Set `Root Directory` to `frontend`
- Add `VITE_API_URL` as environment variable
- Set `Build Command` to `npm run build`
- Set `Output Directory` to `dist`

#### Step 1.3.3: Verify

```bash
curl https://finwize.vercel.app
# Expected: HTML page loading without CORS errors
# Check browser console for any API connection issues
```

---

### 1.4 Flutter Production Build

**Problem**: API URL hardcoded to `10.0.2.2:8100` (Android emulator loopback). Blocking real device testing.

#### Step 1.4.1: Add build flavors to Flutter

**File: `mobile/lib/services/api_service.dart`** — update to support flavors:

```dart
class ApiConfig {
  static const String devBaseUrl = 'http://10.0.2.2:8100/api/v1';
  static const String stagingBaseUrl = 'https://finwize-staging.up.railway.app/api/v1';
  static const String prodBaseUrl = 'https://finwize.up.railway.app/api/v1';
}
```

#### Step 1.4.2: Configure build flavors (Android)

**File: `mobile/android/app/build.gradle`:**

```gradle
android {
    buildTypes {
        debug {
            buildConfigField "String", "API_BASE_URL", '"http://10.0.2.2:8100/api/v1"'
        }
        staging {
            buildConfigField "String", "API_BASE_URL", '"https://finwize-staging.up.railway.app/api/v1"'
        }
        release {
            buildConfigField "String", "API_BASE_URL", '"https://finwize.up.railway.app/api/v1"'
        }
    }
}
```

**File: `mobile/lib/services/api_service.dart`** — read from BuildConfig:

```dart
import 'package:flutter/foundation.dart';

class ApiConfig {
  static String get baseUrl {
    if (kDebugMode) return 'http://10.0.2.2:8100/api/v1';
    // In release, read from BuildConfig or a runtime env
    return 'https://finwize.up.railway.app/api/v1';
  }
}
```

#### Step 1.4.3: Build production APK

```bash
cd mobile

# Clean previous builds
flutter clean

# Production build
flutter build apk --release --split-per-abi

# Test on a real device
flutter install

# Verify by checking network requests hit the production API
```

#### Step 1.4.4: Distribute the APK

**Option A — GitHub Releases (free, immediate):**
```bash
# Tag the release
git tag v1.0.0
git push origin v1.0.0

# Upload APKs to GitHub Releases
gh release create v1.0.0 \
  mobile/build/app/outputs/flutter-apk/app-arm64-v8a-release.apk \
  mobile/build/app/outputs/flutter-apk/app-armeabi-v7a-release.apk \
  mobile/build/app/outputs/flutter-apk/app-x86_64-release.apk \
  --title "EcoFinwize v1.0.0" \
  --notes "First production release"
```

**Option B — Google Play Console** (for wider distribution): Requires $25 fee, store listing, privacy policy.

---

### 1.5 API Key Provisioning

**Problem**: All AI features (Kemi, Chidi, Business Plan, RAG) are non-functional without API keys.

#### Step 1.5.1: OpenRouter API Key

1. Go to https://openrouter.ai/keys
2. Sign up (free $1 credit)
3. Create a new key
4. Set in `.env.production`:
   ```
   OPENROUTER_API_KEY=sk-or-v1-your-key-here
   OPENROUTER_MODEL=openai/gpt-4o-mini
   ```

**Cost**: ~$0.15/1M input tokens, ~$0.60/1M output tokens. A typical 10-turn conversation costs ~$0.002.

#### Step 1.5.2: Groq API Key (fallback)

1. Go to https://console.groq.com/keys
2. Sign up (free tier: 30 req/min, 14,400 req/day)
3. Create a key
4. Set in `.env.production`:
   ```
   GROQ_API_KEY=gsk_your-key-here
   GROQ_MODEL=llama-3.3-70b-versatile
   ```

**Cost**: Free tier is generous. Llama-3.3-70b on Groq is free for personal/development use.

#### Step 1.5.3: Pinecone API Key (RAG)

1. Go to https://app.pinecone.io/
2. Sign up (free tier: 1 pod index, up to 100K vectors)
3. Create index: `finwize-knowledge`, dimension: 384, metric: cosine
4. Copy API key and environment
5. Set in `.env.production`:
   ```
   PINECONE_API_KEY=pcsk_your-key-here
   PINECONE_ENVIRONMENT=us-east-1-aws
   PINECONE_INDEX_NAME=finwize-knowledge
   ```

#### Step 1.5.4: Test the keys

```bash
# Test OpenRouter
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"openai/gpt-4o-mini","messages":[{"role":"user","content":"Hello"}]}'

# Test RAG (after deployment)
curl -X POST https://finwize.up.railway.app/api/v1/intelligence/rag/status
# Expected: {"status":"connected","index":"finwize-knowledge"}
```

---

## 2. High Priority

### 2.1 Email Service Integration

**Problem**: Password reset (US-004b) and email verification (US-001b) endpoints exist but have no SMTP backend. Users cannot recover accounts.

#### Step 2.1.1: Add SendGrid to backend

```bash
# In backend/ directory
pip install sendgrid
```

**File: `backend/app/modules/notifications/email.py`** (new file):

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.config import get_settings

settings = get_settings()

async def send_email(to_email: str, subject: str, html_content: str):
    message = Mail(
        from_email="noreply@finwize.app",
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )
    try:
        sg = SendGridAPIClient(settings.sendgrid_api_key)
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

async def send_password_reset(email: str, reset_token: str):
    reset_link = f"{settings.frontend_url}/reset-password?token={reset_token}"
    html = f"""
        <h2>Reset Your EcoFinwize Password</h2>
    <p>Click below to reset your password (expires in 1 hour):</p>
    <a href="{reset_link}" style="padding:12px 24px;background:#38BDF8;color:white;
        text-decoration:none;border-radius:6px;">Reset Password</a>
    <p>If you didn't request this, ignore this email.</p>
    """
    return await send_email(email, "Reset Your EcoFinwize Password", html)

async def send_verification_email(email: str, verify_token: str):
    verify_link = f"{settings.frontend_url}/verify-email?token={verify_token}"
    html = f"""
        <h2>Welcome to EcoFinwize!</h2>
    <p>Verify your email to get started:</p>
    <a href="{verify_link}" style="padding:12px 24px;background:#38BDF8;color:white;
        text-decoration:none;border-radius:6px;">Verify Email</a>
    """
    return await send_email(email, "Verify Your EcoFinwize Account", html)
```

#### Step 2.1.2: Update config

**File: `backend/app/config.py`** — add:
```python
sendgrid_api_key: str = ""
frontend_url: str = "http://localhost:5300"
```

#### Step 2.1.3: Wire into auth router

**File: `backend/app/modules/auth/service.py`** — after successful registration, add:
```python
from app.modules.notifications.email import send_verification_email

# In register function, after creating user:
if settings.app_env == "production":
    await send_verification_email(user.email, verify_token)
```

#### Step 2.1.4: Sign up for SendGrid

1. Go to https://sendgrid.com
2. Sign up (free tier: 100 emails/day)
3. Create API key with "Mail Send" permission
4. Set in `.env.production`:
   ```
   SENDGRID_API_KEY=SG.your-key-here
   FRONTEND_URL=https://finwize.vercel.app
   ```

---

### 2.2 Rate Limiting Middleware

**Problem**: `RateLimited` exception exists but no middleware enforces it.

#### Step 2.2.1: Add slowapi

```bash
pip install slowapi
```

#### Step 2.2.2: Update main.py

**File: `backend/app/main.py`**:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

#### Step 2.2.3: Apply limits per router

**Authentication endpoints (strict):**
```python
@router.post("/auth/login")
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest, db: AsyncSession = Depends(get_db)):
    ...
```

**AI endpoints (moderate):**
```python
@router.post("/ai/advisor/chat")
@limiter.limit("30/minute")
async def advisor_chat(...):
    ...
```

**General API (broad):**
```python
@router.get("/finance/budgets")
@limiter.limit("100/minute")
async def list_budgets(...):
    ...
```

**Alternative — nginx-level rate limiting** (if using nginx reverse proxy):
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;
location /api/ {
    limit_req zone=api burst=20 nodelay;
}
```

---

### 2.3 Load Testing

#### Step 2.3.1: Install k6

```bash
# Windows (PowerShell)
winget install k6

# Or download from https://k6.io/docs/get-started/installation/
```

#### Step 2.3.2: Create load test script

**File: `scripts/load_test.js`** (new):

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up to 50 users
    { duration: '5m', target: 100 },  // Sustained at 100 users
    { duration: '2m', target: 200 },  // Peak at 200 users
    { duration: '3m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests < 2s
    http_req_failed: ['rate<0.01'],     // < 1% failure rate
  },
};

const BASE_URL = 'https://finwize.up.railway.app/api/v1';

export default function () {
  // Health check
  const health = http.get(`${BASE_URL}/health`);
  check(health, { 'health ok': (r) => r.status === 200 });

  // Auth flow
  const loginRes = http.post(`${BASE_URL}/auth/login`, {
    email: 'demo@finwize.app',
    password: 'password123',
  });
  check(loginRes, { 'login ok': (r) => r.status === 200 });

  const token = loginRes.json('access_token');
  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };

  // Budget list
  const budgets = http.get(`${BASE_URL}/finance/budgets`, { headers });
  check(budgets, { 'budgets ok': (r) => r.status === 200 });

  // Transactions
  const txns = http.get(`${BASE_URL}/finance/transactions`, { headers });
  check(txns, { 'transactions ok': (r) => r.status === 200 });

  // Savings goals
  const goals = http.get(`${BASE_URL}/finance/savings-goals`, { headers });
  check(goals, { 'savings ok': (r) => r.status === 200 });

  // Daily tip
  const tip = http.get(`${BASE_URL}/intelligence/tips/daily`, { headers });
  check(tip, { 'tip ok': (r) => r.status === 200 });

  sleep(1);
}
```

#### Step 2.3.3: Run the test

```bash
k6 run scripts/load_test.js
```

#### Step 2.3.4: Key metrics to capture

| Metric | Target | Action if Failed |
|--------|--------|-----------------|
| p95 response time | < 2s | Add database indexing, enable Redis caching, increase instance size |
| Error rate | < 1% | Check DB connection pool size, add retry logic |
| P95 AI response time | < 10s | Consider Groq (faster inference), reduce context window |
| Memory usage | < 80% | Increase instance RAM, add connection pooling limits |
| CPU usage | < 70% | Add horizontal scaling, optimize query patterns |

---

## 3. Medium Priority

### 3.1 Error Monitoring (Sentry)

**Problem**: No error tracking. Crashes in production are invisible.

#### Step 3.1.1: Backend Sentry integration

```bash
pip install sentry-sdk
```

**File: `backend/app/main.py`** — add near top:
```python
import sentry_sdk
from app.config import get_settings

settings = get_settings()

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.app_env,
        traces_sample_rate=0.2,  # 20% of requests for performance tracing
    )
```

#### Step 3.1.2: Frontend Sentry integration

```bash
cd frontend
npm install @sentry/react @sentry/vite-plugin
```

**File: `frontend/src/main.tsx`**:
```typescript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.NODE_ENV,
  tracesSampleRate: 0.2,
});

// Wrap the app with Sentry error boundary
<Sentry.ErrorBoundary fallback={<ErrorPage />}>
  <App />
</Sentry.ErrorBoundary>
```

#### Step 3.1.3: Set up Sentry

1. Go to https://sentry.io
2. Create project -> Python (FastAPI) + React
3. Copy DSN to `.env.production`:
   ```
   SENTRY_DSN=https://key@o123.ingest.sentry.io/project
   VITE_SENTRY_DSN=https://key@o123.ingest.sentry.io/project
   ```

---

### 3.2 Offline Resilience

**Problem**: Target users have intermittent connectivity. Currently requires always-on internet.

#### Step 3.2.1: Frontend — Service Worker

```bash
cd frontend
npm install vite-plugin-pwa
```

**File: `vite.config.ts`** (update or create):
```typescript
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.png', 'icons.svg'],
      manifest: {
        name: 'EcoFinwize',
        short_name: 'EcoFinwize',
        theme_color: '#38BDF8',
        icons: [{ src: 'icon.png', sizes: '192x192', type: 'image/png' }],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^https?:\/\/.*\/api\/v1\/finance\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'finance-cache',
              expiration: { maxEntries: 50, maxAgeSeconds: 60 * 60 * 24 },
            },
          },
        ],
      },
    }),
  ],
});
```

#### Step 3.2.2: Flutter — local caching with Hive

```bash
cd mobile
flutter pub add hive hive_flutter
flutter pub add connectivity_plus
```

**File: `mobile/lib/services/local_cache_service.dart`** (new):

```dart
import 'package:hive_flutter/hive_flutter.dart';

class LocalCacheService {
  static final LocalCacheService _instance = LocalCacheService._();
  factory LocalCacheService() => _instance;
  LocalCacheService._();

  static Future<void> init() async {
    await Hive.initFlutter();
    await Hive.openBox('budgets');
    await Hive.openBox('transactions');
    await Hive.openBox('pending_sync');
  }

  Future<void> cacheData(String boxName, String key, dynamic data) async {
    final box = Hive.box(boxName);
    await box.put(key, data);
  }

  Future<dynamic> getCached(String boxName, String key) async {
    final box = Hive.box(boxName);
    return box.get(key);
  }

  Future<void> queueForSync(String endpoint, Map body) async {
    final box = Hive.box('pending_sync');
    await box.add({'endpoint': endpoint, 'body': body, 'timestamp': DateTime.now().toIso8601String()});
  }

  Future<List> getPendingSync() async {
    return Hive.box('pending_sync').values.toList();
  }
}
```

**Integration in `api_service.dart`**:
```dart
Future<dynamic> get(String path, {Map<String, String>? params, bool cacheable = false}) async {
  if (cacheable) {
    final cached = await LocalCacheService().getCached('budgets', path);
    if (cached != null) return cached;
  }
  try {
    final result = await _handle(await http.get(...));
    if (cacheable) await LocalCacheService().cacheData('budgets', path, result);
    return result;
  } catch (e) {
    if (cacheable) {
      final cached = await LocalCacheService().getCached('budgets', path);
      if (cached != null) return cached;
    }
    rethrow;
  }
}
```

---

### 3.3 Database Backups

#### PostgreSQL (if using Railway — automated)
- Railway: Automatic daily backups with 7-day retention (Pro plan)
- Render: Automatic daily backups with 7-day retention

#### Manual backup script

**File: `scripts/backup.sh`** (for use with cron or GitHub Actions):

```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

# PostgreSQL
pg_dump "$DATABASE_URL" > "$BACKUP_DIR/finwize_pg_$TIMESTAMP.sql"

# MongoDB
mongodump --uri="$MONGODB_URL" --out="$BACKUP_DIR/mongo_$TIMESTAMP"

# Upload to S3-compatible storage (Backblaze B2, AWS S3)
# rclone copy $BACKUP_DIR b2:finwize-backups/

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
```

#### GitHub Actions backup workflow

**File: `.github/workflows/backup.yml`**:

```yaml
name: Database Backup
on:
  schedule:
    - cron: '0 4 * * *'  # Daily at 4 AM

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Backup PostgreSQL
        run: |
          pg_dump "${{ secrets.DATABASE_URL }}" > backup.sql
      - name: Upload to S3
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      - run: aws s3 cp backup.sql s3://finwize-backups/$(date +%Y%m%d).sql
```

---

## 4. Nice to Have

### 4.1 Frontend Tests

**File: `frontend/src/__tests__/Dashboard.test.tsx`**:

```bash
cd frontend
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

**File: `frontend/vite.config.ts`** — add test config:
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test-setup.ts',
  },
});
```

**File: `frontend/src/__tests__/Dashboard.test.tsx`**:

```typescript
import { render, screen } from '@testing-library/react';
import Dashboard from '../pages/Dashboard';

test('renders dashboard title', () => {
  render(<Dashboard />);
  expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
});
```

### 4.2 Flutter Tests

```bash
cd mobile
flutter test --coverage  # Run existing test
```

**File: `mobile/test/api_service_test.dart`**:

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:finwize/services/api_service.dart';

void main() {
  group('ApiConfig', () {
    test('baseUrl returns emulator URL in debug', () {
      // This test validates the config logic
      expect(ApiConfig.baseUrl, contains('10.0.2.2'));
    });
  });
}
```

### 4.3 PDF Export

**Problem**: Business plans are JSON-only. Banks expect PDF.

```bash
pip install reportlab
```

**File: `backend/app/modules/business/pdf_service.py`** (new):

```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_business_plan_pdf(plan_data: dict) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.drawString(100, 800, f"Business Plan: {plan_data['business_name']}")
    c.drawString(100, 780, f"Industry: {plan_data['industry']}")
    y = 740
    for section in ['executive_summary', 'market_analysis', 'financial_projections']:
        c.drawString(100, y, section.replace('_', ' ').title())
        y -= 20
        c.drawString(120, y, plan_data.get(section, '')[:100])
        y -= 30
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
```

**API endpoint**:
```python
@router.get("/business/business-plans/{id}/pdf")
async def download_plan_pdf(id: int, ...):
    plan = await get_plan(id)
    pdf_bytes = generate_business_plan_pdf(plan.to_dict())
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=business_plan_{id}.pdf"},
    )
```

### 4.4 WCAG Accessibility Audit

**Automated audit**:
```bash
cd frontend
npm install -D axe-core @axe-core/react
```

**File: `frontend/src/main.tsx`** — add in dev only:
```typescript
if (import.meta.env.DEV) {
  import('@axe-core/react').then((axe) => {
    axe.default(React, ReactDOM, 1000);
  });
}
```

**Key WCAG checks to fix**:
| Issue | File | Fix |
|-------|------|-----|
| Color contrast (Sky Blue on White: 1.8:1) | tailwind.config.js | Use darker blue (#0284C7) for text, keep #38BDF8 for accents only |
| Missing aria-labels on buttons | Layout.tsx | Add `aria-label="Navigation"` to bottom nav |
| Form labels | Login.tsx, Register.tsx | Ensure all inputs have associated `<label>` elements |
| Focus indicators | global CSS | Add `*:focus { outline: 2px solid #38BDF8; }` |
| Image alt text | Landing.tsx | Add alt text to hero images |

### 4.5 Dark Mode

**File: `frontend/tailwind.config.js`**:

```javascript
module.exports = {
  darkMode: 'class',
  theme: { extend: { ... } },
};
```

**File: `frontend/src/context/ThemeContext.tsx`** (new):

```typescript
import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext({ dark: false, toggle: () => {} });

export function ThemeProvider({ children }) {
  const [dark, setDark] = useState(localStorage.getItem('theme') === 'dark');

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark);
    localStorage.setItem('theme', dark ? 'dark' : 'light');
  }, [dark]);

  return (
    <ThemeContext.Provider value={{ dark, toggle: () => setDark(!dark) }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => useContext(ThemeContext);
```

---

## 5. Post-Launch Roadmap

### v1.1 (Month 1-2 after launch)
- **Payment integration**: Paystack + Flutterwave for Pro/Business subscriptions
- **Feature gating**: Enforce usage quotas by plan tier
- **Ad activation**: Start serving curated ads to free tier, recruit 10+ advertisers
- **Email workflows**: Welcome emails, re-engagement nudges, payment receipts

### v1.2 (Month 3-4)
- **Advertiser self-serve portal**: Campaign creation, budget management, analytics
- **White-label proposition**: Package platform for banks/NGOs
- **CSV export**: Transaction and budget export
- **Performance optimization**: CDN caching, query optimization, image optimization

### v2.0 (Month 6+)
- **API marketplace**: Public API for fintech partner integrations
- **Multi-currency**: Support for KES, GHS, ZAR, XOF
- **Programmatic ads**: Audience targeting by user segment
- **iOS app**: Flutter build for App Store
- **P2P learning**: Community features, mentorship matching

---

## Quick Reference: Environment Variables

| Variable | Location | Production Value |
|----------|----------|-----------------|
| `SECRET_KEY` | backend/.env | `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `DATABASE_URL` | backend/.env | From Railway/PostgreSQL dashboard |
| `MONGODB_URL` | backend/.env | From MongoDB Atlas or Railway |
| `REDIS_URL` | backend/.env | From Railway/Redis dashboard |
| `CORS_ORIGINS` | backend/.env | `https://finwize.vercel.app` |
| `OPENROUTER_API_KEY` | backend/.env | From openrouter.ai/keys |
| `GROQ_API_KEY` | backend/.env | From console.groq.com/keys |
| `PINECONE_API_KEY` | backend/.env | From app.pinecone.io |
| `SENDGRID_API_KEY` | backend/.env | From sendgrid.com |
| `SENTRY_DSN` | backend/.env + frontend | From sentry.io |
| `VITE_API_URL` | frontend | `https://finwize.up.railway.app/api/v1` |
| Flutter API URL | mobile/lib/services/ | `https://finwize.up.railway.app/api/v1` |

---

## Verification Checklist

After completing each section, check off:

- [ ] **1.1 Backend deployed** — `GET /api/v1/health` returns 200
- [ ] **1.2 CORS configured** — Frontend can reach backend without CORS errors
- [ ] **1.3 Frontend deployed** — `https://finwize.vercel.app` loads without errors
- [ ] **1.4 Flutter APK** — Production APK installs on real Android device
- [ ] **1.5 API keys** — AI advisor responds, RAG status shows "connected"
- [ ] **2.1 Email** — Password reset email arrives in inbox
- [ ] **2.2 Rate limiting** — 10 rapid requests return 429
- [ ] **2.3 Load test** — k6 reports p95 < 2s, error rate < 1%
- [ ] **3.1 Sentry** — Error appears in Sentry dashboard within 5 minutes
- [ ] **3.2 Offline** — Service Worker caches pages; Flutter caches transactions
- [ ] **3.3 Backups** — Daily pg_dump runs successfully
- [ ] **Closed beta live** — 50 test users onboarded
- [ ] **Open beta live** — Invite-only public access activated
