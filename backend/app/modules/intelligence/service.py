import hashlib
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlalchemy import select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    User, Document, Bookmark, UserLesson, UserPreference,
    BadgeRule, UserBadge, Notification, Article, Course,
)
from app.modules.intelligence.rag import (
    index_document as rag_index,
    remove_document as rag_remove,
    query_knowledge_base,
    answer_with_rag,
    get_index_stats,
)
from app.modules.intelligence.schemas import (
    DocumentResponse, DocumentUpdate,
    RAGQuery, RAGResult, RAGQueryResponse, RAGIndexResponse,
    Recommendation, RecommendationList, DailyTip,
)
from app.shared.logger import get_logger

logger = get_logger(__name__)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")


# =====================================================================
# DOCUMENTS
# =====================================================================

async def _ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


async def upload_document(
    file: UploadFile,
    user_id: UUID,
    category: str = "general",
    tags: Optional[list[str]] = None,
    db: AsyncSession = None,
) -> Document:
    await _ensure_upload_dir()

    content = await file.read()
    size_bytes = len(content)
    filename = f"{uuid.uuid4()}-{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    content_type = file.content_type or "application/octet-stream"
    storage_path = filepath

    doc = Document(
        user_id=user_id,
        filename=filename,
        original_filename=file.filename or "unknown",
        content_type=content_type,
        size_bytes=size_bytes,
        storage_path=storage_path,
        category=category,
        tags={"tags": tags} if tags else None,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    try:
        text = content.decode("utf-8", errors="ignore")
        if len(text) > 50:
            meta = {"user_id": str(user_id), "category": category, "source": file.filename}
            chunk_count = await rag_index(str(doc.id), text, meta)
            if chunk_count > 0:
                doc.is_indexed = True
                await db.commit()
    except Exception as e:
        logger.warning("Document upload: RAG indexing skipped: %s", e)

    return doc


async def list_documents(
    user_id: UUID,
    db: AsyncSession,
    category: Optional[str] = None,
) -> list[Document]:
    query = select(Document).where(Document.user_id == user_id)
    if category:
        query = query.where(Document.category == category)
    result = await db.execute(query.order_by(Document.created_at.desc()))
    return list(result.scalars().all())


async def get_document(doc_id: UUID, user_id: UUID, db: AsyncSession) -> Document:
    result = await db.execute(
        select(Document).where(and_(Document.id == doc_id, Document.user_id == user_id))
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


async def update_document(doc_id: UUID, data: DocumentUpdate, user_id: UUID, db: AsyncSession) -> Document:
    doc = await get_document(doc_id, user_id, db)
    updates = data.model_dump(exclude_unset=True)
    if "tags" in updates:
        updates["tags"] = {"tags": updates["tags"]} if updates["tags"] else None
    for key, val in updates.items():
        if val is not None:
            setattr(doc, key, val)
    await db.commit()
    await db.refresh(doc)
    return doc


async def delete_document(doc_id: UUID, user_id: UUID, db: AsyncSession) -> bool:
    doc = await get_document(doc_id, user_id, db)
    try:
        if os.path.exists(doc.storage_path):
            os.remove(doc.storage_path)
    except Exception as e:
        logger.warning("Failed to delete file: %s", e)
    await rag_remove(str(doc.id))
    await db.delete(doc)
    await db.commit()
    return True


async def get_document_file(doc_id: UUID, user_id: UUID, db: AsyncSession) -> tuple[str, str, str]:
    doc = await get_document(doc_id, user_id, db)
    if not os.path.exists(doc.storage_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    return doc.storage_path, doc.original_filename, doc.content_type


# =====================================================================
# RECOMMENDATIONS
# =====================================================================

async def get_recommendations(
    user_id: UUID,
    db: AsyncSession,
) -> RecommendationList:
    items = []

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    persona = user.persona_type if user and user.persona_type else "student"

    bookmarked = await db.execute(
        select(Bookmark.content_id).where(
            and_(Bookmark.user_id == user_id, Bookmark.content_type == "article")
        )
    )
    bookmarked_ids = [row[0] for row in bookmarked.all()]

    completed = await db.execute(
        select(UserLesson.content_id).where(
            and_(
                UserLesson.user_id == user_id,
                UserLesson.content_type == "lesson",
                UserLesson.completed.is_(True),
            )
        )
    )
    completed_ids = [row[0] for row in completed.all()]

    category_map = {
        "student": ["budgeting", "savings", "investing"],
        "freelancer": ["savings", "investing", "tax"],
        "sme_owner": ["business", "investing", "savings"],
        "professional": ["investing", "retirement", "savings"],
        "youth": ["budgeting", "savings", "side-hustle"],
    }
    preferred_cats = category_map.get(persona, ["savings"])

    articles_result = await db.execute(
        select(Article).where(
            and_(
                Article.is_published.is_(True),
                Article.category.in_(preferred_cats),
            )
        ).order_by(Article.created_at.desc()).limit(10)
    )
    articles = articles_result.scalars().all()

    for art in articles:
        aid = str(art.id)
        score = 1.0
        if aid in bookmarked_ids:
            score += 0.5
        if aid in completed_ids:
            score -= 0.3
        items.append(Recommendation(
            content_type="article",
            content_id=aid,
            title=art.title,
            summary=art.summary,
            score=score,
            reason=f"Recommended based on your {persona} profile",
        ))

    courses_result = await db.execute(
        select(Course).where(
            and_(
                Course.is_published.is_(True),
                Course.difficulty.in_(["beginner", "intermediate"]),
            )
        ).order_by(Course.created_at.desc()).limit(5)
    )
    courses = courses_result.scalars().all()

    for c in courses:
        cid = str(c.id)
        score = 0.8
        items.append(Recommendation(
            content_type="course",
            content_id=cid,
            title=c.title,
            summary=c.description,
            score=score,
            reason="Popular course for your skill level",
        ))

    items.sort(key=lambda x: x.score, reverse=True)
    return RecommendationList(items=items[:10], based_on=f"Your {persona} profile and interests")


# =====================================================================
# DAILY TIPS
# =====================================================================

FINANCIAL_TIPS = [
    {
        "title": "50/30/20 Rule",
        "content": "Allocate 50% of income to needs, 30% to wants, and 20% to savings. This simple framework helps you build wealth without strict budgeting.",
        "category": "budgeting",
    },
    {
        "title": "Emergency Fund First",
        "content": "Before investing, save 3-6 months of expenses in an emergency fund. This protects you from unexpected events and prevents high-interest debt.",
        "category": "savings",
    },
    {
        "title": "Start Small, Invest Consistently",
        "content": "You don't need a lot to start investing. Even NGN 1,000 monthly in a mutual fund or ETF grows significantly over time through compound interest.",
        "category": "investing",
    },
    {
        "title": "Track Every Expense",
        "content": "Use the EcoFinwize app to log all transactions. Awareness is the first step to financial freedom — you can't manage what you don't measure.",
        "category": "budgeting",
    },
    {
        "title": "Separate Business & Personal Finances",
        "content": "If you run an SME, maintain separate bank accounts for business and personal finances. This simplifies tax filing and gives you a clear profit picture.",
        "category": "business",
    },
    {
        "title": "Negotiate Better Rates",
        "content": "Review your subscriptions, insurance, and bank charges quarterly. A 30-minute call to negotiate could save you 10-20% annually.",
        "category": "savings",
    },
    {
        "title": "Cash Flow is King",
        "content": "For SMEs, managing cash flow is more important than profitability. Track receivables tightly and maintain a 30-day cash reserve.",
        "category": "business",
    },
    {
        "title": "Diversify Your Income",
        "content": "Relying on a single income source is risky. Explore side hustles, freelance work, or passive income streams aligned with your skills.",
        "category": "investing",
    },
    {
        "title": "Pay Yourself First",
        "content": "When you receive income, immediately transfer your savings goal to a separate account. What you don't see, you won't spend.",
        "category": "savings",
    },
    {
        "title": "Review Your Credit Report",
        "content": "In Nigeria, check your CRC Credit Bureau report annually. A good credit score opens doors to better loan terms and business opportunities.",
        "category": "credit",
    },
    {
        "title": "Set SMART Financial Goals",
        "content": "Specific, Measurable, Achievable, Relevant, Time-bound goals increase your likelihood of success by 10x. Write them down in EcoFinwize.",
        "category": "budgeting",
    },
    {
        "title": "Automate Your Savings",
        "content": "Set up automatic transfers to your savings goal on payday. Automation removes the temptation to spend and builds discipline effortlessly.",
        "category": "savings",
    },
    {
        "title": "Understand Compound Interest",
        "content": "Compound interest is the 8th wonder of the world. At 10% annual return, your investment doubles every 7.2 years. Start today.",
        "category": "investing",
    },
    {
        "title": "Invoice Promptly",
        "content": "Send invoices immediately after completing work. Use EcoFinwize's invoice tool to track payments and send reminders for overdue amounts.",
        "category": "business",
    },
    {
        "title": "Build an Emergency Budget",
        "content": "Create a bare-bones budget covering only essentials (food, rent, utilities, transport). Use this template during income disruptions.",
        "category": "budgeting",
    },
]

BUSINESS_TIPS = [
    {
        "title": "Know Your Numbers",
        "content": "Track your revenue, expenses, profit margin, and customer acquisition cost weekly. Data-driven decisions outperform gut feelings.",
        "category": "business",
    },
    {
        "title": "Validate Before You Scale",
        "content": "Test your product with 20 real customers before investing heavily. Feedback at this stage is worth millions in avoided mistakes.",
        "category": "business",
    },
    {
        "title": "Build a Digital Presence",
        "content": "60% of African consumers discover businesses online. A simple website + Instagram/TikTok presence is your cheapest marketing channel.",
        "category": "business",
    },
    {
        "title": "Network Strategically",
        "content": "Join industry associations, attend business events, and connect on LinkedIn. Your network is your net worth in African business ecosystems.",
        "category": "business",
    },
    {
        "title": "Plan for Taxes",
        "content": "Set aside 30% of all business income for taxes. Use EcoFinwize to track deductible expenses and avoid last-minute filing stress.",
        "category": "business",
    },
]


async def get_daily_tip(
    user: User,
    db: AsyncSession,
) -> DailyTip:
    tip_pool = FINANCIAL_TIPS + BUSINESS_TIPS
    digest = hashlib.md5(f"{user.id}-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}".encode())
    index = int(digest.hexdigest()[:8], 16) % len(tip_pool)
    tip = tip_pool[index]
    return DailyTip(id=str(index), action_url=None, **tip)


async def get_tips_by_category(category: str, limit: int = 5) -> list[DailyTip]:
    pool = FINANCIAL_TIPS + BUSINESS_TIPS
    filtered = [t for t in pool if t["category"] == category]
    return [DailyTip(id=str(i), action_url=None, **t) for i, t in enumerate(filtered[:limit])]


# =====================================================================
# RAG ENDPOINT
# =====================================================================

async def query_rag(data: RAGQuery) -> RAGQueryResponse:
    result = await answer_with_rag(data.query, data.top_k)
    if result:
        return RAGQueryResponse(
            query=result["query"],
            results=[RAGResult(**r) for r in result["results"]],
            answer=result.get("answer"),
        )
    return RAGQueryResponse(query=data.query, results=[], answer=None)


async def get_rag_status() -> dict:
    return await get_index_stats()
