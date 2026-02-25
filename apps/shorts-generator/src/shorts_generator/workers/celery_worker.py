"""Celery worker configuration and tasks for async video generation.

This module handles:
- Celery app configuration with Redis broker
- Async video generation tasks
- Job progress tracking
- Retry logic with exponential backoff
- Priority queue support
"""

import logging
import os
from datetime import timedelta

from celery import Celery, shared_task
from celery.exceptions import SoftTimeLimitExceeded, TimeLimitExceeded
from celery.schedules import crontab

from shorts_generator.core.config import settings

logger = logging.getLogger(__name__)

# Create Celery app
# Upstash Redis requires SSL - convert redis:// to rediss://
broker_url = settings.redis_url
if broker_url.startswith("redis://"):
    broker_url = broker_url.replace("redis://", "rediss://", 1)

celery_app = Celery(
    "shorts_generator",
    broker=broker_url,
    backend=broker_url,
    include=["shorts_generator.workers.tasks"],
    broker_use_ssl=True,
    redis_socket_connect_timeout=10,
    redis_socket_timeout=10,
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3300,  # 55 minutes soft limit
    task_acks_late=True,  # Only acknowledge if task succeeded
    task_reject_on_worker_lost=True,
    task_send_sent_event=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # Result settings
    result_expires=86400,  # Results expire after 24 hours
    result_extended=True,  # Store partial results
    # Worker settings
    worker_prefetch_multiplier=1,  # Disable prefetch for long tasks
    worker_max_tasks_per_child=10,  # Restart worker after 10 tasks
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Priority queues
    task_default_queue="normal",
    task_queues={
        "high": {
            "exchange": "high",
            "routing_key": "high",
        },
        "normal": {
            "exchange": "normal",
            "routing_key": "normal",
        },
        "low": {
            "exchange": "low",
            "routing_key": "low",
        },
    },
    task_default_exchange="normal",
    task_default_routing_key="normal",
    # Retry settings
    task_autoretry_for=(Exception,),  # Retry all exceptions by default
    task_retry_delay=60,  # Wait 60s before retry
    task_retry_max=3,  # Max 3 retries
    task_retry_backoff=True,  # Enable exponential backoff
    task_retry_backoff_max=600,  # Max 10 minutes between retries
    # Rate limiting (optional - prevents API abuse)
    task_annotations={
        "shorts_generator.workers.tasks.generate_short_task": {
            "rate_limit": "10/m",  # Max 10 generations per minute
        },
    },
    # Beat scheduler (for periodic tasks)
    beat_schedule={
        # Auto-generate shorts daily at 10 AM UTC
        "daily-auto-generate-shorts": {
            "task": "shorts_generator.workers.tasks.auto_generate_shorts",
            "schedule": crontab(hour=10, minute=0),  # 10 AM daily
        },
        # Cleanup old jobs at 2 AM daily
        "cleanup-old-jobs": {
            "task": "shorts_generator.workers.tasks.cleanup_old_jobs",
            "schedule": crontab(hour=2, minute=0),  # 2 AM daily
        },
        # Purge old videos at 3 AM daily
        "purge-old-videos": {
            "task": "shorts_generator.workers.tasks.purge_old_videos",
            "schedule": crontab(hour=3, minute=0),  # 3 AM daily
        },
    },
)


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task to verify Celery is working."""
    print(f"Request: {self.request!r}")


# Health check task
@shared_task
def health_check():
    """Simple health check task."""
    return {"status": "healthy", "service": "celery-worker"}


if __name__ == "__main__":
    # Start Celery worker
    celery_app.start()
