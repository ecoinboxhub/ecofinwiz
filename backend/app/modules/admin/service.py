from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    User, Notification, Transaction, BusinessPlan, Task,
    Invoice, ForumTopic, ForumReply, Bookmark, UserLesson,
    AIConversation, AIMessage, Article, Course,
)
from app.modules.admin.schemas import (
    PlatformStats, UserGrowthPoint, EngagementMetrics,
    AdminUserResponse, AdminUserUpdate,
    AdminNotificationCreate, AnalyticsSummary,
)


async def get_platform_stats(
    db: AsyncSession,
) -> PlatformStats:
    users = await db.execute(select(func.count(User.id)))
    total_users = users.scalar() or 0
    active = await db.execute(
        select(func.count(User.id)).where(
            User.is_active.is_(True),
            User.created_at >= datetime.now(timezone.utc) - timedelta(days=30),
        )
    )
    active_users = active.scalar() or 0
    txns = await db.execute(select(func.count(Transaction.id)))
    total_txns = txns.scalar() or 0
    inv_sum = await db.execute(select(func.coalesce(func.sum(Invoice.total), 0)))
    total_inv = float(inv_sum.scalar() or 0)
    bps = await db.execute(select(func.count(BusinessPlan.id)))
    total_bp = bps.scalar() or 0
    topics = await db.execute(select(func.count(ForumTopic.id)))
    total_topics = topics.scalar() or 0
    convos = await db.execute(select(func.count(AIConversation.id)))
    total_convos = convos.scalar() or 0

    courses_count_result = await db.execute(select(func.count(Course.id)))
    courses_count = courses_count_result.scalar() or 0
    articles_count_result = await db.execute(
        select(func.count(Article.id)).where(Article.is_published.is_(True))
    )
    articles_count = articles_count_result.scalar() or 0

    return PlatformStats(
        total_users=total_users, active_users=active_users,
        total_transactions=total_txns, total_invoices=total_inv,
        total_business_plans=total_bp, total_forum_topics=total_topics,
        total_courses=courses_count, total_articles=articles_count,
        total_ai_conversations=total_convos,
    )


async def get_user_growth(
    db: AsyncSession, days: int = 30
) -> list[UserGrowthPoint]:
    from sqlalchemy import cast, Date
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(
            cast(User.created_at, Date).label("date"),
            func.count(User.id).label("count"),
        ).where(User.created_at >= cutoff)
         .group_by(cast(User.created_at, Date))
         .order_by("date")
    )
    return [UserGrowthPoint(date=str(row[0]), count=row[1]) for row in result.all()]


async def get_engagement_metrics(db: AsyncSession) -> EngagementMetrics:
    lessons = await db.execute(select(func.count(UserLesson.id)).where(UserLesson.completed.is_(True)))
    bookmarks = await db.execute(select(func.count(Bookmark.id)))
    replies = await db.execute(select(func.count(ForumReply.id)))
    msgs = await db.execute(select(func.count(AIMessage.id)))
    return EngagementMetrics(
        total_lessons_completed=lessons.scalar() or 0,
        total_quiz_attempts=(await db.execute(
            select(func.count(UserLesson.id)).where(UserLesson.score.isnot(None))
        )).scalar() or 0,
        total_bookmarks=bookmarks.scalar() or 0,
        total_forum_replies=replies.scalar() or 0,
        total_ai_messages=msgs.scalar() or 0,
    )


async def list_all_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    is_active: Optional[bool] = None,
    is_admin: Optional[bool] = None,
    search: Optional[str] = None,
) -> tuple[list[User], int]:
    query = select(User)
    count_query = select(func.count(User.id))
    if is_active is not None:
        query = query.where(User.is_active == is_active)
        count_query = count_query.where(User.is_active == is_active)
    if is_admin is not None:
        query = query.where(User.is_admin == is_admin)
        count_query = count_query.where(User.is_admin == is_admin)
    if search:
        search_filter = or_(
            User.full_name.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    total = (await db.execute(count_query)).scalar() or 0
    result = await db.execute(query.order_by(User.created_at.desc()).offset(skip).limit(limit))
    return list(result.scalars().all()), total


async def get_user_detail(user_id: UUID, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def update_user(user_id: UUID, data: AdminUserUpdate, db: AsyncSession) -> User:
    user = await get_user_detail(user_id, db)
    updates = data.model_dump(exclude_unset=True)
    for key, val in updates.items():
        if val is not None:
            setattr(user, key, val)
    await db.commit()
    await db.refresh(user)
    return user


async def send_admin_notification(data: AdminNotificationCreate, db: AsyncSession) -> int:
    count = 0
    for uid in data.user_ids:
        notif = Notification(
            user_id=uid,
            title=data.title,
            body=data.body,
            type=data.type,
            data=data.data or {"source": "admin"},
        )
        db.add(notif)
        count += 1
    await db.commit()
    return count


async def get_analytics_summary(
    db: AsyncSession,
    period_days: int = 30,
) -> AnalyticsSummary:
    cutoff = datetime.now(timezone.utc) - timedelta(days=period_days)
    new_users = (await db.execute(
        select(func.count(User.id)).where(User.created_at >= cutoff)
    )).scalar() or 0
    active_users = (await db.execute(
        select(func.count(User.id)).where(
            User.is_active.is_(True),
            User.created_at >= cutoff,
        )
    )).scalar() or 0
    txns_count = (await db.execute(
        select(func.count(Transaction.id)).where(Transaction.created_at >= cutoff)
    )).scalar() or 0
    txns_vol = (await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.created_at >= cutoff)
    )).scalar() or 0

    top_cats = await db.execute(
        select(
            Transaction.category,
            func.count(Transaction.id).label("count"),
        ).where(Transaction.created_at >= cutoff)
         .group_by(Transaction.category)
         .order_by(func.count(Transaction.id).desc())
         .limit(5)
    )
    categories = [{"category": str(row[0]), "count": row[1]} for row in top_cats.all()]

    return AnalyticsSummary(
        period=f"last_{period_days}_days",
        new_users=new_users,
        active_users=active_users,
        transactions_count=txns_count,
        transactions_volume=float(txns_vol),
        top_categories=categories,
    )
