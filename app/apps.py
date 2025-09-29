from __future__ import annotations

from django.apps import AppConfig


class AppConfigConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"
    verbose_name = "Credit Approval App"
