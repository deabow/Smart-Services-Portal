from __future__ import annotations

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

from .models import PasswordResetRequest


User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ("id", "username", "email", "full_name", "phone", "national_id", "address", "is_staff", "is_active", "date_joined")
	list_display_links = ("username", "email")
	search_fields = ("username", "email", "full_name", "phone", "address", "national_id")
	list_filter = ("is_staff", "is_active", "date_joined")
	readonly_fields = ("date_joined", "last_login")
	fieldsets = (
		("المعلومات الأساسية", {
			"fields": ("username", "email", "password")
		}),
		("البيانات الشخصية", {
			"fields": ("first_name", "last_name", "full_name", "phone", "national_id", "address")
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


@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "national_id_display", "phone", "status_display", "created_at", "admin_user", "handled_at")
	list_display_links = ("id", "user")
	list_filter = ("status", "created_at", "handled_at")
	search_fields = ("user__username", "user__email", "user__full_name", "national_id", "phone", "reason")
	readonly_fields = ("created_at",)
	date_hierarchy = "created_at"
	ordering = ("-created_at",)
	
	fieldsets = (
		("معلومات الطلب", {
			"fields": ("user", "national_id", "phone", "reason", "status")
		}),
		("معلومات المعالجة", {
			"fields": ("admin_user", "admin_notes", "handled_at")
		}),
		("التواريخ", {
			"fields": ("created_at",),
			"classes": ("collapse",)
		}),
	)
	
	def national_id_display(self, obj):
		"""عرض الرقم القومي مع مؤشر التطابق"""
		user_national_id = obj.user.national_id if obj.user.national_id else "غير مسجل"
		if obj.national_id == user_national_id:
			return format_html(
				'{} <span class="badge bg-success">✓</span>',
				obj.national_id
			)
		else:
			return format_html(
				'{} <span class="badge bg-danger">✗</span> (المسجل: {})',
				obj.national_id, user_national_id
			)
	national_id_display.short_description = "الرقم القومي"
	
	def status_display(self, obj):
		"""عرض الحالة مع ألوان"""
		colors = {
			'pending': 'warning',
			'approved': 'info',
			'completed': 'success',
			'rejected': 'danger'
		}
		icons = {
			'pending': 'clock',
			'approved': 'check',
			'completed': 'check-circle',
			'rejected': 'times'
		}
		color = colors.get(obj.status, 'secondary')
		icon = icons.get(obj.status, 'circle')
		
		return format_html(
			'<span class="badge bg-{}">{}</span>',
			color,
			f'<i class="fas fa-{icon} me-1"></i>{obj.get_status_display()}'
		)
	status_display.short_description = "الحالة"

