from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select, func as sa_func, and_, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    User, Bookmark as BookmarkModel, ForumTopic, ForumReply, UserLesson,
    BadgeRule, UserBadge, Article, BlogPost, BlogComment, NewsArticle, Course,
)
from app.modules.content.schemas import (
    CourseCreate, CourseUpdate, CourseResponse, LessonResponse,
    ArticleCreate, ArticleUpdate, ArticleResponse,
    BlogPostCreate, BlogPostUpdate, BlogPostResponse,
    BlogCommentCreate, BlogCommentResponse,
    NewsCreate, NewsUpdate, NewsResponse,
    ForumTopicCreate, ForumTopicUpdate, ForumTopicResponse,
    ForumReplyCreate, ForumReplyResponse,
    BookmarkCreate, BookmarkResponse,
    QuizSubmission, QuizResult, CourseProgressResponse,
)
from app.modules.users.schemas import UserProfileResponse

import logging
logger = logging.getLogger(__name__)


def _slugify(title: str) -> str:
    import re
    s = title.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s)
    return s[:200]


async def _author_name(db: AsyncSession, user_id: UUID) -> str:
    result = await db.execute(select(User.full_name).where(User.id == user_id))
    row = result.first()
    if row and row.full_name:
        return row.full_name
    return "Unknown User"


# =============================================================================
# COURSES
# =============================================================================

async def create_course(data: CourseCreate, db: AsyncSession) -> str:
    now = datetime.now(timezone.utc)
    lessons = []
    for i, l in enumerate(data.lessons):
        lessons.append({
            "id": f"lesson_{i+1}",
            "title": l.title,
            "content": l.content,
            "content_type": l.content_type,
            "video_url": l.video_url,
            "duration_minutes": l.duration_minutes,
            "order": l.order or i + 1,
            "quiz": l.quiz.model_dump() if l.quiz else None,
        })
    course = Course(
        title=data.title,
        description=data.description,
        difficulty=data.difficulty,
        category=data.category,
        thumbnail_url=data.thumbnail_url,
        duration_hours=data.duration_hours,
        is_published=data.is_published,
        lessons=lessons,
        enrolled_count=0,
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return str(course.id)


async def update_course(course_id: str, data: CourseUpdate, db: AsyncSession) -> bool:
    result = await db.execute(select(Course).where(Course.id == UUID(course_id)))
    course = result.scalar_one_or_none()
    if not course:
        return False
    for field, val in data.model_dump(exclude_unset=True).items():
        if val is not None:
            setattr(course, field, val)
    course.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return True


async def get_course(course_id: str, db: AsyncSession) -> Optional[Course]:
    try:
        result = await db.execute(select(Course).where(Course.id == UUID(course_id)))
    except Exception:
        return None
    return result.scalar_one_or_none()


async def list_courses(
    db: AsyncSession,
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    published_only: bool = True,
    skip: int = 0,
    limit: int = 20,
) -> list[Course]:
    query = select(Course)
    if published_only:
        query = query.where(Course.is_published.is_(True))
    if category:
        query = query.where(Course.category == category)
    if difficulty:
        query = query.where(Course.difficulty == difficulty)
    result = await db.execute(query.order_by(Course.created_at.desc()).offset(skip).limit(limit))
    return list(result.scalars().all())


async def delete_course(course_id: str, db: AsyncSession) -> bool:
    result = await db.execute(select(Course).where(Course.id == UUID(course_id)))
    course = result.scalar_one_or_none()
    if not course:
        return False
    await db.delete(course)
    await db.commit()
    return True


async def enroll_in_course(course_id: str, db: AsyncSession) -> bool:
    result = await db.execute(select(Course).where(Course.id == UUID(course_id)))
    course = result.scalar_one_or_none()
    if not course:
        return False
    course.enrolled_count = (course.enrolled_count or 0) + 1
    await db.commit()
    return True


async def submit_quiz(
    user_id: UUID,
    course_id: str,
    data: QuizSubmission,
    db: AsyncSession,
) -> QuizResult:
    course = await get_course(course_id, db)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    lessons = course.lessons or []
    lesson = None
    for l in lessons:
        if l.get("id") == data.lesson_id:
            lesson = l
            break
    if not lesson or not lesson.get("quiz"):
        raise HTTPException(status_code=400, detail="Lesson has no quiz")

    questions = lesson["quiz"]["questions"]
    if len(data.answers) != len(questions):
        raise HTTPException(status_code=400, detail="Answer count mismatch")

    correct_answers = [q["correct_answer"] for q in questions]
    explanations = [q.get("explanation") for q in questions]
    score = sum(1 for i, ans in enumerate(data.answers) if ans == correct_answers[i])
    total = len(questions)
    percentage = (score / total) * 100
    passing_score = lesson["quiz"].get("passing_score", 70)
    passed = percentage >= passing_score

    exist = await db.execute(
        select(UserLesson).where(
            and_(UserLesson.user_id == user_id, UserLesson.content_id == data.lesson_id)
        )
    )
    existing = exist.scalar_one_or_none()
    if existing:
        existing.completed = passed
        existing.score = percentage
        existing.completed_at = datetime.now(timezone.utc)
    else:
        ul = UserLesson(
            user_id=user_id,
            content_type="lesson",
            content_id=data.lesson_id,
            completed=passed,
            score=percentage,
        )
        db.add(ul)
    await db.commit()

    if passed:
        all_lessons = lessons
        quiz_lesson_ids = [l["id"] for l in all_lessons if l.get("quiz")]
        completed_result = await db.execute(
            select(sa_func.count(UserLesson.id)).where(
                and_(
                    UserLesson.user_id == user_id,
                    UserLesson.content_id.in_(quiz_lesson_ids),
                    UserLesson.completed.is_(True),
                )
            )
        )
        completed_count = completed_result.scalar()
        if completed_count == len(quiz_lesson_ids) and len(quiz_lesson_ids) > 0:
            await _award_badge(user_id, "course_completion", course_id, db)

    return QuizResult(
        score=score,
        total=total,
        percentage=round(percentage, 1),
        passed=passed,
        correct_answers=correct_answers,
        explanations=explanations,
    )


async def mark_lesson_complete(
    user_id: UUID, lesson_id: str, db: AsyncSession
) -> bool:
    exist = await db.execute(
        select(UserLesson).where(
            and_(UserLesson.user_id == user_id, UserLesson.content_id == lesson_id)
        )
    )
    ul = exist.scalar_one_or_none()
    if ul:
        if not ul.completed:
            ul.completed = True
            ul.completed_at = datetime.now(timezone.utc)
            await db.commit()
        return True
    ul = UserLesson(
        user_id=user_id,
        content_type="lesson",
        content_id=lesson_id,
        completed=True,
    )
    db.add(ul)
    await db.commit()
    return True


async def get_course_progress(
    user_id: UUID, course_id: str, db: AsyncSession
) -> CourseProgressResponse:
    course = await get_course(course_id, db)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    lessons = course.lessons or []
    total_lessons = len(lessons)
    lesson_ids = [l["id"] for l in lessons if "id" in l]

    result = await db.execute(
        select(sa_func.count(UserLesson.id)).where(
            and_(
                UserLesson.user_id == user_id,
                UserLesson.content_id.in_(lesson_ids),
                UserLesson.completed.is_(True),
            )
        )
    )
    completed_count = result.scalar() or 0

    quiz_lesson_ids = [l["id"] for l in lessons if l.get("quiz") and "id" in l]
    result2 = await db.execute(
        select(sa_func.count(UserLesson.id)).where(
            and_(
                UserLesson.user_id == user_id,
                UserLesson.content_id.in_(quiz_lesson_ids),
                UserLesson.completed.is_(True),
            )
        )
    )
    passed_quizzes = result2.scalar() or 0

    percentage = round((completed_count / total_lessons) * 100, 1) if total_lessons > 0 else 0

    return CourseProgressResponse(
        course_id=course_id,
        course_title=course.title,
        total_lessons=total_lessons,
        completed_lessons=completed_count,
        percentage=percentage,
        passed_quizzes=passed_quizzes,
        total_quizzes=len(quiz_lesson_ids),
    )


# =============================================================================
# ARTICLES
# =============================================================================

async def create_article(data: ArticleCreate, author: str, db: AsyncSession) -> str:
    slug = _slugify(data.title)
    read_time = data.read_time_minutes or max(1, len(data.content.split()) // 200)
    article = Article(
        title=data.title,
        slug=slug,
        summary=data.summary,
        content=data.content,
        category=data.category,
        author=author,
        read_time_minutes=read_time,
        tags=data.tags,
        cover_image_url=data.cover_image_url,
        is_featured=data.is_featured,
        is_published=True,
        view_count=0,
    )
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return str(article.id)


async def update_article(article_id: str, data: ArticleUpdate, db: AsyncSession) -> bool:
    result = await db.execute(select(Article).where(Article.id == UUID(article_id)))
    article = result.scalar_one_or_none()
    if not article:
        return False
    updates = data.model_dump(exclude_unset=True)
    if "title" in updates:
        updates["slug"] = _slugify(updates["title"])
    for field, val in updates.items():
        if val is not None:
            setattr(article, field, val)
    article.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return True


async def get_article(article_id: str, db: AsyncSession) -> Optional[Article]:
    try:
        result = await db.execute(select(Article).where(Article.id == UUID(article_id)))
    except Exception:
        return None
    article = result.scalar_one_or_none()
    if article:
        article.view_count = (article.view_count or 0) + 1
        await db.commit()
    return article


async def get_article_by_slug(slug: str, db: AsyncSession) -> Optional[Article]:
    result = await db.execute(
        select(Article).where(Article.slug == slug, Article.is_published.is_(True))
    )
    article = result.scalar_one_or_none()
    if article:
        article.view_count = (article.view_count or 0) + 1
        await db.commit()
    return article


async def list_articles(
    db: AsyncSession,
    category: Optional[str] = None,
    featured_only: bool = False,
    skip: int = 0,
    limit: int = 20,
) -> list[Article]:
    query = select(Article).where(Article.is_published.is_(True))
    if category:
        query = query.where(Article.category == category)
    if featured_only:
        query = query.where(Article.is_featured.is_(True))
    result = await db.execute(query.order_by(Article.created_at.desc()).offset(skip).limit(limit))
    return list(result.scalars().all())


async def delete_article(article_id: str, db: AsyncSession) -> bool:
    result = await db.execute(select(Article).where(Article.id == UUID(article_id)))
    article = result.scalar_one_or_none()
    if not article:
        return False
    await db.delete(article)
    await db.commit()
    return True


# =============================================================================
# BLOG
# =============================================================================

async def create_blog_post(data: BlogPostCreate, author: str, db: AsyncSession) -> str:
    slug = _slugify(data.title)
    post = BlogPost(
        title=data.title,
        slug=slug,
        summary=data.summary,
        content=data.content,
        category=data.category,
        author=author,
        cover_image_url=data.cover_image_url,
        tags=data.tags,
        is_published=False,
        comments_enabled=data.comments_enabled,
        view_count=0,
        comment_count=0,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return str(post.id)


async def update_blog_post(post_id: str, data: BlogPostUpdate, db: AsyncSession) -> bool:
    result = await db.execute(select(BlogPost).where(BlogPost.id == UUID(post_id)))
    post = result.scalar_one_or_none()
    if not post:
        return False
    updates = data.model_dump(exclude_unset=True)
    if "title" in updates:
        updates["slug"] = _slugify(updates["title"])
    for field, val in updates.items():
        if val is not None:
            setattr(post, field, val)
    post.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return True


async def get_blog_post(post_id: str, db: AsyncSession) -> Optional[BlogPost]:
    try:
        result = await db.execute(select(BlogPost).where(BlogPost.id == UUID(post_id)))
    except Exception:
        return None
    post = result.scalar_one_or_none()
    if post:
        post.view_count = (post.view_count or 0) + 1
        await db.commit()
    return post


async def get_blog_post_by_slug(slug: str, db: AsyncSession) -> Optional[BlogPost]:
    result = await db.execute(
        select(BlogPost).where(BlogPost.slug == slug, BlogPost.is_published.is_(True))
    )
    post = result.scalar_one_or_none()
    if post:
        post.view_count = (post.view_count or 0) + 1
        await db.commit()
    return post


async def list_blog_posts(
    db: AsyncSession,
    category: Optional[str] = None,
    published_only: bool = True,
    skip: int = 0,
    limit: int = 20,
) -> list[BlogPost]:
    query = select(BlogPost)
    if published_only:
        query = query.where(BlogPost.is_published.is_(True))
    if category:
        query = query.where(BlogPost.category == category)
    result = await db.execute(query.order_by(BlogPost.created_at.desc()).offset(skip).limit(limit))
    return list(result.scalars().all())


async def delete_blog_post(post_id: str, db: AsyncSession) -> bool:
    result = await db.execute(select(BlogPost).where(BlogPost.id == UUID(post_id)))
    post = result.scalar_one_or_none()
    if not post:
        return False
    await db.delete(post)
    await db.commit()
    return True


# --- Blog Comments ---

async def create_blog_comment(
    post_id: str, data: BlogCommentCreate, user_id: UUID, db: AsyncSession
) -> str:
    result = await db.execute(select(BlogPost).where(BlogPost.id == UUID(post_id)))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    if not post.comments_enabled:
        raise HTTPException(status_code=403, detail="Comments are disabled on this post")

    name = await _author_name(db, user_id)
    comment = BlogComment(
        post_id=post.id,
        user_id=user_id,
        author_name=name,
        content=data.content,
        is_approved=True,
    )
    db.add(comment)
    post.comment_count = (post.comment_count or 0) + 1
    await db.commit()
    await db.refresh(comment)
    return str(comment.id)


async def list_blog_comments(post_id: str, db: AsyncSession, skip: int = 0, limit: int = 50) -> list[dict]:
    result = await db.execute(
        select(BlogComment)
        .where(BlogComment.post_id == UUID(post_id), BlogComment.is_approved.is_(True))
        .order_by(BlogComment.created_at.asc())
        .offset(skip).limit(limit)
    )
    comments = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "post_id": str(c.post_id),
            "user_id": str(c.user_id),
            "author_name": c.author_name,
            "content": c.content,
            "is_approved": c.is_approved,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in comments
    ]


async def delete_blog_comment(
    comment_id: str, db: AsyncSession, current_user_id: UUID, is_admin: bool = False
) -> bool:
    try:
        result = await db.execute(select(BlogComment).where(BlogComment.id == UUID(comment_id)))
    except Exception:
        raise HTTPException(status_code=404, detail="Comment not found")
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if not is_admin and comment.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Cannot delete another user's comment")
    post_id = comment.post_id
    await db.delete(comment)
    post_result = await db.execute(select(BlogPost).where(BlogPost.id == post_id))
    post = post_result.scalar_one_or_none()
    if post:
        post.comment_count = max(0, (post.comment_count or 1) - 1)
    await db.commit()
    return True


# =============================================================================
# NEWS
# =============================================================================

async def create_news(data: NewsCreate, db: AsyncSession) -> str:
    slug = _slugify(data.title)
    news = NewsArticle(
        title=data.title,
        slug=slug,
        summary=data.summary,
        content=data.content,
        source=data.source,
        source_url=data.source_url,
        category=data.category,
        cover_image_url=data.cover_image_url,
        is_breaking=data.is_breaking,
        is_published=True,
        view_count=0,
    )
    db.add(news)
    await db.commit()
    await db.refresh(news)
    return str(news.id)


async def update_news(news_id: str, data: NewsUpdate, db: AsyncSession) -> bool:
    result = await db.execute(select(NewsArticle).where(NewsArticle.id == UUID(news_id)))
    news = result.scalar_one_or_none()
    if not news:
        return False
    updates = data.model_dump(exclude_unset=True)
    if "title" in updates:
        updates["slug"] = _slugify(updates["title"])
    for field, val in updates.items():
        if val is not None:
            setattr(news, field, val)
    news.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return True


async def get_news(news_id: str, db: AsyncSession) -> Optional[NewsArticle]:
    try:
        result = await db.execute(select(NewsArticle).where(NewsArticle.id == UUID(news_id)))
    except Exception:
        return None
    news = result.scalar_one_or_none()
    if news:
        news.view_count = (news.view_count or 0) + 1
        await db.commit()
    return news


async def get_news_by_slug(slug: str, db: AsyncSession) -> Optional[NewsArticle]:
    result = await db.execute(
        select(NewsArticle).where(NewsArticle.slug == slug, NewsArticle.is_published.is_(True))
    )
    news = result.scalar_one_or_none()
    if news:
        news.view_count = (news.view_count or 0) + 1
        await db.commit()
    return news


async def list_news(
    db: AsyncSession,
    category: Optional[str] = None,
    breaking_only: bool = False,
    skip: int = 0,
    limit: int = 20,
) -> list[NewsArticle]:
    query = select(NewsArticle).where(NewsArticle.is_published.is_(True))
    if category:
        query = query.where(NewsArticle.category == category)
    if breaking_only:
        query = query.where(NewsArticle.is_breaking.is_(True))
    result = await db.execute(query.order_by(NewsArticle.published_date.desc()).offset(skip).limit(limit))
    return list(result.scalars().all())


async def delete_news(news_id: str, db: AsyncSession) -> bool:
    result = await db.execute(select(NewsArticle).where(NewsArticle.id == UUID(news_id)))
    news = result.scalar_one_or_none()
    if not news:
        return False
    await db.delete(news)
    await db.commit()
    return True


# =============================================================================
# FORUM
# =============================================================================

async def create_forum_topic(
    data: ForumTopicCreate, user_id: UUID, db: AsyncSession
) -> ForumTopic:
    topic = ForumTopic(
        user_id=user_id,
        title=data.title,
        content=data.content,
        category=data.category,
        tags={"tags": data.tags} if data.tags else None,
    )
    db.add(topic)
    await db.commit()
    await db.refresh(topic)
    return topic


async def get_forum_topic(topic_id: UUID, db: AsyncSession) -> Optional[ForumTopic]:
    result = await db.execute(
        select(ForumTopic).where(ForumTopic.id == topic_id)
    )
    topic = result.scalar_one_or_none()
    if topic:
        topic.view_count += 1
        await db.commit()
    return topic


async def list_forum_topics(
    db: AsyncSession,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[ForumTopic], int]:
    query = select(ForumTopic)
    count_query = select(sa_func.count(ForumTopic.id))
    if category:
        query = query.where(ForumTopic.category == category)
        count_query = count_query.where(ForumTopic.category == category)
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    result = await db.execute(
        query.order_by(ForumTopic.is_pinned.desc(), ForumTopic.last_activity_at.desc())
        .offset(skip).limit(limit)
    )
    topics = result.scalars().all()
    return list(topics), total


async def update_forum_topic(
    topic_id: UUID, data: ForumTopicUpdate, user_id: UUID, is_admin: bool, db: AsyncSession
) -> ForumTopic:
    topic = await get_forum_topic(topic_id, db)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    if topic.user_id != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Cannot edit another user's topic")

    for field in ("title", "content", "is_pinned", "is_locked"):
        val = getattr(data, field, None)
        if val is not None:
            setattr(topic, field, val)
    await db.commit()
    await db.refresh(topic)
    return topic


async def delete_forum_topic(topic_id: UUID, user_id: UUID, is_admin: bool, db: AsyncSession) -> bool:
    topic = await db.execute(select(ForumTopic).where(ForumTopic.id == topic_id))
    topic = topic.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    if topic.user_id != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Cannot delete another user's topic")
    await db.delete(topic)
    await db.commit()
    return True


async def create_forum_reply(
    topic_id: UUID, data: ForumReplyCreate, user_id: UUID, db: AsyncSession
) -> ForumReply:
    topic = await db.execute(select(ForumTopic).where(ForumTopic.id == topic_id))
    topic = topic.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    if topic.is_locked:
        raise HTTPException(status_code=403, detail="Topic is locked")

    reply = ForumReply(topic_id=topic_id, user_id=user_id, content=data.content)
    db.add(reply)
    topic.reply_count += 1
    topic.last_activity_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(reply)
    return reply


async def mark_reply_as_solution(
    reply_id: UUID, user_id: UUID, is_admin: bool, db: AsyncSession
) -> ForumReply:
    reply = await db.execute(select(ForumReply).where(ForumReply.id == reply_id))
    reply = reply.scalar_one_or_none()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    topic = await db.execute(select(ForumTopic).where(ForumTopic.id == reply.topic_id))
    topic = topic.scalar_one_or_none()
    if topic.user_id != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Only the topic author can mark a solution")
    reply.is_solution = True
    await db.commit()
    await db.refresh(reply)
    return reply


# =============================================================================
# BOOKMARKS
# =============================================================================

async def create_bookmark(data: BookmarkCreate, user_id: UUID, db: AsyncSession) -> BookmarkModel:
    existing = await db.execute(
        select(BookmarkModel).where(
            and_(
                BookmarkModel.user_id == user_id,
                BookmarkModel.content_type == data.content_type,
                BookmarkModel.content_id == data.content_id,
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already bookmarked")
    bm = BookmarkModel(user_id=user_id, content_type=data.content_type, content_id=data.content_id)
    db.add(bm)
    await db.commit()
    await db.refresh(bm)
    return bm


async def delete_bookmark(bookmark_id: UUID, user_id: UUID, db: AsyncSession) -> bool:
    result = await db.execute(
        select(BookmarkModel).where(
            and_(BookmarkModel.id == bookmark_id, BookmarkModel.user_id == user_id)
        )
    )
    bm = result.scalar_one_or_none()
    if not bm:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    await db.delete(bm)
    await db.commit()
    return True


async def list_bookmarks(
    user_id: UUID, content_type: Optional[str] = None, db: AsyncSession = None, skip: int = 0, limit: int = 20
) -> list[BookmarkModel]:
    query = select(BookmarkModel).where(BookmarkModel.user_id == user_id)
    if content_type:
        query = query.where(BookmarkModel.content_type == content_type)
    result = await db.execute(query.order_by(BookmarkModel.created_at.desc()).offset(skip).limit(limit))
    return list(result.scalars().all())


# =============================================================================
# BADGE AWARDING
# =============================================================================

async def _award_badge(user_id: UUID, badge_key: str, content_ref: str, db: AsyncSession):
    rule = await db.execute(select(BadgeRule).where(BadgeRule.key == badge_key))
    rule = rule.scalar_one_or_none()
    if not rule:
        return
    already = await db.execute(
        select(UserBadge).where(
            and_(
                UserBadge.user_id == user_id,
                UserBadge.badge_key == badge_key,
                UserBadge.content_ref == content_ref,
            )
        )
    )
    if already.scalar_one_or_none():
        return
    ub = UserBadge(user_id=user_id, badge_key=badge_key, content_ref=content_ref)
    db.add(ub)
    await db.commit()
