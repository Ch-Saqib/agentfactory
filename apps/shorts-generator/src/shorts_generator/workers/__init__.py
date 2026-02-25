"""Celery workers for async video generation.

This package provides Celery-based async task processing for:
- Single video generation
- Batch video generation
- Job cleanup and maintenance
"""

from shorts_generator.workers.celery_worker import celery_app

__all__ = ["celery_app"]
