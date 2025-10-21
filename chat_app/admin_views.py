from __future__ import annotations

import json
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator

from .models import ChatRoom, Message, AdminMessage, ChatNotification
from users.models import User


@staff_member_required
def admin_chat_dashboard(request: HttpRequest) -> HttpResponse:
    """لوحة تحكم الإدارة للدردشة"""
    # إحصائيات عامة
    total_chat_rooms = ChatRoom.objects.count()
    active_chat_rooms = ChatRoom.objects.filter(is_active=True).count()
    total_messages = Message.objects.count()
    unread_notifications = ChatNotification.objects.filter(is_read=False).count()
    urgent_notifications = ChatNotification.objects.filter(
        is_read=False, 
        priority__gte=8
    ).count()
    
    # آخر الرسائل
    recent_messages = Message.objects.filter(
        message_type='user'
    ).order_by('-created_at')[:10]
    
    # الإشعارات العاجلة
    urgent_notifications_list = ChatNotification.objects.filter(
        is_read=False,
        priority__gte=8
    ).order_by('-created_at')[:5]
    
    # غرف الدردشة النشطة
    active_chats = ChatRoom.objects.filter(
        is_active=True
    ).annotate(
        message_count=Count('messages'),
        unread_count=Count('messages', filter=Q(messages__is_read=False))
    ).order_by('-updated_at')[:10]
    
    context = {
        'total_chat_rooms': total_chat_rooms,
        'active_chat_rooms': active_chat_rooms,
        'total_messages': total_messages,
        'unread_notifications': unread_notifications,
        'urgent_notifications': urgent_notifications,
        'recent_messages': recent_messages,
        'urgent_notifications_list': urgent_notifications_list,
        'active_chats': active_chats,
    }
    
    return render(request, 'chat_app/admin_dashboard.html', context)


@staff_member_required
def admin_chat_room(request: HttpRequest, chat_room_id: str) -> HttpResponse:
    """عرض غرفة دردشة محددة للإدارة"""
    chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
    
    # الحصول على جميع الرسائل باستثناء رسائل الإدارة لتجنب التكرار
    messages = chat_room.messages.exclude(message_type='admin').order_by('created_at')
    
    # الحصول على الرسائل الإدارية
    admin_messages = chat_room.admin_messages.all().order_by('created_at')
    
    # تحديث الإشعارات كمقروءة
    ChatNotification.objects.filter(
        chat_room=chat_room,
        is_read=False
    ).update(is_read=True)
    
    context = {
        'chat_room': chat_room,
        'messages': messages,
        'admin_messages': admin_messages,
    }
    
    return render(request, 'chat_app/admin_chat_room.html', context)


@staff_member_required
@require_http_methods(["POST"])
def send_admin_message(request: HttpRequest) -> JsonResponse:
    """إرسال رسالة إدارية"""
    try:
        data = json.loads(request.body)
        chat_room_id = data.get('chat_room_id')
        content = data.get('content', '').strip()
        message_type = data.get('message_type', 'admin')
        is_important = data.get('is_important', False)
        
        if not content:
            return JsonResponse({'error': 'الرسالة فارغة'}, status=400)
        
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        
        # إنشاء الرسالة الإدارية
        admin_message = AdminMessage.objects.create(
            chat_room=chat_room,
            admin_user=request.user,
            content=content,
            message_type=message_type,
            is_important=is_important
        )
        
        # إنشاء رسالة عادية في الدردشة
        message = Message.objects.create(
            chat_room=chat_room,
            message_type='admin',
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'message': 'تم إرسال الرسالة الإدارية بنجاح',
            'admin_message': {
                'id': str(admin_message.id),
                'content': admin_message.content,
                'message_type': admin_message.message_type,
                'is_important': admin_message.is_important,
                'created_at': admin_message.created_at.isoformat(),
                'admin_user': admin_message.admin_user.username
            },
            'message': {
                'id': str(message.id),
                'content': message.content,
                'message_type': message.message_type,
                'created_at': message.created_at.isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
def get_chat_rooms(request: HttpRequest) -> JsonResponse:
    """الحصول على قائمة غرف الدردشة"""
    try:
        # فلترة البحث
        search = request.GET.get('search', '')
        status_filter = request.GET.get('status', '')
        priority_filter = request.GET.get('priority', '')
        
        # بناء الاستعلام
        chat_rooms = ChatRoom.objects.annotate(
            message_count=Count('messages'),
            unread_count=Count('messages', filter=Q(messages__is_read=False)),
            admin_message_count=Count('admin_messages'),
            notification_count=Count('notifications', filter=Q(notifications__is_read=False))
        ).order_by('-updated_at')
        
        # تطبيق الفلاتر
        if search:
            chat_rooms = chat_rooms.filter(
                Q(user__username__icontains=search) |
                Q(user__full_name__icontains=search)
            )
        
        if status_filter == 'active':
            chat_rooms = chat_rooms.filter(is_active=True)
        elif status_filter == 'inactive':
            chat_rooms = chat_rooms.filter(is_active=False)
        
        if priority_filter:
            priority_value = int(priority_filter)
            chat_rooms = chat_rooms.filter(
                notifications__priority__gte=priority_value,
                notifications__is_read=False
            ).distinct()
        
        # التصفح
        page = request.GET.get('page', 1)
        paginator = Paginator(chat_rooms, 20)
        page_obj = paginator.get_page(page)
        
        chat_rooms_data = []
        for chat_room in page_obj:
            # الحصول على آخر رسالة
            last_message = chat_room.messages.last()
            last_message_data = None
            if last_message:
                last_message_data = {
                    'content': last_message.content[:100] + '...' if len(last_message.content) > 100 else last_message.content,
                    'message_type': last_message.message_type,
                    'created_at': last_message.created_at.isoformat()
                }
            
            chat_rooms_data.append({
                'id': str(chat_room.id),
                'user': {
                    'username': chat_room.user.username,
                    'full_name': chat_room.user.full_name,
                    'email': chat_room.user.email
                },
                'is_active': chat_room.is_active,
                'message_count': chat_room.message_count,
                'unread_count': chat_room.unread_count,
                'admin_message_count': chat_room.admin_message_count,
                'notification_count': chat_room.notification_count,
                'last_message': last_message_data,
                'created_at': chat_room.created_at.isoformat(),
                'updated_at': chat_room.updated_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'chat_rooms': chat_rooms_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'total_count': paginator.count
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
def get_notifications(request: HttpRequest) -> JsonResponse:
    """الحصول على الإشعارات"""
    try:
        notification_type = request.GET.get('type', '')
        is_read = request.GET.get('is_read', '')
        
        notifications = ChatNotification.objects.select_related(
            'chat_room__user', 'message'
        ).order_by('-priority', '-created_at')
        
        # تطبيق الفلاتر
        if notification_type:
            notifications = notifications.filter(notification_type=notification_type)
        
        if is_read == 'true':
            notifications = notifications.filter(is_read=True)
        elif is_read == 'false':
            notifications = notifications.filter(is_read=False)
        
        notifications_data = []
        for notification in notifications[:50]:  # آخر 50 إشعار
            notifications_data.append({
                'id': str(notification.id),
                'chat_room': {
                    'id': str(notification.chat_room.id),
                    'user': notification.chat_room.user.username
                },
                'message': {
                    'id': str(notification.message.id),
                    'content': notification.message.content[:100] + '...' if len(notification.message.content) > 100 else notification.message.content,
                    'message_type': notification.message.message_type
                },
                'notification_type': notification.notification_type,
                'priority': notification.priority,
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'notifications': notifications_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@require_http_methods(["POST"])
def mark_notification_read(request: HttpRequest) -> JsonResponse:
    """تحديد الإشعار كمقروء"""
    try:
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        
        notification = get_object_or_404(ChatNotification, id=notification_id)
        notification.is_read = True
        notification.save()
        
        return JsonResponse({
            'success': True,
            'message': 'تم تحديد الإشعار كمقروء'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
def get_chat_messages(request: HttpRequest, chat_room_id: str) -> JsonResponse:
    """الحصول على رسائل غرفة دردشة محددة"""
    try:
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        
        # الحصول على الرسائل العادية باستثناء رسائل الإدارة لتجنب التكرار
        messages = chat_room.messages.exclude(message_type='admin').order_by('created_at')
        
        # الحصول على الرسائل الإدارية
        admin_messages = chat_room.admin_messages.all().order_by('created_at')
        
        messages_data = []
        
        # إضافة الرسائل العادية
        for message in messages:
            messages_data.append({
                'id': str(message.id),
                'content': message.content,
                'message_type': message.message_type,
                'is_read': message.is_read,
                'created_at': message.created_at.isoformat(),
                'sender_type': 'user' if message.message_type == 'user' else 'bot'
            })
        
        # إضافة الرسائل الإدارية
        for admin_message in admin_messages:
            messages_data.append({
                'id': str(admin_message.id),
                'content': admin_message.content,
                'message_type': admin_message.message_type,
                'is_read': admin_message.is_read_by_user,
                'created_at': admin_message.created_at.isoformat(),
                'sender_type': 'admin',
                'admin_user': admin_message.admin_user.username,
                'is_important': admin_message.is_important
            })
        
        # ترتيب حسب التاريخ
        messages_data.sort(key=lambda x: x['created_at'])
        
        return JsonResponse({
            'success': True,
            'messages': messages_data,
            'chat_room': {
                'id': str(chat_room.id),
                'user': {
                    'username': chat_room.user.username,
                    'full_name': chat_room.user.full_name,
                    'email': chat_room.user.email
                },
                'is_active': chat_room.is_active
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

