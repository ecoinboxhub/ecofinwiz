from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.modules.auth.dependencies import get_current_user
from app.models import User, Article, BlogPost, BlogComment, NewsArticle, Course
from app.modules.content import service
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

router = APIRouter()


# ---------------------------------------------------------------------------
# Helper: convert PostgreSQL model to response dict
# ---------------------------------------------------------------------------

def _article_to_response(article: Article) -> dict:
    return {
        "id": str(article.id),
        "title": article.title,
        "slug": article.slug,
        "summary": article.summary,
        "content": article.content,
        "category": article.category,
        "author": article.author,
        "read_time_minutes": article.read_time_minutes,
        "tags": article.tags if isinstance(article.tags, list) else [],
        "cover_image_url": article.cover_image_url,
        "is_featured": article.is_featured,
        "is_published": article.is_published,
        "view_count": article.view_count,
        "created_at": article.created_at,
        "updated_at": article.updated_at,
    }


def _blog_post_to_response(post: BlogPost) -> dict:
    return {
        "id": str(post.id),
        "title": post.title,
        "slug": post.slug,
        "summary": post.summary,
        "content": post.content,
        "category": post.category,
        "author": post.author,
        "cover_image_url": post.cover_image_url,
        "tags": post.tags if isinstance(post.tags, list) else [],
        "is_published": post.is_published,
        "view_count": post.view_count,
        "comment_count": post.comment_count,
        "comments_enabled": post.comments_enabled,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
    }


def _news_to_response(news: NewsArticle) -> dict:
    return {
        "id": str(news.id),
        "title": news.title,
        "slug": news.slug,
        "summary": news.summary,
        "content": news.content,
        "source": news.source,
        "source_url": news.source_url,
        "category": news.category,
        "cover_image_url": news.cover_image_url,
        "is_breaking": news.is_breaking,
        "is_published": news.is_published,
        "view_count": news.view_count,
        "published_date": news.published_date,
        "created_at": news.created_at,
    }


def _course_response(course: Course) -> CourseResponse:
    lessons_data = course.lessons or []
    lessons = []
    for l in lessons_data:
        q = l.get("quiz")
        if isinstance(q, list):
            q = {"questions": [{"question": x.get("question",""), "options": x.get("options",[]), "correct_answer": x.get("correct_answer",0)} for x in q], "passing_score": 70}
        elif q and isinstance(q, dict) and "questions" not in q:
            q = {"questions": [{"question": q.get("question",""), "options": q.get("options",[]), "correct_answer": q.get("correct_answer",0)}], "passing_score": 70}
        lessons.append(LessonResponse(
            id=l.get("id", ""),
            course_id=str(course.id),
            title=l["title"],
            content=l["content"],
            content_type=l.get("content_type", "text"),
            video_url=l.get("video_url"),
            duration_minutes=l.get("duration_minutes", 10),
            order=l.get("order", 0),
            quiz=q,
        ))
    return CourseResponse(
        id=str(course.id),
        title=course.title,
        description=course.description,
        difficulty=course.difficulty,
        category=course.category,
        thumbnail_url=course.thumbnail_url,
        duration_hours=float(course.duration_hours),
        is_published=course.is_published,
        lesson_count=len(lessons_data),
        enrolled_count=course.enrolled_count,
        created_at=course.created_at,
        updated_at=course.updated_at,
        lessons=lessons,
    )


def _lesson_response(course_id: str, lesson: dict) -> LessonResponse:
    q = lesson.get("quiz")
    if isinstance(q, list):
        q = {"questions": [{"question": x.get("question",""), "options": x.get("options",[]), "correct_answer": x.get("correct_answer",0)} for x in q], "passing_score": 70}
    elif q and isinstance(q, dict) and "questions" not in q:
        q = {"questions": [{"question": q.get("question",""), "options": q.get("options",[]), "correct_answer": q.get("correct_answer",0)}], "passing_score": 70}
    return LessonResponse(
        id=lesson.get("id", ""),
        course_id=course_id,
        title=lesson["title"],
        content=lesson["content"],
        content_type=lesson.get("content_type", "text"),
        video_url=lesson.get("video_url"),
        duration_minutes=lesson.get("duration_minutes", 10),
        order=lesson.get("order", 0),
        quiz=q,
    )


# =========================================================================
# COURSES
# =========================================================================

@router.post("/courses", status_code=201, tags=["Courses"])
async def create_course(
    data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    course_id = await service.create_course(data, db)
    return {"id": course_id}


@router.get("/courses", tags=["Courses"])
async def list_courses(
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    published_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    courses = await service.list_courses(db, category, difficulty, published_only, skip, limit)
    return [_course_response(c) for c in courses]


@router.get("/courses/{course_id}", tags=["Courses"])
async def get_course(
    course_id: str,
    db: AsyncSession = Depends(get_db),
):
    course = await service.get_course(course_id, db)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return _course_response(course)


@router.patch("/courses/{course_id}", tags=["Courses"])
async def update_course(
    course_id: str,
    data: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ok = await service.update_course(course_id, data, db)
    if not ok:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"updated": True}


@router.delete("/courses/{course_id}", status_code=204, tags=["Courses"])
async def delete_course(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ok = await service.delete_course(course_id, db)
    if not ok:
        raise HTTPException(status_code=404, detail="Course not found")


@router.post("/courses/{course_id}/enroll", tags=["Courses"])
async def enroll_course(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await service.enroll_in_course(course_id, db)
    return {"enrolled": True}


@router.get("/courses/{course_id}/lessons/{lesson_id}", tags=["Courses"])
async def get_lesson(
    course_id: str,
    lesson_id: str,
    db: AsyncSession = Depends(get_db),
):
    course = await service.get_course(course_id, db)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    for l in (course.lessons or []):
        if l.get("id") == lesson_id:
            return _lesson_response(course_id, l)
    raise HTTPException(status_code=404, detail="Lesson not found")


@router.post("/courses/{course_id}/lessons/{lesson_id}/complete", tags=["Courses"])
async def complete_lesson(
    course_id: str,
    lesson_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await service.mark_lesson_complete(user.id, lesson_id, db)
    return {"completed": True}


@router.post("/courses/{course_id}/lessons/{lesson_id}/quiz", tags=["Courses"])
async def submit_quiz(
    course_id: str,
    lesson_id: str,
    data: QuizSubmission,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data.lesson_id = lesson_id
    data.course_id = course_id
    result = await service.submit_quiz(user.id, course_id, data, db)
    return result


@router.get("/courses/{course_id}/progress", tags=["Courses"])
async def get_course_progress(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await service.get_course_progress(user.id, course_id, db)
    return result


# =========================================================================
# ARTICLES
# =========================================================================

@router.post("/articles", status_code=201, tags=["Articles"])
async def create_article(
    data: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    article_id = await service.create_article(data, user.full_name or "EcoFinwize Team", db)
    return {"id": article_id}


@router.get("/articles", tags=["Articles"])
async def list_articles(
    category: Optional[str] = Query(None),
    featured_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    articles = await service.list_articles(db, category, featured_only, skip, limit)
    return [_article_to_response(a) for a in articles]


@router.get("/articles/{article_id}", tags=["Articles"])
async def get_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
):
    article = await service.get_article(article_id, db)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return _article_to_response(article)


@router.get("/articles/slug/{slug}", tags=["Articles"])
async def get_article_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    article = await service.get_article_by_slug(slug, db)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return _article_to_response(article)


@router.patch("/articles/{article_id}", tags=["Articles"])
async def update_article(
    article_id: str,
    data: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ok = await service.update_article(article_id, data, db)
    if not ok:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"updated": True}


@router.delete("/articles/{article_id}", status_code=204, tags=["Articles"])
async def delete_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ok = await service.delete_article(article_id, db)
    if not ok:
        raise HTTPException(status_code=404, detail="Article not found")


# =========================================================================
# BLOG
# =========================================================================

@router.post("/blog", status_code=201, tags=["Blog"])
async def create_blog_post(
    data: BlogPostCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post_id = await service.create_blog_post(data, user.full_name or "EcoFinwize Team", db)
    return {"id": post_id}


@router.get("/blog", tags=["Blog"])
async def list_blog_posts(
    category: Optional[str] = Query(None),
    published_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    posts = await service.list_blog_posts(db, category, published_only, skip, limit)
    return [_blog_post_to_response(p) for p in posts]


@router.get("/blog/{post_id}", tags=["Blog"])
async def get_blog_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
):
    post = await service.get_blog_post(post_id, db)
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return _blog_post_to_response(post)


@router.get("/blog/slug/{slug}", tags=["Blog"])
async def get_blog_post_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    post = await service.get_blog_post_by_slug(slug, db)
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return _blog_post_to_response(post)


@router.patch("/blog/{post_id}", tags=["Blog"])
async def update_blog_post(
    post_id: str,
    data: BlogPostUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ok = await service.update_blog_post(post_id, data, db)
    if not ok:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return {"updated": True}


@router.delete("/blog/{post_id}", status_code=204, tags=["Blog"])
async def delete_blog_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ok = await service.delete_blog_post(post_id, db)
    if not ok:
        raise HTTPException(status_code=404, detail="Blog post not found")


# --- Blog Comments ---

@router.post("/blog/{post_id}/comments", status_code=201, tags=["Blog"])
async def create_blog_comment(
    post_id: str,
    data: BlogCommentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    comment_id = await service.create_blog_comment(post_id, data, user.id, db)
    return {"id": comment_id}


@router.get("/blog/{post_id}/comments", tags=["Blog"])
async def list_blog_comments(
    post_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    docs = await service.list_blog_comments(post_id, db, skip, limit)
    return docs


@router.delete("/blog/comments/{comment_id}", status_code=204, tags=["Blog"])
async def delete_blog_comment(
    comment_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await service.delete_blog_comment(comment_id, db, user.id)


# =========================================================================
# NEWS
# =========================================================================

@router.post("/news", status_code=201, tags=["News"])
async def create_news(
    data: NewsCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    news_id = await service.create_news(data, db)
    return {"id": news_id}


@router.get("/news", tags=["News"])
async def list_news(
    category: Optional[str] = Query(None),
    breaking_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    news = await service.list_news(db, category, breaking_only, skip, limit)
    return [_news_to_response(n) for n in news]


@router.get("/news/{news_id}", tags=["News"])
async def get_news(
    news_id: str,
    db: AsyncSession = Depends(get_db),
):
    news = await service.get_news(news_id, db)
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
    return _news_to_response(news)


@router.get("/news/slug/{slug}", tags=["News"])
async def get_news_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    news = await service.get_news_by_slug(slug, db)
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
    return _news_to_response(news)


@router.patch("/news/{news_id}", tags=["News"])
async def update_news(
    news_id: str,
    data: NewsUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ok = await service.update_news(news_id, data, db)
    if not ok:
        raise HTTPException(status_code=404, detail="News item not found")
    return {"updated": True}


@router.delete("/news/{news_id}", status_code=204, tags=["News"])
async def delete_news(
    news_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ok = await service.delete_news(news_id, db)
    if not ok:
        raise HTTPException(status_code=404, detail="News item not found")


# =========================================================================
# FORUM
# =========================================================================

@router.post("/forum/topics", status_code=201, tags=["Forum"])
async def create_topic(
    data: ForumTopicCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    topic = await service.create_forum_topic(data, user.id, db)
    return ForumTopicResponse(
        id=topic.id,
        user_id=topic.user_id,
        title=topic.title,
        content=topic.content,
        category=topic.category,
        tags=topic.tags.get("tags") if topic.tags else None,
        is_pinned=topic.is_pinned,
        is_locked=topic.is_locked,
        view_count=topic.view_count,
        reply_count=topic.reply_count,
        last_activity_at=topic.last_activity_at,
        created_at=topic.created_at,
        updated_at=topic.updated_at,
        author_name=await service._author_name(db, topic.user_id),
        replies=[],
    )


@router.get("/forum/topics", tags=["Forum"])
async def list_topics(
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    topics, total = await service.list_forum_topics(db, category, skip, limit)
    items = []
    for t in topics:
        items.append(ForumTopicResponse(
            id=t.id,
            user_id=t.user_id,
            title=t.title,
            content=t.content,
            category=t.category,
            tags=t.tags.get("tags") if t.tags else None,
            is_pinned=t.is_pinned,
            is_locked=t.is_locked,
            view_count=t.view_count,
            reply_count=t.reply_count,
            last_activity_at=t.last_activity_at,
            created_at=t.created_at,
            updated_at=t.updated_at,
            author_name=await service._author_name(db, t.user_id),
            replies=[],
        ))
    return {"items": items, "total": total}


@router.get("/forum/topics/{topic_id}", tags=["Forum"])
async def get_topic(
    topic_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    topic = await service.get_forum_topic(topic_id, db)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    replies = []
    for r in topic.replies:
        replies.append(ForumReplyResponse(
            id=r.id,
            topic_id=r.topic_id,
            user_id=r.user_id,
            content=r.content,
            is_solution=r.is_solution,
            created_at=r.created_at,
            updated_at=r.updated_at,
            author_name=await service._author_name(db, r.user_id),
        ))
    return ForumTopicResponse(
        id=topic.id,
        user_id=topic.user_id,
        title=topic.title,
        content=topic.content,
        category=topic.category,
        tags=topic.tags.get("tags") if topic.tags else None,
        is_pinned=topic.is_pinned,
        is_locked=topic.is_locked,
        view_count=topic.view_count,
        reply_count=topic.reply_count,
        last_activity_at=topic.last_activity_at,
        created_at=topic.created_at,
        updated_at=topic.updated_at,
        author_name=await service._author_name(db, topic.user_id),
        replies=replies,
    )


@router.patch("/forum/topics/{topic_id}", tags=["Forum"])
async def update_topic(
    topic_id: UUID,
    data: ForumTopicUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    topic = await service.update_forum_topic(topic_id, data, user.id, False, db)
    return ForumTopicResponse(
        id=topic.id,
        user_id=topic.user_id,
        title=topic.title,
        content=topic.content,
        category=topic.category,
        tags=topic.tags.get("tags") if topic.tags else None,
        is_pinned=topic.is_pinned,
        is_locked=topic.is_locked,
        view_count=topic.view_count,
        reply_count=topic.reply_count,
        last_activity_at=topic.last_activity_at,
        created_at=topic.created_at,
        updated_at=topic.updated_at,
        author_name=await service._author_name(db, topic.user_id),
        replies=[],
    )


@router.delete("/forum/topics/{topic_id}", status_code=204, tags=["Forum"])
async def delete_topic(
    topic_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await service.delete_forum_topic(topic_id, user.id, False, db)


@router.post("/forum/topics/{topic_id}/replies", status_code=201, tags=["Forum"])
async def create_reply(
    topic_id: UUID,
    data: ForumReplyCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    reply = await service.create_forum_reply(topic_id, data, user.id, db)
    return ForumReplyResponse(
        id=reply.id,
        topic_id=reply.topic_id,
        user_id=reply.user_id,
        content=reply.content,
        is_solution=reply.is_solution,
        created_at=reply.created_at,
        updated_at=reply.updated_at,
        author_name=await service._author_name(db, reply.user_id),
    )


@router.post("/forum/replies/{reply_id}/mark-solution", tags=["Forum"])
async def mark_solution(
    reply_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    reply = await service.mark_reply_as_solution(reply_id, user.id, False, db)
    return ForumReplyResponse(
        id=reply.id,
        topic_id=reply.topic_id,
        user_id=reply.user_id,
        content=reply.content,
        is_solution=reply.is_solution,
        created_at=reply.created_at,
        updated_at=reply.updated_at,
        author_name=await service._author_name(db, reply.user_id),
    )


@router.get("/forum/categories", tags=["Forum"])
async def list_forum_categories(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select, func
    from app.models import ForumTopic
    result = await db.execute(
        select(ForumTopic.category, func.count(ForumTopic.id))
        .group_by(ForumTopic.category)
        .order_by(func.count(ForumTopic.id).desc())
    )
    return [{"category": row[0], "count": row[1]} for row in result.all()]


# =========================================================================
# BOOKMARKS
# =========================================================================

@router.post("/bookmarks", status_code=201, tags=["Bookmarks"])
async def create_bookmark(
    data: BookmarkCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    bm = await service.create_bookmark(data, user.id, db)
    return BookmarkResponse(
        id=bm.id,
        user_id=bm.user_id,
        content_type=bm.content_type,
        content_id=bm.content_id,
        created_at=bm.created_at,
    )


@router.get("/bookmarks", tags=["Bookmarks"])
async def list_bookmarks(
    content_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    bms = await service.list_bookmarks(user.id, content_type, db, skip, limit)
    return [
        BookmarkResponse(id=b.id, user_id=b.user_id, content_type=b.content_type,
                         content_id=b.content_id, created_at=b.created_at)
        for b in bms
    ]


@router.delete("/bookmarks/{bookmark_id}", status_code=204, tags=["Bookmarks"])
async def delete_bookmark(
    bookmark_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await service.delete_bookmark(bookmark_id, user.id, db)


# =========================================================================
# BADGES
# =========================================================================

@router.get("/badges", tags=["Badges"])
async def list_badges(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.models import UserBadge
    from sqlalchemy import select
    result = await db.execute(
        select(UserBadge.badge_key, UserBadge.content_ref, UserBadge.earned_at)
        .where(UserBadge.user_id == user.id)
        .order_by(UserBadge.earned_at.desc())
    )
    return [
        {"badge_key": row[0], "content_ref": row[1], "earned_at": row[2]}
        for row in result.all()
    ]
