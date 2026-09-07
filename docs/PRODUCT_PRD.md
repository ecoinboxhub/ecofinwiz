# EcoFinwize — Product Requirements Document

> **Companion to**: AGENTS.md (Engineering Constitution)
> **Purpose**: Product requirements centered on Kemi and Chidi as the primary user interfaces. All backend modules exist as capabilities supporting the conversational agents.

---

## 1. Product Vision

EcoFinwize is a single conversational AI platform where users interact primarily through two AI assistants — Kemi (Personal Finance) and Chidi (Business Mentor). All other features (budgets, transactions, invoices, courses) are backend capabilities that the assistants access on the user's behalf.

The assistant *is* the application. Everything else is infrastructure.

---

## 2. User Experience Principles

| Principle | Description |
|-----------|-------------|
| **Conversation First** | The primary interaction mode is chat. Screens display what the assistant already knows or has done. |
| **Progressive Disclosure** | New users get guided conversations. Advanced users get shortcuts and direct commands. |
| **Offline Resilience** | The platform works without connectivity. Conversations queue and sync. |
| **Voice Ready** | Every interaction can eventually be hands-free. No feature depends exclusively on reading. |
| **Plain Language** | No financial jargon unless explained. No complex dashboards as the default view. |
| **Trust Through Transparency** | AI cites sources, admits uncertainty, and never fabricates information. |

---

## 3. Primary Interfaces

### 3.1 Kemi — Personal Finance Assistant

**Personality**: Empathetic, encouraging, practical. Speaks in plain language.

**Core Job**: Help users understand and improve their personal finances through conversation.

**Capabilities:**

| Capability | Description | Backend Module | Priority |
|-----------|-------------|----------------|----------|
| Budget coaching | Create, review, and adjust budgets via conversation | Finance | P0 |
| Expense tracking | Log and categorize transactions by chatting | Finance | P0 |
| Savings guidance | Set goals, track progress, get saving tips | Finance | P0 |
| Financial Q&A | Answer questions about spending, saving, investing | Finance + RAG | P0 |
| Financial education | Recommend courses and articles based on needs | Learning | P1 |
| Spending insights | "You spent 20% more on transport this month" | Finance | P1 |
| Bill reminders | "Your subscription renews tomorrow" | Finance | P2 |
| Budget alerts | "You've used 80% of your food budget" | Finance | P1 |

**Conversation flows:**

```
User: "I want to set a budget for food"
Kemi: "Sure! How much would you like to budget for food this month?"
User: "30,000 naira"
Kemi: "Done! I've created a food budget of ₦30,000 for this month. 
       Would you like me to track food expenses automatically?"
```

```
User: "How did I spend last month?"
Kemi: "Here's your March summary:
       • Total income: ₦180,000
       • Total expenses: ₦145,000
       • Top category: Transport (₦45,000 — 31%)
       • You saved ₦35,000 — that's 19% of income!
       
       Would you like to see a detailed breakdown?"
```

### 3.2 Chidi — Business Mentor

**Personality**: Direct, practical, experienced. Focuses on actionable business advice.

**Core Job**: Help SMEs and entrepreneurs grow their businesses through mentoring conversation.

**Capabilities:**

| Capability | Description | Backend Module | Priority |
|-----------|-------------|----------------|----------|
| Business mentoring | Strategy advice, pricing, client acquisition | AI + RAG | P0 |
| Business plan generation | Create structured business plans via Q&A | Business | P0 |
| Invoice assistance | Create, send, track invoices via chat | Business | P0 |
| Task management | Create and track business tasks | Business | P1 |
| Financial projections | Basic revenue and cost projections | Business | P1 |
| Market insights | Industry trends from news and knowledge base | Intelligence + RAG | P2 |
| Entrepreneurship learning | Recommend courses for business growth | Learning | P1 |

**Conversation flows:**

```
User: "I need a business plan for my catering business"
Chidi: "Great! I'll help you create one. Let me ask a few questions.
       
       What's your business name?"
User: "Aisha's Kitchen"
Chidi: "And what's your target market? Who are your customers?"
...
Chidi: "Here's your business plan draft. I've included:
       • Executive Summary
       • Market Analysis
       • Financial Projections
       • Operations Plan
       
       You can review and edit anytime."
```

```
User: "Create an invoice for client XYZ — ₦150,000 for catering services"
Chidi: "I've created invoice #INV-043 for XYZ:
       • Amount: ₦150,000
       • Service: Catering — March Wedding Event
       • Due: April 30, 2026
       
       Shall I send this to the client?"
```

---

## 4. User Stories

### Epic 1: Kemi Conversations

| ID | Story | Priority |
|----|-------|----------|
| KEMI-01 | As a user, I can chat with Kemi about my finances using natural language | P0 |
| KEMI-02 | As a user, Kemi remembers my financial context across conversations | P0 |
| KEMI-03 | As a user, I can ask Kemi to create or update my budget | P0 |
| KEMI-04 | As a user, I can tell Kemi about an expense and it gets tracked | P0 |
| KEMI-05 | As a user, I can ask Kemi "how much I spent" on any category | P0 |
| KEMI-06 | As a user, I can set savings goals through conversation | P0 |
| KEMI-07 | As a user, Kemi alerts me when I'm overspending | P1 |
| KEMI-08 | As a user, Kemi recommends courses based on my financial goals | P1 |
| KEMI-09 | As a user, I can ask Kemi to explain financial terms in plain language | P0 |
| KEMI-10 | As a user, Kemi cites sources when giving financial advice | P0 |
| KEMI-11 | As a user, I can rate Kemi's responses and report issues | P1 |

### Epic 2: Chidi Conversations

| ID | Story | Priority |
|----|-------|----------|
| CHIDI-01 | As an SME owner, I can chat with Chidi about my business | P0 |
| CHIDI-02 | As a user, Chidi helps me generate a business plan step by step | P0 |
| CHIDI-03 | As a user, I can create invoices by describing them to Chidi | P0 |
| CHIDI-04 | As a user, I can ask Chidi to create and track tasks | P1 |
| CHIDI-05 | As a user, Chidi recommends learning content for my business | P1 |
| CHIDI-06 | As a user, Chidi helps me estimate pricing and costs | P1 |
| CHIDI-07 | As a user, Chidi provides industry news and trends | P2 |
| CHIDI-08 | As a user, Chidi cites sources for business advice | P0 |

### Epic 3: Cross-Cutting

| ID | Story | Priority |
|----|-------|----------|
| CROSS-01 | As a user, I can switch between Kemi and Chidi seamlessly | P0 |
| CROSS-02 | As a user, conversations work offline and sync when reconnected | P1 |
| CROSS-03 | As a user, I can use voice input instead of typing | P2 |
| CROSS-04 | As a user, AI responses are safe and never give harmful advice | P0 |
| CROSS-05 | As a user, my financial data is private and secure | P0 |

---

## 5. Non-Functional Requirements

| ID | Requirement | Target | AGENTS Principle |
|----|-------------|--------|-----------------|
| NFR-01 | Conversation response time (first token) | < 3s | Principle 1 (Conversation First) |
| NFR-02 | Offline conversation capability | Full functionality queued | Principle 3 (Offline First) |
| NFR-03 | Voice input/output support | All major workflows | Principle 2 (Voice First) |
| NFR-04 | Application size (mobile) | < 15 MB | Principle 4 (Africa First) |
| NFR-05 | Data usage per conversation | < 50 KB | Principle 10 (Low-Bandwidth) |
| NFR-06 | RAG citation included | Every financial answer | Section 5 (AI Safety) |
| NFR-07 | Source verification | Never fabricate regulations/tax rules | Section 5 |
| NFR-08 | AI hallucination rate | < 1% of responses | Section 6 (RAG) |
| NFR-09 | User can report bad responses | Every AI message | Section 5 |
| NFR-10 | Feature serves Kemi or Chidi | Every feature passes MVP filter | Section 8 (MVP Filter) |

---

## 6. Success Metrics

| Metric | Definition | Target | Measurement |
|--------|-----------|--------|-------------|
| Conversation completion | % of conversations that achieve user intent | > 80% | PostHog events |
| User retention (D7) | Users returning within 7 days | > 40% | PostHog |
| Active conversations/user/week | Weekly chat sessions per user | > 3 | PostHog |
| Budgets created via conversation | % of budgets created through Kemi | > 60% | Analytics |
| Business plans generated | Total plans via Chidi | > 100/mo at scale | Analytics |
| AI rating | Average user rating of responses | > 4.0 / 5.0 | Feedback system |
| Hallucination rate | AI responses flagged as incorrect | < 1% | Moderation |
| Offline reliability | Conversations completed offline without data loss | > 95% | Sync logs |
| Voice adoption | % of conversations using voice input | > 20% | Analytics |

---

## 7. MVP Scope Boundaries

### In Scope (v1.0 — Fellowship MVP)

- Kemi: Budget coaching, expense tracking, savings guidance, financial Q&A, financial education
- Chidi: Business mentoring, business plan generation, invoice assistance, task management
- RAG: Verified knowledge base with source citations
- Web + Mobile (Android) clients
- JWT authentication
- Offline resilience (basic: caching, token persistence)

### Out of Scope (Post-Fellowship)

- iOS app
- WhatsApp / Telegram bot integration
- Advanced analytics dashboards
- P2P lending marketplace
- Crypto/stock trading
- Banking API integration (Open Banking)
- White-label licensing platform

---

## 8. Release Criteria

### Beta Release

- [ ] Kemi handles 5 core conversation flows (budget, track, savings, Q&A, education)
- [ ] Chidi handles 3 core conversation flows (mentoring, business plan, invoice)
- [ ] All conversations include RAG citations
- [ ] 27/28 backend smoke tests pass
- [ ] Web app deploys to Vercel without errors
- [ ] Mobile APK installs on Android 8+ device
- [ ] User can register and login

### Production Release

- [ ] All Epic 1 and Epic 2 stories implemented
- [ ] Rate limiting enforced
- [ ] Load test: 200 concurrent users, p95 < 2s
- [ ] Offline resilience: conversations work without connectivity
- [ ] Voice input available on mobile
- [ ] Error monitoring active (Sentry)
- [ ] Security audit passed
- [ ] WCAG accessibility baseline met
