from __future__ import annotations

from django.contrib import admin

from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "action", "timestamp")
	list_display_links = ("action",)
	search_fields = ("action", "user__username", "user__email")
	list_filter = ("timestamp", "user")
	readonly_fields = ("timestamp",)
	fieldsets = (
		("معلومات النشاط", {
			"fields": ("user", "action")
		}),
		("التوقيت", {
			"fields": ("timestamp",),
			"classes": ("collapse",)
		}),
	)
	ordering = ("-timestamp",)

