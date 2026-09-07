"""News aggregation Celery task.

Fetches news from RSS feeds and NewsAPI, stores in PostgreSQL.
"""
from app.core.celery_app import celery_app
from app.shared.logger import get_logger

logger = get_logger(__name__)


@celery_app.task(name="app.scripts.news_scheduler.aggregate_news_task")
def aggregate_news_task():
    import asyncio

    async def run():
        from app.services.news_service import aggregate_news
        from app.database.postgres import async_session_factory
        from app.models import NewsArticle
        from datetime import datetime, timezone
        import hashlib

        items = await aggregate_news()
        if not items:
            return 0

        count = 0
        async with async_session_factory() as session:
            for item in items:
                title_hash = hashlib.md5(item["title"].encode()).hexdigest()
                from sqlalchemy import select
                existing = await session.execute(
                    select(NewsArticle).where(NewsArticle.title == item["title"])
                )
                if existing.scalar_one_or_none():
                    continue

                news = NewsArticle(
                    title=item["title"],
                    summary=item.get("summary", ""),
                    content=item.get("summary", ""),
                    source=item.get("source_name", item.get("source", "Unknown")),
                    source_url=item.get("url", ""),
                    category=item.get("category", "general"),
                    region=item.get("region", "Pan-Africa"),
                    is_published=True,
                    view_count=0,
                )
                session.add(news)
                count += 1

            await session.commit()

        logger.info("News aggregation complete: %d new items", count)
        return count

    return asyncio.run(run())
