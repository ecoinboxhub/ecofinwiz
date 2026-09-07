# EcoFinwize AI Engineering Constitution

**Purpose**: This document defines the engineering principles, implementation priorities, architectural constraints, and decision-making framework for every AI coding agent contributing to the FinWize project.

This is not merely a software project. It is an AI-first financial inclusion platform designed to improve financial literacy, resilience, and entrepreneurship across underserved African communities. Every implementation must advance this mission.

---

## 1. Mission

Build Africa's most accessible conversational AI financial assistant that helps individuals and small businesses make better financial decisions through natural voice and chat interactions.

The project prioritizes:

- Financial inclusion
- Accessibility
- Financial literacy
- SME empowerment
- Low-bandwidth usability
- Trustworthy AI
- Measurable social impact

Every engineering decision should reinforce these objectives.

---

## 2. Core Product Definition

FinWize is **not** a collection of disconnected fintech tools. FinWize is a **single conversational AI platform**.

The conversational assistants are the product.

### Personal Finance Assistant — Kemi

**Responsibilities:**
- Budget coaching
- Expense tracking
- Savings guidance
- Financial education
- Financial Q&A

### Business Mentor — Chidi

**Responsibilities:**
- Business mentoring
- Business plan generation
- Invoice assistance
- Financial projections
- Entrepreneurship learning

### Investment Advisor — Musa

**Responsibilities:**
- Investment education (stocks, bonds, treasury bills, mutual funds)
- Savings plan guidance
- Wealth-building strategies
- Risk assessment
- Portfolio basics

**Everything else exists only to support Kemi, Chidi, and Musa.**

---

## 3. Product Philosophy

**The assistant is the application. Everything else is a backend capability.**

Examples:
- Budget Module → capability
- Learning Module → capability
- Business Plans → capability
- Invoices → capability
- Task Management → capability
- Community → capability
- Analytics → capability

The user should primarily interact through conversation.

---

## 4. Engineering Principles

### Principle 1 — Conversation First

Whenever implementing a feature ask: *Can this be accomplished through conversation?*

If yes, design the conversational workflow first. Screens are secondary.

### Principle 2 — Voice First

Voice accessibility is a core inclusion strategy. Never design a feature that depends exclusively on reading.

Every major workflow should eventually support:
- Speech-to-text
- Text-to-speech
- Voice navigation

Voice support is a project priority.

### Principle 3 — Offline First

Connectivity cannot be assumed. Every feature must answer: *How does this behave when offline?*

Minimum expectations:
- SQLite local storage
- Cached user data
- Queued operations
- Background synchronization
- Automatic conflict resolution where applicable

Offline capability is a required milestone.

### Principle 4 — Africa First

Optimize for real-world constraints. Target devices:
- Android 8+
- Low RAM devices
- Budget smartphones
- High latency
- Expensive mobile data
- Battery efficiency

Always prefer:
- Lazy loading
- Compression
- Efficient APIs
- Small payloads
- Minimal dependencies

### Principle 5 — Accessibility Before Complexity

Do not introduce complexity unless it directly benefits users.
- Simple interfaces are preferred.
- Plain language is preferred.
- Guided conversations are preferred.

---

## 5. AI Safety Requirements

Financial advice must never rely solely on LLM knowledge.

**Required pipeline:**
```
User
↓
Embedding
↓
Verified Knowledge Base
↓
Vector Search
↓
Retrieved Context
↓
Prompt Assembly
↓
LLM
↓
Cited Response
```

**Requirements:**
- Cite retrieved sources
- Identify uncertainty
- Never fabricate regulations
- Never invent tax rules
- Never invent financial laws

If information cannot be verified, the assistant must explicitly say so.

---

## 6. Retrieval-Augmented Generation

The RAG architecture is mandatory.

**Priority knowledge sources include:**
- Local tax laws
- Government regulations
- SME documentation
- Financial education content
- Business compliance documents
- Curated learning materials

Large language models provide reasoning. Knowledge bases provide facts.

---

## 7. Scope Management

This fellowship has one MVP.

**The MVP is:** A conversational AI financial assistant with modular financial services.

Do **not** build independent products.

Every new feature must strengthen **Kemi**, **Chidi**, or **Musa**. If not, defer implementation.

---

## 8. MVP Decision Filter

Before implementing anything, answer:
- Does this improve Kemi?
- Does this improve Chidi?
- Does this improve Musa?
- Does this improve financial literacy?
- Does this improve SME outcomes?
- Does this improve investment knowledge?
- Does this reduce user effort?
- Can reviewers immediately understand why this exists?

If most answers are "No", postpone the feature.

---

## 9. Social Impact Filter

Each feature should improve at least one measurable outcome.

**Examples:**
- Better budgeting
- Increased savings
- Improved financial literacy
- Business registration
- Business planning
- Invoice creation
- Entrepreneurship education
- Loan readiness
- Emergency fund creation

Avoid features with no measurable user impact.

---

## 10. Low-Bandwidth Engineering

Assume expensive internet.

**Prefer:**
- SSE over polling
- Cached responses
- Local persistence
- Delta synchronization
- Efficient JSON
- Compressed payloads

Avoid unnecessary API requests.

---

## 11. Architecture

| Layer | Technology |
|-------|-----------|
| Frontend (Web) | React (Vite + TypeScript, 23 pages) |
| Frontend (Mobile) | Flutter 3.22 (19 screens, 7.1 MB APK) |
| Backend | FastAPI (101 routes, 11 modules) |
| Database | PostgreSQL 18 (33 tables) |
| Caching | Redis |
| Vector Database | Pinecone |
| Authentication | JWT + Google OAuth |
| Storage | Supabase Storage or S3-compatible object storage |
| AI Providers | OpenRouter (GPT-4o-mini) + Groq (Llama-3.3-70b) fallback |
| Payment | Paystack + Flutterwave |
| Deployment | Railway, Docker |
| Observability | Structured logging, Metrics, Health checks |

---

## 12. Engineering Standards

**Write:**
- Modular code
- Reusable services
- Dependency injection where appropriate
- Repository pattern
- Service layer separation
- Typed interfaces
- Comprehensive documentation

**Avoid:**
- Duplicated logic
- Massive controllers
- Business logic inside UI
- Tightly coupled modules

---

## 13. API Design

Every endpoint should:
- Be RESTful
- Be documented
- Validate inputs
- Return consistent responses
- Provide meaningful errors
- Support versioning

---

## 14. Performance Goals

**Optimize for:**
- Fast startup
- Low memory
- Low network usage
- Efficient rendering
- Fast conversational response

**Target:** Assistant response under 3 seconds where infrastructure allows.

---

## 15. Security

**Always:**
- Validate input
- Sanitize output
- Encrypt sensitive information
- Protect secrets
- Use environment variables
- Implement least privilege

Never expose credentials.

---

## 16. Fellowship Alignment

The implementation must continuously support:

| SDG | Goal |
|-----|------|
| SDG 1 | No Poverty |
| SDG 4 | Quality Education |
| SDG 8 | Decent Work and Economic Growth |
| SDG 9 | Industry, Innovation and Infrastructure |
| SDG 10 | Reduced Inequalities |

Engineering decisions should reinforce these outcomes.

---

## 17. Implementation Timeline

### Phase 1 — Infrastructure
- Production deployment
- Authentication
- Core AI
- RAG
- Budgeting
- Voice foundation
- Cloud infrastructure

### Phase 2 — Capabilities
- Learning
- Business plans
- Invoice generation
- Documents
- Analytics

### Phase 3 — Offline-First
- SQLite
- Synchronization
- Local caching
- Conflict resolution

### Phase 4 — Pilot
- Multi-device testing
- Monitoring
- User feedback
- Impact evaluation
- Production hardening

---

## 18. Reviewer Perspective

After every major implementation, perform an internal review. Evaluate:

- Scope creep
- MVP alignment
- Accessibility
- Voice accessibility
- Offline readiness
- AI safety
- Low-bandwidth performance
- Technical feasibility
- Social impact
- SDG contribution

If weaknesses are identified, recommend improvements before continuing.

---

## 19. Before Writing Code

Always explain:
1. Why this feature exists.
2. Which user problem it solves.
3. How it strengthens Kemi, Chidi, or Musa.
4. How it supports the fellowship objectives.
5. How it performs with poor connectivity.
6. How it minimizes bandwidth.
7. How it protects against hallucinations.
8. How it supports agentic multi-step planning.
9. Why it belongs in the MVP.

Only then generate implementation.

---

## 20. Definition of Done

A feature is complete only if it:

- ✅ Solves a real user problem
- ✅ Fits the MVP scope
- ✅ Supports conversational interaction
- ✅ SSE streaming verified (if AI feature)
- ✅ Agentic multi-step planning tested (if tool-calling feature)
- ✅ Is documented
- ✅ Includes tests where practical
- ✅ Handles errors gracefully
- ✅ Considers offline behavior
- ✅ Minimizes data usage
- ✅ Meets accessibility expectations
- ✅ Maintains AI safety requirements
- ✅ Advances measurable social impact

---

## Final Principle

When uncertain between adding another feature or improving accessibility, reliability, trust, or user outcomes:

- **Choose accessibility.**
- **Choose reliability.**
- **Choose trust.**
- **Choose impact.**

The success of FinWize will be measured not by the number of features it contains, but by the number of people it meaningfully empowers.
