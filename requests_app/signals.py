from __future__ import annotations

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import RequestStatus


@receiver(post_migrate)
def ensure_default_statuses(sender, **kwargs):
	for name in ("قيد المراجعة", "قيد التنفيذ", "مكتمل", "مرفوض"):
		RequestStatus.objects.get_or_create(name=name)

