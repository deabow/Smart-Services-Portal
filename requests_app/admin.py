from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html

from .models import Request, RequestAttachment, RequestStatus


@admin.register(RequestStatus)
class RequestStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color_display", "description", "created_at")
    search_fields = ("name", "description")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at")
    
    def color_display(self, obj):
        if obj.color:
            return format_html(
                '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">{}</span>',
                obj.color, obj.name
            )
        return obj.name
    color_display.short_description = "عرض الحالة"


class RequestAttachmentInline(admin.TabularInline):
    model = RequestAttachment
    extra = 0
    readonly_fields = ("uploaded_at",)


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ("tracking_number", "title", "user", "full_name", "status", "status_display", "created_at", "updated_at")
    list_display_links = ("tracking_number", "title")
    list_filter = ("status", "created_at", "updated_at", "user")
    search_fields = ("title", "tracking_number", "full_name", "phone", "user__username", "user__email")
    readonly_fields = ("tracking_number", "created_at", "updated_at")
    date_hierarchy = "created_at"
    
    fieldsets = (
        ("معلومات الطلب", {
            "fields": ("tracking_number", "title", "description", "status")
        }),
        ("معلومات مقدم الطلب", {
            "fields": ("user", "full_name", "phone", "address")
        }),
        ("التواريخ", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    ordering = ("-created_at",)
    inlines = [RequestAttachmentInline]
    
    def status_display(self, obj):
        if obj.status and obj.status.color:
            return format_html(
                '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">{}</span>',
                obj.status.color, obj.status.name
            )
        return obj.status.name if obj.status else "غير محدد"
    status_display.short_description = "عرض الحالة"
    
    actions = ["mark_as_received", "mark_as_reviewing", "mark_as_in_progress", "mark_as_completed", "mark_as_rejected"]
    
    def mark_as_received(self, request, queryset):
        status = RequestStatus.objects.get(name="تم استلام الطلب")
        updated = queryset.update(status=status)
        self.message_user(request, f"تم تحديث {updated} طلب إلى حالة 'تم استلام الطلب'")
    mark_as_received.short_description = "تحديث إلى: تم استلام الطلب"
    
    def mark_as_reviewing(self, request, queryset):
        status = RequestStatus.objects.get(name="قيد المراجعة")
        updated = queryset.update(status=status)
        self.message_user(request, f"تم تحديث {updated} طلب إلى حالة 'قيد المراجعة'")
    mark_as_reviewing.short_description = "تحديث إلى: قيد المراجعة"
    
    def mark_as_in_progress(self, request, queryset):
        status = RequestStatus.objects.get(name="قيد التنفيذ")
        updated = queryset.update(status=status)
        self.message_user(request, f"تم تحديث {updated} طلب إلى حالة 'قيد التنفيذ'")
    mark_as_in_progress.short_description = "تحديث إلى: قيد التنفيذ"
    
    def mark_as_completed(self, request, queryset):
        status = RequestStatus.objects.get(name="مكتمل")
        updated = queryset.update(status=status)
        self.message_user(request, f"تم تحديث {updated} طلب إلى حالة 'مكتمل'")
    mark_as_completed.short_description = "تحديث إلى: مكتمل"
    
    def mark_as_rejected(self, request, queryset):
        status = RequestStatus.objects.get(name="مرفوض")
        updated = queryset.update(status=status)
        self.message_user(request, f"تم تحديث {updated} طلب إلى حالة 'مرفوض'")
    mark_as_rejected.short_description = "تحديث إلى: مرفوض"

