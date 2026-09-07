# EcoFinwize (FinWize)

**Africa's most accessible conversational AI financial assistant.**

EcoFinwize is an AI-first financial inclusion platform that helps individuals and small
businesses budget, save, plan, and invest through natural voice and chat conversations.
The product centers on three AI personas — **Kemi** (personal finance), **Chidi** (business
mentor), and **Musa** (investment advisor) — with everything else implemented as a backend
capability that powers them.

---

## Live Applications

| App | URL |
|-----|-----|
| Web frontend | https://ecofinwiz.vercel.app |
| API / backend | https://ecofinwiz-api.onrender.com |
| API docs (Swagger) | upcoming at `/docs` on the backend host |

---

## Highlights

- **Conversation-first** — the assistant is the application; UI screens are secondary.
- **Voice-first** — browser-native Speech-to-Text / Text-to-Speech across all AI features in 13 African languages.
- **i18n** — 384 UI strings translated across 13 languages.
- **Agentic AI** — multi-step tool calling: creates budgets, records transactions, generates invoices, business plans, and more (10 tools), with automatic fallback between Groq (Llama-3.3-70b) and OpenRouter (GPT-4o-mini).
- **RAG knowledge base** — Pinecone vector search feeds a verified knowledge base into every response with mandatory citations and guardrails.
- **SSE streaming** — token-by-token streaming via Server-Sent Events.
- **Monetization** — freemium tiers, usage quotas, and Paystack / Flutterwave payments.
- **Cross-platform** — React web app plus Flutter Android APK from a single backend.

---

## Architecture

```
┌──────────────── Clients (conversation-first) ────────────────┐
│   React Web (Vercel)              Flutter Mobile (APK)        │
│   Nav: Kemi → Chidi → Home → Learn → Musa → Finance          │
└──────────────────────────┬───────────────────────────────────┘
                           │  REST API v1 (JWT Bearer)
┌──────────────────────────▼───────────────────────────────────┐
│                 FastAPI backend (Render, Docker)              │
│    Conversational AI layer: Kemi · Chidi · Musa               │
│      guardrails → RAG context → action dispatch → SSE         │
│    Capability modules: auth, users, finance, content,         │
│      business, intelligence, markets, calculators,            │
│      subscriptions, ads, admin                                │
└──────────┬────────────────────────────────┬───────────────────┘
           │                                 │
   ┌───────▼────────┐               ┌────────▼─────────┐
   │  PostgreSQL 18  │               │  Redis 7         │
   │  (primary store)│               │  cache/sessions  │
   └────────────────┘               └──────────────────┘
   External services: Pinecone (RAG) · Groq · OpenRouter · OpenAI ·
     Paystack · Flutterwave · SendGrid/Mailgun · Twilio/AfricasTalking ·
     News API · Sentry
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/04_SWR.md](docs/04_SWR.md) for the full system,
API, and data specification. The engineering constitution is in [docs/AGENTS.md](docs/AGENTS.md).

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy (async), Alembic, Celery |
| Web frontend | React 19, Vite 8, TypeScript, Tailwind CSS, Axios |
| Mobile | Flutter 3.22 (Android APK, ~7 MB) |
| Database | PostgreSQL 18 (all app data) |
| Cache / sessions | Redis 7 |
| Vector search | Pinecone (`ecofinwize` index) |
| AI providers | Groq (primary) → OpenRouter (fallback), OpenAI-compatible |
| Auth | JWT (HS256) + Google OAuth |
| Payments | Paystack + Flutterwave (test mode) |
| Deployment | Render (backend), Vercel (frontend), GitHub Actions CI |

---

## Repository Layout

```
backend/    FastAPI modular-monolith API (12 modules, 141 routes, 33 models)
frontend/   React web app (31 pages, i18n, SSE chat, voice)
mobile/     Flutter app (29 screens)
docs/       Authoritative docs: AGENTS.md, ARCHITECTURE.md, PRD, SWR, personas,
            deployment guide, gap analysis, status, QA reports
scripts/    Utilities (backups, doc generation, seeders)
monitoring/ Sentry alert rules
screen/     UI design spec + design reference screenshots
QA_artifacts/  QA screenshots and demo video
```

Root config: `docker-compose.yml`, `Dockerfile` (backend), `render.yaml`, `vercel.json`, `nginx.prod.conf`.

---

## Local Development

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv && .venv/Scripts/activate   # Windows
pip install -r requirements.txt
cp .env.example .env                             # fill in real keys
alembic upgrade head
uvicorn app.main:app --reload --port 8100
# API: http://localhost:8100/api/v1  ·  OpenAPI: http://localhost:8100/docs
```

### Web frontend (Vite)

```bash
cd frontend
npm install
npm run dev                                     # http://localhost:5300
```

### Everything with Docker

```bash
docker compose up --build
# api :8100 · postgres :5432 · redis :6379
```

### Mobile (Flutter)

```bash
cd mobile
flutter pub get
flutter run
```

---

## Documentation Index

| Document | Purpose |
|----------|---------|
| [docs/AGENTS.md](docs/AGENTS.md) | Engineering constitution & decision filter |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture, data flow, security |
| [docs/03_PRD.md](docs/03_PRD.md) | Product requirements (16 epics, 55 stories) |
| [docs/04_SWR.md](docs/04_SWR.md) | Software requirements, 141 endpoints, DB schema |
| [docs/01_PERSONAS.md](docs/01_PERSONAS.md) | 6 user personas |
| [docs/05_PRODUCTION_DEPLOYMENT_GUIDE.md](docs/05_PRODUCTION_DEPLOYMENT_GUIDE.md) | Deployment guide |
| [docs/status.md](docs/status.md) | Implementation status (all phases) |
| [docs/QA_TEST_REPORT.md](docs/QA_TEST_REPORT.md) | QA & test results |
| [docs/GAP_ANALYSIS_REPORT.md](docs/GAP_ANALYSIS_REPORT.md) | Gap analysis & action plan |

---

## CI / CD

- **GitHub Actions**: lint (ruff) → tests (pytest) → Docker image build; plus a secrets-validation
  workflow that fails if real credentials ever get committed. See [.github/workflows](.github/workflows).
- **Render**: auto-deploys the backend Docker service on push to `main`.
- **Vercel**: builds and deploys the frontend from `frontend/` on push to `main`.

---

## License / Status

Built for the NextGen Leaders Fellowship (AI Fintech). Reach MVP v1.1 — in pilot and
production-hardening phase. Report status and progress in [docs/status.md](docs/status.md).