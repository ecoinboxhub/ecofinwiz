# EcoFinwize — System Architecture

> **Companion to**: AGENTS.md (Engineering Constitution)
> **Purpose**: Defines system architecture, service boundaries, API interactions, and data flow centered on Kemi and Chidi as the primary user interfaces.

---

## 1. Architectural Philosophy

The architecture follows the **Conversation First** principle. All backend modules exist as capabilities served through the conversational agents, never as standalone products.

```
┌─────────────────────────────────────────────────────────────┐
│                      Clients                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │  Flutter  │  │  React   │  │   SMS    │  │  WhatsApp  │  │
│  │  Mobile   │  │   Web    │  │  Gateway  │  │   Bot      │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └─────┬──────┘  │
│       │             │             │              │          │
└───────┼─────────────┼─────────────┼──────────────┼──────────┘
        │             │             │              │
        ▼             ▼             ▼              ▼
┌──────────────────────────────────────────────────────────────┐
│                    API Gateway / Load Balancer                 │
│              (JWT Auth, Rate Limiting, Request Routing)        │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                   Conversational AI Layer                      │
│                                                               │
│  ┌─────────────────────┐  ┌───────────────────────────────┐   │
│  │   Kemi (Advisor)    │  │   Chidi (Business Mentor)     │   │
│  │  ─────────────────  │  │  ───────────────────────────  │   │
│  │  • Budget coaching  │  │  • Business mentoring         │   │
│  │  • Expense tracking │  │  • Business plan generation   │   │
│  │  • Savings guidance │  │  • Invoice assistance         │   │
│  │  • Financial ed.    │  │  • Financial projections      │   │
│  │  • Financial Q&A    │  │  • Entrepreneurship learning  │   │
│  └──────────┬──────────┘  └──────────────┬────────────────┘   │
│             │                             │                    │
└─────────────┼─────────────────────────────┼────────────────────┘
              │                             │
              ▼                             ▼
┌──────────────────────────────────────────────────────────────┐
│                      Orchestration Layer                       │
│                                                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │  Prompt  │ │ Context  │ │Guardrails│ │   RAG Pipeline   │ │
│  │ Assembly │ │Assembly  │ │(Safety)  │ │ (Embed → Search  │ │
│  └──────────┘ └──────────┘ └──────────┘ │  → Retrieve →    │ │
│                                         │   Cite)          │ │
│                                         └──────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    Capability Layer (Backend Modules)          │
│                                                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Finance  │ │ Business │ │ Learning │ │ Intelligence/RAG  │ │
│  │ Module   │ │ Module   │ │ Module   │ │ Module            │ │
│  ├──────────┤ ├──────────┤ ├──────────┤ ├──────────────────┤ │
│  │ Budgets  │ │ Bus.Plans│ │ Courses  │ │ Document Upload  │ │
│  │ Txns     │ │ Tasks    │ │ Articles │ │ Vector Search    │ │
│  │ Savings  │ │ Invoices │ │ Quizzes  │ │ Recommendations  │ │
│  │ Categories│ │          │ │ Badges   │ │ Daily Tips      │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘ │
│                                                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │  Auth    │ │  Users   │ │  Admin   │ │ External Services │ │
│  │ Module   │ │ Module   │ │ Module   │ │ Module            │ │
│  ├──────────┤ ├──────────┤ ├──────────┤ ├──────────────────┤ │
│  │ JWT      │ │ Profile  │ │ Stats    │ │ Email (SendGrid)  │ │
│  │ Google   │ │ Prefs    │ │ Users    │ │ SMS (AfricasTalk) │ │
│  │ OAuth    │ │ Progress │ │ Analytics│ │ Payments(Paystack)│ │
│  └──────────┘ └──────────┘ └──────────┘ │ News (RSS+API)   │ │
│                                          │ Forex Rates       │ │
│                                          └──────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                       Data Layer                               │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐│
│  │  PostgreSQL   │  │   MongoDB    │  │      Pinecone        ││
│  │  (Relational) │  │  (Documents) │  │   (Vector Store)     ││
│  ├──────────────┤  ├──────────────┤  ├──────────────────────┤│
│  │ Users        │  │ Courses      │  │ Knowledge Embeddings ││
│  │ Budgets      │  │ Articles     │  │ Document Vectors     ││
│  │ Transactions │  │ Blog Posts   │  │                      ││
│  │ Goals        │  │ News Items   │  │                      ││
│  │ Invoices     │  │              │  │                      ││
│  └──────────────┘  └──────────────┘  └──────────────────────┘│
│                                                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                     Redis (Cache)                         │ │
│  │  ──────────────────────────────────────────────────────  │ │
│  │  Session Store | Rate Limits | Forex Cache | API Cache   │ │
│  └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Service Boundaries

### 2.1 Conversational AI Layer

| Service | Responsibility | Owns |
|---------|---------------|------|
| **Kemi Service** | Personal finance conversations | Chat history, conversation state, response streaming |
| **Chidi Service** | Business mentoring conversations | Chat history, business context, response streaming |
| **LLM Provider** | Abstraction over OpenRouter/Groq | Model selection, retry logic, fallback chain |
| **Context Assembler** | Builds user context for prompts | Budget summary, goals, history, persona |
| **Guardrails** | Input/output safety checks | PII filter, harmful content detection, output sanitization |
| **Prompt Assembly** | Constructs system + user prompts | Template selection, context injection, instruction formatting |

### 2.2 Capability Layer

| Module | Capabilities | Consumed By |
|--------|-------------|-------------|
| **Finance** | Budgets, transactions, savings, categories, spending summaries | Kemi |
| **Business** | Business plans, tasks, invoices | Chidi |
| **Learning** | Courses, articles, quizzes, badges, progress | Kemi, Chidi |
| **Intelligence/RAG** | Document upload, vector search, recommendations, daily tips | Kemi, Chidi |
| **Auth** | Registration, login, JWT, OAuth, password reset | All clients |
| **Users** | Profile, preferences, progress, notifications | Kemi, Chidi |
| **Admin** | Platform stats, user management, analytics | Internal |
| **External Services** | Email, SMS, payments, news, forex | Kemi, Chidi, system |

### 2.3 Data Layer

| Store | Data | Access Pattern |
|-------|------|---------------|
| PostgreSQL | Structured: users, budgets, transactions, goals, invoices, tasks, forum | ORM (SQLAlchemy async) |
| MongoDB | Unstructured: courses, articles, blog, news | Document (Motor async) |
| Pinecone | Vector embeddings for RAG | Similarity search |
| Redis | Sessions, cache, rate limits, forex rates | Key-value |

---

## 3. API Interactions

### 3.1 Conversation Flow (Kemi/Chidi)

```
Client                  API Gateway            Orchestrator          LLM Provider          Capability Modules
  │                         │                      │                     │                      │
  │── POST /ai/advisor──────►                      │                     │                      │
  │   {message, user_id}    │                      │                     │                      │
  │                         │── authenticate ─────►│                     │                      │
  │                         │                      │── check_quota ─────►│                      │
  │                         │                      │◄── quota_ok ───────│                      │
  │                         │                      │                     │                      │
  │                         │                      │── guard_input ─────►│                      │
  │                         │                      │◄── sanitized ──────│                      │
  │                         │                      │                     │                      │
  │                         │                      │── assemble_context ─┤                      │
  │                         │                      │   ├── get_budgets───┼──────────────────────►│
  │                         │                      │   ├── get_goals ────┼──────────────────────►│
  │                         │                      │   ├── get_history ──┤                      │
  │                         │                      │   └── get_persona──┼──────────────────────►│
  │                         │                      │                     │                      │
  │                         │                      │── embed + search ──►│ (RAG)                │
  │                         │                      │◄── context ────────│                      │
  │                         │                      │                     │                      │
  │                         │                      │── build_prompt ────►│                      │
  │                         │                      │                     │                      │
  │                         │                      │── stream_response──►│                      │
  │                         │                      │◄── token_stream ───│                      │
  │── SSE stream ◄──────────┤◄───── SSE ──────────│                     │                      │
  │                         │                      │                     │                      │
  │                         │                      │── store_message ───►│                      │
  │                         │                      │── track_analytics ─►│                      │
  │                         │                      │── update_quota ────►│                      │
```

### 3.2 API Endpoint Categories

| Category | Base Path | Used By | Auth |
|----------|-----------|---------|------|
| Auth | `/api/v1/auth` | Login/Register | Public + JWT |
| AI | `/api/v1/ai` | Kemi & Chidi conversations | JWT |
| Finance | `/api/v1/finance` | Budget, transactions, savings | JWT |
| Business | `/api/v1/business` | Plans, tasks, invoices | JWT |
| Content | `/api/v1/content` | Courses, articles, forum, news | JWT (read public) |
| Intelligence | `/api/v1/intelligence` | RAG, documents, tips | JWT |
| Users | `/api/v1/users` | Profile, preferences, notifications | JWT |
| Admin | `/api/v1/admin` | Stats, user management | JWT + Admin |
| Subscriptions | `/api/v1/subscriptions` | Plans, upgrade, usage | JWT |
| Ads | `/api/v1/ads` | Serve ads, track impressions | JWT + Public |

---

## 4. Data Flow

### 4.1 Read Flow (e.g., "How much did I spend on food this month?")

```
Kemi receives query
  → Guardrails: check input safety
  → Intent classification: "budget_query"
  → Context assembly: fetch user budgets + transactions
  → RAG: search knowledge base for relevant financial tips
  → Prompt assembly: build LLM prompt with context
  → LLM: generate response citing sources
  → Guardrails: check output safety
  → Streaming response to user
```

### 4.2 Write Flow (e.g., "Create an invoice for client XYZ")

```
Chidi receives request
  → Guardrails: check input safety
  → Intent classification: "create_invoice"
  → Context assembly: fetch user's business profile
  → Capability call: Business Module → invoice creation
  → Response assembly: "Invoice #INV-042 created for XYZ"
  → Store in PostgreSQL
  → Return confirmation with invoice details
```

### 4.3 RAG Flow

```
User query → Embed text (OpenAI/text-embedding-3-small)
  → Search Pinecone (cosine similarity > 0.75 threshold)
  → Retrieve top-k chunks (k=5)
  → Format as context with source citations
  → Inject into LLM prompt
  → LLM generates cited response
  → Return response with [1][2][] inline citations
```

---

## 5. Scaling & Performance

| Metric | Target | Strategy |
|--------|--------|----------|
| Conversation latency | < 3s first token | SSE streaming, Groq for speed, response caching |
| API response time (p95) | < 500ms reads | Redis caching, DB indexing, connection pooling |
| RAG query time | < 1.5s | Pinecone serverless, embedding cache |
| Concurrent users (v1) | 1,000 | Horizontal scaling via Railway, connection pooling |
| Database connections | 20 pool / 40 overflow | SQLAlchemy pool_size + max_overflow |
| Frontend bundle | < 300 kB gzipped | Code splitting, lazy loading, tree shaking |

---

## 6. Security Boundaries

| Layer | Measure |
|-------|---------|
| Transport | TLS 1.3, HSTS (post-launch) |
| API | JWT Bearer auth, CORS whitelist, rate limiting |
| AI | Input guardrails, PII redaction, output sanitization, source citation |
| Database | Parameterized queries (SQLAlchemy ORM), credential rotation |
| Secrets | Environment variables (Pydantic Settings), never in code |
| External | API keys in .env, webhook signature verification (Paystack, Flutterwave) |

---

## 7. External Service Integration

| Service | Integration Point | Fallback |
|---------|------------------|----------|
| OpenRouter (LLM) | Chat completions API | Groq |
| Groq (LLM) | Chat completions API | OpenRouter |
| OpenAI (Embeddings) | text-embedding-3-small | Jina AI / sentence-transformers |
| Pinecone (Vector) | upsert + query | Local FAISS (future) |
| SendGrid (Email) | Mail send API | Mailgun |
| Mailgun (Email) | Mail send API | Log warning |
| Paystack (Payments) | Initialize + verify + webhook | Flutterwave |
| Flutterwave (Payments) | Initialize + verify + webhook | Manual activation |
| AfricasTalking (SMS) | Send message API | Twilio |
| Twilio (SMS) | Send message API | Log warning |
| PostHog (Analytics) | Capture + identify | Silent no-op |
| AWS S3 (Storage) | Put object + get URL | Local disk |

---

## 8. Monitoring & Observability

- **Health checks**: `GET /api/v1/health` — DB, Redis, Pinecone status
- **Logging**: Structured JSON logs (request_id, user_id, latency)
- **Metrics**: Request count, error rate, p50/p95/p99 latency, AI token usage
- **Alerting**: Sentry for errors, Railway metrics for infrastructure
- **Analytics**: PostHog for user behavior (signup, chat, budget create)
