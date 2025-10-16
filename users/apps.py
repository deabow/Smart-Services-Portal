from __future__ import annotations

from django.apps import AppConfig


class UsersConfig(AppConfig):
	default_auto_field = "django.db.models.BigAutoField"
	name = "users"

	def ready(self):  # noqa: D401
		# Connect signals (e.g., auto-create superuser on migrate)
		from . import signals  # noqa: F401

