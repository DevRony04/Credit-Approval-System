from __future__ import annotations

from django.core.management.base import BaseCommand

from app.tasks import ingest_excel_data


class Command(BaseCommand):
    help = "Ingest Excel files from data directory into DB"

    def handle(self, *args, **options):
        # Run synchronously to ensure on startup we have data; in worker it'll be async
        try:
            created = ingest_excel_data.apply(args=()).get(disable_sync_subtasks=False)  # type: ignore
        except Exception:
            # Fallback to direct call if celery not running
            created = ingest_excel_data()  # type: ignore
        self.stdout.write(self.style.SUCCESS(f"Ingestion completed. New customers: {created}"))
