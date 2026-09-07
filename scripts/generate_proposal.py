from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
import datetime

doc = Document()

# ── Styles ──
style = doc.styles['Normal']
font = style.font
font.name = 'Calibri'
font.size = Pt(11)

# ── Helper functions ──
def add_heading_styled(text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = RGBColor(0x0C, 0x4A, 0x6E)
    return h

def add_bold_text(paragraph, bold_text, normal_text):
    run = paragraph.add_run(bold_text)
    run.bold = True
    paragraph.add_run(normal_text)
    return paragraph

def add_bullet(text, bold_prefix=""):
    p = doc.add_paragraph(style='List Bullet')
    if bold_prefix:
        add_bold_text(p, bold_prefix, text)
    else:
        p.add_run(text)
    return p

# ═══════════════════════════════════════════════
# TITLE PAGE
# ═══════════════════════════════════════════════
doc.add_paragraph()
doc.add_paragraph()

title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run("PROJECT PROPOSAL")
run.bold = True
run.font.size = Pt(26)
run.font.color.rgb = RGBColor(0x0C, 0x4A, 0x6E)

doc.add_paragraph()

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = subtitle.add_run("EcoFinwize: AI-Powered Financial & Business Guidance Platform")
run.bold = True
run.font.size = Pt(18)
run.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

doc.add_paragraph()

date_para = doc.add_paragraph()
date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = date_para.add_run(f"Date: {datetime.date.today().strftime('%B %Y')}")
run.font.size = Pt(12)
run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

doc.add_paragraph()
doc.add_paragraph()

# Horizontal rule
doc.add_paragraph("_" * 80)

doc.add_page_break()

# ═══════════════════════════════════════════════
# TABLE OF CONTENTS (manual)
# ═══════════════════════════════════════════════
add_heading_styled("Table of Contents", level=1)
toc_items = [
    "1. Title of Proposal",
    "2. Thematic Area",
    "3. Problem Statement",
    "4. Target Audience",
    "5. Type of Project",
    "6. Type of Expected Output",
    "7. Description of the Innovative Project Idea",
    "8. Measurable Social & Economic Outcomes (SDG Alignment)",
    "9. Project Contribution to Real-World Impact",
    "10. Project Plan, Methodology & Data Sources",
    "11. Experts & Collaborators",
    "12. Sustainability & Revenue Model",
    "13. Abstract / Executive Summary",
]
for item in toc_items:
    p = doc.add_paragraph(item)
    p.paragraph_format.space_after = Pt(6)
    p.runs[0].font.size = Pt(11)

doc.add_page_break()

# ═══════════════════════════════════════════════
# 1. TITLE OF PROPOSAL
# ═══════════════════════════════════════════════
add_heading_styled("1. Title of Proposal", level=1)
doc.add_paragraph(
    "EcoFinwize: AI-Powered Financial & Business Guidance Platform for African Youths, "
    "SMEs, Freelancers, Students, and Public Service Workers"
)

# ═══════════════════════════════════════════════
# 2. THEMATIC AREA
# ═══════════════════════════════════════════════
add_heading_styled("2. Thematic Area", level=1)

themes = [
    ("Primary: ", "Fintech for Financial Inclusion — Leveraging AI and mobile-first technology to "
     "democratize access to financial guidance for underserved populations."),
    ("Secondary: ", "AI for Sustainable Development — Applying large language models and "
     "retrieval-augmented generation (RAG) to deliver personalized, contextual, and "
     "trustworthy financial education at scale."),
    ("Tertiary: ", "Youth Empowerment & SME Development — Building human capital and "
     "enterprise capacity through digital tools, business mentorship, and financial literacy."),
]
for bold, normal in themes:
    add_bullet(normal, bold_prefix=bold)

# ═══════════════════════════════════════════════
# 3. PROBLEM STATEMENT
# ═══════════════════════════════════════════════
add_heading_styled("3. Problem Statement", level=1)

doc.add_paragraph(
    "Across Africa, over 70% of the population lacks access to formal financial advice. "
    "Youths, freelancers, small business owners, students, and public servants — the backbone "
    "of the continent's economy — face a compounding crisis:"
)

problems = [
    ("No adaptive financial tools: ", "Most budgeting and financial planning applications are "
     "designed for salaried workers with predictable income. Freelancers and SMEs, whose income "
     "is irregular, find these tools frustrating and irrelevant, leading to abandonment."),
    ("Financial literacy gap: ", "Over 60% of young Africans cannot define basic financial "
     "concepts like compound interest, diversification, or risk assessment. Existing educational "
     "content is either too academic (jargon-heavy) or too superficial."),
    ("No access to trusted mentorship: ", "SMEs and freelancers need business guidance — "
     "pricing strategy, client acquisition, cash flow management — but professional business "
     "mentors are expensive and inaccessible. Meanwhile, unregulated 'finfluencers' spread "
     "misinformation."),
    ("Time poverty: ", "SME owners and public service workers cannot dedicate hours to "
     "financial courses or complex dashboards. They need micro-learning and instant, "
     "conversational guidance that fits into their daily routine."),
    ("Trust deficit in digital finance: ", "Scams, failed fintech startups, and complex "
     "user interfaces have created deep skepticism, particularly among older and less "
     "tech-comfortable demographics."),
    ("Fragmented ecosystem: ", "Users currently juggle 3-5 different apps for budgeting, "
     "invoicing, learning, and news — there is no unified platform that understands their "
     "complete financial context."),
]
for bold, normal in problems:
    add_bullet(normal, bold_prefix=bold)

# ═══════════════════════════════════════════════
# 4. TARGET AUDIENCE
# ═══════════════════════════════════════════════
add_heading_styled("4. Who Are the Targets for This Project?", level=1)

doc.add_paragraph(
    "EcoFinwize targets five primary user personas, representing over 200 million individuals "
    "across Africa's emerging economies:"
)

targets = [
    ("Tunde (The Freelancer) — Age 22, Lagos", ": Irregular-income creative professionals who "
     "need adaptive budgeting, business mentorship, and micro-investing education to grow "
     "from gig-worker to agency owner."),
    ("Aisha (The SME Owner) — Age 34, Abuja", ": Small business operators with 5-15 employees "
     "who need business plan generation, expense separation, team productivity tools, and "
     "industry-specific market intelligence."),
    ("Chidi (The University Student) — Age 20, Enugu", ": Students with part-time income "
     "who need gamified financial literacy, savings goals, and simplified investment education."),
    ("Mr. Eze (The Public Servant) — Age 45, Port Harcourt", ": Stable-salary professionals "
     "with debt, no investments, and low tech comfort who need plain-language AI advice, "
     "debt repayment planning, and retirement preparation."),
    ("Funmi (The Aspiring Investor) — Age 29, Nairobi", ": Mid-career professionals with "
     "savings who need curated investment education, personalized recommendations, and "
     "vetted market information."),
    ("Ifeanyi (The Student Freelancer — Cross-over) — Age 24, Benin City", ": A rapidly growing "
     "demographic that needs dual-persona support: managing both personal finances as a student "
     "and business finances as a freelancer in one unified experience."),
]
for bold, normal in targets:
    add_bullet(normal, bold_prefix=bold)

# ═══════════════════════════════════════════════
# 5. TYPE OF PROJECT
# ═══════════════════════════════════════════════
add_heading_styled("5. Type of Project", level=1)

project_types = [
    "✔ Product Development — Design, build, and launch a fully branded digital product (Finwize)",
    "✔ Application Development — Three interconnected applications: React web app, Flutter mobile APK, and Python FastAPI backend",
    "✔ Capacity Building / Training — Built-in financial literacy courses and AI-guided mentorship for users",
    "✔ Service Delivery Enhancement — AI-powered financial advisory as a scalable public service",
    "✔ Research & Development — RAG-based knowledge retrieval, personalized recommendation engine, and adaptive budgeting algorithms",
]
for pt in project_types:
    add_bullet(pt)

# ═══════════════════════════════════════════════
# 6. TYPE OF EXPECTED OUTPUT
# ═══════════════════════════════════════════════
add_heading_styled("6. Type of Expected Output", level=1)

outputs = [
    "✔ Digital Platform / App / Tool — Fully functional Finwize platform comprising:",
    "    • React web application (Vercel-hosted, responsive, mobile-first)",
    "    • Flutter Android APK (GitHub Releases distribution, < 30MB, offline-capable)",
    "    • Python FastAPI RESTful backend (modular monolith, auto-generated OpenAPI docs)",
    "    • PostgreSQL + MongoDB + Pinecone multi-database architecture",
    "    • Docker containerization with CI/CD via GitHub Actions",
    "",
    "✔ Training Program / Workshop / Campaign — Embedded financial literacy curriculum:",
    "    • 4 learning tracks (Beginner, Freelancer, SME, Investor)",
    "    • Micro-lessons (3-5 minutes each) with gamification and progress streaks",
    "    • Interactive quizzes and milestone-based badge rewards",
    "    • AI-delivered personalized daily tips",
    "",
    "✔ Pilot Implementation —",
    "    • Closed beta with 50 users across all five persona groups",
    "    • 3-month pilot measuring D7/D30 retention, course completion rates, and NPS",
    "    • Iterative refinement based on usage analytics and user feedback",
]
for o in outputs:
    doc.add_paragraph(o)

# ═══════════════════════════════════════════════
# 7. DESCRIPTION OF INNOVATIVE PROJECT IDEA
# ═══════════════════════════════════════════════
add_heading_styled("7. Description of the Innovative Project Idea", level=1)

add_heading_styled("7.1 The Problem", level=2)
doc.add_paragraph(
    "Financial exclusion in Africa is not just about access to bank accounts — it is about "
    "access to understanding. Over 400 million adults in Sub-Saharan Africa remain financially "
    "excluded, and among those with bank accounts, the majority lack the knowledge, tools, and "
    "trust to make informed financial decisions. Existing solutions fail because they:"
)
failures = [
    "Assume stable, predictable income (ignoring 80%+ of African workers in informal/freelance sectors)",
    "Present complex dashboards with financial jargon instead of conversational guidance",
    "Offer generic advice without personal context (income, goals, risk tolerance, life stage)",
    "Require expensive human advisors that cannot scale to the population's needs",
]
for f in failures:
    add_bullet(f)

add_heading_styled("7.2 The Proposed Solution: EcoFinwize", level=2)
doc.add_paragraph(
    "EcoFinwize is an AI-powered, mobile-first financial and business guidance platform that "
    "combines four breakthrough innovations into a single, unified experience:"
)

solutions = [
    ("Conversational AI Financial Advisor & Mentor: ",
     "Unlike traditional fintech dashboards, EcoFinwize's primary interface is a chat-based AI "
     "assistant. Using large language models (LLMs) with Retrieval-Augmented Generation (RAG), "
     "the AI advisor understands the user's full financial context — income, spending patterns, "
     "savings goals, and learning progress — and delivers personalized, actionable guidance "
     "in plain language. It cites sources, avoids harmful advice, and improves through "
     "user feedback."),
    ("Adaptive Budgeting for Irregular Income: ",
     "A patent-ready innovation: instead of fixed monthly limits, Finwize uses percentage-based "
     "budgeting that adapts to actual income. If a freelancer earns 200,000 NGN one month and "
     "80,000 the next, spending limits adjust proportionally. Surplus from good months rolls "
     "over, and the AI suggests saving targets during high-earning periods."),
    ("Multi-Layer RAG Knowledge Base: ",
     "EcoFinwize maintains a curated knowledge base of financial regulations, tax guides, "
     "investment fundamentals, and business best practices — grounded in local context "
     "(Nigeria Tax Code, Kenya Capital Markets Authority, etc.). User questions are embedded, "
     "matched against vectorized documents in Pinecone, and answered with verifiable citations, "
     "dramatically reducing hallucination risk."),
    ("Unified Platform, Three Surfaces: ",
     "A React web app for deep work (business plans, course taking, analytics), a Flutter APK "
     "for daily mobile use (expense tracking, AI chat, notifications), and a shared FastAPI "
     "backend. All three share one API, one database, and one user profile, ensuring seamless "
     "cross-device experience."),
]
for bold, normal in solutions:
    add_bullet(normal, bold_prefix=bold)

add_heading_styled("7.3 How Fintech and AI Innovation Are Integrated", level=2)

innovations = [
    ("LLM-as-a-Service Advisor: ",
     "EcoFinwize wraps GPT-4o-mini and Claude Haiku with a safety layer, persona-based "
     "system prompts, and RAG context assembly. This makes AI-generated financial advice "
     "safe, contextual, and cost-effective ($0.05 per conversation)."),
    ("Hybrid Recommendation Engine: ",
     "Combining rule-based logic (persona + financial goals), collaborative filtering "
     "(what similar users learned/saved), and LLM scoring to recommend the right course, "
     "article, or action at the right time."),
    ("Offline-First Architecture: ",
     "Core data (transactions, budgets, goals) cached locally via Hive (Flutter) with "
     "background sync. AI queries are queued and processed on reconnect — critical for "
     "markets with intermittent connectivity."),
    ("OpenAPI-Driven Development: ",
     "60+ RESTful endpoints with auto-generated documentation, Pydantic v2 validation, "
     "SQLAlchemy async ORM, and full OpenAPI specs. This enables API-first development "
     "where web, mobile, and third-party integrations all consume the same contract."),
    ("Multi-Database Strategy: ",
     "PostgreSQL for transactional reliability (budgets, transactions, user data), "
     "MongoDB for document flexibility (courses, articles, news), and Pinecone vector "
     "database for semantic RAG retrieval — each chosen for optimal performance per use case."),
]
for bold, normal in innovations:
    add_bullet(normal, bold_prefix=bold)

# ═══════════════════════════════════════════════
# 8. MEASURABLE SOCIAL & ECONOMIC OUTCOMES
# ═══════════════════════════════════════════════
add_heading_styled("8. Measurable Social & Economic Outcomes Focused on Sustainable Development", level=1)

doc.add_paragraph(
    "EcoFinwize directly contributes to multiple United Nations Sustainable Development Goals "
    "(SDGs) with measurable, quantified targets:"
)

add_heading_styled("SDG 1: No Poverty", level=2)
doc.add_paragraph(
    "Target 1.4: Ensure equal access to financial services.\n"
    "• Outcome: 10,000 active users in Year 1, with > 65% from low-to-middle-income brackets.\n"
    "• Metric: % of users who create and maintain savings goals for 30+ days.\n"
    "• Target: > 50% of active users have ≥ 1 active savings goal within 30 days."
)

add_heading_styled("SDG 4: Quality Education", level=2)
doc.add_paragraph(
    "Target 4.4: Increase technical and vocational skills for employment, decent jobs, and entrepreneurship.\n"
    "• Outcome: 4 learning tracks with 40+ micro-lessons covering financial literacy, "
    "business management, and investment fundamentals.\n"
    "• Metric: Course completion rate ≥ 30%; quiz pass rate ≥ 70%.\n"
    "• Target: 2,000+ course completions in Year 1."
)

add_heading_styled("SDG 8: Decent Work and Economic Growth", level=2)
doc.add_paragraph(
    "Target 8.3: Promote development-oriented policies that support productive activities, "
    "decent job creation, entrepreneurship, creativity, and innovation.\n"
    "• Outcome: 500+ SMEs and freelancers using productivity tools and business plan generator.\n"
    "• Metric: Number of business plans generated; SME task completion rates.\n"
    "• Target: 1,000+ business plans generated in Year 1; 60% rated as 'bank-ready' by users."
)

add_heading_styled("SDG 9: Industry, Innovation and Infrastructure", level=2)
doc.add_paragraph(
    "Target 9.C: Significantly increase access to information and communications technology.\n"
    "• Outcome: Mobile-first platform functioning reliably on 3G networks with < 30MB APK size.\n"
    "• Metric: Offline functionality for 72h; page load < 2s on 3G.\n"
    "• Target: < 1% crash rate; 99.5% uptime."
)

add_heading_styled("SDG 10: Reduced Inequalities", level=2)
doc.add_paragraph(
    "Target 10.2: Empower and promote the social, economic, and political inclusion of all.\n"
    "• Outcome: Serving low-tech-comfort users (Persona 4: Mr. Eze) alongside digital natives.\n"
    "• Metric: NPS stratified by persona type; accessibility compliance (WCAG 2.1 AA).\n"
    "• Target: NPS > 40 across ALL persona segments; zero accessibility P0 bugs."
)

# ═══════════════════════════════════════════════
# 9. PROJECT CONTRIBUTION TO REAL-WORLD IMPACT
# ═══════════════════════════════════════════════
add_heading_styled("9. Project Contribution to Real-World Impact", level=1)

impacts = [
    ("Democratizing Financial Intelligence: ",
     "By making personalized financial advice accessible to anyone with a smartphone, "
     "EcoFinwize bridges the gap between the wealthy (who can afford human advisors) and "
     "the underserved. This is not just a convenience — it is a pathway out of poverty. "
     "A freelancer who learns to budget adaptively and save consistently is less likely "
     "to fall into debt cycles. An SME owner with a professional business plan can access "
     "bank loans and grow their enterprise, creating jobs."),
    ("Scaling Human Expertise with AI: ",
     "Africa has fewer than 1 financial advisor per 100,000 people. Finwize's AI advisor "
     "and business mentor provide scalable, 24/7 access to guidance that approximates "
     "human expertise — without the cost or availability constraints. The RAG knowledge base "
     "ensures this guidance is grounded in verified, local-context sources."),
    ("Breaking the Intergenerational Cycle: ",
     "Financial literacy is rarely taught in African schools or homes. By embedding "
     "financial education into a daily-use tool (not a separate course platform), Finwize "
     "makes learning a habit. A student who learns about compound interest at 20 will make "
     "fundamentally different life decisions than one who discovers it at 40."),
    ("Building Trust in Digital Finance: ",
     "By prioritizing transparency — source citations, clear disclaimers, user rating of "
     "AI responses, and a report inappropriate content mechanism — Finwize tackles the "
     "trust deficit head-on. Every AI answer is auditable. Every recommendation is "
     "explainable. This sets a new standard for responsible AI in fintech."),
    ("Catalyzing the Gig and SME Economy: ",
     "Freelancers and micro-SMEs represent the fastest-growing employment segment in Africa. "
     "EcoFinwize's productivity tools, invoice generation, and business mentorship help "
     "formalize and professionalize this sector, enabling tax compliance, access to credit, "
     "and sustainable business growth."),
]
for bold, normal in impacts:
    add_bullet(normal, bold_prefix=bold)

# ═══════════════════════════════════════════════
# 10. PROJECT PLAN, METHODOLOGY & DATA SOURCES
# ═══════════════════════════════════════════════
add_heading_styled("10. Project Plan, Methodology & Data Sources", level=1)

add_heading_styled("10.1 Development Methodology", level=2)
doc.add_paragraph(
    "EcoFinwize will be built using an Agile (Scrum) methodology with 2-week sprint cycles. "
    "Each sprint includes planning, development, code review, testing, and a demo. The "
    "product backlog is organized by feature epic (see PRD) with MoSCoW prioritization. "
    "CI/CD via GitHub Actions ensures automated testing and deployment on every push to main."
)

add_heading_styled("10.2 Phased Implementation Plan", level=2)

doc.add_paragraph()

# Create a table for the timeline
table = doc.add_table(rows=8, cols=4)
table.style = 'Light Shading Accent 1'

# Header
for i, header in enumerate(["Phase", "Timeline", "Key Deliverables", "Milestone"]):
    cell = table.rows[0].cells[i]
    cell.text = header
    cell.paragraphs[0].runs[0].bold = True if cell.paragraphs[0].runs else False

phases = [
    ("Phase 0: Foundation", "Month 1", 
     "Project scaffolding, Docker setup, CI/CD pipeline, database schema (Alembic migrations), "
     "JWT + Google OAuth, user profile API",
     "Green CI pipeline running"),
    ("Phase 1: Core Finance", "Month 2-3",
     "Budget CRUD, transaction tracking, expense categorization, adaptive budget algorithm, "
     "savings goals, financial summary APIs",
     "User can add income/expenses and see spending charts"),
    ("Phase 2: AI Advisor MVP", "Month 3-4",
     "LLM integration (GPT-4o-mini), conversation management, SSE streaming, context assembly, "
     "PII filter, safety guardrails, response rating system",
     "AI responds to financial questions with user context"),
    ("Phase 3: Content & Learning", "Month 4-5",
     "Course/lesson CRUD (MongoDB), quiz engine, progress tracking, badge system, "
     "investment articles, bookmarking",
     "User can complete a course and earn a badge"),
    ("Phase 4: Business Tools", "Month 5-6",
     "Business plan generator, SME task manager, AI business mentor, invoice generation",
     "SME can generate a bank-ready business plan"),
    ("Phase 5: Intelligence Layer", "Month 6-7",
     "RAG knowledge base (Pinecone vector index), document upload/management, news aggregation, "
     "hybrid recommendation engine, personalized daily tips",
     "AI answers grounded in verified local documents"),
    ("Phase 6: Admin & Polish", "Month 7-8",
     "Admin dashboard, analytics/reporting, notification system, user management, "
     "load testing, accessibility audit, beta release preparation",
     "Platform ready for closed beta"),
]

for i, (phase, timeline, deliverables, milestone) in enumerate(phases):
    table.rows[i + 1].cells[0].text = phase
    table.rows[i + 1].cells[1].text = timeline
    table.rows[i + 1].cells[2].text = deliverables
    table.rows[i + 1].cells[3].text = milestone

doc.add_paragraph()

add_heading_styled("10.3 Pilot & Rollout", level=2)
doc.add_paragraph(
    "Months 8-9: Closed beta with 50 users across all 5 persona groups. Bug fixes and UX "
    "refinement based on Sentry crash reports and LogRocket session replays.\n"
    "Month 10: Open beta — invite-only public access with referral system. Scale monitoring.\n"
    "Months 11-12: Public launch. Marketing campaign targeting freelancer communities "
    "(Twitter/X, LinkedIn, WhatsApp groups), university partnerships, and SME networks."
)

add_heading_styled("10.4 Data Sources", level=2)
data_sources = [
    ("User-Generated Data (Primary): ", "Transactions, budgets, savings goals, task lists, "
     "and AI conversation history provided directly by users through the app interface."),
    ("Curated RAG Knowledge Base: ", "Public-domain financial regulations (Nigeria SEC, "
     "Kenya CMA, South Africa FSCA), tax codes (FIRS Nigeria, KRA Kenya), central bank "
     "policy documents, SME business guides, and vetted investment education content "
     "from authoritative sources."),
    ("News Aggregation: ", "RSS feeds from major African financial news outlets "
     "(Nairametrics, BusinessDay, TechCabal, Ventures Africa, Bloomberg Africa), "
     "supplemented by selected global financial news APIs."),
    ("AI Training & Evaluation Data: ", "Anonymized conversation logs (12-month retention) "
     "used to fine-tune system prompts, improve RAG retrieval, and train safety guardrails. "
     "No PII is used for training."),
    ("Market/Reference Data: ", "Public benchmark data for financial product comparisons "
     "(interest rates, inflation, exchange rates) from central bank APIs."),
]
for bold, normal in data_sources:
    add_bullet(normal, bold_prefix=bold)

add_heading_styled("10.5 AI Evaluation Methodology", level=2)
doc.add_paragraph(
    "AI response quality is evaluated using a four-layer framework:\n"
    "1. Automated Safety Checks: PII filter, harmful content detection, financial advice "
    "guardrails (no stock tips, no unlicensed recommendations).\n"
    "2. User Ratings: Each AI response is rateable (1-5 stars). Responses with < 3 stars "
    "trigger human review.\n"
    "3. RAG Relevance Scoring: Cosine similarity between query and retrieved chunks must "
    "exceed 0.75 threshold; below-threshold queries return 'I don't have enough information.'\n"
    "4. Periodic Human Evaluation: 100 random conversations per month evaluated by financial "
    "literacy experts for accuracy, helpfulness, and safety."
)

# ═══════════════════════════════════════════════
# 11. EXPERTS & COLLABORATORS
# ═══════════════════════════════════════════════
add_heading_styled("11. Experts & Collaborators", level=1)

doc.add_paragraph(
    "To ensure feasibility, originality, and responsible AI deployment, Finwize seeks "
    "consultation and collaboration with experts in the following domains:"
)

add_heading_styled("11.1 AI & Machine Learning", level=2)
ai_experts = [
    "LLM Safety & Alignment Researcher — To audit system prompts, guardrails, and "
    "red-team the AI advisor against harmful financial advice scenarios.",
    "NLP / RAG Engineer — To optimize chunking strategy, embedding model selection, "
    "and Pinecone index configuration for low-latency retrieval.",
    "Recommendation Systems Specialist — To design and validate the hybrid "
    "recommendation engine (collaborative filtering + LLM scoring).",
]
for e in ai_experts:
    add_bullet(e)

add_heading_styled("11.2 Fintech & Financial Services", level=2)
fintech_experts = [
    "Certified Financial Advisor (CFA or equivalent) — To validate AI responses for "
    "regulatory compliance and financial accuracy; to serve as ground-truth for RAG content.",
    "Fintech Regulatory Compliance Expert — To ensure compliance with Nigeria SEC, "
    "Kenya CMA, and other African market regulations on digital financial advice.",
    "Banking / Mobile Money API Specialist — To advise on future integration with "
    "Open Banking APIs, mobile money (M-Pesa, MoMo), and payment gateways.",
]
for e in fintech_experts:
    add_bullet(e)

add_heading_styled("11.3 Business & Innovation Scaling", level=2)
biz_experts = [
    "Product-Led Growth (PLG) Strategist — To design viral loops, referral mechanics, "
    "and freemium-to-premium conversion for sustainable user acquisition.",
    "Africa-Focused Venture Advisor — To guide go-to-market strategy, partnership "
    "development (telcos, universities, SME associations), and fundraising.",
    "UX Researcher (African Markets) — To conduct usability testing across diverse "
    "user demographics and validate the mobile-first, low-literacy-friendly design.",
]
for e in biz_experts:
    add_bullet(e)

add_heading_styled("11.4 Technical Advisory", level=2)
tech_experts = [
    "Cloud Infrastructure Engineer — To optimize Render/Railway deployment, monitoring "
    "(Sentry + Prometheus), and cost management as the platform scales.",
    "Flutter / Mobile Performance Expert — To ensure APK < 30MB, offline sync reliability, "
    "and smooth performance on budget Android devices (2GB RAM target).",
]
for e in tech_experts:
    add_bullet(e)

# ═══════════════════════════════════════════════
# 12. SUSTAINABILITY & REVENUE MODEL
# ═══════════════════════════════════════════════
add_heading_styled("12. Sustainability & Revenue Model", level=1)

doc.add_paragraph(
    "EcoFinwize is designed for long-term financial sustainability through a multi-tier "
    "freemium model, ensuring the core mission (financial inclusion) is never paywalled:"
)

revenue = [
    ("Free Tier (Freemium — 80% of users): ", "AI Financial Advisor (up to 30 conversations/month), "
     "budget & expense tracking (up to 50 transactions/month), 1 savings goal, 1 learning track, "
     "news aggregation, and basic AI daily tips. Supported by the lean cost structure ($0.05 per "
     "AI conversation)."),
    ("Pro Tier ($4.99/month or $49/year): ", "Unlimited AI conversations, unlimited transactions, "
     "unlimited savings goals, all 4 learning tracks with certificates, business plan generator, "
     "SME task manager, priority AI response speed, and CSV export."),
    ("Business Tier ($19.99/month): ", "Everything in Pro + team accounts (up to 10 users), "
     "invoice generation, inventory tracking, multi-currency support (future), dedicated "
     "AI business mentor session priority, and admin analytics dashboard."),
    ("Institutional Partnerships: ", "Universities, NGOs, and government agencies can license "
     "EcoFinwize for their constituents at negotiated rates, with custom branding and reporting."),
]
for bold, normal in revenue:
    add_bullet(normal, bold_prefix=bold)

doc.add_paragraph(
    "Cost projections show Finwize reaching breakeven at approximately 3,000 paying users "
    "(Pro + Business tiers combined), which represents < 5% conversion of the 10,000 MAU target. "
    "The lean infrastructure cost ($168/mo) and efficient AI API usage ($62/mo at 1K MAU) ensure "
    "the free tier can be sustained indefinitely through cross-subsidization from premium tiers "
    "and institutional partnerships."
)

# ═══════════════════════════════════════════════
# 13. ABSTRACT / EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════
add_heading_styled("10. Abstract / Executive Summary", level=1)

doc.add_paragraph(
    "EcoFinwize is an AI-powered, mobile-first financial and business guidance platform designed "
    "to serve the 200+ million African youths, freelancers, SME owners, students, and public "
    "service workers who are underserved by existing financial tools. The platform addresses "
    "a critical gap: while mobile money and banking access have expanded dramatically across "
    "Africa, the knowledge, tools, and trust needed to make sound financial decisions have not "
    "kept pace."
)
doc.add_paragraph(
    "EcoFinwize's core innovation is its conversational AI Financial Advisor and Business Mentor — "
    "powered by large language models (GPT-4o-mini, Claude Haiku) and grounded by a "
    "Retrieval-Augmented Generation (RAG) knowledge base. Unlike traditional fintech dashboards "
    "that assume stable salary income and present complex charts, Finwize engages users in "
    "natural-language conversations, understands their unique financial context (persona, income "
    "pattern, goals, risk tolerance), and delivers personalized, actionable guidance with "
    "verifiable citations."
)
doc.add_paragraph(
    "The platform introduces an adaptive budgeting system purpose-built for irregular-income "
    "users — using percentage-based limits that adjust proportionally to actual earnings, rather "
    "than fixed monthly caps that fail freelancers and seasonal business owners. A hybrid "
    "recommendation engine (rule-based + collaborative filtering + LLM scoring) surfaces the "
    "right courses, articles, and actions at the right time."
)
doc.add_paragraph(
    "EcoFinwize is built as a modular monolith (FastAPI + SQLAlchemy async + PostgreSQL + MongoDB + "
    "Pinecone), deployed as three surfaces: a React web app for deep work, a Flutter Android "
    "APK for daily mobile use, and a shared RESTful API. The platform is Dockerized, "
    "CI/CD-enabled via GitHub Actions, and designed to be microservice-ready for future scaling."
)
doc.add_paragraph(
    "Over a 12-month pilot, Finwize targets 10,000 active users, 2,000+ course completions, "
    "1,000+ business plans generated, and a Net Promoter Score above 40. The project directly "
    "contributes to SDGs 1 (No Poverty), 4 (Quality Education), 8 (Decent Work), 9 (Innovation), "
    "and 10 (Reduced Inequalities), with measurable outcomes in savings behavior, learning "
    "completion, and business formalization."
)
doc.add_paragraph(
    "With a lean monthly operating budget of approximately $230 (at 1,000 MAU) and a "
    "technology stack that maximizes open-source tools and free tiers, Finwize is designed "
    "for sustainability, scalability, and real-world impact from day one."
)

# ── Footer note ──
doc.add_paragraph()
doc.add_paragraph("_" * 80)
footer = doc.add_paragraph()
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = footer.add_run("— End of Proposal —")
run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
run.font.size = Pt(10)
run.italic = True

# ═══════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════
output_path = "Finwize/docs/ECOFINWIZE_PROPOSAL_NEW.docx"
doc.save(output_path)
print(f"✅ Proposal saved to: {output_path}")
