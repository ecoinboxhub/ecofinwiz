# Production Readiness Implementation Prompts

> **Context**: EcoFinwize/Finwize project — 85% complete, blocking gaps prevent production launch.
> **Target**: Senior Full-Stack + Mobile + DevOps + QA + UX engineer.
> **Constraint**: Zero regressions. All changes must pass existing 65 integration + 29 smoke tests.

---

## 1. Configure CORS for Production Domains

### Role: DevOps Engineer + Backend Developer

### Prompt
```
TASK: Configure CORS in FastAPI for production frontend domains.

CURRENT STATE:
- backend/app/main.py:43-49 allows only ["http://localhost:5300", "http://localhost:3000"]
- No environment-based configuration
- docker-compose.yml exposes port 8100

REQUIREMENTS:
1. Read allowed origins from environment variable `CORS_ORIGINS` (comma-separated)
2. Support both development (localhost) and production (https://app.finwize.com, https://finwize.vercel.app, etc.)
3. Allow credentials (cookies/auth headers)
4. Allow all methods and headers for API routes
5. Validate origins format on startup (warn if invalid)
6. Update docker-compose.yml to pass CORS_ORIGINS via env_file
7. Update .env.example with documented example

FILES TO MODIFY:
- backend/app/main.py
- backend/app/config.py (add CORS_ORIGINS setting)
- backend/.env.example
- docker-compose.yml

ACCEPTANCE CRITERIA:
- `curl -H "Origin: https://app.finwize.com" -H "Access-Control-Request-Method: POST" -X OPTIONS http://localhost:8100/api/v1/auth/login` returns 200 with `Access-Control-Allow-Origin: https://app.finwize.com`
- Invalid origins in CORS_ORIGINS log warning but don't crash startup
- All existing tests pass (pytest backend/tests/ -v)
```

---

## 2. Implement Redis-Based Rate Limiting

### Role: Backend Developer + DevOps Engineer

### Prompt
```
TASK: Implement sliding-window rate limiting using Redis across all API endpoints.

CURRENT STATE:
- `RateLimited` exception exists in backend/app/core/exceptions.py but never raised
- Redis client available at `backend/app/core/redis.py` (async redis.Redis)
- No middleware or dependency for rate limiting

REQUIREMENTS:
1. Create `RateLimiter` class in `backend/app/core/rate_limiter.py`:
   - Sliding window algorithm (Redis sorted sets with timestamps)
   - Configurable: requests per window (default: 100 req / 60 sec)
   - Per-IP + per-user (when authenticated) keys
   - Returns `Retry-After` header on 429
2. Add `RateLimitConfig` to `backend/app/config.py`:
   - `RATE_LIMIT_ENABLED` (bool, default True)
   - `RATE_LIMIT_REQUESTS` (int, default 100)
   - `RATE_LIMIT_WINDOW_SECONDS` (int, default 60)
   - `RATE_LIMIT_EXEMPT_PATHS` (list: ["/health", "/docs", "/openapi.json", "/api/v1/auth/login", "/api/v1/auth/register"])
3. Create FastAPI middleware in `backend/app/middleware/rate_limit.py`:
   - Skip exempt paths
   - Extract client IP (respect X-Forwarded-For behind proxy)
   - Use user ID from JWT when authenticated
   - Inject `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers
4. Register middleware in `main.py` before CORS
5. Update `.env.example` with rate limit config

FILES TO CREATE:
- backend/app/core/rate_limiter.py
- backend/app/middleware/rate_limit.py

FILES TO MODIFY:
- backend/app/config.py
- backend/app/main.py
- backend/.env.example

ACCEPTANCE CRITERIA:
- 101st request in 60s returns 429 with `Retry-After` header
- Authenticated users tracked by user_id, anonymous by IP
- `/health` and auth endpoints exempt
- Headers present on all responses
- All existing tests pass
- Load test: 200 concurrent requests to `/api/v1/finance/budgets` — only first 100 succeed
```

---

## 3. Provision Production API Keys (OpenRouter, Groq, Pinecone, Paystack)

### Role: DevOps Engineer + Security Engineer

### Prompt
```
TASK: Securely provision and validate all production API keys via environment variables.

CURRENT STATE:
- backend/app/config.py has 30+ settings but keys are empty/placeholder
- .env.example documents variables but no validation
- AI features fallback to local sentence-transformers when Pinecone/OpenRouter/Groq keys missing
- Paystack keys exist in test mode only

REQUIREMENTS:
1. Add validation in `config.py` `@model_validator(mode="after")`:
   - Require `OPENROUTER_API_KEY` OR `GROQ_API_KEY` (at least one for AI)
   - Require `PINECONE_API_KEY` + `PINECONE_INDEX_NAME` for RAG (warn if missing, don't crash)
   - Require `PAYSTACK_SECRET_KEY` + `PAYSTACK_PUBLIC_KEY` for payments
   - Require `FLUTTERWAVE_SECRET_KEY` + `FLUTTERWAVE_PUBLIC_KEY` (optional, warn)
   - Validate key formats (prefix checks: `sk_` for Paystack, `sk_live_` for production)
2. Create `backend/app/scripts/validate_keys.py`:
   - Test each key against provider API (health check endpoint)
   - Output structured JSON: `{service: "openrouter", status: "valid|invalid|missing", latency_ms: 123}`
   - Exit code 0 if all required keys valid, 1 otherwise
3. Add GitHub Actions workflow `.github/workflows/validate-secrets.yml`:
   - Run on PR to main, manual dispatch
   - Use repository secrets (never log values)
   - Fail PR if required keys invalid
4. Document rotation procedure in `docs/SECRETS_ROTATION.md`

FILES TO MODIFY:
- backend/app/config.py
- backend/.env.example

FILES TO CREATE:
- backend/app/scripts/validate_keys.py
- .github/workflows/validate-secrets.yml
- docs/SECRETS_ROTATION.md

ACCEPTANCE CRITERIA:
- `python -m backend.app.scripts.validate_keys` returns JSON with all services "valid"
- Missing required key → clear error message at startup (not silent fallback)
- Invalid key format → validation error with example format
- GitHub Action passes on main branch
- No keys in logs, docker history, or repo
```

---

## 4. Set Flutter Production API URL

### Role: Mobile App Developer + DevOps Engineer

### Prompt
```
TASK: Configure Flutter app for production API URL with build flavors.

CURRENT STATE:
- mobile/lib/services/api_service.dart:12 hardcodes `baseUrl = "http://10.0.2.2:8100/api/v1"`
- No flavor configuration
- APK builds use emulator IP

REQUIREMENTS:
1. Create build flavors in `mobile/android/app/build.gradle.kts`:
   - `development` → `http://10.0.2.2:8100/api/v1`
   - `staging` → `https://staging-api.finwize.com/api/v1`
   - `production` → `https://api.finwize.com/api/v1`
2. Update `mobile/lib/services/api_service.dart`:
   - Read base URL from `--dart-define=API_BASE_URL` or flavor-specific constant
   - Add `ApiService.configure(String baseUrl)` for runtime override (deep links, testing)
   - Keep singleton pattern
3. Add `mobile/.env` support via `flutter_dotenv` for non-secret config
4. Update `mobile/pubspec.yaml` with `flutter_dotenv` dependency
5. Create `mobile/lib/config/app_config.dart` with `AppConfig` class:
   - `apiBaseUrl`, `appName`, `bundleId` per flavor
   - `isProduction`, `isStaging` getters
6. Update GitHub Actions `flutter-build.yml` to build all three flavors
7. Document flavor usage in `mobile/README.md`

FILES TO MODIFY:
- mobile/android/app/build.gradle.kts
- mobile/lib/services/api_service.dart
- mobile/pubspec.yaml
- .github/workflows/flutter-build.yml (if exists)

FILES TO CREATE:
- mobile/lib/config/app_config.dart
- mobile/.env.development, .env.staging, .env.production (template)
- mobile/README.md (flavor section)

ACCEPTANCE CRITERIA:
- `flutter build apk --flavor production --dart-define=API_BASE_URL=https://api.finwize.com/api/v1` produces APK calling production URL
- `flutter run --flavor development` works on emulator (10.0.2.2)
- No hardcoded URLs in Dart code
- All 19 screens functional in each flavor
- APK size increase < 100 KB
```

---

## 5. Add Frontend Error Boundaries + Flutter Error Handler

### Role: Frontend Developer + Mobile App Developer + UX Designer

### Prompt
```
TASK: Implement comprehensive error boundaries (React) and global error handler (Flutter) with user-friendly fallback UI.

CURRENT STATE:
- React: No error boundaries. Unhandled errors white-screen the app.
- Flutter: Only default `FlutterError.onError` (prints to console).
- No error reporting integration.

REQUIREMENTS:

### React (frontend/)
1. Create `frontend/src/components/ErrorBoundary.tsx`:
   - Class component (required for `componentDidCatch`)
   - State: `hasError: boolean`, `error: Error | null`, `errorInfo: ErrorInfo | null`
   - Fallback UI: Centered card with:
     - Icon (AlertTriangle from lucide-react)
     - Title: "Something went wrong"
     - Message: "We've been notified. Please try again."
     - Button: "Reload Page" → `window.location.reload()`
     - Button: "Go Home" → `navigate("/")`
     - Details expander (dev only): stack trace + component stack
   - `componentDidCatch`: Log to console + send to Sentry (if configured)
2. Wrap entire app in `ErrorBoundary` in `App.tsx` (inside AuthProvider)
3. Add per-route boundaries for heavy pages (Advisor, Mentor, Investment, Dashboard)
4. Create `frontend/src/hooks/useErrorHandler.ts`:
   - `handleError(error, context?)` → captures + reports
   - `withErrorBoundary(Component)` HOC for class components

### Flutter (mobile/)
1. Create `mobile/lib/core/errors/app_error_handler.dart`:
   - `AppErrorHandler.init()` called in `main.dart` before `runApp`
   - Override `FlutterError.onError`, `PlatformDispatcher.instance.onError`
   - Collect: error, stack trace, device info, user ID (if logged in), route
   - Send to Sentry (if DSN configured) + local log file
2. Create `mobile/lib/widgets/error_fallback.dart`:
   - `ErrorFallbackWidget({required VoidCallback onRetry, String? message})`
   - Material 3 design matching brand colors
   - Illustrated empty state (custom illustration or Icon)
   - Actions: "Retry", "Go Home", "Report Issue" (mailto:support@finwize.com)
3. Wrap `MaterialApp` with `ErrorWidget.builder` using `ErrorFallbackWidget`
4. Add `mobile/lib/core/errors/exceptions.dart` with custom exceptions:
   - `NetworkException`, `AuthException`, `ServerException`, `ValidationException`

FILES TO CREATE:
- frontend/src/components/ErrorBoundary.tsx
- frontend/src/hooks/useErrorHandler.ts
- mobile/lib/core/errors/app_error_handler.dart
- mobile/lib/core/errors/exceptions.dart
- mobile/lib/widgets/error_fallback.dart

FILES TO MODIFY:
- frontend/src/App.tsx
- frontend/src/main.tsx
- mobile/lib/main.dart

ACCEPTANCE CRITERIA:
- React: Throw in any component → fallback UI renders, no white screen, reload works
- Flutter: Throw in any widget → fallback UI renders, retry works, no red screen
- Errors logged to console + structured JSON for Sentry
- UX: Friendly, non-technical language, clear recovery actions
- Accessibility: Focus management, ARIA labels, screen reader announcements
```

---

## 6. Set Up Monitoring (Sentry), SSL, Backup Strategy

### Role: DevOps Engineer + SRE + Security Engineer

### Prompt
```
TASK: Implement production monitoring, SSL termination, and automated backup strategy.

CURRENT STATE:
- Basic logging to stdout (backend_server.log)
- No APM, no error tracking, no uptime monitoring
- No SSL/TLS (localhost HTTP only)
- No backup strategy documented

REQUIREMENTS:

### Sentry Integration
1. Backend: Add `sentry-sdk[fastapi,sqlalchemy,redis]` to `backend/requirements.txt`
   - Initialize in `backend/app/main.py` before app creation
   - Configure: `traces_sample_rate=0.1`, `profiles_sample_rate=0.1`
   - Add `SentryAsgiMiddleware` for request context
   - Tag events with `user_id`, `endpoint`, `environment`
   - Filter: ignore 404, 401, 429 (expected errors)
2. Frontend: Add `@sentry/react` + `@sentry/tracing` to `frontend/package.json`
   - Initialize in `frontend/src/main.tsx` with `browserTracingIntegration()`
   - Wrap `ErrorBoundary` fallback with `Sentry.captureException`
   - Track route changes via `Sentry.addNavigationInstrumentation`
3. Flutter: Add `sentry_flutter` to `mobile/pubspec.yaml`
   - Initialize in `mobile/lib/main.dart` with `SentryFlutter.init()`
   - Auto-capture Dart errors + native crashes
   - Add breadcrumbs for navigation, network requests
4. Create `monitoring/sentry.rules.yml` for alert rules:
   - Error rate > 1% / 5min → critical
   - 5xx rate > 5% / 5min → critical
   - P95 latency > 2s → warning

### SSL/TLS Termination
1. Document production SSL strategy in `docs/SSL_SETUP.md`:
   - Option A: Cloudflare (recommended) — full SSL, WAF, CDN, free tier
   - Option B: Let's Encrypt + nginx reverse proxy
   - Option C: Railway/Vercel/Render managed SSL
2. Update `docker-compose.prod.yml` with nginx service:
   - Terminate TLS, proxy to backend:8100, frontend:80
   - Security headers: HSTS, CSP, X-Frame-Options, Referrer-Policy
   - Rate limit at nginx level (burst protection)
3. Generate self-signed cert for local HTTPS testing (`mkcert`)

### Backup Strategy
1. Create `scripts/backup_postgres.sh`:
   - `pg_dump` with `--format=custom --compress=9 --no-owner --no-privileges`
   - Encrypt with `age` (age-encryption.org) using `BACKUP_ENCRYPTION_KEY`
   - Upload to S3-compatible storage (R2, MinIO, AWS S3) with lifecycle policy
   - Retention: daily × 7, weekly × 4, monthly × 12
   - Verify restore monthly (automated test restore to staging)
2. Create `scripts/restore_postgres.sh` for disaster recovery
3. Document RTO/RPO in `docs/DISASTER_RECOVERY.md`:
   - RTO: 4 hours (manual restore from backup)
   - RPO: 24 hours (daily backup)
   - Target: RTO < 1 hour, RPO < 1 hour (future: PITR with WAL-G)
4. Add GitHub Actions workflow `.github/workflows/backup.yml`:
   - Schedule: daily 02:00 UTC
   - Manual dispatch
   - Notify on failure (Slack/email)

FILES TO CREATE:
- monitoring/sentry.rules.yml
- docs/SSL_SETUP.md
- docs/DISASTER_RECOVERY.md
- scripts/backup_postgres.sh
- scripts/restore_postgres.sh
- docker-compose.prod.yml
- .github/workflows/backup.yml

FILES TO MODIFY:
- backend/requirements.txt
- backend/app/main.py
- frontend/package.json
- frontend/src/main.tsx
- mobile/pubspec.yaml
- mobile/lib/main.dart

ACCEPTANCE CRITERIA:
- Sentry dashboard shows backend + frontend + mobile errors
- Test error captured in Sentry with full context (user, route, stack)
- Local HTTPS works with `mkcert` (no browser warnings)
- Backup script runs, produces encrypted dump, uploads to S3
- Restore script works on clean PostgreSQL instance
- All workflows pass in GitHub Actions
- No secrets in repo (use GitHub Environments + Secrets)
```

---

## Cross-Cutting Quality Gates

### All Tasks Must Satisfy:
```bash
# Backend
cd backend && pytest -v --tb=short          # 65 integration + 29 smoke = 94 pass
cd backend && ruff check . && mypy .         # Lint + typecheck clean

# Frontend
cd frontend && npm run build                 # 0 TS errors, bundle < 1 MB
cd frontend && npm run lint                  # ESLint clean

# Flutter
cd mobile && flutter analyze                 # 0 issues
cd mobile && flutter test                    # All widget tests pass
cd mobile && flutter build apk --flavor production  # Success

# Integration
docker-compose -f docker-compose.prod.yml up -d  # All services healthy
curl -f https://staging-api.finwize.com/health  # 200 OK
```

### Definition of Done per Task:
- [ ] Implementation complete per requirements
- [ ] All existing tests pass
- [ ] New tests added for new behavior
- [ ] Documentation updated
- [ ] Code reviewed (self-review checklist)
- [ ] Deployed to staging, smoke tested
- [ ] No console errors, no warnings in logs