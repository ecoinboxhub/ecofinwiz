"""EcoFinwize — Database seed script.
Creates demo user with sample data across all modules.
Run: python -m app.scripts.seed
"""
import asyncio
import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.database.postgres import async_session_factory
from app.models import (
    Article, BlogPost, Budget, Category, Course, ForumTopic, Invoice, NewsArticle, Notification,
    SavingsContribution, SavingsGoal, Task, Transaction, User, UserPreference,
)

DEMO_EMAIL = "demo@finwize.com"
DEMO_PASSWORD = "Demo@123"
DEMO_USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")

NOW = datetime.now(timezone.utc)
TODAY = date.today()


async def clear_data(session: AsyncSession):
    """Remove existing demo data idempotently."""
    for table in [BlogPost, ForumTopic, Notification, Invoice, Task, SavingsContribution, SavingsGoal, Transaction, Budget, Category, Course, Article, NewsArticle, UserPreference, User]:
        await session.execute(delete(table))
    await session.commit()


async def seed_user(session: AsyncSession) -> User:
    user = User(
        id=DEMO_USER_ID,
        email=DEMO_EMAIL,
        password_hash=hash_password(DEMO_PASSWORD),
        full_name="Demo User",
        persona_type="freelancer",
        onboarding_completed=True,
        is_admin=True,
    )
    session.add(user)
    prefs = UserPreference(user_id=user.id)
    session.add(prefs)
    await session.commit()
    print(f"    + User: {DEMO_EMAIL} / {DEMO_PASSWORD}")
    return user


async def seed_categories(session: AsyncSession) -> dict[str, Category]:
    cats = {}
    for name, typ in [
        ("Salary", "income"), ("Freelance", "income"), ("Business", "income"),
        ("Investments", "income"), ("Food & Drinks", "expense"),
        ("Transport", "expense"), ("Rent", "expense"), ("Utilities", "expense"),
        ("Shopping", "expense"), ("Healthcare", "expense"), ("Entertainment", "expense"),
        ("Education", "expense"), ("Business Supplies", "expense"),
        ("Savings", "expense"), ("Miscellaneous", "expense"),
    ]:
        cat = Category(user_id=DEMO_USER_ID, name=name, type=typ)
        session.add(cat)
        cats[name] = cat
    await session.commit()
    print(f"  + {len(cats)} categories")
    return cats


async def seed_budgets(session: AsyncSession, cats: dict[str, Category]):
    budgets_data = [
        ("Monthly Living", "Food & Drinks", 200_000),
        ("Transport", "Transport", 100_000),
        ("Rent", "Rent", 350_000),
        ("Business Ops", "Business Supplies", 150_000),
        ("Learning", "Education", 80_000),
    ]
    budgets = []
    for name, cat, limit in budgets_data:
        b = Budget(
            user_id=DEMO_USER_ID, name=name, category=cat,
            monthly_limit=limit, start_date=TODAY.replace(day=1),
        )
        session.add(b)
        budgets.append(b)
    await session.commit()
    print(f"    + {len(budgets)} budgets")


async def seed_transactions(session: AsyncSession, cats: dict[str, Category]):
    txns_data = [
        ("income", 1_200_000, "Salary", "Monthly salary - May 2026", TODAY - timedelta(days=5)),
        ("income", 450_000, "Freelance", "Website redesign project", TODAY - timedelta(days=3)),
        ("income", 85_000, "Investments", "Dividend payment", TODAY - timedelta(days=10)),
        ("expense", 45_000, "Food & Drinks", "Weekly groceries", TODAY - timedelta(days=2)),
        ("expense", 12_000, "Transport", "Fuel top-up", TODAY - timedelta(days=1)),
        ("expense", 350_000, "Rent", "June rent payment", TODAY),
        ("expense", 25_000, "Utilities", "Electricity bill", TODAY - timedelta(days=4)),
        ("expense", 65_000, "Shopping", "New work clothes", TODAY - timedelta(days=6)),
        ("expense", 15_000, "Entertainment", "Movie night", TODAY - timedelta(days=7)),
        ("expense", 30_000, "Education", "Online course subscription", TODAY - timedelta(days=8)),
        ("expense", 55_000, "Business Supplies", "Office stationery", TODAY - timedelta(days=9)),
        ("expense", 8_000, "Healthcare", "Pharmacy", TODAY - timedelta(days=11)),
        ("expense", 20_000, "Miscellaneous", "Mobile data", TODAY - timedelta(days=12)),
        ("income", 300_000, "Business", "Consulting fee", TODAY - timedelta(days=14)),
        ("expense", 50_000, "Business Supplies", "Software subscription", TODAY - timedelta(days=13)),
    ]
    for typ, amount, cat, desc, dt in txns_data:
        txn = Transaction(
            user_id=DEMO_USER_ID, type=typ, amount=amount,
            category=cat, description=desc, transaction_date=dt,
        )
        session.add(txn)
    await session.commit()
    print(f"    + {len(txns_data)} transactions")


async def seed_savings(session: AsyncSession):
    goals_data = [
        ("Emergency Fund", 2_000_000, 450_000, date(2026, 12, 31)),
        ("New Laptop", 800_000, 320_000, date(2026, 9, 30)),
        ("Business Startup", 5_000_000, 500_000, date(2027, 6, 30)),
    ]
    for name, target, current, target_date in goals_data:
        goal = SavingsGoal(
            user_id=DEMO_USER_ID, name=name, target_amount=target,
            current_amount=current, target_date=target_date,
        )
        session.add(goal)
        await session.flush()
        contrib = SavingsContribution(goal_id=goal.id, amount=current, note="Initial seed contribution")
        session.add(contrib)
    await session.commit()
    print(f"    + {len(goals_data)} savings goals with contributions")


async def seed_tasks(session: AsyncSession):
    tasks_data = [
        ("File quarterly tax returns", "Complete VAT and income tax filings for Q2", "high", "pending", TODAY + timedelta(days=14)),
        ("Review business insurance", "Compare renewal quotes from 3 providers", "medium", "in_progress", TODAY + timedelta(days=7)),
        ("Update client contracts", "Add new payment terms to standard contract", "medium", "pending", TODAY + timedelta(days=21)),
        ("Prepare monthly financial report", "Compile June income, expenses, and projections", "high", "in_progress", TODAY + timedelta(days=3)),
        ("Team standup meeting", "Weekly sync with freelance collaborators", "low", "completed", TODAY - timedelta(days=1)),
    ]
    for title, desc, priority, status, due in tasks_data:
        task = Task(user_id=DEMO_USER_ID, title=title, description=desc, priority=priority, status=status, due_date=due)
        session.add(task)
    await session.commit()
    print(f"    + {len(tasks_data)} tasks")


async def seed_invoices(session: AsyncSession):
    invoices_data = [
        ("INV-001", "TechCorp Ltd", "techcorp@example.com", [{"description": "UI/UX Design", "quantity": 40, "unit_price": 45000}], "paid"),
        ("INV-002", "GreenLeaf Agro", "info@greenleaf.ng", [{"description": "Brand Identity Package", "quantity": 1, "unit_price": 650000}], "sent"),
        ("INV-003", "EduPrime Schools", "accounts@eduprime.edu", [{"description": "Website Maintenance (Jun)", "quantity": 1, "unit_price": 120000}], "draft"),
    ]
    for num, client, email, items, status in invoices_data:
        subtotal = sum(i["quantity"] * i["unit_price"] for i in items)
        tax = subtotal * 0.075
        total = subtotal + tax
        inv = Invoice(
            user_id=DEMO_USER_ID, number=num, client_name=client,
            client_email=email, items=items, subtotal=subtotal,
            tax_rate=7.5, tax_amount=tax, total=total, status=status,
            due_date=TODAY + timedelta(days=30),
            paid_at=NOW if status == "paid" else None,
        )
        session.add(inv)
    await session.commit()
    print(f"    + {len(invoices_data)} invoices")


async def seed_forum_topics(session: AsyncSession):
    topics_data = [
        ("Best budgeting strategies for freelancers with irregular income?", "I've been freelancing for 2 years and still struggle with budgeting when income varies month to month. Any tips?", "Finance"),
        ("How to calculate your hourly rate as a creative professional?", "I keep undercharging. What formula do you use to determine your rate?", "Business"),
        ("Recommended books for financial literacy?", "Looking for beginner-friendly books on personal finance and investing.", "Learning"),
        ("Naira devaluation - how are you protecting your savings?", "With the Naira volatility, what strategies are you using to preserve value?", "Investing"),
    ]
    for title, content, category in topics_data:
        topic = ForumTopic(
            user_id=DEMO_USER_ID, title=title, content=content,
            category=category, view_count=42,
        )
        session.add(topic)
    await session.commit()
    print(f"    + {len(topics_data)} forum topics")


async def seed_notifications(session: AsyncSession):
    notifications_data = [
        ("Budget Alert", "You've used 85% of your Food & Drinks budget this month", "budget_alert"),
        ("Goal Milestone", "Congratulations! You're 40% toward your Emergency Fund goal", "goal_milestone"),
        ("New Course Available", "Advanced Investment Strategies course is now available", "content_update"),
        ("Daily Tip", "Try the 50/30/20 rule: 50% needs, 30% wants, 20% savings", "daily_tip"),
    ]
    for title, body, typ in notifications_data:
        notif = Notification(user_id=DEMO_USER_ID, title=title, body=body, type=typ)
        session.add(notif)
    await session.commit()
    print(f"    + {len(notifications_data)} notifications")


async def seed_content_pg(session: AsyncSession):
    """Seed PostgreSQL with sample courses, articles, and news."""
    from sqlalchemy import select

    # Courses
    existing = await session.execute(select(Course).limit(1))
    if not existing.scalar_one_or_none():
        courses = [
            Course(
                title="Financial Literacy for Beginners",
                description="Master the basics of personal finance in 7 short lessons. Learn budgeting, saving, investing, and more.",
                category="personal_finance",
                difficulty="beginner",
                duration_hours=12,
                is_published=True,
            ),
            Course(
                title="Smart Investing for African Markets",
                description="Learn how to invest in stocks, bonds, treasury bills, and real estate across African markets.",
                category="investing",
                difficulty="intermediate",
                duration_hours=18,
                is_published=True,
            ),
            Course(
                title="Starting and Growing Your Small Business",
                description="From business registration to scaling operations - everything you need to succeed as an entrepreneur.",
                category="business",
                difficulty="beginner",
                duration_hours=24,
                is_published=True,
            ),
        ]
        for c in courses:
            session.add(c)
        print(f"    + PostgreSQL: {len(courses)} courses seeded")

    # Articles
    existing = await session.execute(select(Article).limit(1))
    if not existing.scalar_one_or_none():
        article_data = [
            ("Understanding Compound Interest", "understanding-compound-interest", "How compound interest works and why starting early matters most.", "Compound interest is the eighth wonder of the world. When you earn interest on both your principal AND your accumulated interest, your money grows exponentially over time. The key is starting early - even small amounts can grow significantly over decades.", "investing", 5, True),
            ("A Beginner's Guide to the Nigerian Stock Exchange", "guide-nigerian-stock-exchange", "Everything you need to know to start investing in the NSE.", "The Nigerian Stock Exchange offers opportunities for both new and experienced investors. This guide covers account setup, trading platforms, key indices, and strategies for building a diversified portfolio.", "stocks", 8, True),
            ("Real Estate Investing on a Budget", "real-estate-investing-budget", "How to get started in real estate without millions in capital.", "You don't need millions to invest in real estate. REITs, real estate crowdfunding, and cooperative ownership models make property investment accessible.", "real_estate", 6, False),
            ("Understanding Inflation and Your Purchasing Power", "understanding-inflation", "What inflation means for your savings and how to protect your money.", "Inflation erodes purchasing power over time. If your savings earn 3% but inflation is 15%, you're actually losing value. Protect your wealth through inflation-beating investments.", "economy", 4, False),
            ("Building an Emergency Fund: A Step-by-Step Guide", "building-emergency-fund", "Why you need 3-6 months of expenses saved and how to get there.", "An emergency fund is your financial safety net. Aim for 3-6 months of essential expenses in a readily accessible account. Start small and automate your savings.", "savings", 5, True),
            ("Tax Planning for Freelancers and Small Business Owners", "tax-planning-freelancers", "Smart tax strategies to keep more of your hard-earned money.", "As a freelancer or small business owner, understanding your tax obligations is crucial. This guide covers deductible expenses, quarterly estimated taxes, and more.", "tax", 7, False),
            ("Diversification: Don't Put All Your Eggs in One Basket", "diversification-guide", "Why spreading your investments across asset classes reduces risk.", "Diversification is the most important principle in investing. Spread your money across different asset classes, sectors, and geographies.", "investing", 4, False),
            ("How to Negotiate Your Salary Like a Pro", "salary-negotiation-guide", "Practical tips for getting the compensation you deserve.", "Salary negotiation can dramatically impact your lifetime earnings. Research market rates, quantify your value, practice your pitch.", "career", 6, True),
        ]
        articles = [
            Article(title=t, slug=s, summary=su, content=c, category=cat, read_time_minutes=rt, is_featured=f, author="EcoFinwize Team", is_published=True)
            for t, s, su, c, cat, rt, f in article_data
        ]
        for a in articles:
            session.add(a)
        print(f"    + PostgreSQL: {len(articles)} articles seeded")

    # News
    existing = await session.execute(select(NewsArticle).limit(1))
    if not existing.scalar_one_or_none():
        news_data = [
            ("CBN Holds Monetary Policy Rate at 27.50%", "cbn-rate-2026", "The Central Bank of Nigeria maintains interest rate amid inflation concerns.", "The Central Bank of Nigeria has voted to hold the monetary policy rate at 27.50% as it continues to balance inflation control with economic growth.", "Financial Times", "economy"),
            ("African Tech Startups Raise $1.2B in Q2 2026", "african-tech-q2-2026", "Fintech dominates with 45% of total funding across the continent.", "African tech startups raised $1.2 billion in Q2 2026, with fintech accounting for 45% of total funding.", "TechCrunch", "tech"),
            ("Kenya's Mobile Money Transactions Hit Record High", "kenya-mobile-money-record", "M-Pesa processes over $50B in Q2.", "Kenya's mobile money platforms processed over $50 billion in transactions during Q2 2026, setting a new record.", "Business Daily Africa", "fintech"),
            ("Nigeria's SMEs to Benefit from New $200M World Bank Loan", "nigeria-sme-loan-2026", "Funds aimed at improving access to finance for small businesses.", "The World Bank has approved a $200 million loan to Nigeria to improve access to finance for SMEs.", "Reuters", "business"),
            ("Ghana Pension Funds Invest in Treasury Bills", "ghana-pension-tbills", "Fund managers increase allocation to government securities.", "Ghana's pension fund managers have increased allocation to treasury bills, seeking safe-haven returns.", "Bloomberg", "financial"),
            ("AfCFTA Trade Volume Reaches $25B Milestone", "afcfta-milestone-2026", "Continental free trade area surpasses key milestone in intra-African trade.", "Trade under the African Continental Free Trade Area has reached $25 billion, surpassing initial projections.", "African Business", "business"),
            ("South Africa Launches Digital Identity Pilot", "sa-digital-id-pilot", "Biometric digital IDs to expand financial inclusion.", "South Africa has launched a pilot program for biometric digital identities to expand financial inclusion.", "TechCentral", "tech"),
            ("Egypt's Fintech Sector Grows 35% Year-on-Year", "egypt-fintech-growth", "Regulatory reforms drive fintech innovation in North Africa.", "Egypt's fintech sector has grown 35% year-on-year, driven by regulatory reforms and increasing smartphone penetration.", "Financial Times", "fintech"),
        ]
        news = [
            NewsArticle(title=t, slug=s, summary=su, content=c, source=src, category=cat, is_published=True)
            for t, s, su, c, src, cat in news_data
        ]
        for n in news:
            session.add(n)
        print(f"    + PostgreSQL: {len(news)} news items seeded")

    # Blog posts
    existing = await session.execute(select(BlogPost).limit(1))
    if not existing.scalar_one_or_none():
        blog_data = [
            ("My Journey to Financial Freedom", "financial-freedom-journey", "One freelancer's story of going from paycheck to paycheck to building wealth.", "Two years ago, I was struggling as a freelance designer. Today, I have a 6-month emergency fund, a growing portfolio, and a clear roadmap.", "Guest Contributor", "personal_finance"),
            ("5 Budgeting Apps That Actually Work for Africans", "budgeting-apps-africa", "A review of popular budgeting tools for Nigeria and Africa.", "We tested 5 popular budgeting apps and ranked them based on currency support, offline capability, and local relevance.", "EcoFinwize Team", "technology"),
            ("Understanding the New Pension Reform Act", "pension-reform-2026", "What the 2026 pension reforms mean for Nigerian workers.", "The Pension Reform Act 2026 introduces higher contribution rates and expanded coverage for informal sector workers.", "Legal Contributor", "finance"),
        ]
        posts = [
            BlogPost(title=t, slug=s, summary=su, content=c, author=a, category=cat, is_published=True)
            for t, s, su, c, a, cat in blog_data
        ]
        for p in posts:
            session.add(p)
        print(f"    + PostgreSQL: {len(posts)} blog posts seeded")

    await session.commit()


async def main():
    print("\n EcoFinwize — Seeding database...\n")

    async with async_session_factory() as session:
        await clear_data(session)
        user = await seed_user(session)
        cats = await seed_categories(session)
        await seed_budgets(session, cats)
        await seed_transactions(session, cats)
        await seed_savings(session)
        await seed_tasks(session)
        await seed_invoices(session)
        await seed_forum_topics(session)
        await seed_notifications(session)
        await seed_content_pg(session)

    print(f"""
  + Seeding complete!
   ─────────────────────────────────
   Login:  {DEMO_EMAIL}
   Pass:   {DEMO_PASSWORD}
   ─────────────────────────────────
   User:   1 (admin + freelancer persona)
   Categories: 15 (10 expense, 5 income)
   Budgets: 5
   Transactions: 15 (income + expense)
   Savings Goals: 3 (with contributions)
   Tasks: 5
   Invoices: 3
    Forum Topics: 4
    Notifications: 4
    Content (PG): 3 courses, 8 articles, 3 blog posts, 8 news items
""")


if __name__ == "__main__":
    asyncio.run(main())
