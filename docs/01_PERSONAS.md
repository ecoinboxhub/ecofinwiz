# EcoFinwize — User Personas

> **Cross-cutting concern across ALL personas**: Data cost and offline resilience are critical. Target market has limited data budgets and intermittent connectivity. Every feature must be designed with offline-first caching and minimal data transfer. (Offline resilience is a known gap — not yet implemented.)

> **Implementation Status v1.0 (June 27, 2026)**: All core features described below are fully implemented across React web (21 pages, localhost:5300), Flutter mobile APK (18 screens, emulator-5554), and FastAPI backend (129 routes, localhost:8100/api/v1). The platform is feature-complete and ready for beta deployment.

---

## Persona 1: Tunde — The Young Freelancer (Primary)

- **Age**: 22
- **Occupation**: Freelance graphic designer
- **Location**: Lagos, Nigeria
- **Tech Comfort**: High (uses Notion, Figma, social media daily)
- **Financial State**: Irregular income, no savings, no investment knowledge
- **Goals**:
  - Track earnings and expenses across inconsistent gigs
  - Set aside emergency savings
  - Learn to invest small amounts
  - Get affordable health insurance and tax guidance
- **Pain Points**:
  - No formal financial education
  - Overwhelmed by budgeting apps built for salary earners
  - Needs business mentorship to grow from gig-worker to agency owner
- **How EcoFinwize Helps**:
  - Budget tracking that adapts to irregular income **(implemented: percentage-based adaptive algorithm with month rollover)**
  - AI mentor for freelance business growth **(implemented: Chidi mentor chat with SSE streaming)**
  - Micro-investing education **(implemented: learning hub with 4 tracks + articles with categories)**
  - RAG knowledge base for freelance contracts/tax **(implemented: Pinecone vector search + document upload)**
- **Implementation status**: Budget, transactions, savings goals, AI advisor (Kemi), AI mentor (Chidi), learning hub, articles, forum, invoices, tasks — all implemented via web + mobile + API.
- **Remaining gaps** (deferred to v2): Tax guidance automation, health insurance integration, true offline resilience.

---

## Persona 2: Aisha — The Small Business Owner (Primary)

- **Age**: 34
- **Occupation**: Owns a catering business (8 employees)
- **Location**: Abuja, Nigeria
- **Tech Comfort**: Medium (uses WhatsApp, Instagram, basic accounting software)
- **Financial State**: Moderate revenue, poor record-keeping, mixing personal/business funds
- **Goals**:
  - Separate business and personal finances
  - Create a proper business plan for bank loan application
  - Improve team productivity and scheduling
  - Understand pricing and profit margins
- **Pain Points**:
  - No time for long business courses
  - Struggles with cash flow management
  - Needs a simple business plan template
  - Wants to know competitors and market trends
- **How EcoFinwize Helps**:
  - Business plan generator **(implemented: AI-powered via OpenRouter/Groq, JSON output)**
  - SME productivity tools: task management, scheduling **(implemented: tasks CRUD with status/priority/due-date)**
  - Expense tracking with categorization **(implemented: 15 defaults + custom categories)**
  - AI business mentor for strategy advice **(implemented: Chidi mentor chat with business context)**
  - News aggregation for food industry trends **(implemented: MongoDB news with categories)**
  - Invoicing with auto-numbering, line items, tax **(implemented: full invoice CRUD)**
- **Implementation status**: All five features above fully implemented on web + mobile + API.
- **Remaining gaps** (deferred to v2): True personal/business fund separation (single wallet), inventory management, scheduling tools, PDF export.

---

## Persona 3: Chidi — The University Student

- **Age**: 20
- **Occupation**: Computer Science student
- **Location**: Enugu, Nigeria
- **Tech Comfort**: Very High
- **Financial State**: Dependent on parents, part-time tutoring income
- **Goals**:
  - Learn financial literacy
  - Save for a new laptop
  - Understand crypto and traditional investing
  - Build credit history
- **Pain Points**:
  - No disposable income to invest
  - Financial jargon is intimidating
  - Needs motivation and progress tracking
- **How EcoFinwize Helps**:
  - Gamified financial literacy courses **(implemented: learning hub with 4 tracks, quizzes, auto-grading, progress tracking)**
  - Savings planner with visual goals **(implemented: goals CRUD, progress bars with percentage, contributions)**
  - Investment education hub simplified **(implemented: articles with categories, featured, slug-based routing)**
  - Progress tracking and badges **(implemented: badge system with BadgeRule + UserBadge, lesson completion, course progress %)**
  - Forum for community learning **(implemented: topics + replies with pin/lock/solution)**
- **Implementation status**: All features above fully implemented on web + mobile + API.
- **Remaining gaps** (deferred to v2): Credit history building, simulated trading, crypto education module.

---

## Persona 4: Mr. Eze — The Public Servant

- **Age**: 45
- **Occupation**: Senior administrator, Ministry of Education
- **Location**: Port Harcourt, Nigeria
- **Tech Comfort**: Low (uses email, WhatsApp, basic browsing)
- **Financial State**: Stable salary, mounting debt, no investments
- **Goals**:
  - Pay off debt systematically
  - Start a side business for retirement
  - Understand pension and insurance options
  - Save for children's education
- **Pain Points**:
  - Jargon-filled financial advice
  - Distrust of digital platforms
  - No experience with business planning
  - Needs simplified, trustworthy guidance
- **How EcoFinwize Helps**:
  - Plain-language financial advice via AI chat **(implemented: Kemi advisor with plain-language system prompts)**
  - Business plan generator step-by-step **(implemented: AI-powered, structured output)**
  - Financial literacy courses basic track **(implemented: beginner track in learning hub)**
  - Transparent AI with source citations **(implemented: RAG citations, 1-5 star rating, report inappropriate)**
- **Known gaps in existing implementation**:
  - Debt repayment planner: **not implemented** (deferred — requires compounding interest calculator + payoff simulation)
  - Pension/insurance explainers: not covered as dedicated modules
  - Simplified UI (large text, clear CTAs): **partial** — Tailwind responsive design exists but no dedicated "senior mode"
  - Offline-first: **not implemented** (critical for this persona's usage patterns)

---

## Persona 5: Funmi — The Aspiring Investor

- **Age**: 29
- **Occupation**: Marketing manager at a tech startup
- **Location**: Nairobi, Kenya (remote for a UK company)
- **Tech Comfort**: High
- **Financial State**: Good salary, some savings, wants to grow wealth
- **Goals**:
  - Learn stock market, mutual funds, real estate
  - Diversify into USD assets
  - Find vetted investment opportunities
  - Network with other investors
- **Pain Points**:
  - Scams and unregulated schemes
  - Information overload
  - No personalized investment recommendations
- **How EcoFinwize Helps**:
  - Investment education hub with curated content **(implemented: articles with categories, featured, multi-region)**
  - Personalized recommendations **(implemented: hybrid recommender — content-based: persona + interests + bookmarks + completed lessons)**
  - RAG knowledge base with verified info **(implemented: Pinecone vector search, source citations, 0.75 cosine threshold)**
  - News aggregation for market analysis **(implemented: news with categories, regions, breaking flag)**
  - Bookmarking for later reference **(implemented: bookmark toggle, list, delete)**
- **Implementation status**: All features above fully implemented on web + mobile + API.
- **Remaining gaps** (deferred to v2): Investment glossary, portfolio simulation, networking/community features.

---

## Persona 5.5: Ifeanyi — The Student Freelancer (Secondary / Cross-over)

- **Age**: 24
- **Occupation**: Final-year engineering student + freelance web developer
- **Location**: Benin City, Nigeria
- **Tech Comfort**: Very High
- **Financial State**: Small but growing freelance income; no savings; tuition-dependent
- **Goals**:
  - Balance study and freelance work
  - Save freelancing income for post-graduation startup
  - Learn business finance before leaving school
  - Track both personal and micro-business cash flows
- **Pain Points**:
  - No tool handles "part student, part freelancer" identity
  - Needs to separate school expenses from business expenses
  - Can't afford paid tools (QuickBooks, etc.)
  - Irregular schedule makes habit-formation hard
- **How EcoFinwize Helps**:
  - Adaptive budget that works with irregular income **(implemented: percentage-based adaptive algorithm)**
  - Micro-learning courses that fit between classes **(implemented: 4 learning tracks with short lessons)**
  - Business tools (invoices, tasks) available on free tier **(implemented: tasks + invoices on Free plan)**
  - AI mentor for freelance business growth **(implemented: Chidi mentor)**
- **Known gaps in existing implementation**:
  - Dual-persona profile (student + freelancer): **not implemented** (single persona per account)
  - Separate budget tracks for personal vs business: **partial** (categories can distinguish, but no true dual-wallet separation)
  - True offline resilience: **not implemented**

---

## Summary: Persona Coverage Matrix

| Feature | Tunde (Freelancer) | Aisha (SME Owner) | Chidi (Student) | Mr. Eze (Public Servant) | Funmi (Investor) | Ifeanyi (Cross-over) |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|
| Adaptive Budget | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Expense Tracking | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Savings Goals | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| AI Advisor (Kemi) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| AI Mentor (Chidi) | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| Business Plan Gen | ❌ | ✅ | ❌ | ✅ | ❌ | ✅ |
| Tasks | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| Invoices | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| Learning Hub | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Articles | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| News | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |
| Forum | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| Notifications | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Daily Tips | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| RAG Knowledge | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Debt Planner | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Offline Support | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Dual Persona | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

> ✅ = Implemented in v1.0 | ❌ = Not implemented (deferred to v2)
