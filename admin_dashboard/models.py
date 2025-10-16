from __future__ import annotations

from django.conf import settings
from django.db import models


class ActivityLog(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
	action = models.CharField(max_length=255)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f"{self.user} - {self.action}"

