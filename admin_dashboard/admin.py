from __future__ import annotations

from django.contrib import admin

from .models import ActivityLog, SiteVisitor, VisitorStats


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


@admin.register(SiteVisitor)
class SiteVisitorAdmin(admin.ModelAdmin):
	list_display = ("id", "ip_address", "user", "page_visited", "visit_date")
	list_display_links = ("ip_address",)
	search_fields = ("ip_address", "user__username", "user__email", "page_visited")
	list_filter = ("visit_date", "user")
	readonly_fields = ("visit_date",)
	fieldsets = (
		("معلومات الزائر", {
			"fields": ("ip_address", "user", "page_visited", "session_key")
		}),
		("معلومات فنية", {
			"fields": ("user_agent",),
			"classes": ("collapse",)
		}),
		("التوقيت", {
			"fields": ("visit_date",),
			"classes": ("collapse",)
		}),
	)
	ordering = ("-visit_date",)
	date_hierarchy = "visit_date"


@admin.register(VisitorStats)
class VisitorStatsAdmin(admin.ModelAdmin):
	list_display = ("date", "total_visits", "unique_visitors", "registered_users", "guest_visitors")
	list_display_links = ("date",)
	list_filter = ("date",)
	readonly_fields = ("date", "total_visits", "unique_visitors", "registered_users", "guest_visitors")
	fieldsets = (
		("إحصائيات اليوم", {
			"fields": ("date", "total_visits", "unique_visitors", "registered_users", "guest_visitors")
		}),
	)
	ordering = ("-date",)
	date_hierarchy = "date"

