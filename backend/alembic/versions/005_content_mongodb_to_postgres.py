"""Migrate content from MongoDB to PostgreSQL

Revision ID: 005
Revises: 004
Create Date: 2026-07-03
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "articles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False, unique=True),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("author", sa.String(255), nullable=False),
        sa.Column("read_time_minutes", sa.Integer, server_default="5"),
        sa.Column("tags", JSONB, nullable=True),
        sa.Column("cover_image_url", sa.String(1024), nullable=True),
        sa.Column("is_featured", sa.Boolean, server_default="false"),
        sa.Column("is_published", sa.Boolean, server_default="false"),
        sa.Column("view_count", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_articles_slug", "articles", ["slug"], unique=True)
    op.create_index("idx_articles_category", "articles", ["category"])
    op.create_index("idx_articles_published", "articles", ["is_published", "created_at"])

    op.create_table(
        "blog_posts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False, unique=True),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("author", sa.String(255), nullable=False),
        sa.Column("cover_image_url", sa.String(1024), nullable=True),
        sa.Column("tags", JSONB, nullable=True),
        sa.Column("is_published", sa.Boolean, server_default="false"),
        sa.Column("view_count", sa.Integer, server_default="0"),
        sa.Column("comment_count", sa.Integer, server_default="0"),
        sa.Column("comments_enabled", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_blog_posts_slug", "blog_posts", ["slug"], unique=True)
    op.create_index("idx_blog_posts_category", "blog_posts", ["category"])
    op.create_index("idx_blog_posts_published", "blog_posts", ["is_published", "created_at"])

    op.create_table(
        "blog_comments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("post_id", UUID(as_uuid=True), sa.ForeignKey("blog_posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_name", sa.String(255), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("is_approved", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_blog_comments_post", "blog_comments", ["post_id"])
    op.create_index("idx_blog_comments_user", "blog_comments", ["user_id"])

    op.create_table(
        "news",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False, unique=True),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("source", sa.String(255), nullable=False),
        sa.Column("source_url", sa.String(1024), nullable=True),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("cover_image_url", sa.String(1024), nullable=True),
        sa.Column("is_breaking", sa.Boolean, server_default="false"),
        sa.Column("is_published", sa.Boolean, server_default="false"),
        sa.Column("view_count", sa.Integer, server_default="0"),
        sa.Column("published_date", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_news_slug", "news", ["slug"], unique=True)
    op.create_index("idx_news_category", "news", ["category"])
    op.create_index("idx_news_published", "news", ["is_published", "published_date"])

    op.create_table(
        "courses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("difficulty", sa.String(50), server_default="beginner"),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("thumbnail_url", sa.String(1024), nullable=True),
        sa.Column("duration_hours", sa.Float, server_default="1.0"),
        sa.Column("is_published", sa.Boolean, server_default="false"),
        sa.Column("lessons", JSONB, nullable=True),
        sa.Column("enrolled_count", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_courses_category", "courses", ["category"])
    op.create_index("idx_courses_published", "courses", ["is_published", "created_at"])


def downgrade() -> None:
    op.drop_table("courses")
    op.drop_table("news")
    op.drop_table("blog_comments")
    op.drop_table("blog_posts")
    op.drop_table("articles")
