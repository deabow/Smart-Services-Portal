from django.urls import path
from . import views, admin_views

app_name = 'chat'

urlpatterns = [
    # URLs للمستخدمين
    path('', views.chat_view, name='chat'),
    path('send-message/', views.send_message, name='send_message'),
    path('get-messages/', views.get_messages, name='get_messages'),
    path('get-stats/', views.get_user_stats, name='get_user_stats'),
    
    # URLs للإدارة
    path('admin/dashboard/', admin_views.admin_chat_dashboard, name='admin_dashboard'),
    path('admin/chat-room/<str:chat_room_id>/', admin_views.admin_chat_room, name='admin_chat_room'),
    path('admin/send-message/', admin_views.send_admin_message, name='admin_send_message'),
    path('admin/chat-rooms/', admin_views.get_chat_rooms, name='admin_get_chat_rooms'),
    path('admin/notifications/', admin_views.get_notifications, name='admin_get_notifications'),
    path('admin/mark-notification-read/', admin_views.mark_notification_read, name='admin_mark_notification_read'),
    path('admin/chat-messages/<str:chat_room_id>/', admin_views.get_chat_messages, name='admin_get_chat_messages'),
]
