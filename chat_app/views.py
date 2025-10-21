from __future__ import annotations

import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction

from .models import ChatRoom, Message, ChatRequest, AdminMessage, ChatNotification
from requests_app.models import Request, RequestStatus


@login_required
def chat_view(request: HttpRequest) -> HttpResponse:
    """عرض صفحة الدردشة"""
    # إنشاء أو الحصول على غرفة الدردشة للمستخدم
    chat_room, created = ChatRoom.objects.get_or_create(
        user=request.user,
        defaults={'is_active': True}
    )
    
    # الحصول على جميع رسائل جدول Message باستثناء رسائل الإدارة لتجنب التكرار مع AdminMessage
    messages = chat_room.messages.exclude(message_type='admin').order_by('created_at')
    admin_messages = chat_room.admin_messages.all().order_by('created_at')
    
    # إرسال رسالة ترحيب إذا كانت الغرفة جديدة
    if created:
        welcome_message = Message.objects.create(
            chat_room=chat_room,
            message_type='system',
            content='مرحباً بك في خدمة الدردشة! يمكنك التواصل مع الإدارة هنا. سيقوم أحد أعضاء الفريق بالرد عليك قريباً.'
        )
        # استبعد رسائل الإدارة من الجدول العام حتى لا تتكرر مع AdminMessage
        messages = chat_room.messages.exclude(message_type='admin').order_by('created_at')
    
    context = {
        'chat_room': chat_room,
        'messages': messages,
        'admin_messages': admin_messages,
    }
    return render(request, 'chat_app/chat.html', context)


@login_required
@require_http_methods(["POST"])
def send_message(request: HttpRequest) -> JsonResponse:
    """إرسال رسالة جديدة"""
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'error': 'الرسالة فارغة'}, status=400)
        
        # الحصول على غرفة الدردشة
        chat_room = get_object_or_404(ChatRoom, user=request.user)
        
        # حفظ رسالة المستخدم
        user_message = Message.objects.create(
            chat_room=chat_room,
            message_type='user',
            content=content
        )
        
        # إنشاء إشعار للإدارة
        ChatNotification.objects.create(
            chat_room=chat_room,
            message=user_message,
            notification_type='new_message',
            priority=1
        )
        
        return JsonResponse({
            'success': True,
            'user_message': {
                'id': str(user_message.id),
                'content': user_message.content,
                'created_at': user_message.created_at.isoformat(),
                'message_type': user_message.message_type
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_messages(request: HttpRequest) -> JsonResponse:
    """الحصول على الرسائل"""
    try:
        chat_room = get_object_or_404(ChatRoom, user=request.user)
        # استبعاد رسائل الإدارة من جدول Message لتجنب الازدواج مع AdminMessage
        messages = chat_room.messages.exclude(message_type='admin').order_by('created_at')
        admin_messages = chat_room.admin_messages.all().order_by('created_at')
        
        messages_data = []
        
        # إضافة الرسائل العادية
        for message in messages:
            messages_data.append({
                'id': str(message.id),
                'content': message.content,
                'created_at': message.created_at.isoformat(),
                'message_type': message.message_type,
                'is_read': message.is_read,
                'sender_type': 'user' if message.message_type == 'user' else 'system'
            })
        
        # إضافة الرسائل الإدارية
        for admin_message in admin_messages:
            messages_data.append({
                'id': str(admin_message.id),
                'content': admin_message.content,
                'created_at': admin_message.created_at.isoformat(),
                'message_type': admin_message.message_type,
                'is_read': admin_message.is_read_by_user,
                'sender_type': 'admin',
                'admin_user': admin_message.admin_user.username,
                'is_important': admin_message.is_important
            })
        
        # ترتيب حسب التاريخ
        messages_data.sort(key=lambda x: x['created_at'])
        
        return JsonResponse({
            'success': True,
            'messages': messages_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_user_stats(request: HttpRequest) -> JsonResponse:
    """الحصول على إحصائيات المستخدم"""
    try:
        # إحصائيات الطلبات
        total_requests = Request.objects.filter(user=request.user).count()
        completed_requests = Request.objects.filter(
            user=request.user, 
            status__name="مكتمل"
        ).count()
        pending_requests = Request.objects.filter(
            user=request.user, 
            status__name="قيد المراجعة"
        ).count()
        in_progress_requests = Request.objects.filter(
            user=request.user, 
            status__name="قيد التنفيذ"
        ).count()
        
        # إحصائيات الدردشة
        chat_room = ChatRoom.objects.filter(user=request.user).first()
        total_messages = 0
        if chat_room:
            total_messages = chat_room.messages.count()
        
        # آخر طلب
        last_request = Request.objects.filter(user=request.user).order_by('-created_at').first()
        last_request_data = None
        if last_request:
            last_request_data = {
                'title': last_request.title,
                'status': last_request.status.name,
                'tracking_number': last_request.tracking_number,
                'created_at': last_request.created_at.isoformat()
            }
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_requests': total_requests,
                'completed_requests': completed_requests,
                'pending_requests': pending_requests,
                'in_progress_requests': in_progress_requests,
                'total_messages': total_messages,
                'last_request': last_request_data
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)