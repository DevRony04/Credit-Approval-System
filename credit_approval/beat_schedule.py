from __future__ import annotations

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "ingest-excel-hourly": {
        "task": "app.tasks.ingest_excel_data",
        "schedule": crontab(minute=0, hour="*/6"),
    }
}

