# EcoFinwize — Implementation Roadmap

> **Companion to**: AGENTS.md (Engineering Constitution)
> **Purpose**: Maps implementation milestones to the 12-month fellowship timeline, aligned with the AGENTS constitution MVP filter and social impact goals.

---

## Timeline Overview

```
Month   1    2    3    4    5    6    7    8    9    10   11   12
Phase   │ P1 │ P2 │ P3 │ P4 │ P5 │ P6 │ P7 │ P8 │ P9 │ P10│ P11│ P12│
        ├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤
Core    │████████████████████│    │    │    │    │    │    │    │    │
AI/RAG  │████████████████████████████████████│    │    │    │    │    │
Offline │    │    │    │████████████████████████████████│    │    │    │
Voice   │    │    │    │    │████████████████████████████████│    │    │
Pilot   │    │    │    │    │    │    │    │    │████████████████████│
```

---

## Phase 1: Foundation (Month 1)

**Theme**: Core infrastructure and authentication

| Milestone | Deliverable | AGENTS Alignment |
|-----------|-------------|-----------------|
| 1.1 Project scaffolding | FastAPI monolith structure, Docker compose, CI/CD | Principle 11 (Architecture) |
| 1.2 Database setup | PostgreSQL (28 models), MongoDB (6 collections), Alembic | Data Layer |
| 1.3 Authentication | JWT register/login/refresh/logout, Google OAuth | Principle 13 (API Design) |
| 1.4 User model | Profile, preferences, device tokens | Supports Kemi/Chidi personalization |
| 1.5 Redis setup | Caching, session store, rate limiter foundation | Principle 10 (Low-Bandwidth) |

**Review gate**: Can a user register, login, and persist their profile? ✅

---

## Phase 2: Core Finance (Month 2)

**Theme**: Backend capabilities for Kemi — personal finance

| Milestone | Deliverable | AGENTS Alignment |
|-----------|-------------|-----------------|
| 2.1 Budget module | Create, list, update, delete budgets with spending tracking | Strengthens Kemi |
| 2.2 Transaction tracking | Income/expense CRUD, filtering, pagination, summaries | Strengthens Kemi |
| 2.3 Adaptive budget algorithm | Percentage-based for irregular income, month rollover | Principle 4 (Africa First) |
| 2.4 Savings goals | Goal CRUD, contributions, progress tracking, auto-complete | Strengthens Kemi |
| 2.5 Categories | 15 defaults + custom user categories | Strengthens Kemi |

**Review gate**: Can Kemi answer "How much did I spend on food?" with real data? ✅

---

## Phase 3: AI Advisor — Kemi (Month 3)

**Theme**: Conversational AI layer — Kemi as primary interface

| Milestone | Deliverable | AGENTS Alignment |
|-----------|-------------|-----------------|
| 3.1 LLM integration | OpenRouter + Groq providers, SSE streaming | Principle 1 (Conversation First) |
| 3.2 Conversation management | Create, list, archive, delete conversations | Core product |
| 3.3 Context assembly | Inject budget, goals, history, persona into prompts | Principle 1 |
| 3.4 Safety guardrails | PII redaction, harmful content detection, output filtering | Principle 5 (AI Safety) |
| 3.5 System prompts | Kemi persona — empathetic, plain-language financial advisor | Section 2 (Product Definition) |
| 3.6 Response rating | 1-5 star feedback, report inappropriate | Principle 5 |
| 3.7 RAG foundation | Pinecone setup, document chunking, embedding, retrieval, citation | Section 6 (RAG Mandatory) |

**Review gate**: Can a user have a full conversation with Kemi about their finances? ✅

---

## Phase 4: Business Mentor — Chidi (Month 4)

**Theme**: Conversational AI layer — Chidi as business mentor

| Milestone | Deliverable | AGENTS Alignment |
|-----------|-------------|-----------------|
| 4.1 Business plan generator | AI-powered structured plan generation | Strengthens Chidi |
| 4.2 Task management | CRUD with status/priority/due-date | Strengthens Chidi |
| 4.3 Invoice system | Auto-numbering, line items, tax, status flow | Strengthens Chidi |
| 4.4 Chidi system prompt | Business mentor persona — practical, actionable advice | Section 2 (Product Definition) |
| 4.5 Business context assembly | Inject business profile, tasks, invoices into Chidi prompts | Principle 1 |

**Review gate**: Can Chidi help a user create an invoice and generate a business plan? ✅

---

## Phase 5: Learning & Content (Month 5)

**Theme**: Educational content that both Kemi and Chidi reference

| Milestone | Deliverable | AGENTS Alignment |
|-----------|-------------|-----------------|
| 5.1 Course/lesson system | MongoDB courses with embedded lessons, 4 tracks | Section 9 (Social Impact) |
| 5.2 Quiz engine | Per-lesson quizzes, auto-grading, passing threshold | SDG 4 (Quality Education) |
| 5.3 Progress tracking | Lesson completion, course progress %, quiz scores | Section 9 |
| 5.4 Badge system | BadgeRule + UserBadge, achievement tracking | Section 9 |
| 5.5 Articles hub | Investment education articles with categories, featured | SDG 4 |
| 5.6 Blog with comments | Blog posts + comments with moderation | Community learning |
| 5.7 Forum | Topics + replies with pin/lock/solution | Community learning |

**Review gate**: Can Kemi recommend a course based on a user's financial goals? ✅

---

## Phase 6: Intelligence & RAG (Month 6)

**Theme**: Knowledge retrieval, recommendations, and personalization

| Milestone | Deliverable | AGENTS Alignment |
|-----------|-------------|-----------------|
| 6.1 Document upload | File upload to S3/local, metadata in PostgreSQL, auto-index to RAG | Section 6 (RAG) |
| 6.2 Hybrid recommendation engine | Content-based: persona + interests + bookmarks + completed | Principle 4 |
| 6.3 Personalized daily tips | 20+ deterministic tips, hash-based daily rotation | Strengthens Kemi |
| 6.4 News aggregation | RSS feeds (6 African sources) + NewsAPI, MongoDB storage | Section 6 |
| 6.5 Budget alert system | Threshold-based alerts via in-app notification | Strengthens Kemi |

**Review gate**: Can Kemi cite a specific document while answering a financial question? ✅

---

## Phase 7: Frontend & Mobile (Month 7)

**Theme**: Client applications that surface Kemi and Chidi

| Milestone | Deliverable | AGENTS Alignment |
|-----------|-------------|-----------------|
| 7.1 React web app | 21 pages, responsive, SSE streaming for AI chat | Principle 1 |
| 7.2 Flutter mobile app | 18 screens, Android APK, Provider state management | Principle 2 (Voice First) |
| 7.3 Shared API client | Axios (web) + http package (mobile) with JWT refresh | Principle 13 |
| 7.4 Auth UI | Login/Register with JWT + Google OAuth | Principle 1 |
| 7.5 Dashboard | Budget summary, recent transactions, AI tip, quick actions | Strengthens Kemi |
| 7.6 AI chat UI | SSE streaming, typing indicator, markdown rendering | Principle 1 |
| 7.7 Offline foundation | Basic local caching, token persistence, connectivity check | Principle 3 (Offline First) |

**Review gate**: Can a user talk to Kemi and Chidi from both web and mobile? ✅

---

## Phase 8: Monetization & Admin (Month 8)

**Theme**: Subscription plans, ad serving, and platform management

| Milestone | Deliverable | AGENTS Alignment |
|-----------|-------------|-----------------|
| 8.1 Subscription plans | Free/Pro/Business definitions with feature limits | Supports sustainability |
| 8.2 Usage quotas | Per-plan enforcement (AI chats, invoices, savings goals) | Scope management |
| 8.3 Upgrade endpoint | Paystack/Flutterwave payment integration | Supports sustainability |
| 8.4 Payment webhooks | Paystack + Flutterwave signature verification | Supports sustainability |
| 8.5 Ad serving engine | Contextual ad serving by page, impression tracking | Free tier sustainability |
| 8.6 Admin dashboard | Platform stats, user management, analytics, broadcast | Operations |
| 8.7 Email service | SendGrid + Mailgun for verification, password reset, welcome | Principle 1 |

**Review gate**: Can a user upgrade to Pro and get unlimited AI chats? ✅

---

## Phase 9: External Service Integration (Month 9)

**Theme**: Complete external API integrations with degradation chains

| Milestone | Deliverable | AGENTS Alignment |
|-----------|-------------|-----------------|
| 9.1 Analytics (PostHog) | Event tracking: signup, login, AI chat, budget, savings, subscription | Section 9 (Measurable Impact) |
| 9.2 SMS (AfricasTalking/Twilio) | Budget alerts, transaction confirmations | Principle 4 (Africa First) |
| 9.3 Cloud storage (AWS S3) | Document uploads with local disk fallback | Principle 10 |
| 9.4 Exchange rates (ExchangeRate-API) | Live forex with CBN fallback + Redis cache | Principle 4 |
| 9.5 Embedding fallback (Jina AI) | Alternative to OpenAI embeddings | Principle 5 |

**Review gate**: Do all external services have graceful fallback when keys are missing? ✅

---

## Phase 10: Production Deployment (Month 10)

**Theme**: Launch readiness

| Milestone | Deliverable | AGENTS Alignment |
|-----------|-------------|-----------------|
| 10.1 Backend deployment | Railway production with PostgreSQL, MongoDB, Redis | Section 11 (Architecture) |
| 10.2 Frontend deployment | Vercel production, custom domain, SSL | Principle 1 |
| 10.3 Flutter production build | Split APKs, build flavors, release signing | Principle 4 |
| 10.4 CORS configuration | Allow production frontend domains | Section 15 (Security) |
| 10.5 API key provisioning | OpenRouter, Groq, Pinecone, SendGrid, Paystack | Section 15 |
| 10.6 Rate limiting | Slowapi middleware, per-endpoint limits | Section 15 |
| 10.7 Monitoring | Sentry error tracking, health checks, structured logging | Section 18 (Review) |
| 10.8 Load testing | k6: 200 concurrent users, p95 < 2s, error rate < 1% | Section 18 |

**Review gate**: Is the platform accessible at finwize.app with all features working? ✅

---

## Phase 11: Offline & Voice (Month 11)

**Theme**: Offline resilience and voice accessibility — core inclusion features

| Milestone | Deliverable | AGENTS Alignment |
|-----------|-------------|-----------------|
| 11.1 Offline-first (web) | Service Worker, Workbox caching, NetworkFirst strategy | Principle 3 (Offline First) |
| 11.2 Offline-first (mobile) | Hive local storage, queued operations, background sync | Principle 3 |
| 11.3 Voice input (mobile) | Speech-to-text for chat input | Principle 2 (Voice First) |
| 11.4 Text-to-speech (mobile) | Read AI responses aloud, voice navigation | Principle 2 |
| 11.5 Low-bandwidth mode | Compressed payloads, lazy loading, image optimization | Principle 10 |
| 11.6 Delta sync | Only transfer changed data on reconnect | Principle 10 |

**Review gate**: Can a user budget and chat with Kemi while completely offline? ✅

---

## Phase 12: Pilot & Impact Evaluation (Month 12)

**Theme**: Real-world testing and social impact measurement

| Milestone | Deliverable | AGENTS Alignment |
|-----------|-------------|-----------------|
| 12.1 Closed beta (50 users) | Invite-only, real device testing, feedback collection | Section 18 |
| 12.2 Open beta | Public access, referral system | Section 9 (Social Impact) |
| 12.3 Impact evaluation | Measure: budgets created, savings goals, courses completed, plans generated | Section 9 |
| 12.4 Fellowship presentation | Demo, metrics, lessons learned, future roadmap | Section 16 (SDGs) |
| 12.5 Production hardening | Bug fixes, performance optimization, security audit | Section 20 (Definition of Done) |
| 12.6 Documentation finalization | All companion docs finalized, onboarding materials | Section 20 |

**Review gate**: Are measurable social impact outcomes documented and presented? ✅

---

## Dependency Map

```
P1 (Foundation)
  └── P2 (Finance) ──┐
                      ├── P3 (Kemi) ──┐
P5 (Learning) ────────┘              │
                                      ├── P7 (Frontends)
P4 (Chidi) ───────────────────────────┘
                                      │
P6 (Intelligence/RAG) ────────────────┤
                                      │
P8 (Monetization) ────────────────────┤
                                      │
P9 (External Services) ───────────────┘
                                      │
                          P10 (Deployment) ──┐
                                              ├── P12 (Pilot)
                          P11 (Offline/Voice) ┘
```

## MVP Decision Filter Reference

Per AGENTS.md section 8, every milestone above should pass:

- [ ] Does this improve Kemi?
- [ ] Does this improve Chidi?
- [ ] Does this improve financial literacy?
- [ ] Does this improve SME outcomes?
- [ ] Does this reduce user effort?
- [ ] Can reviewers immediately understand why this exists?

If most answers are "No", the milestone should be re-prioritized.
