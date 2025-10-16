from __future__ import annotations

from django.contrib import admin
from django.contrib.auth import get_user_model


User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ("id", "username", "email", "full_name", "phone", "address", "is_staff", "is_active", "date_joined")
	list_display_links = ("username", "email")
	search_fields = ("username", "email", "full_name", "phone", "address")
	list_filter = ("is_staff", "is_active", "date_joined")
	readonly_fields = ("date_joined", "last_login")
	fieldsets = (
		("المعلومات الأساسية", {
			"fields": ("username", "email", "password")
		}),
		("البيانات الشخصية", {
			"fields": ("first_name", "last_name", "full_name", "phone", "address")
		}),
		("الصلاحيات", {
			"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
		}),
		("معلومات مهمة", {
			"fields": ("date_joined", "last_login"),
			"classes": ("collapse",)
		}),
	)
	ordering = ("-date_joined",)

