from django.contrib import admin
from .models import ChatRoom, Message, ChatRequest, ChatBotResponse, AdminMessage, ChatNotification


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'created_at', 'message_count')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'user__full_name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'عدد الرسائل'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat_room', 'message_type', 'content_preview', 'is_read', 'created_at')
    list_filter = ('message_type', 'is_read', 'created_at')
    search_fields = ('content', 'chat_room__user__username')
    readonly_fields = ('id', 'created_at')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'محتوى الرسالة'


@admin.register(ChatRequest)
class ChatRequestAdmin(admin.ModelAdmin):
    list_display = ('chat_room', 'suggested_title', 'status', 'user_approved', 'created_at')
    list_filter = ('status', 'user_approved', 'created_at')
    search_fields = ('suggested_title', 'suggested_description')
    readonly_fields = ('id', 'created_at')


@admin.register(ChatBotResponse)
class ChatBotResponseAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'action_type', 'response_preview', 'is_active')
    list_filter = ('action_type', 'is_active')
    search_fields = ('keyword', 'response')
    
    def response_preview(self, obj):
        return obj.response[:50] + '...' if len(obj.response) > 50 else obj.response
    response_preview.short_description = 'الرد'


@admin.register(AdminMessage)
class AdminMessageAdmin(admin.ModelAdmin):
    list_display = ['admin_user', 'chat_room', 'message_type', 'is_important', 'is_read_by_user', 'created_at']
    list_filter = ['message_type', 'is_important', 'is_read_by_user', 'created_at']
    search_fields = ['content', 'admin_user__username', 'chat_room__user__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(ChatNotification)
class ChatNotificationAdmin(admin.ModelAdmin):
    list_display = ['chat_room', 'notification_type', 'priority', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'priority', 'created_at']
    search_fields = ['chat_room__user__username', 'message__content']
    readonly_fields = ['created_at']
    ordering = ['-priority', '-created_at']