from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "finwize",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_ignore_result=False,
    beat_schedule={
        "aggregate-news-every-hour": {
            "task": "app.scripts.news_scheduler.aggregate_news_task",
            "schedule": 3600.0,
        },
    },
)
