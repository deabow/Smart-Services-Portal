from __future__ import annotations

from django.apps import AppConfig


class RequestsAppConfig(AppConfig):
	default_auto_field = "django.db.models.BigAutoField"
	name = "requests_app"

	def ready(self):
		from . import signals  # noqa: F401

