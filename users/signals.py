from __future__ import annotations

import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver


User = get_user_model()


@receiver(post_migrate)
def create_default_superuser(sender, **kwargs):
	# Only run for the users app
	if sender.name != 'users':
		return
		
	admin_email = os.environ.get("DEFAULT_ADMIN_EMAIL", "diabm4930@gmail.com")
	admin_password = os.environ.get("DEFAULT_ADMIN_PASSWORD", "admin123")
	username = os.environ.get("DEFAULT_ADMIN_USERNAME", "admin")
	
	try:
		if not User.objects.filter(is_superuser=True).exists():
			user, created = User.objects.get_or_create(username=username, defaults={"email": admin_email})
			if created:
				user.set_password(admin_password)
				user.is_superuser = True
				user.is_staff = True
				user.full_name = "المدير"
				user.save()
	except Exception:
		# Ignore errors during migration
		pass

