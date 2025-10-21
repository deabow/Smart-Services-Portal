from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
	full_name = models.CharField(max_length=255, blank=True)
	phone = models.CharField(max_length=20, blank=False, verbose_name="رقم الهاتف")
	address = models.CharField(max_length=255, blank=True)

	def __str__(self) -> str:  # pragma: no cover - simple display
		return self.username

