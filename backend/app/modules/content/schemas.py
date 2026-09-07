from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, str):
            return v
        return str(v)


# --- Courses ---
import uuid

class QuizQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    options: list[str]
    correct_answer: int
    explanation: Optional[str] = None


class Quiz(BaseModel):
    questions: list[QuizQuestion]
    passing_score: int = 70


class LessonCreate(BaseModel):
    title: str
    content: str
    content_type: str = "text"
    video_url: Optional[str] = None
    duration_minutes: int = 10
    order: int = 0
    quiz: Optional[Quiz] = None


class CourseCreate(BaseModel):
    title: str
    description: str
    difficulty: str = "beginner"
    category: str
    thumbnail_url: Optional[str] = None
    duration_hours: float = 1.0
    is_published: bool = False
    lessons: list[LessonCreate] = []


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    category: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_hours: Optional[float] = None
    is_published: Optional[bool] = None


class LessonResponse(BaseModel):
    id: str
    course_id: str
    title: str
    content: str
    content_type: str
    video_url: Optional[str] = None
    duration_minutes: int
    order: int
    quiz: Optional[Quiz] = None


class CourseResponse(BaseModel):
    id: str
    title: str
    description: str
    difficulty: str
    category: str
    thumbnail_url: Optional[str] = None
    duration_hours: float
    is_published: bool
    lesson_count: int = 0
    enrolled_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    lessons: list[LessonResponse] = []


class QuizSubmission(BaseModel):
    lesson_id: str
    answers: list[int]
    course_id: str


class QuizResult(BaseModel):
    score: int
    total: int
    percentage: float
    passed: bool
    correct_answers: list[int]
    explanations: list[Optional[str]]


# --- Articles ---
class ArticleCreate(BaseModel):
    title: str
    summary: str
    content: str
    category: str
    author: str = "EcoFinwize Team"
    read_time_minutes: Optional[int] = None
    tags: list[str] = []
    cover_image_url: Optional[str] = None
    is_featured: bool = False


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    cover_image_url: Optional[str] = None
    is_featured: Optional[bool] = None
    is_published: Optional[bool] = None


class ArticleResponse(BaseModel):
    id: str
    title: str
    slug: str
    summary: str
    content: str
    category: str
    author: str
    read_time_minutes: int
    tags: list[str]
    cover_image_url: Optional[str] = None
    is_featured: bool
    is_published: bool
    view_count: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# --- Blog ---
class BlogPostCreate(BaseModel):
    title: str
    summary: str
    content: str
    category: str
    tags: list[str] = []
    cover_image_url: Optional[str] = None
    comments_enabled: bool = True


class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    cover_image_url: Optional[str] = None
    is_published: Optional[bool] = None
    comments_enabled: Optional[bool] = None


class BlogPostResponse(BaseModel):
    id: str
    title: str
    slug: str
    summary: str
    content: str
    category: str
    author: str
    cover_image_url: Optional[str] = None
    tags: list[str]
    is_published: bool
    view_count: int
    comment_count: int
    comments_enabled: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BlogCommentCreate(BaseModel):
    content: str


class BlogCommentResponse(BaseModel):
    id: str
    post_id: str
    user_id: str
    author_name: Optional[str] = None
    content: str
    is_approved: bool
    created_at: Optional[datetime] = None


# --- News ---
class NewsCreate(BaseModel):
    title: str
    summary: str
    content: str
    source: str
    source_url: Optional[str] = None
    category: str
    cover_image_url: Optional[str] = None
    is_breaking: bool = False


class NewsUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    category: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_breaking: Optional[bool] = None
    is_published: Optional[bool] = None


class NewsResponse(BaseModel):
    id: str
    title: str
    slug: str
    summary: str
    content: str
    source: str
    source_url: Optional[str] = None
    category: str
    cover_image_url: Optional[str] = None
    is_breaking: bool
    is_published: bool
    view_count: int
    published_date: Optional[datetime] = None
    created_at: Optional[datetime] = None


# --- Forum ---
class ForumTopicCreate(BaseModel):
    title: str
    content: str
    category: str
    tags: Optional[list[str]] = None


class ForumTopicUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_locked: Optional[bool] = None


class ForumTopicResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    content: str
    category: str
    tags: Optional[list[str]] = None
    is_pinned: bool
    is_locked: bool
    view_count: int
    reply_count: int
    last_activity_at: datetime
    created_at: datetime
    updated_at: datetime
    author_name: Optional[str] = None
    replies: list["ForumReplyResponse"] = []


class ForumReplyCreate(BaseModel):
    content: str


class ForumReplyResponse(BaseModel):
    id: UUID
    topic_id: UUID
    user_id: UUID
    content: str
    is_solution: bool
    created_at: datetime
    updated_at: datetime
    author_name: Optional[str] = None


# --- Bookmarks ---
class BookmarkCreate(BaseModel):
    content_type: str
    content_id: str


class BookmarkResponse(BaseModel):
    id: UUID
    user_id: UUID
    content_type: str
    content_id: str
    created_at: datetime


# --- Progress ---
class LessonProgressResponse(BaseModel):
    user_id: UUID
    content_type: str
    content_id: str
    completed: bool
    score: Optional[float] = None
    completed_at: Optional[datetime] = None


class CourseProgressResponse(BaseModel):
    course_id: str
    course_title: str
    total_lessons: int
    completed_lessons: int
    percentage: float
    passed_quizzes: int
    total_quizzes: int
